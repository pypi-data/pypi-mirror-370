import asyncio
import websockets
import json
from typing import Callable
import logging,time
from .model.device_key import DeviceKey
from typing import Callable, Dict, Tuple
logger = logging.getLogger(__name__)

class DevicePusher:
    def __init__(self, device_factory: Callable[[], 'AbstractDevice']):
        self.device_factory = device_factory
        self.status_tasks: Dict[DeviceKey, asyncio.Task] = {}  # 存储每个设备的状态上报任务
        self.devices: Dict[DeviceKey, 'AbstractDevice'] = {}  # 存储每个设备的实例

    async def _report_status_continuously(self, ws, device: 'AbstractDevice', my_device: DeviceKey, report_interval=1):
        """
        持续上报设备状态的协程
        """
        try:
            while True:
                if device.is_connected(my_device):
                    try:
                        drone_id = my_device.device_id
                        connection_str = my_device.connection_str
                        status = device.get_device_status(drone_id,connection_str)
                        await ws.send(json.dumps({
                            "type": "status_update",
                            "status": status,
                            "timestamp": time.time(),
                            "drone_id": drone_id,
                            "connection_str": connection_str
                        }))
                    except Exception as e:
                        logger.warning(f"设备 {my_device} 状态上报失败: {e}")
                        break  # 退出循环，触发重连
                # await asyncio.sleep(report_interval)
        except asyncio.CancelledError:
            logger.info(f"设备 {my_device} 状态上报任务被取消")
        except Exception as e:
            logger.error(f"设备 {my_device} 状态上报任务异常: {e}")
        finally:
            # 清理资源
            if my_device in self.status_tasks:
                del self.status_tasks[my_device]
            if my_device in self.devices:
                del self.devices[my_device]

    async def cleanup(self):
        """清理所有资源"""
        for task in self.status_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.status_tasks.clear()
        self.devices.clear()
    async def connect_server(self, base_url: str, protocol_name: str):
        """
        断线后自动重连，指数回退策略
        """
        url = f"ws://{base_url}/device_ws/{protocol_name}"
        headers = {"protocol_name": protocol_name}
        delay = 1  # 初始重连间隔（秒）
        last_heartbeat_sent = 0
        HEARTBEAT_INTERVAL = 10  # 心跳间隔(秒)
        while True:  # 一直循环，直到外部取消
            try:
                async with websockets.connect(url, extra_headers=headers) as ws:
                    logger.info(f"WebSocket connected: {url}")
                    delay = 1  # 成功连接后重置回退时间
                    device = self.device_factory()

                    # 推送当前状态
                    try:
                        await ws.send(json.dumps({
                            "type": "register",
                            "protocol": protocol_name,
                            "actions": device.to_json(),
                            "is_heartbeat": True,  # 标记为心跳包
                            "heartbeat_interval": HEARTBEAT_INTERVAL  # 告知服务端心跳间隔
                        }))
                    except Exception as e:
                        logger.warning(f"发送状态失败: {e}")
                        break  # 触发重连
                    last_heartbeat_sent = time.time()
                    while True:
                        # 检查是否需要发送心跳
                        now = time.time()
                        if now - last_heartbeat_sent > HEARTBEAT_INTERVAL:
                            try:
                                await ws.send(json.dumps({
                                    "type": "heartbeat",
                                    "status": "success",
                                    "protocol": protocol_name,
                                    "timestamp": now
                                }))
                                last_heartbeat_sent = now
                            except Exception as e:
                                logger.warning(f"心跳发送失败: {e}")
                                break  # 触发重连

                        # 接收指令
                        try:
                            command = await asyncio.wait_for(ws.recv(), timeout=0.1)
                            command_obj = json.loads(command)
                            command_type = command_obj['command_type']
                            message_id = command_obj['message_id']
                            if command_type == "ping":
                                await ws.send(json.dumps({"status": "success","type": "pong", "message_id": message_id}))
                                continue
                            try:
                                params = command_obj['params']
                                drone_id = command_obj['drone_id']
                                connection_str = command_obj['connection_str']
                                my_device = DeviceKey(device_id=drone_id, connection_str=connection_str)

                                # 获取或创建设备实例
                                if my_device not in self.devices:
                                    device = self.device_factory()
                                    self.devices[my_device] = device
                                    # 连接设备
                                    device.connect(my_device)

                                    # 启动状态上报任务（如果尚未启动）
                                    if my_device not in self.status_tasks:
                                        self.status_tasks[my_device] = asyncio.create_task(
                                            self._report_status_continuously(ws, device, my_device))
                                        logger.info(f"为设备 {my_device} 启动状态上报任务")

                                device = self.devices[my_device]

                                # if not device.is_connected():
                                #     my_device = DeviceKey(device_id=drone_id, connection_str=connection_str)
                                #     device.connect(my_device)
                                result = device.excute_command(drone_id,connection_str,command_type,params)
                                await ws.send(json.dumps({"status": "success", "data": result, "message_id": message_id}))
                            except Exception as e:
                                await ws.send(json.dumps({"status": "error", "message": str(e), "message_id": message_id}))
                        except json.JSONDecodeError:
                            await ws.send(json.dumps({"status": "error", "message": "invalid JSON", "message_id": message_id}))
                        except asyncio.TimeoutError:
                            pass  # 无指令，继续
                        except websockets.exceptions.ConnectionClosed:
                            break  # 网络断开，触发重连

            except Exception as e:
                logger.warning(f"WebSocket 断开，{delay}s 后重连: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)  # 指数回退，最大 30 秒