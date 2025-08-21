__author__ = "Thomas Popp, Thomas@chriesibaum.com"
__copyright__ = "Copyright 2025, Chriesibaum GmbH"
__version__ = "0.2.0"

import time
import serial


class MCDUsbHubCtrl():
    def __init__(self, serial_port, baud_rate=19200, timeout=1):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout

        self.s = None

        self.MAX_PORTS = 6  # Maximum number of ports

        self.open()

    def __del__(self):
        self.close()

    def open(self):
        self.s = serial.Serial(self.serial_port,
                               self.baud_rate,
                               timeout=self.timeout)

    def close(self):
        if self.s is not None and self.s.is_open:
            self.s.close()

    def write_cmd(self, cmd, ret_size=0):
        if not self.s.is_open:
            raise Exception("Serial port is not open")

        for i in range(3):
            try:
                self.s.write(cmd)
                ret = self.s.read(ret_size)
            except serial.SerialException as e:
                print(f"Error occurred: {e}")
                time.sleep(0.1)
                self.s.flushInput()
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(0.1)
                self.s.flushInput()

            if len(ret) == ret_size:
                return ret
            else:
                print(f"Unexpected response length: {len(ret)}")
                time.sleep(0.1)

        raise Exception("Failed to get valid response")

    def switch_ports(self, ports_on_bits):
        cmd = f'P{ports_on_bits:02X}\r'.encode('utf-8')
        ret = self.write_cmd(cmd, 3)

        if ret == b'ok\r':
            return True
        else:
            raise Exception(f"Failed to switch ports, response: {ret}")

    def get_ports_status(self):
        cmd = 'RPP\r'.encode('utf-8')
        ret = self.write_cmd(cmd, 3)

        if len(ret) == 3:
            return int(ret[0:2])
        else:
            raise Exception(f"Failed to get port status, response: {ret}")

    def ena_port(self, port_num):
        """Enable a specific port by its number."""
        if port_num not in range(self.MAX_PORTS):
            raise ValueError(f"Port number must be between " +
                             f"0 and {self.MAX_PORTS - 1}")

        ports_status = self.get_ports_status()

        ports_status |= (1 << port_num)

        self.switch_ports(ports_status)

    def dis_port(self, port_num):
        """Disable a specific port by its number."""
        if port_num not in range(self.MAX_PORTS):
            raise ValueError(f"Port number must be between " +
                             f"0 and {self.MAX_PORTS - 1}")

        ports_status = self.get_ports_status()

        ports_status &= ~(1 << port_num)

        self.switch_ports(ports_status)

    def disable_all_ports(self):
        """Disable all ports."""
        self.switch_ports(0)
