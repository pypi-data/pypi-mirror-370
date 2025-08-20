from abc import ABC, abstractmethod


class ServiceBase(ABC):
    """服务基类，定义接口"""

    @abstractmethod
    def backends(self):
        pass

    @abstractmethod
    def backend(self, device_id=None):
        pass


class BackendBase(ABC):
    """后端基类，定义接口"""

    @abstractmethod
    def run(self, circuit, **options):
        pass


class JobBase(ABC):
    """作业基类，定义接口"""

    @abstractmethod
    def result(self):
        pass