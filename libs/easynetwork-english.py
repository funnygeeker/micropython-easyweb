```python
import network

class Client(network.WLAN):
    def __init__(self):
        super().__init__(network.STA_IF)
        self.PM_NONE = 0
        self.PM_PERFORMANCE = 1
        self.PM_POWERSAVE = 2

    def connect(self, *args, **kwargs):
        """
        Connects to a wireless network.

        Args:
            ssid: Wireless network name.
            key: Wireless network password.
            bssid: Connects to a specific device with the specified MAC address if the network name matches (default: None).
            reconnects: The number of reconnection attempts (int, 0 for no limit, -1 for unlimited).
        """
        if not super().active():
            super().active(True)
        super().disconnect()
        super().connect(*args, **kwargs)

    def scan(self) -> list:
        """
        Scans for wireless networks.

        Returns:
            List of tuples containing information about each network:
            [(ssid, bssid, channel, RSSI, security, hidden), ...]
        """
        if not super().active():
            super().active(True)
            result = super().scan()
            super().active(False)
            return result
        else:
            return super().scan()

    def config(self, *args, **kwargs):
        """
        Gets or sets general network interface parameters.

        Args:
            pm: Power management setting.
                Client.PM_NONE - High-performance mode (0).
                Client.PM_PERFORMANCE - Balanced mode (1) (default).
                Client.PM_POWERSAVE - Power-saving mode (2).
            mac: Wireless network MAC address.
            ssid: Wireless network name (read-only).
            hostname: Hostname, length should not exceed 32 characters.
            tx_power: Maximum transmit power (dBm), generally ranging from 2 to 21.

        Example:
            # Get PM configuration info.
            config = client.config('pm')

            # Set IP configuration info.
            client.config(pm = 2)
        """
        return super().config(*args, **kwargs)

    def active(self, *args, **kwargs):
        """
        Sets or gets the active status of WLAN.

        Args:
            True or False (default: None for getting the status).

        Returns:
            None / bool
        """
        return super().active(*args, **kwargs)

    def status(self):
        """
        Gets the network connection status.

        Returns:
            network.STAT_IDLE - No connection and no activity (1000)
            network.STAT_CONNECTING - Connection in progress (1001)
            network.STAT_BEACON_TIMEOUT - Connection failed due to beacon timeout (200)
            network.STAT_NO_AP_FOUND - Connection failed due to no access point reply (201)
            network.STAT_WRONG_PASSWORD - Connection failed due to wrong password (202)
            network.STAT_ASSOC_FAIL - Connection failed due to association problem (203)
            network.STAT_HANDSHAKE_TIMEOUT - Connection failed due to handshake timeout (204)
            network.STAT_GOT_IP - Connection successful (1010)
        """
        return super().status()

    def isconnected(self) -> bool:
        """
        Checks if the network is connected.

        Returns:
            True: Connected.
            False: Not connected.
        """
        return super().isconnected()

    def disconnect(self):
        """
        Disconnects from the network.
        """
        if super().active():
            super().disconnect()
            super().active(False)  # Disable the Wi-Fi interface.

    def ifconfig(self, *args, **kwargs) -> tuple:
        """
        Gets or sets IP-level network interface parameters.

        Args:
            A tuple containing the IP address, subnet mask, gateway, and DNS server. The default value is None, which returns the network status.

        Returns:
            A tuple containing the IP address, subnet mask, gateway, and DNS server.

        Example:
            # Get IP configuration info.
            ip_config = client.ifconfig()

            # Set IP configuration info.
            client.ifconfig(('192.168.3.4', '255.255.255.0', '192.168.3.1', '8.8.8.8'))
        """
        return super().ifconfig(*args, **kwargs)



class AP(network.WLAN):
    def __init__(self):
        super().__init__(network.AP_IF)
        self.PM_NONE = 0
        self.PM_PERFORMANCE = 1
        self.PM_POWERSAVE = 2

    def config(self, *args, **kwargs):
        """
        Gets or sets general network interface parameters.

        Args:
            pm: Power management setting.
                AP.PM_NONE - High-performance mode (0).
                AP.PM_PERFORMANCE - Balanced mode (1) (default).
                AP.PM_POWERSAVE - Power-saving mode (2).
            mac: Wireless network MAC address.
            key: Connection password. Set the length to be greater than 8 or set it as None, '', or 0. When changing the password, the security is automatically changed as well (write-only, cannot read).
            hidden: Whether the network is hidden.
                0 - Visible.
                1 - Hidden.
            channel: Channel (generally 1-13).
            security: Authentication mode.
                0 - Open.
                1 - WEP.
                2 - WPA-PSK.
                3 - WPA2-PSK.
                4 - WPA/WPA2-PSK.
            ssid: Wireless network name.
            hostname: Hostname, length should not exceed 32 characters.
            tx_power: Maximum transmit power (dBm), generally ranging from 2 to 21.

        Example:
            # Get PM configuration info.
            config = client.config('pm')

            # Set IP configuration info.
            client.config(pm = 2)
        """
        if kwargs.get('key') is not None:
            if kwargs['key']:
                if super().config('security') == 0 and kwargs.get('security') is None:
                    if len(kwargs['key']) >= 8:
                        super().config(key=kwargs['key'], security=4)
                    else:
                        print('[ERROR] The password length should not be less than 8.')
            else:
                super().config(security=0)
        return super().config(*args, **kwargs)

    def ifconfig(self, *args, **kwargs) -> tuple:
        """
        Gets or sets IP-level network interface parameters.

        Args:
            A tuple containing the IP address, subnet mask, gateway, and DNS server. The default value is None, which returns the network status.

        Returns:
            A tuple containing the IP address, subnet mask, gateway, and DNS server.

        Example:
            # Get IP configuration info.
            ip_config = client.ifconfig()

            # Set IP configuration info.
            client.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '0.0.0.0'))
        """
        return super().ifconfig(*args, **kwargs)

    def isconnected(self) -> bool:
        """
        Checks if any device is connected.

        Returns:
            True: Device(s) connected.
            False: No device connected.
        """
        return super().isconnected()

    def active(self, *args, **kwargs):
        """
        Sets or gets the active status of WLAN.

        Args:
            True or False (default: None for getting the status).

        Returns:
            None / bool
        """
        return super().active(*args, **kwargs)
