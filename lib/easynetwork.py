import network


def _active(func):
    """
    检查 WLAN 是否开启，若未开启，则开启后关闭
    """
    def change_active(self, *args, **kwargs):
        if not self.active():  # wlan 不常用时尽量减小功耗
            self.active(True)
            result = func(self, *args, **kwargs)
            self.active(False)
            return result
        else:
            return func(self, *args, **kwargs)

    return change_active


class Client(network.WLAN):
    def __init__(self):
        super().__init__(network.STA_IF)
        self.PM_NONE = 0
        self.PM_PERFORMANCE = 1
        self.PM_POWERSAVE = 2

    def connect(self, *args, **kwargs):
        """
        连接无线网络

        Args:
            ssid: 无线网络名称
            key: 无线网络密码
            bssid: 无线网络名称相符时，连接指定 MAC地址 的设备，（默认不指定）
            reconnects: 重新连接尝试次数（int, 0=无，-1=无限制）
        """
        super().active(True)
        super().disconnect()
        super().connect(*args, **kwargs)

    @_active
    def scan(self) -> list:
        """
        扫描无线网络

        Returns:
            List[Tuple[bytes, bytes, int, int, int, bool]]
            [(ssid, bssid, channel, RSSI, security, hidden), ...]
        """
        return super().scan()

    @_active
    def config(self, *args, **kwargs):
        """
        获取或设置常规网络接口参数

        Args:
            pm: 电源管理设置
                Client.PM_NONE - 高性能模式 (0)
                Client.PM_PERFORMANCE - 平衡模式 (1)（默认）
                Client.PM_POWERSAVE - 节能模式 (2)
            mac: 无线网络 MAC 地址
            ssid: 无线网络名称，不能设置（只读）
            hostname: 主机名，设置时长度不应超过 32
            tx_power: 最大发射功率（dBm），一般范围在：2-21

        Example:
            # 获取 PM 配置信息
            config = client.config('pm')

            # 设置IP配置信息
            client.config(pm = 2)
        """
        return super().config(*args, **kwargs)

    def active(self, *args, **kwargs):
        """
        设置 或 获取 WLAN 的活动状态

        Args:
            True or False （不填写参数则为获取）

        Returns:
            None / bool
        """
        return super().active(*args, **kwargs)

    def status(self, *args, **kwargs):
        """
        获取网络连接状态

        Returns:
            network.STAT_IDLE – 无连接且无活动 (1000)
            network.STAT_CONNECTING – 连接进行中 (1001)
            network.STAT_BEACON_TIMEOUT – 因广播帧超时而连接失败 (200)
            network.STAT_NO_AP_FOUND – 因没有接入点回复而连接失败 (201)
            network.STAT_WRONG_PASSWORD – 因密码错误而连接失败 (202)
            network.STAT_ASSOC_FAIL – 因关联出现问题而连接失败 (203)
            network.STAT_HANDSHAKE_TIMEOUT – 因握手超时而连接失败 (204)
            network.STAT_GOT_IP – 连接成功 (1010)
        """
        return super().status(*args, **kwargs)

    def isconnected(self) -> bool:
        """
        网络是否已连接

        Returns:
            True: 已连接
            False: 未连接
        """
        return super().isconnected()

    def disconnect(self):
        """
        断开连接的网络
        """
        if super().active():
            super().disconnect()
            super().active(False)  # 关闭 WIFI 接口

    @_active
    def ifconfig(self, *args, **kwargs) -> tuple:
        """
        获取或设置IP级网络接口参数。

        Args:
            包含IP地址、子网掩码、网关和 DNS服务器的元组。默认值为 None，即获取网络状态

        Returns:
            tuple: 包含IP地址、子网掩码、网关和 DNS服务器的元组。

        Example:
            # 获取IP配置信息
            ip_config = client.ifconfig()

            # 设置IP配置信息
            client.ifconfig(('192.168.3.4', '255.255.255.0', '192.168.3.1', '8.8.8.8'))
        """
        return super().ifconfig(*args, **kwargs)


class AP(network.WLAN):
    def __init__(self):
        super().__init__(network.AP_IF)
        self.PM_NONE = 0
        self.PM_PERFORMANCE = 1
        self.PM_POWERSAVE = 2

    @_active
    def config(self, *args, **kwargs):
        """
        获取或设置常规网络接口参数

        Args:
            pm: 电源管理设置
                AP.PM_NONE - 高性能模式 (0)
                AP.PM_PERFORMANCE - 平衡模式 (1)（默认）
                AP.PM_POWERSAVE - 节能模式 (2)
            mac: 无线网络 MAC 地址
            key: 连接密码，设置时长度应大于 8，或者为 None, '', 0，修改密码时会自动修改 security（只写，不能读取）
            hidden: 是否隐藏
                0 - 可见
                1 - 隐藏
            channel: 信道
                一般为 1 - 13
            security: 认证模式
                0 - Open
                1 - WEP
                2 - WPA-PSK
                3 - WPA2-PSK
                4 - WPA/WPA2-PSK
            ssid: 无线网络名称
            hostname: 主机名，设置时长度不应超过 32
            tx_power: 最大发射功率（dBm），一般范围在：2-21

        Example:
            # 获取 PM 配置信息
            config = client.config('pm')

            # 设置IP配置信息
            client.config(pm = 2)
        """
        if kwargs.get('key') is not None:  # 修改密码时自动修改 认证模式
            if kwargs['key']:
                if super().config('security') == 0 and kwargs.get('security') is None:
                    if len(kwargs['key']) >= 8:
                        super().config(key=kwargs['key'], security=4)
                    else:
                        print('[ERROR] The password length should not be less than 8.')
            else:
                super().config(security=0)
        return super().config(*args, **kwargs)

    @_active
    def ifconfig(self, *args, **kwargs) -> tuple:
        """
        获取或设置IP级网络接口参数。

        Args:
            包含IP地址、子网掩码、网关和 DNS服务器的元组。默认值为 None，即获取网络状态

        Returns:
            tuple: 包含IP地址、子网掩码、网关和 DNS服务器的元组。

        Example:
            # 获取IP配置信息
            ip_config = client.ifconfig()

            # 设置IP配置信息
            client.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '0.0.0.0'))
        """
        return super().ifconfig(*args, **kwargs)

    def isconnected(self) -> bool:
        """
        是否有设备接入

        Returns:
            True: 有
            False: 无
        """
        return super().isconnected()

    def active(self, *args, **kwargs):
        """
        设置 或 获取 WLAN 的活动状态

        Args:
            True or False （不填写参数则为获取）

        Returns:
            None / bool
        """
        return super().active(*args, **kwargs)
