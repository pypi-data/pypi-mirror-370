# Serial driver that runs in its own thread

# GSE Proprietary Software License
# Copyright (c) 2025 Global Satellite Engineering, LLC. All rights reserved.
# This software and associated documentation files (the "Software") are the proprietary and confidential information of Global Satellite Engineering, LLC ("GSE"). The Software is provided solely for the purpose of operating applications distributed by GSE and is subject to the following conditions:

# 1. NO RIGHTS GRANTED: This license does not grant any rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the Software.
# 2. RESTRICTED ACCESS: You may only access the Software as part of a GSE application package and only to the extent necessary for operation of that application package.
# 3. PROHIBITION ON REVERSE ENGINEERING: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
# 4. PROPRIETARY NOTICES: You must retain all copyright, patent, trademark, and attribution notices present in the Software.
# 5. NO WARRANTIES: The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# 6. LIMITATION OF LIABILITY: In no event shall GSE be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.
# 7. TERMINATION: This license will terminate automatically if you fail to comply with any of the terms and conditions of this license. Upon termination, you must destroy all copies of the Software in your possession.

# THE SOFTWARE IS PROTECTED BY UNITED STATES COPYRIGHT LAW AND INTERNATIONAL TREATY. UNAUTHORIZED REPRODUCTION OR DISTRIBUTION IS SUBJECT TO CIVIL AND CRIMINAL PENALTIES.

import serial
import time
import atexit
from threading import Thread, Lock
from queue import Queue, Empty
from . import utils
import re
from contextlib import contextmanager

DEFAULT_SER_TIMEOUT = 2.0               # timeout for all the serial reads

#####################################################################################################################
# Serial driver

class ProtocolError(Exception):
    def __init__(self, message, extra=None):
        self.message = message
        self.extra = extra
        super().__init__(self.message)

class Terminated(Exception):
    def __init__(self):
        super().__init__("serial port error")

# Parity values mirrored from pySerial
(PARITY_NONE, PARITY_ODD, PARITY_EVEN) = (serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN)

# I'm lazy
def ascii(d):
    return d.decode('ascii', errors='ignore')

# An infinite timeout can be specified by using either None or a negative timeout value
# This function convers all infinite timeout to None
def check_to(to):
    return None if to < 0 else to

# Receive thread. This threads reads data from the serial port in an infinite loop and sends it to the given
# qeuue. The only reason to make this into a thread is to be able to echo the received data as soon as possible.
class ReceiveThread(Thread):
    def __init__(self, ser, data_q, echo_rx=False, echo_rx_repls=None):
        super().__init__(daemon=True)
        self.ser, self.data_q = ser, data_q
        self.echo_rx, self.echo_rx_repls = echo_rx, echo_rx_repls or {}

    def run(self):
        ok = True
        self.ser.timeout = 1.0
        while ok:
            try: # read as much data as possible
                data = self.ser.read(max(1, self.ser.in_waiting))
                while self.ser.in_waiting > 0:
                    data += self.ser.read(self.ser.in_waiting)
                if data:
                    if self.echo_rx:
                        temp = ascii(data)
                        for i, r in self.echo_rx_repls.items():
                            temp = re.sub(i, r, temp)
                        utils.debug(temp, raw=True, sync=None)
                    self.data_q.put(data)
            except: # exit on error
                ok = False

    def exit(self):
        try:
            self.ser.dtr = False
            self.ser.close() # this will cause ser.read to raise an exception
        except:
            pass

# User facing driver class
class SerialHandler:
    def __init__(self, port, speed, parity=PARITY_NONE, echo_rx=False, echo_tx=False):
        self.ser, self.ser_port = None, port
        self.speed, self.parity = speed, parity
        self.rx_q = Queue() # data receive queue
        # Serial receive thread (not yet created)
        self.rx_thread = None
        self.back_buffer = b"" # data received from the serial thread and not processed yet
        # Automatically destroy thread on exit
        atexit.register(self.kill_handler)
        self.endline_char = b'\n' # default end of line char used by readline
        self.replacements = {} # replacement data
        self.echo_rx, self.echo_tx, self.echo_tx_repls = echo_rx, echo_tx, {} # echo data
        self.usage_cnt, self.auto_close = 0, False # auto-close variables
        self.usage_lock = Lock() # lock for usage_cnt above

    # Enable or disable auto-closing
    # When enabled and the usage_cnt becomes 0 after a call to release(), the port is closed automatically
    def set_auto_close(self, enable):
        self.auto_close = enable

    # Acquire the serial port (increment usage count)
    def acquire(self):
        with self.usage_lock:
            if (self.ser == None or self.rx_thread == None) and self.usage_cnt != 0:
                utils.warning(f"Expected usage_cnt 0 but value is {self.usage_cnt}, ser={self.ser}, rx_thread={self.rx_thread}")
                self.usage_cnt = 0
            self.usage_cnt += 1
            if self.usage_cnt == 1: # automatically open port if needed
                self.init()

    # Release the serial port (decrease usage count and close if it is 0 and the auto close flag is True)
    def release(self):
        with self.usage_lock:
            if self.usage_cnt > 0:
                self.usage_cnt -= 1
            if self.usage_cnt == 0 and self.auto_close:
                self.exit()

    # Context manager for the above acquire/release
    @contextmanager
    def keep(self):
        self.acquire()
        try:
            yield self
        finally:
            self.release()

    # Terminate receive thread and close serial port
    def exit(self):
        utils.debug2("Closing serial port")
        if self.rx_thread != None:
            try:
                self.rx_thread.exit()
                self.rx_thread.join()
            except:
                pass
            self.rx_thread = None
        if self.ser != None:
            try:
                self.ser.dtr = False
                self.ser.close()
            except:
                pass
            self.ser = None
        self.usage_cnt = 0

    # Exit handler if needed
    def kill_handler(self):
        self.exit()

    # Initilize the serial port (needs to be the first call before and I/O operations on the port)
    def init(self):
        utils.debug2("Opening serial port")
        if self.ser == None:
            try:
                self.ser = serial.Serial(self.ser_port, self.speed, parity=self.parity)
                self.ser.dtr = True
            except:
                utils.fatal("Unable to open serial port '{}'".format(self.ser_port))
        if self.rx_thread == None:
            self.rx_thread = ReceiveThread(self.ser, self.rx_q, self.echo_rx)
            self.rx_thread.start()
            self.back_buffer = b""

    # Set the default endline char
    def set_eol_char(self, c):
        self.endline_char = c

    # Setup a set of replacements that will be applied to the received data.
    # Call with None to disable replacements
    def set_replacements(self, r=None):
        self.replacements = r or {}

    # Apply user replacements to the given data
    def apply_replacements(self, data, repl):
        for i, r in repl.items():
            data = re.sub(i, r, data)
        return data

    # Read from the serial port until the tineout expires or the given function returns True
    # Returns the data read or None in case of timeout error
    def rx_generic(self, timeout, check_f):
        with self.keep():
            # Keep on reading until we read the required data or until the timeout expires
            to, elapsed, start_ts, res = check_to(timeout), 0, time.time(), None
            while (to == None) or (elapsed <= to): # continue while the timeout doesn't expire
                if (ok := check_f(self.back_buffer)) != None: # we already have enough data
                    res, self.back_buffer = self.back_buffer[:ok], self.back_buffer[ok:]
                    break
                # Check if the RX thread is still alive and exit if it isn't
                if not self.rx_thread.is_alive():
                    raise Terminated()
                # There isn't enough data, so wait for the RX thread to give us more without exceeding the timeout
                try:
                    self.back_buffer += self.rx_q.get(to != 0, to - elapsed if to != None else None)
                    elapsed = time.time() - start_ts
                except Empty: # timeout expired
                    break
            return res

    # Read maximum "cnt" bytes from the serial port, without exceeding the timeout
    def read_cnt(self, cnt, timeout=DEFAULT_SER_TIMEOUT, repl=False):
        if (res := self.rx_generic(timeout, lambda d: cnt if len(d) >= cnt else None)) == None:
            # Return all available data in case of timeout
            res, self.back_buffer = self.back_buffer, b""
        # Apply replacements if needed
        if repl != False:
            res = self.apply_replacements(res, repl if isinstance(repl, dict) else self.replacements)
        return res

    # Reads a single line from the output
    def read_line(self, timeout=DEFAULT_SER_TIMEOUT, endl_char=None, repl=True):
        data = self.read_until_char(endl_char or self.endline_char, timeout, include_char=True)
        if repl != False:
            data = self.apply_replacements(data, repl if isinstance(repl, dict) else self.replacements)
        return data

    # Send the given data to the serial port
    # "skip_echo" skips echoing the data even if echo_tx is enabled
    # Returns the numnber of bytes actually wrote
    def write(self, data, skip_echo=False):
        with self.keep():
            wrote = 0
            if isinstance(data, str):
                data = data.encode('ascii')
            if data:
                if self.echo_tx and not skip_echo:
                    temp = ascii(data)
                    for i, r in self.echo_tx_repls.items():
                        temp = re.sub(i, r, temp)
                    utils.debug(utils.yellow(temp), raw=True, sync=None)
                try:
                    wrote = self.ser.write(data)
                    self.ser.flush()
                except:
                    raise Terminated()
            return wrote

    # Reset the driver state
    def reset(self):
        self.back_buffer = b""

    # Set RX/TX echo
    def set_echo(self, echo_rx, echo_tx):
        self.echo_tx = echo_tx
        if self.rx_thread != None:
            self.rx_thread.echo_rx = echo_rx

    # Flush input buffers
    def flush_input(self):
        with self.keep():
            # Just keep on reading with 0 timeout until there's no more data
            while True:
                if not self.read_cnt(1024, 0):
                    break

    # Flush output buffers
    def flush_output(self):
        if self.ser != None and self.ser.is_open:
            self.ser.flush()

    # Set baud rate
    def set_baud(self, baud):
        self.speed = baud
        if self.ser != None and self.ser.is_open:
            self.ser.baudrate = baud

    # Send a break
    def send_break(self):
        with self.keep():
            self.ser.send_break()

    # Set the parity on the serial port
    def set_parity(self, p):
        self.parity = p
        if self.ser != None and self.ser.is_open:
            self.ser.parity = p

    # Waits for the given data, without exceeding the timeout.
    # If "ignore_case" is True, the case of the response is ignored (for both textual match and RE match)
    # If "verbose" is True, the received data is also displayed on the console
    # Returns all the data that was read until "data" was found, without "data" itself (unless append_input is True)
    def wait_for(self, data, timeout=DEFAULT_SER_TIMEOUT, append_input=False, ignore_case=False, verbose=False, endl_char=None, repl=True):
        with self.keep():
            now, out, timeout = time.time(), b'', check_to(timeout)
            while timeout == None or time.time() - now <= timeout:
                extra = self.read_line(timeout, endl_char, repl)
                if verbose:
                    print("'{}'".format(ascii(extra)))
                did_match = extra.lower() == data.lower() if ignore_case else extra == data
                if did_match:
                    return out + (extra if append_input else b'')
                out += extra
            raise ProtocolError("Timeout while waiting for '{}'".format(ascii(data)), out)

    # Wait for the given regular expression, without exceeding the timeout
    # If "ignore_case" is True, the case of the response is ignored (for both textual match and RE match)
    # If "verbose" is True, the received data is also displayed on the console
    # Returns all the data that was read until "data" was found, without "data" itself (unless append_input is True)
    # Also returns the result of re.search
    def wait_for_re(self, data, timeout=DEFAULT_SER_TIMEOUT, append_input=False, ignore_case=False, verbose=False, endl_char=None, repl=True):
        with self.keep():
            now, out, timeout = time.time(), b'', check_to(timeout)
            while timeout == None or time.time() - now <= timeout:
                extra = self.read_line(timeout, endl_char, repl)
                if verbose:
                    print("'{}'".format(ascii(extra)))
                did_match = re.search(data, extra, flags=re.I if ignore_case else 0)
                if did_match != None:
                    return out + (extra if append_input else b''), did_match
                out += extra
            raise ProtocolError("Timeout while waiting for '{}'".format(ascii(data)), out)

    # Read until the given char is received
    # If "include_char" is True, the returned data includes ch, otherwise it discards it
    def read_until_char(self, ch, timeout=DEFAULT_SER_TIMEOUT, include_char=True):
        assert len(ch) == 1
        if (res := self.rx_generic(timeout, lambda d: i + 1 if (i := d.find(ch[0])) != -1 else None)) == None:
            if check_to(timeout) != None:
                raise ProtocolError("Timeout while reading line")
            else:
                res = b""
        else:
            assert res[-1] == ch[0]
        return res if include_char else res[:-1]

    # Set echo RX replacement rules
    def set_echo_rx_replacements(self, r):
        if self.rx_thread != None:
            self.rx_thread.echo_rx_repls = r

    # Set echo TX replacement rules
    def set_echo_tx_replacements(self, r):
        self.echo_tx_repls = r

