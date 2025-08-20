from typing import Optional, Literal

from qiskit import QuantumCircuit
from base import ServiceBase
from client import GjqClient
from job import GjqJob
from device_types import DeviceType, ChannelType


class GjqRuntimeService(ServiceBase):
    """为公司量子设备提供访问接口的服务"""

    def __init__(self, channel: ChannelType, **kwargs):
        """
        初始化服务

        Args:
            api_key: API访问密钥
            url: API端点URL
            **kwargs: 其他连接参数
        """
        # 不调用父类初始化，因为我们不想连接到IBM Quantum
        self.channel = channel
        self._backends = {}
        self._options = kwargs.get("options", {})
        self._client = GjqClient(base_url="http://192.168.12.134:9998/scheduler/api/v1", api_key="your_api_key_here")
        # self._client = GjqClient(base_url="http://localhost:9998/scheduler/api/v1", api_key="your_api_key_here")
        self._initialize_backends()

    def _initialize_backends(self):
        """初始化指定channel的可用后端列表"""
        from backend import GjqBackend  # 延迟导入，避免循环依赖
        list_of_available_backends_info = self._client.get_available_backends()
        for backend_info in list_of_available_backends_info:
            # 这里可以根据设备信息创建 TgqBackend 实例
            if backend_info["deviceType"] == getattr(DeviceType, self.channel).value:
                backend = GjqBackend(
                    service=self,
                    name=backend_info["deviceName"],
                    num_qubits=backend_info["maxQubits"],
                    device_id=backend_info["deviceId"]
                )
                self._backends[backend.device_id] = backend
        if not self._backends:
            raise ValueError(f"No available backends for channel '{self.channel}'")

    def backends(self):
        """后端列表按照量子比特数从大到小排序"""
        backend_list = list(self._backends.values())
        # 按照量子比特数从大到小排序
        backend_list.sort(key=lambda x: x.num_qubits, reverse=True)
        # 返回所有后端
        return backend_list

    def backend(self, device_id: Optional[str] = None):
        """获取指定名称的后端"""
        if device_id is None:
            # 如果未指定deviceId，返回第一个可用后端
            if self._backends:
                return next(iter(self._backends.values()))
            raise ValueError("No backends available")

        # 查找匹配名称的后端
        if device_id in self._backends:
            return self._backends[device_id]

        # 如果没有精确匹配，尝试部分匹配
        # for backend_name, backend in self._backends.items():
        #     if device_id in backend_name:
        #         return backend

        raise ValueError(f"Backend '{device_id}' not found")

    def least_busy(self):
        """获取当前channel最空闲的后端"""
        from backend import GjqBackend  # 延迟导入，避免循环依赖
        least_busy_backend_info = self._client.get_least_busy_device_info(getattr(DeviceType, self.channel).value)
        return GjqBackend(service=self,
                          name=least_busy_backend_info["deviceName"],
                          num_qubits=least_busy_backend_info["maxQubits"],
                          device_id=least_busy_backend_info["deviceId"])

    def _run(self, circuit: QuantumCircuit, device_id: str):
        return GjqJob(service=self, backend=self.backend(device_id), circuit=circuit)

