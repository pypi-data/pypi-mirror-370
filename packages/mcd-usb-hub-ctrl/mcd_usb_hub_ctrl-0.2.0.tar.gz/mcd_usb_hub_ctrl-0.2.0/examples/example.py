#!/usr/bin/env python3

import time
from key_stroke import Key_Stroke
from mcd_usb_hub_ctrl import MCDUsbHubCtrl


# Configuration/Parameters
serial_port = '/dev/ttyUSB0'  # Adjust this to your serial port


def main():
    """Main function to show the basic usage of the MCDusbHub module."""

    port = 1

    m = MCDUsbHubCtrl(serial_port)

    k = Key_Stroke()
    print('Press ESC to terminate!')

    while True:

        # Enable port
        print(f'Enabling port {port}...')
        m.ena_port(port)

        time.sleep(0.5)

        # Disable port 1
        print(f'Disabling port {port}...')
        m.dis_port(port)

        # check whether a key from the list has been pressed
        if k.check(['\x1b', 'q', 'x']):
            break

        time.sleep(0.5)

    m.disable_all_ports()

    m.close()


if __name__ == '__main__':
    main()
