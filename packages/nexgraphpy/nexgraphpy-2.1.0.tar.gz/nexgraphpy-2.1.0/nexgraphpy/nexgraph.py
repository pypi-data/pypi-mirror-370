#!/usr/bin/env python3
"""
Module: nexgraph.py
Description: NexGraph Python library for Nextech force gauges.
Author: Shawn Myratchapon
Website: https://simplyshawn.co.th
NexGraph: https://nexgraphapp.com
Version: 2.1.0
"""

from datetime import datetime
import time
import platform
import re
import threading
import matplotlib.pyplot as plt
import numpy as np
import serial
import serial.tools.list_ports


class NexGraph:
    """NexGraph Python Library
        - Finds and connects to Nextech devices over USB serial port
        - Send and receive data to and from the device
            - Force Mode:
                - Download saved values
                - Get device information
                - Query different force value formats
                - Send commands Print, Reset, Zero, Unit, and Mode
            - Torque Mode:
                - Read data from the device

        Attributes:
        - `device_info`: string: Device model, and details.
        - `device_path`: string: Path or port device is connected to.
        - `device_command`: dict: Commands to send to the device.
        - `usb_serial`: serial.Serial: Serial connection to the device.
        - `force_mode`: bool: Current force mode (True for tension, False for compression).

        Methods:
        - `find()`: Searches for connected USB serial devices.
        - `connect()`: Tries to connect to the device on device_path.
        - `get_info()`: Returns the device information.        
        - `zero()`: Zeroes the current value on the device.
        - `mode()`: Changes the mode (track and peak) on the device.
        - `unit()`: Changes the unit of measurement on the device.
        - `reset()`: Resets the value on the device.
        - `print_value()`: Returns the current value or max value from the device.
        - `peak_tension()`: Returns the current peak tension value.
        - `peak_compression()`: Returns the current peak compression value.        
        - `mini_output()`: Returns the current value in mini format.
        - `short_output()`: Returns the current value in short format.
        - `long_output()`: Returns the current value in long format.
        - `download(out_format="raw")`: Return the data stored on the device memory.
        - `read_torque_data(out_format="raw")`: Reads torque data from the device.
        - `disconnect()`: Disconnects from the Nextech Gauge.
    """

    def __init__(self, device_path=""):
        self.device_info: str = ""
        self.device_path: str = device_path if device_path else ""
        self.device_command: dict = {
            "!": '!'.encode(),  # device info
            "x": 'x'.encode(),  # print
            "p": 'p'.encode(),  # peak tension
            "c": 'c'.encode(),  # peak compression
            "l": 'l'.encode(),  # long output
            "v": 'v'.encode(),  # short output
            "L": 'L'.encode(),  # mini output
            "d": 'd'.encode(),  # download memory
            "z": 'z'.encode(),  # zero/tare
            "r": 'r'.encode(),  # reset values
            "u": 'u'.encode(),  # change unit
            "m": 'm'.encode()  # change mode
        }
        self.usb_serial = None
        self.force_mode: bool = True

    def find(self) -> bool:
        """Finds USB serial devices.

        Returns: boolean: "True" if a device was found.
        """
        usb_ports = serial.tools.list_ports.comports(include_links=True)
        device_found: bool = False

        for port in usb_ports:
            if port.manufacturer is None:
                continue
            if platform.system() == 'Windows':
                if "COM" in port.device and "FTDI" in port.manufacturer:
                    device_found = True
                    self.device_path = port.device
            elif platform.system() == 'Darwin':
                if "usbserial" in port.device and "FTDI" in port.manufacturer:
                    self.device_path = f"/dev/tty.{port.device.split('.')[1]}"
                    device_found = True
            elif platform.system() == 'Linux':
                if "ttyUSB" in port.device and "FTDI" in port.manufacturer:
                    self.device_path = port.device
                    device_found = True

        return device_found

    def connect(self, force_mode=True, rate="high") -> bool:
        """Connect to a force gauge or torque tester.

        Args:
            force_mode (bool): If True, connect in force mode; if False, connect in torque mode.
            rate (str): The baud rate ("high" or "low").

        Returns: boolean: "True" if connection was successful.
        """
        status: bool = False
        if self.device_path:
            if rate == "high":
                baud_rate = 38400
            elif rate == "low":
                baud_rate = 9600
            else:
                print("Invalid rate specified. Use 'high' or 'low'.")
                return status

            if force_mode:
                self.force_mode = True
            else:
                self.force_mode = False

            self.usb_serial = serial.Serial(port=self.device_path,
                                            bytesize=8,
                                            baudrate=baud_rate,
                                            timeout=2,
                                            stopbits=serial.STOPBITS_ONE)
            try:
                if self.force_mode:
                    self.usb_serial.write(self.device_command['!'])
                    time.sleep(0.1)

                    if self.usb_serial.in_waiting:
                        self.device_info += self.usb_serial.readline().decode("Ascii")
                        arr_info = self.device_info.split()

                        if arr_info and len(arr_info) > 2:
                            status = True

                else:
                    status = True

                return status
            except (OSError, serial.SerialException, PermissionError) as e:
                print(str(e))
                return status
        else:
            print("The device connection path is empty.")
            return status

    def get_info(self) -> str:
        """Gets the device details.        

        Returns:
            string: Model number, Current offset, Overload counter."""
        if self.force_mode:
            return self.device_info

        return ""

    def zero(self) -> bool:
        """Send the zero/tare command to the device.

        Returns:
            boolean: "True" if successful."""
        if self.force_mode:
            return self._send_command('z')

        return False

    def mode(self) -> bool:
        """Send the change mode command to the device.

        Returns:
            boolean: "True" if successful."""
        if self.force_mode:
            return self._send_command('m')

        return False

    def unit(self) -> bool:
        """Send the change unit command to the device.

        Returns:
            boolean: "True" if successful."""
        if self.force_mode:
            return self._send_command('u')

        return False

    def reset(self) -> bool:
        """Send the reset values command to the device.

        Returns:
            boolean: "True" if successful."""
        if self.force_mode:
            return self._send_command('r')

        return False

    def _send_command(self, command: str) -> bool:
        """Helper method to send a command to the Nextech Gauge.

        Args:
            command (str): The command to send to the device.

        Returns:
            bool: True if the command was sent successfully, False otherwise.
        """
        try:
            if not self.usb_serial:
                print("Error: Device is not connected.")
                return False

            self.usb_serial.write(self.device_command[command])
            return True
        except (OSError, serial.SerialException) as e:
            print(str(e))
            return False

    def print_value(self) -> str:
        """Send a print command to the device.

        Returns:
            boolean: "True" if successful."""
        if self.force_mode:
            return self._get_output('x')

        return ""

    def peak_tension(self) -> str:
        """Get the current peak tension value from the device.

        Returns:
            string: Current peak tension value."""
        if self.force_mode:
            return self._get_output('p')

        return ""

    def peak_compression(self) -> str:
        """Get the current peak compression value from the device.

        Returns:
            string: Current peak compression value."""
        if self.force_mode:
            return self._get_output('c')

        return ""

    def mini_output(self) -> str:
        """Get mini output from Nextech Gauge.

        Returns:
            str: Current value from the device. Mini format.
        """
        if self.force_mode:
            return self._get_output('L')

        return ""

    def short_output(self) -> str:
        """Get short output from Nextech Gauge.

        Returns:
            str: Current value from the device. Short format.
        """
        if self.force_mode:
            return self._get_output('v')

        return ""

    def long_output(self) -> str:
        """Get the long output from Nextech Gauge.

        Returns:
            str: Current value from the device. Long format.
        """
        if self.force_mode:
            return self._get_output('l')

        return ""

    def _get_output(self, command_key: str) -> str:
        """Helper method to get output from Nextech Gauge.

        Args:
            command_key (str): The command key to send to the device.

        Returns:
            str: Current value from the device.
        """
        try:
            if not self.usb_serial:
                print("Error: Device is not connected.")
                return ""

            self.usb_serial.write(self.device_command[command_key])
            time.sleep(0.1)
            s_output: str = ""
            while self.usb_serial.in_waiting:
                s_output += self.usb_serial.readline().decode("Ascii")
            return s_output
        except (OSError, serial.SerialException) as e:
            print(str(e))
            return ""

    def download(self, out_format="raw", gen_chart=False) -> str:
        """Download stored data from device memory.

        Args:
            out_format (str): The format of the output data. Values: ['raw', 'csv'].
            gen_chart (bool): Whether to generate a chart from the data.

        Returns:
            string: Stored tension and compression values."""
        try:
            if out_format not in ["raw", "csv"]:
                print(
                    "Error: Unsupported format. Use 'raw' (default) or 'csv'")
                return ""

            if not self.force_mode:
                return ""

            if not self.usb_serial:
                print("Error: Device is not connected.")
                return ""

            mem_data: str = ""
            self.usb_serial.write(self.device_command['d'])
            time.sleep(0.1)

            while self.usb_serial.in_waiting > 0:
                try:
                    raw_data = self.usb_serial.read_all()
                    if raw_data:
                        mem_data += raw_data.decode("Ascii")
                    time.sleep(0.1)
                except UnicodeDecodeError:
                    continue

            if gen_chart:
                self._save_mem_chart(mem_data)

            if out_format == "csv":
                csv_data = ""
                for line in mem_data.splitlines():
                    csv_data += line.strip().replace(' ', ',') + "\n"
                mem_data = csv_data

            return mem_data
        except (OSError, serial.SerialException) as e:
            print(str(e))
            return ""

    def _save_mem_chart(self, chart_data: str):
        """
        Generate a bar chart and save the image to a file.

        Args:
            chart_data (str): Memory data to create a chart from.
        """
        try:
            # Parse the chart data
            lines = chart_data.strip().split('\n')
            values = []
            labels = []

            for line in lines:
                parts = line.split(' ')
                if len(parts) > 3:
                    labels.append(parts[0].strip())
                    values.append(float(parts[3].strip()))

            # Create a bar chart
            x = np.arange(len(labels))
            plt.figure(figsize=(10, 6))
            plt.bar(x, values, color='blue')
            plt.xlabel('Labels')
            plt.ylabel('Values')
            plt.title('Memory Data Chart')
            plt.xticks(x, labels, rotation=45)

            # Save the chart to a file
            plt.tight_layout()
            imagefile = f"memory-data-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
            plt.savefig(imagefile)
            plt.close()
        except (IndexError, PermissionError, OSError) as e:
            print(str(e))

    def read_torque_data(self, out_format="raw", gen_chart=False) -> str:
        """Read torque data from the device.

        Args:
            out_format (str): The format of the output data. Values: ['raw', 'csv'].
            gen_chart (bool): Whether to generate a chart from the data.

        Returns:
            string: Torque values."""
        try:
            if out_format not in ["raw", "csv"]:
                print(
                    "Error: Unsupported format. Use 'raw' (default) or 'csv'.")
                return ""

            if self.force_mode:
                return ""

            if not self.usb_serial:
                print("Error: Device is not connected.")
                return ""

            stop_event = threading.Event()
            torque_data = []

            def serial_reader():
                while not stop_event.is_set():
                    if self.usb_serial and self.usb_serial.in_waiting > 0:
                        line = self.usb_serial.read_all()
                        if line:
                            torque_data.append(line.decode("Ascii").strip())
                    else:
                        time.sleep(0.1)

            reader_thread = threading.Thread(target=serial_reader)
            reader_thread.start()

            input("Press Enter to stop reading torque data...\n")
            stop_event.set()
            reader_thread.join()

            tor_data = ""
            tmp_data = ""
            dts_pattern = re.compile(
                r"^\s*(\w+)\s*([+-])\s*([\d\.]+)\s*([^\d\s].+)$")
            dtt_pattern = re.compile(
                r"^\s*\(?\s*([\w ]+)\s*,\s*([+-])\s*,\s*([\d\.]+)\s*,\s*([^\d,]+)\s*,*,\s*([\d\/ :]+)\s*,?\s*([^\)]*)\)?$")
            for line in torque_data:
                if dts_pattern.match(tmp_data) or dtt_pattern.match(tmp_data):
                    tor_data += tmp_data + "\n"
                    tmp_data = ""
                if dts_pattern.match(line) or dtt_pattern.match(line):
                    tor_data += line + "\n"
                else:
                    tmp_data += line

            if gen_chart:
                self._save_tor_chart(tor_data)

            if out_format == "csv":
                csv_data = ""
                for line in tor_data.splitlines():
                    if '(' in line:
                        csv_data += line.strip().replace('(', '').replace(')', '') + "\n"
                    else:
                        csv_data += line.replace(' ', ',') + "\n"

                tor_data = csv_data

            return tor_data

        except (OSError, serial.SerialException) as e:
            print(str(e))
            return ""

    def _save_tor_chart(self, chart_data: str):
        """
        Generate a bar chart and save the image to a file.

        Args:
            chart_data (str): Memory data to create a chart from.
        """
        try:
            # Parse the chart data
            lines = chart_data.strip().split('\n')
            if len(lines) == 0:
                return

            values = []
            labels = []

            counter = 0
            v_idx = 3
            s_char = ' '
            if '(' in lines[0]:
                v_idx = 2
                s_char = ','

            for line in lines:
                parts = line.split(s_char)
                if len(parts) > 3:
                    labels.append(counter)
                    values.append(float(parts[v_idx].strip()))
                    counter += 1

            # Create a bar chart
            x = np.arange(len(labels))
            plt.figure(figsize=(10, 6))
            plt.bar(x, values, color='blue')
            plt.xlabel('Labels')
            plt.ylabel('Values')
            plt.title('Torque Data Chart')
            plt.xticks(x, labels, rotation=45)

            # Save the chart to a file
            plt.tight_layout()
            imagefile = f"torque-data-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
            plt.savefig(imagefile)
            plt.close()
        except (IndexError, PermissionError, OSError) as e:
            print(str(e))

    def disconnect(self) -> bool:
        """Disconnect from the Nextech Gauge.

        Returns:
            boolean: "True" if garcefully disconnected."""
        status: bool = False
        try:
            if not self.usb_serial:
                print("Error: Device is not connected.")
                return False

            self.usb_serial.close()
            self.usb_serial = None
            status = True
            return status
        except (OSError, serial.SerialException) as e:
            print(str(e))
            return status
