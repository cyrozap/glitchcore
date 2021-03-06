#!/usr/bin/env python3

import argparse
import struct
import time

import serial


class GlitcherInitError(Exception):
    pass

class NotEnoughDataException(Exception):
    pass

class Glitcher:
    commands = {
        'TEST': ord(b'\r'),
        'READ': ord(b'R'),
        'WRITE': ord(b'W'),
    }

    def __init__(self, port, baudrate=115200, timeout=0.1, write_timeout=1, debug=False, verbose=False):
        self.debug = debug
        self.verbose = verbose or debug
        self.ser = serial.Serial(port, baudrate, timeout=timeout, write_timeout=write_timeout)
        self._send_bytes(b'\r' * 10)
        try:
            self._recv_bytes(1000)
        except:
            pass
        self._send_bytes([self.commands['TEST']])
        expected_ack = b'OK\r\n'
        ack = self._recv_bytes(len(expected_ack))
        if ack != expected_ack:
            raise GlitcherInitError("Invalid glitcher ACK bytes: {} ({})".format(ack.hex(), repr(ack)))

    def close(self):
        self.ser.close()

    def _send_bytes(self, data):
        data = bytes(data)
        if self.debug:
            print("-> {}".format(data.hex()))
        self.ser.write(data)

    def _recv_bytes(self, count):
        data = self.ser.read(count)
        if self.debug:
            print("<- {}".format(data.hex()))
        if len(data) != count:
            raise NotEnoughDataException
        return bytes(data)

    def get_dword(self):
        '''Read a little-endian 32-bit integer from the serial port.'''
        return struct.unpack('<I', self._recv_bytes(4))[0]

    def put_dword(self, dword):
        '''Write a little-endian 32-bit integer to the serial port.'''
        self._send_bytes(struct.pack('<I', dword))

    def readw(self, addr):
        '''Read a 32-bit word.

        addr: The 32-bit starting address as an int.
        '''
        self._send_bytes([self.commands['READ']])
        #self.put_dword(addr)
        self._send_bytes([addr & 0xff])

        word = self.get_dword()

        if self.verbose:
            print("0x{:08x} => 0x{:08x}".format(addr, word))

        return word

    def writew(self, addr, word):
        '''Write a 32 bit word.

        addr: A 32-bit address as an int.
        word: The 32-bit word to write.
        '''
        if self.verbose:
            print("0x{:08x} <= 0x{:08x}".format(addr, word))

        self._send_bytes([self.commands['WRITE']])
        #self.put_dword(addr)
        self._send_bytes([addr & 0xff])
        self.put_dword(word)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    args = parser.parse_args()

    glitcher = Glitcher(args.port, baudrate=args.baudrate)
    glitcher.verbose=True

    events = 16
    delay_seconds = 5
    duration_seconds = 3

    delay_ticks = 12e6 * delay_seconds
    duration_ticks = 12e6 * duration_seconds

    config = (
        (0x10, 0),
        (0x20, 0),
        (0x30, 0),
        (0x00, (0 << 4) | (0 << 2) | (0 << 1) | 0),
        (0x14, events),
        (0x24, delay_ticks),
        (0x34, duration_ticks),
        (0x30, 1),
        (0x20, 1),
        (0x10, 1),
    )

    for addr, data in config:
        glitcher.readw(addr)
        glitcher.writew(addr, int(data))
        glitcher.readw(addr)

    glitcher.verbose=False
    while True:
        event_trigger = (glitcher.readw(0x10) >> 1) & 1
        delay_trigger_delayed = (glitcher.readw(0x20) >> 1) & 1
        pulse = (glitcher.readw(0x30) >> 1) & 1
        fired = (glitcher.readw(0x30) >> 2) & 1
        print("event_trigger: {}, delay_trigger_delayed: {}, pulse: {}, fired: {}".format(event_trigger, delay_trigger_delayed, pulse, fired))
        event_count = glitcher.readw(0x18)
        delay_count = glitcher.readw(0x28)
        pulse_count = glitcher.readw(0x38)
        print("event_count: 0x{:08x}, delay_count: 0x{:08x}, pulse_count: 0x{:08x}".format(
                event_count, delay_count, pulse_count))
        if fired and not pulse:
            break
        time.sleep(1)


if __name__ == "__main__":
    main()
