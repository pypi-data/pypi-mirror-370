from typing import Any, Callable, Optional, TypeVar, Dict, List, Union, Literal
from enum import Enum
from threading import Timer, Lock
from dataclasses import dataclass, field
import math

from typing_extensions import deprecated
import requests


T = TypeVar('T')


class StateChangeMode(Enum):
    # 状态变化模式
    AUTO = 1
    MANUAL = 2


class enumConnectionType(Enum):
    TCP          = "TCP"
    UDP          = "UDP"
    MULTICAST    = "MULTICAST"


class _C4:
    NOTHING = math.inf
    ERROR   = 40
    WARNING = 30
    INFO    = 20
    DEBUG   = 10
    NOTSET  = 0

    class BreakException(Exception):
        """用于中断执行流程的异常

        Args:
            message: 异常信息
            level: 异常级别, 默认为 WARING
        """


    @dataclass
    class Song:
        """
        歌曲信息类

        Attributes:
            title: 歌曲名
            artist: 歌手名
            album: 专辑名
            genre: 歌曲风格
            duration: 歌曲时长（秒）
            image_url: 歌曲封面图片URL
            custom_data: 自定义数据
        """
        title: str
        artist: str = None
        album: str = None
        genre: str = None
        duration: int = None
        image_url: str = None
        custom_data: Dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> Dict[str, Union[str, int, Dict[str, Any]]]:
            """
            将歌曲信息类转换为字典

            Returns:
                歌曲信息字典
            """

        def to_json(self) -> str:
            """
            将歌曲信息序列化为JSON字符串

            Returns:
                JSON格式的歌曲信息
            """

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> '_C4.Song':
            """
            从字典创建Song对象

            Args:
                data: 包含歌曲信息的字典

            Returns:
                Song对象
            """

        @classmethod
        def from_json(cls, json_str: str) -> '_C4.Song':
            """
            从JSON字符串创建Song对象

            Args:
                json_str: JSON格式的歌曲信息

            Returns:
                Song对象
            """


    @dataclass
    class SongList:
        """
        歌单，播放列表对象

        Attributes:
            name: 歌单名
            songs: 歌曲列表
        """
        name: str = None
        songs: List['_C4.Song'] = field(default_factory=list)

        def to_dict(self) -> Dict[str, Union[str, int, Dict[str, Any]]]:
            """
            将歌曲信息类转换为字典

            Returns:
                歌曲信息字典
            """

        def to_json(self) -> str:
            """
            将歌曲信息序列化为JSON字符串

            Returns:
                JSON格式的歌曲信息
            """

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> '_C4.SongList':
            """
            从字典创建SongList对象

            Args:
                data: 包含歌单信息的字典

            Returns:
                SongList对象
            """

        @classmethod
        def from_json(cls, json_str: str) -> '_C4.SongList':
            """
            从JSON字符串创建SongList对象

            Args:
                json_str: JSON格式的歌单信息

            Returns:
                SongList对象
            """


    class PlayMode:
        """播放模式"""
        SEQUENTIAL = "SEQUENTIAL"  # 顺序播放
        LOOP = "LOOP"  # 循环播放
        RANDOM = "RANDOM"  # 随机播放
        SINGLE = "SINGLE"  # 单曲循环
        VALID_MODES = {SEQUENTIAL, LOOP, RANDOM, SINGLE}

    # ---------------------- base ----------------------

    def SetPropertyAttribs(self, key, hidden: bool):
        """设置前端属性可见性，hidden=false显示,true隐藏"""

    def UpdateProperty(self, key, value):
        """更新属性表中对应设备属性键值"""

    def InvalidateState(self):
        """保存持久化数据"""

    def FireEvent(self, event_name):
        """触发用户自定义事件，传递参数为自定义事件名称"""

    def GetDeviceID(self):
        """获取设备ID"""

    def GetProxyID(self, idBinding):
        """根据绑定ID获取代理ID"""

    def GetDeviceDisplayName(self, DeviceID=None):
        """根据device_id获取设备显示名称，显示的为第一个设备名称"""
        """根据device_id获取设备显示名称，显示的为第一个设备名称"""

    def GetProxyDisplayName(self, ProxyID):
        """根据proxy_id获取设备显示名称"""

    def ModifyProxyDisplayName(self, name: str, idBinding: int = None) -> bool:
        """
        修改设备显示名称。
        :param self
        :param name: 新的设备显示名称，不能为空且长度不能超过32个字符。
        :param idBinding: 代理设备的绑定ID，如果未提供，则修改主设备的名称。
        :return: 修改成功返回True，否则返回False。
        """

    def GetDriverConfigInfo(self, key):
        """根据xml标签名称返回对应的xml标签内容"""

    def RoomGetID(self):
        """获取此设备的默认房间ID(项目树中房间节点的ID)"""

    def RoomGetVisibleID(self, ProxyID):
        """获取此设备显示在对应房间的ID,非项目树中房间节点的ID"""

    def RoomGetFloorID(self, RoomID):
        """获取房间所在楼层ID"""

    @deprecated('使用 C4.pub_log(...) 代替')
    def Log(self, message, level="INFO", is_display=True):
        """记录日志, is_display=False时不在页面日志显示"""

    def SetLogLevel(self, level: str = "INFO"):
        """设置日志级别 DEBUG, INFO, WARN, ERROR, FATAL, 默认为INFO"""

    def SetHostSerialParameters(self, BindingID: int, SerialParameters: dict):
        """
        若设备对应的BindingID与主机串口绑定，则可设置主机对应的串口参数
        SerialParameters格式为{"baud_rate": 9600, "data_bits": 8, "stop_bits": 1, "parity": 0}
        baud_rate波特率取值为{110, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200}
        data_bits数据位取值为{8}
        stop_bits停止位取值为{1}
        parity校验位取值为{0,1,2}分别标识[none,even,odd]
        其中返回值只有当返回True才表示设置成功
        """

    def AddBindingConnection(self, idDevice1: int, idBinding1: int, idDevice2: int, idBinding2: int) -> bool:
        """
        添加两个设备之间的绑定连接
        :param self:
        :param idDevice1: 要连接的设备1的ID
        :param idBinding1: 要连接的设备1的绑定ID
        :param idDevice2: 要连接的设备2的ID
        :param idBinding2: 要连接的设备2的绑定ID
        :return: 连接成功返回True, 失败返回False
        """

    def AddDevice(self, device_file: str, parent_id: int, init_data: dict = None) -> int | None:
        """
        添加设备到项目树中
        :param self:
        :param device_file: 要添加的设备驱动文件名
        :param parent_id: 要添加到的房间ID
        :param init_data: 驱动OnInit函数传入的初始化数据，字典格式，会进行解包传入
        :return: 添加成功返回设备DeviceID, 失败返回None
        """

    def AddRoom(self, name: str, parent_id: int) -> int | None:
        """
        添加房间到项目树中(若同楼层已有同名房间，则会直接返回该房间的ID)
        :param self:
        :param name: 房间名称
        :param parent_id: 父节点楼层id
        :return: 添加成功返回房间DeviceID, 失败返回None
        """

    def DelDevice(self, proxy_ids: list) -> bool:
        """
        从项目树中删除设备
        :param self:
        :param proxy_ids: 要删除的设备代理ID列表
        :return: 成功返回True, 失败返回False
        """

    def HiddenDevice(self, room_id: int, proxy_id: int) -> None:
        """
        在房间中隐藏设备
        :param self:
        :param room_id: 房间ID
        :param proxy_id: 要隐藏的设备代理ID
        :return:
        """

    def SetDeviceType(self, binding_id: int, device_type: str) -> bool:
        """
        设置设备类型
        :param self:
        :param binding_id: 设备绑定ID
        :param device_type: 要设置的设备类型
        设备类型包括：['开闭灯','调光灯', '双色温灯', '彩灯'...]
        :return: True/False
        """

    def GetDeviceSharedData(self, device_id: int):
        """获取对应设备中的共享数据SharedData"""

    def ModifyDeviceXML(self, path: str, value: Any, attribute: str = None):
        """修改设备的xml配置（支持属性和文本内容）
        :param self:
        :param path: XML路径
        :param value: 要设置的值（文本或XML字符串，当为XML字符串时，将完全替换节点内容）
        :param attribute: 需要设置的属性名
        :return: 修改后的完整XML数据
        """

    def GetDeviceXML(self, path: str, device_id: int = None, attribute: str = None, as_xml: bool = False):
        """
        获取对应设备的xml配置（支持属性和文本内容）
        :param self:
        :param path: XML路径，若传递'.'，则获取整个XML数据
        :param device_id: 设备ID,默认为当前设备ID
        :param attribute: 需要获取的属性名
        :param as_xml: 是否返回XML字符串
        :return:
        """

    def InitButtonInfo(self, button_number: int, pattern_number: int = 1) -> Optional[dict]:
        """
        初始化按键设备信息，自动生成按键模式与按键ID对应的按键名称
        :param self:
        :param button_number: 按键数量
        :param pattern_number: 按键模式数量，默认为1
        :return: 创建成功后的按键信息, 若为None则表示创建失败
        """

    def ModifyButtonInfo(self, button_id: int, name: str, pattern_id: int = 1) -> Optional[dict]:
        """
        修改按键名称
        :param self:
        :param button_id: 按键ID
        :param name: 修改后的按键名称
        :param pattern_id: 按键模式ID，默认为1
        :return: 修改后的按键信息, 若为None则表示修改失败
        """

    def NotifyPlayer(self, event: str, data: Any = None):
        """
        驱动用于通知音乐播放器数据变化
        :param self:
        :param event: 事件类型，playlist/next
        :param data: 数据
        :return:
        """

    # ---------------------- base64 ----------------------

    def Base64Decode(self, data: str) -> str:
        """将 Base64 编码的字符串解码为原始数据。"""

    def Base64DEncode(self, data: str) -> str:
        """将原始数据编码为 Base64 编码的字符串。"""

    def JsonDecode(self, data: str) -> object:
        """将 JSON 字符串解码为 Python 对象。"""

    def JsonEncode(self, data: object) -> str:
        """将 Python 对象编码为 JSON 字符串。"""

    # ---------------------- Device_Interface ----------------------

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def CreateNetworkConnection(self, BindID, NetworkAdds, ConnectionType:enumConnectionType="TCP",Options={}) -> bool:
        """创建发送端 TCP/UDP/MULTICAST"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def DestroyNetworkConnection(self, BindID) -> bool:
        """删除发送端"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def NetPortOptions(self, BindID, Port, ConnectionType:enumConnectionType="TCP", tPortParams={}):
        """修改发送端配置"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def NetConnect(self, BindID, nPort, type=None, nGrowBytes=0, strStart=None , strEnd=None, bSuppressConnectionEvents=None):
        """连接"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def SendToNetwork(self, BindID, Port, Message):
        """发送端发送 TCP/UDP 数据"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def SendBroadcast(self, BindID, Port, Message):
        """发送端发送 MULTICAST 数据"""

    @deprecated('使用 "CreateServer"、"ServerSend"、"StopServer"、"CreateClient"、"ClientSend"、"StopClient" 代替')
    def NetDisconnect(self, BindID, Port):
        """断开连接"""

    # ---------------------- net ----------------------

    def is_port_in_use(self, port):
        """判断端口是否被占用"""

    def GetRandomPort(self):
        """获取随机可用端口"""

    def get_local_ip(self) -> str:
        """获取本机IP地址"""

    def CreateServer(self, port: int, protocol: enumConnectionType = "TCP", host: str = "0.0.0.0", callback: callable = None) -> str | None:
        """
        创建与本设备绑定的Server端服务
        :param self:
        :param port:端口号
        :param protocol:协议类型
        :param callback:回调函数
        :param host:主机地址
        :return:
        """

    def ServerSend(self, server_id: str, data: str | bytes, handle: tuple[str, int]) -> None:
        """
        服务端发送数据
        :param self:
        :param server_id:服务ID
        :param data:要发送的数据
        :param handle:客户端句柄
        :return:
        """

    def StopServer(self, server_id: str) -> None:
        """
        停止与本设备绑定的Server端服务
        :param self:
        :param server_id:服务ID
        :return:
        """

    def CreateClient(self, address: str, port: int, protocol: enumConnectionType = "TCP", callback=None, options=None) -> str | None:
        """
        创建Client模式的网络连接
        :param self:
        :param port: 网络端口
        :param address: 网络地址
        :param protocol: 连接类型，TCP,UDP,MULTICAST
        :param callback: 网络接收时的回调函数
        :param options: 连接参数
        :return:
        """

    def ClientSend(self, client_id: str, data: str | bytes) -> bool:
        """
        发送数据到对应服务器
        :param self:
        :param client_id: 客户端ID
        :param data: 发送数据
        :return:
        """

    def StopClient(self, client_id: str) -> bool:
        """
        断开对应网络的服务器的连接
        :param self:
        :param client_id: 客户端ID
        :return:
        """

    def GetControllerNetworkAddress(self):
        """none"""

    def SendToProxy(self, idBinding, Command, Params, message=None, allowEmptyValues=None) -> None:
        """发送数据到设备"""

    def SendUIRequest(self):
        pass

    def GetBoundConsumerDevices(self, id, idBinding):
        pass

    def GetUniqueMAC(self):
        '''
        Returns
        string
        Example
            print("Unique mac is " .. C4:GetUniqueMAC())
            Output: Unique mac is 000FFF102F73
        Note
            The unique MAC may not be the active MAC if multiple NICs are present. For example, for systems using a wireless interface the MAC returned will be the MAC of the wired Eth
        '''

    def SendToDevice(self, idDevice, CommandType, Command, Params=None):
        """
        如果 CommandType 是 ReceivedFromProxy 则对应驱动的接收接口函数是ReceivedFromProxy()，
        如果 CommandType 是 ExecuteCommand 则对应的驱动接收接口函数是ExecuteCommand()
        """

    def GetConnectionInfo(self, idBinding) -> list[dict]:
        """
        获取当前设备绑定ID对应的连接设备信息

        返回的数据格式：
        [{'device_id':1,'binding_id':1,'classname':'','consumer':true},]
        device_id: 连接设备ID
        binding_id: 连接设备的绑定ID
        classname: 连接的类型
        consumer: true为输入，false为输出
        """

    # ---------------------- Remote_Control ----------------------

    def get_floor_info(self):
        """获取楼层信息"""

    def get_room_info(self, floor_id):
        """根据楼层获取房间信息"""

    def get_device_info(self, room_id):
        """根据房间获取显示在房间的设备信息，根据设备大类分组"""

    def get_all_devices(self) -> list[dict[str, Any]]:
        """获取显示在房间中设备的设备信息，房间信息以及楼层信息"""

    def get_position_in_tree(self, proxy_id: int) -> dict:
        """获取项目树中设备所在房间，楼层信息和获取房间所在楼层信息

        返回的数据格式：
            `{'floor_id':1,'floor_name':'xxx','room_id':'2','room_name':'xxx'}`
        """

    def get_all_room_property(self):
        """获取所有房间的属性信息"""

    def get_room_video(self, room_id):
        """获取房间视频源"""

    def get_room_audio_device(self, room_id) -> list | None:
        """获取房间音频连接设备的device_id"""

    def get_states(self, proxy_id) -> dict | None:
        """获取指定设备的状态"""

    def SetDriverState(self, proxy_id, key, value):
        """设置指定设备的状态"""

    def get_scenes(self) -> list[dict[str, Any]]:
        """获取场景列表"""

    @deprecated('使用 C4.SendToDevice(...) 代替')
    def send_command(self, proxy_id, command, params=None):
        """给指定设备发送指令控制"""

    def register_device(self, device_list):
        """遥控器注册要监听的设备"""

    def FireRoomEvent(self, room_id, event_name='ROOM_OFF'):
        """手动触发房间编程事件，默认为触发关闭房间事件"""

    def RegisterDiscover(self, mac: str) -> bool:
        """注册此状态机设备至discover表中，成功返回True，失败返回False"""

    def UnRegisterDiscover(self, mac: str) -> bool:
        """删除discover表中对应mac的记录，成功返回True，失败返回False"""

    def IsInDiscover(self, mac: str) -> bool:
        """查询设备mac是否在discover表中，存在返回True，不存在返回False"""

    def GetDeviceIPByDiscover(self) -> str | None:
        """根据本设备发现协议mac信息查询IP地址"""

    def GetRoomVisible(self, room_id: int) -> dict:
        """获取房间中显示的设备列表和场景列表"""

    def SetSceneProxyDevice(self, device_id: int):
        """设置当前设备的场景执行代理设备，若设置了代理设备则执行场景时调用代理设备的ReceivedFromScene接口"""

    def ExecuteScene(scene_id: int, command: str = 'EXECUTE'):
        """执行场景，command为EXECUTE时，则为执行场景操作；command为TOGGLE时，反转场景，默认执行场景"""

    # ---------------------- timer ----------------------

    def AddTimer(self, nInterval=None, strUnits=None, bRepeat=False, idTimer=None) -> int:
        """
        添加定时器
        :param self:
        :param nInterval: 间隔时间
        :param strUnits: 定时类型：MILLISECONDS、SECONDS、MINUTES、HOURS
        :param bRepeat: 是否重复
        :param idTimer: 定时器ID
        :return:
        """

    def KillTimer(self, idTimer:int) -> None:
        """删除定时器"""

    # ---------------------- driver_public ----------------------

    def pub_func_log(self: '_C4', log_level = 20) -> Callable:
        """装饰器，打印函数调用日志

        Args:
            log_level (int, optional): 日志级别. 默认为 20.

        Returns:
            function: 装饰器函数。
        """

    def pub_func_catch(self: '_C4', is_raise = False, on_except = None) -> Callable:
        """装饰器，捕获函数异常并打印日志

        注：请在 pub_init 之后调用，否则无法捕获异常。

        Args:
            is_raise (bool, optional): 是否抛出异常. 默认为 False.
            on_except (function, optional): 异常回调函数. 默认为 None.

        Returns:
            function: 装饰器函数。
        """

    def pub_func_hook(self: '_C4', hook) -> Callable:
        """装饰器，在函数调用前后执行 hook 函数

        Args:
            hook (_type_): 钩子函数，参数为 ('before', *args, **kwargs) 或 ('after', *args, **kwargs)
                : `before` 返回 True 则不执行函数
                : `after` 置函数返回值为关键字参数 `__result`, 返回非 `None` 值替换函数返回值

        Returns:
            function: 装饰器函数。
        """

    def pub_func_cache(self: '_C4', timeout: float = 0) -> Callable:
        """装饰器，缓存函数返回值

        Args:
            timeout (float, optional): 缓存超时时间，单位秒，为 `0` 时表示永不过期. 默认为 `0`.

        Returns:
            function: 装饰器函数。
                property: `clear` (lambda) 清除缓存
        """

    def pub_func_debounced(self: '_C4', delay: float | Callable[[tuple, dict], float]):
        """装饰器，给函数添加防抖功能

        Args:
            delay (float | Callable[[tuple, dict], float]): 延迟时间 (秒)
        """

    def pub_init(self: '_C4', PersistData: dict, **kwargs) -> None:
        """初始化公共函数库，并将持久化数据推送到前端（忽略以 _ 开头的属性）"""

    def pub_set_log_level(self: '_C4', level: int | str) -> None:
        """设置日志级别 0 无 10 调试 20 信息 30 警告 40 错误"""

    def pub_log(self: '_C4', *args, level: int = 20, sep: str = ' ') -> None:
        """打印日志"""

    def pub_get_PD(self: '_C4', key: str, default: Optional[T] = None) -> Optional[T]:
        """获取持久化数据"""

    def pub_set_PD(self: '_C4', key: str, value) -> None:
        """更新持久化数据"""

    def pub_save_PD(self: '_C4') -> None:
        """保存持久化数据到数据库"""

    def pub_update_property(self: '_C4', key: str, value, log: str | None = None) -> None:
        """更新设备状态, 并推送到前端"""

    def pub_hide_property(self: '_C4', property: str) -> None:
        """隐藏属性"""

    def pub_show_property(self: '_C4', property: str) -> None:
        """显示属性"""

    def pub_uuid() -> str:
        """获取随机 uuid"""

    def pub_sleep(self: '_C4', seconds: float) -> None:
        """让当前线程休眠指定秒数"""

    def pub_str_time(self: '_C4') -> str:
        """获取当前时间字符串"""

    def pub_time(self: '_C4') -> float:
        """获取当前时间戳 (秒)"""

    def pub_pass_time(self: '_C4', time: float) -> float:
        """返回当前时间戳与指定时间戳的差值 (秒)"""

    def pub_set_interval(self: '_C4', interval: float, unit: str = 'SECONDS') -> int:
        """添加一个定时器，返回定时器 id"""

    def pub_clear_interval(self: '_C4', timer_id: int) -> None:
        """清除一个定时器"""

    def pub_set_timeout(self: '_C4', interval: float, function: Callable, *args, **kwargs) -> Timer:
        """定时 n 秒后执行函数"""

    def pub_clear_timeout(self: '_C4', timer: Timer) -> None:
        """清除一个定时器"""

    def pub_retry(self: '_C4', target: Callable, args: tuple = (), kwargs: dict | None = None, *, condition: Callable, max_retry: int = 3, timeout: float = 3, interval: float = 0.1):
        """重试执行函数，直到满足条件或达到最大重试次数

        Args:
            target (Callable): 要执行的函数
            args (tuple, optional): 位置参数. 默认为 ().
            kwargs (dict, optional): 关键字参数. 默认为 None.
            condition (Callable): 条件函数，返回 True 则停止重试.
            max_retry (int, optional): 最大重试次数. 默认为 3 秒.
            timeout (float, optional): 超时时间. 默认为 3 秒.
            interval (float, optional): 条件检查间隔. 默认为 0.1 秒.

        Returns:
            bool: 成功或失败
        """

    def pub_get_lock(self: '_C4', lock_name: str = 'default_lock') -> Lock:
        """获取一个线程锁，若没有则创建

        Args:
            lock_name (str): 锁名称, 默认为 'default_lock'

        Returns:
            Lock: 线程锁对象
        """

    def pub_task(self: '_C4', target: Callable, args: tuple | None = None, kwargs: dict | None = None, *, delay_before: float = 0, delay_after: float = 0, group: str = 'default') -> None:
        """创建后台任务

        Args:
            target (Callable): 任务函数
            args (tuple | None, optional): 任务参数. 默认为 None.
            kwargs (dict | None, optional): 任务关键字参数. 默认为 None.
            delay_before (float, optional): 任务前延时, 单位毫秒. 默认为 0.
            delay_after (float, optional): 任务后延时, 单位毫秒. 默认为 0.
            group (str, optional): 任务分组. 默认为 'default'.
        """

    def pub_clear_task(self: '_C4', group: str = 'default') -> None:
        """清空指定任务组的任务"""

    def pub_crc16_xmodem(self: '_C4', data: bytes, polynomial = 0x1021) -> int:
        """
        计算给定数据的 CRC-16-XMODEM 校验值。

        :param data: 需要计算CRC的字节数据。
        :param polynomial: CRC-16-XMODEM 多项式。
        :return: 计算得到的CRC-16-XMODEM校验值。
        """

    def pub_crc16_modbus(self: '_C4', data: bytes, polynomial = 0xA001) -> int:
        """计算指定数据的 CRC-16-MODBUS 校验值。

        Args:
            data (bytes): 需要计算CRC的字节数据。
            polynomial (_type_, optional): CRC-16-MODBUS 多项式. Defaults to 0xA001.

        Returns:
            int: 计算得到的 CRC-16-MODBUS 校验值。
        """

    def pub_RC4(self: '_C4', key: str | bytes, data: str | bytes, encoding: str = 'utf-8') -> bytes:
        """使用 RC4 算法加密或解密数据

        Args:
            key (str | bytes): 秘钥
            data (str | bytes): 数据
            encoding (str, optional): 编码. 默认为 'utf-8'.

        Returns:
            bytes: 加密或解密后的结果
        """

    def pub_with_default(self: '_C4', data: dict, default: dict) -> dict:
        """将 `data` 中的 `None` 值替换为 `default` 中的值"""

    def pub_make_jsonrpc(self: '_C4', **kw) -> str:
        """生成 jsonrpc 格式的请求数据，自动添加 id"""

    def pub_table_dumps(self: '_C4', table: list[dict[str, Any]]) -> str:
        """将字典列表转换为表格字符串"""

    def pub_json_loads(self: '_C4', s: str | bytes | bytearray) -> dict:
        """将 json 格式的字符串转换为字典"""

    def pub_json_dumps(self: '_C4', data: dict, indent: int = 4) -> str:
        """将字典数据转换为 json 格式"""

    def pub_ishex(self: '_C4', text: str):
        """判断字符串是否为 16 进制字符串"""

    def pub_format_hex(self: '_C4', hex_str: str, reverse: bool = False) -> str:
        """格式化 16 进制字符串，每 8 位插入一个空格。

        Args:
            hex_str (str): 16 进制字符串。

        Returns:
            str: 格式化后的 16 进制字符串。
        """

    def pub_percent_hex(self: '_C4', percent: int | float) -> str:
        """将百分比转换为 16 进制字符串形式"""

    def pub_dispercent_hex(self: '_C4', hex_str: str) -> float:
        """将 16 进制字符串转换为百分比形式"""

    def pub_bounds(self: '_C4', num: int | float, _min: int | float, _max: int | float):
        """将 num 限定在 [_min:_max]"""

    def pub_percent(self: '_C4', num: int | float, _min: int | float, _max: int | float) -> float:
        """将数值转换为百分比形式"""

    def pub_dispercent(self: '_C4', num: int | float, _min: int | float, _max: int | float) -> int | float:
        """将百分比转换为数值形式"""

    def pub_int_key(self: '_C4', data: dict):
        """将字典的 key 转换为整数"""

    def pub_int_to_bin(self: '_C4', num: int, length: int = 8) -> str:
        """将整数转换为指定长度的2进制字符串形式

        Args:
            num (int): 数字
            length (int, optional): 长度（位，一字节 8 个 2 进制字符）. Defaults to 8.

        Returns:
            str: 2 进制字符串（例：8 -> '00001000'）
        """

    def pub_int_to_hex(self: '_C4', num: int, length: int = 1) -> str:
        """将整数转换为指定长度的16进制字符串形式

        Args:
            num (int): 数字
            length (int, optional): 长度（字节，一字节 2 个 16 进制字符）. Defaults to 1.

        Returns:
            str: 16 进制字符串（例：10 -> '0A'）
        """

    def pub_ip_to_hex(self: '_C4', ip: str) -> str:
        """将IP地址转为16进制字符串形式"""

    def pub_hex_to_ip(self: '_C4', hex_string: str) -> str:
        """将16进制字符串形式的IP地址转为IP地址形式"""

    def pub_hex_to_mac(self: '_C4', hex_str: str) -> str:
        """十六进制字符串转为 MAC 地址"""

    def pub_mac_to_hex(self: '_C4', mac_str: str) -> str:
        """MAC 地址转为十六进制字符串"""

    def pub_xml_to_dict(self: '_C4', xml: str, default = ...) -> dict:
        """将xml字符串转换为字典"""

    def pub_dict_to_xml(self: '_C4', data: dict, root_name: str | None = None, encoding: str = 'unicode') -> str:
        """将字典数据转换为xml格式"""

    def pub_fetch_get(self: '_C4', host, port, path, params = None, protocol = 'http', timeout = 3) -> requests.Response | None:
        """requests.get 封装"""

    def pub_fetch_post(self: '_C4', host, port, path, params = None, data = None, protocol='http', timeout = 3) -> requests.Response | None:
        """requests.post 封装"""

    def pub_knx_connect(self: '_C4', addr: tuple[str, int], rate_limit: int = 20) -> None:
        """创建 KNX 连接"""

    def pub_knx_disconnect(self: '_C4') -> None:
        """断开 KNX 连接"""

    def pub_knx_rate_limit(self: '_C4', rate_limit: int) -> None:
        """设置 KNX 报文队列的发送速率，单位毫秒"""

    def pub_knx_send(self: '_C4', group_address: str, value, value_type) -> None:
        """向 KNX 设备发送数据"""

    def pub_knx_is_alive(self: '_C4') -> bool:
        """判断 KNX 连接是否存活"""

    def pub_knx_check_addr(self: '_C4', addr: str):
        """验证 KNX 地址是否合法"""

    def pub_create_connection(self: '_C4', type: Literal['TC', 'UC', 'MC', 'TS', 'US', 'MS'], port: int, host: str | None = None, pretreatment: Callable | None = None) -> str | None:
        """建立指定连接

        Args:
            type (str): 连接类型
                - 'TC'  TCP 客户端
                - 'UC'  UDP 客户端
                - 'MC'  多播客户端
                - 'TS'  TCP 服务端
                - 'US'  UDP 服务端
                - 'MS'  多播服务端
            port (int): 端口号
            host (str): ip 地址 (服务端为可选项)
            pretreatment (Callable, optional): 预处理函数, 默认为 None.

        Returns:
            str: 连接 ID
        """

    def pub_destroy_connection(self: '_C4', id: str) -> None:
        """关闭指定连接

        Args:
            id (str): 连接 ID
        """

    def pub_send_to_network(self: '_C4', id: str, data: str | bytes, target: tuple[str, int] | None = None, retry: int = 3, interval: float = 3) -> bool:
        """发送网络数据

        Args:
            id (str): 连接 ID
            data (str | bytes): 要发送的数据
            target (tuple[str, int], optional): 目标地址 (服务端连接时有效)
            retry (int, optional): 重试次数. 默认为 3.
            interval (float, optional): 重试间隔. 默认为 3.

        Returns:
            bool: 是否发送成功
        """

    @deprecated('使用 "pub_send_to_network" 代替')
    def pub_send_to_multicast(self: '_C4', channel: int, port: int, message: str) -> None:
        """向对应端口发送多播数据"""

    def pub_send_to_serial(self: '_C4', hex_data: str | list, interval: float = 0.1, is_hex: bool = False, channel: int = 3001) -> None:
        """发送串口数据，格式：{ hex_data: str, interval: float }"""

    def pub_send_to_ir(self: '_C4', code: str, count: int = 1, is_hex: bool = False, channel: int = 3000) -> None:
        """发送红外数据，格式：{ code: str, count: int }"""

    def pub_send_to_internal(self: '_C4', command: str, params: dict, channel: int = 5001) -> None:
        """向内部通道发送命令，改变设备状态"""

    def pub_send_to_device(self: '_C4', cmd: str, params: dict, device_id: int) -> None:
        """向指定设备发送命令"""

    def pub_send_to_master(self: '_C4', command: str, params: dict | str, channel: int = 4000) -> None:
        """向主控设备发送数据"""

    def pub_send_to_slave(self: '_C4', command: str, params: dict | str, channel: int | str = '4000') -> None:
        """向从控设备发送消息，channel 为 str 时，向所有从机发送"""

    def pub_get_broadcast_ip(self: '_C4') -> str:
        """获取广播地址"""

    def pub_broadcast(self: '_C4', message: bytes, port: int | None = None, channel: int = 3999):
        """发送广播数据"""

    def pub_WOL(self: '_C4', mac: str):
        """发送 WOL 包，实现网络唤醒"""

    def pub_longdown_task(self: '_C4', send_to_proxy: Callable, cmd: str, params: dict, delay: float, interval: float = 0.5) -> None:
        """创建长按任务"""

    def pub_mute_switch(self: '_C4', cmd: str) -> str | None:
        """处理静音开关的情况"""

    def pub_mute_toggle(self: '_C4', cmd: str) -> str | None:
        """处理静音切换的情况"""


C4: _C4 = ...
PersistData: dict[str, Any] = ...
SharedData: Any = ...
