from abc import ABC, abstractmethod
from typing import Dict, Any
import threading
import json,uuid
from typing import List
from collections import defaultdict
from .model.device_key import DeviceKey
from .model.action_item import ActionItem
from .model.device_status import DeviceStatus

import logging
logger = logging.getLogger(__name__)

class AbstractDevice(ABC):
    _status_cache: Dict[DeviceKey, dict] = {}
    _connection_pool: Dict[DeviceKey, Any] = {}  # 类级连接池
    _lock = threading.RLock()

    _monitor_flags = defaultdict(bool)  # 状态监控标志
    _monitor_futures = {}
    _lock = threading.Lock()  # 线程安全锁
    _status_lock = threading.RLock()  # 新增：状态读取可重入锁
    @property
    @abstractmethod
    def protocol_name(self) -> str:
        pass

    @abstractmethod
    def get_action_list(self) -> List[ActionItem]:
        pass
    def connect(self, device_key: DeviceKey) -> Any:
        """带设备ID的连接池实现"""
        with self._lock:
            if device_key not in self._connection_pool:
                client = self._create_client(device_key.connection_str)
                self._connection_pool[device_key] = client

    def disconnect(self, protocol: str, device_id: str):
        with self._lock:
            for (p, key), instance in list(self._instance_cache.items()):
                if p == protocol and key.device_id == device_id:
                    instance.disconnect()
                    del self._instance_cache[(p, key)]

    def is_connected(self, device_key: DeviceKey) -> bool:
        with self._lock:
            if conn := self._connection_pool[device_key]:
                return True
        return False

    @abstractmethod
    def _create_client(self, connection_str: str) -> Any:
        pass

    def get_status(self,device_id,connection_str):
        my_device = DeviceKey(device_id=device_id, connection_str=connection_str)
        status = self._status_cache.get(my_device,{})
        return status

    @abstractmethod
    def get_device_status(self,device_id:str,connection_str:str) -> DeviceStatus:
        pass

    def push_status(self,device_id:str,connection_str:str) :
        my_device = DeviceKey(device_id=device_id, connection_str=connection_str)
        result = self.get_device_status(device_id,connection_str)
        self._status_cache.pop(my_device,result)

    def excute_command(self,device_id:str,connection_str:str, command: str, params: Dict[str, Any]):
        my_device = DeviceKey(device_id=device_id, connection_str=connection_str)
        this_client = self._connection_pool[my_device]
        self.execute(this_client,command,params)

    @abstractmethod
    def execute(self,client, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行控制指令"""

    def to_json(self):
        """序列化设备信息"""
        actions = [item.dict() for item in self.get_action_list()]
        return json.dumps({
            "protocol": self.protocol_name,
            "action_list": actions
        }, ensure_ascii=False)