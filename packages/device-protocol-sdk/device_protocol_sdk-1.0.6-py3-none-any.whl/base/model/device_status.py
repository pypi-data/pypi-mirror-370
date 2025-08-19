# device_status.py
from typing import TypedDict, Optional

class DeviceStatus(TypedDict, total=False):
    """设备状态固定格式"""
    is_lock: Optional[int]  # 必填
    heartbeat: Optional[int]  # 必填
    battery: Optional[float]  # 必填
    airspeed: Optional[float]  # 必填
    groundspeed: Optional[float]  # 必填
    yaw_degrees: Optional[float]  # 必填
    roll: Optional[float]  # 必填
    pitch: Optional[float]  # 必填
    yaw: Optional[float]  # 必填
    lat: Optional[float]  # 必填
    lon: Optional[float]  # 必填
    alt: Optional[float]  # 必填
    vzspeed: Optional[float]  # 必填
    height: Optional[float]  # 必填