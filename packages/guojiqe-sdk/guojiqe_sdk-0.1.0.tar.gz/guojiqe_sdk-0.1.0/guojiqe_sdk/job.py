import json
from typing import Optional, Dict, Any

from qiskit_ibm_runtime import RuntimeJob
from qiskit.providers.jobstatus import JobStatus
from qiskit.result import Result
from qiskit.qasm2 import dumps
from qiskit import transpile, QuantumCircuit
from base import JobBase
from client import GjqClient
import time


class GjqJob(JobBase):
    def __init__(self, backend,
                 service,
                 circuit,
                 options: Optional[Dict[str, Any]] = None):
        """
        初始化作业

        Args:
            backend: 执行作业的后端
            job_id: 作业的唯一标识符
            service: 关联的服务实例
            circuit: 要执行的量子电路列表
            options: 运行选项
        """
        self._backend = backend
        self._circuits = circuit
        self._options = options
        self._service = service
        # self._api_config = backend._api_config
        self._status = JobStatus.INITIALIZING
        self._result = None
        self._error_message = None
        self._submit_time = time.time()
        self._api_client = GjqClient(base_url="http://192.168.12.134:9998/scheduler/api/v1",
                                     api_key="your_api_key_here")

        # 提交作业
        self._submit()

    def _submit(self):
        """提交作业到实际硬件"""
        try:
            # qc量子电路预处理
            basis = ['x', 'sx', 'y', 'rx', 'ry', 'rz', 'cz']
            # circuits_transpiled = transpile(circuits=self._circuits, basis_gates=basis, optimization_level=3)
            # qasm_str = dumps(circuits_transpiled)
            circuits_transpiled = transpile(circuits=self._circuits, basis_gates=basis, optimization_level=3)

            # 如果是单个电路，直接转换。多个电路后续自行适配。
            if not isinstance(circuits_transpiled, list):
                circuits_transpiled = [circuits_transpiled]

            # 转换每个电路为QASM字符串并合并
            qasm_strs = []
            for circ in circuits_transpiled:
                qasm_strs.append(dumps(circ))
            qasm_str = "\n".join(qasm_strs)

            # payload = {
            #     'job_name': self._options.get('job_name', 'test'),
            #     'qos': self._options.get('qos', 'normal'),
            #     'time_limit': self._options.get('time_limit', 60),
            #     'repetitions': self._options.get('repetitions', 1000),
            #     'task_desc': self._options.get('task_desc', 'Qiskit Job'),
            #     'req_device_type': self._options.get('req_device_type', 1)
            # }

            payload = {
                "deviceId": self._backend.device_id,
                "taskCode": qasm_str
            }

            response = self._api_client.submit_task(payload)
            remote_job_id = response['data']['jobId']
            self._job_id = remote_job_id

            # 更新状态
            self._status = JobStatus.QUEUED
        except Exception as e:
            self._status = JobStatus.ERROR
            self._error_message = str(e)
            raise e

    def _serialize_circuit(self, circuit):
        """将量子电路序列化为API可接受的格式"""
        # 实现电路转换逻辑
        return {
            "qasm": circuit.qasm(),
            "num_qubits": circuit.num_qubits,
            "metadata": circuit.metadata or {}
        }

    def status(self):
        """获取作业当前状态"""
        if self._status in [JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED]:
            return self._status

        # 查询实际作业状态
        try:
            response = self._api_client.get_task_info(job_id=self._job_id)
            status_str = response["data"]["state"]

            # 映射API返回的状态到Qiskit的JobStatus
            status_mapping = {
                "NEW": JobStatus.QUEUED,
                "RUNNING": JobStatus.RUNNING,
                "SUSPENDED": JobStatus.ERROR,
                "COMPLETED": JobStatus.DONE,
                "CANCELED": JobStatus.CANCELLED,
                "FAILED": JobStatus.ERROR,
                "TIMEOUT": JobStatus.ERROR,
                "NODE_FAILED": JobStatus.ERROR,
                "SERVICE_FAILED": JobStatus.ERROR,
                "ERROR": JobStatus.ERROR
            }
            self._status = status_mapping.get(status_str, JobStatus.ERROR)

        except Exception as e:
            self._error_message = str(e)
            self._status = JobStatus.ERROR

        return self._status

    def result(self):
        """获取作业结果"""
        # 等待作业完成
        current_status = self.status()
        while current_status not in [JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED]:
            time.sleep(2)
            current_status = self.status()

        if current_status == JobStatus.ERROR:
            response = self._api_client.get_task_info(job_id=self._job_id)
            error = response['data']['errorText']
            raise Exception(f"作业执行出错, {JobStatus.ERROR}:\n{error}")

        if current_status == JobStatus.CANCELLED:
            raise Exception("作业已取消")

        # 获取结果
        if self._result is None:
            try:
                response = self._api_client.get_task_info(job_id=self._job_id)
                counts = json.loads(response['data']['resultText'])

                # 将API结果转换为Qiskit Result格式
                self._result = Result.from_dict({
                    "backend_name": self._backend.name,
                    "backend_version": self._backend.version,
                    "job_id": self._job_id,
                    "success": True,
                    "results": [
                        {
                            "shots": 1000,
                            "success": True,
                            "data": counts
                        }
                    ]
                })

            except Exception as e:
                self._error_message = str(e)
                self._status = JobStatus.ERROR
                raise e

        return self._result

    def cancel(self):
        """取消作业"""
        if self._status in [JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED]:
            return False

        try:
            # 实现与公司API通信取消作业的逻辑
            response = self._api_client.cancel_task(job_id=self._job_id)
            success = (response['code'] == 200)

            if success:
                self._status = JobStatus.CANCELLED

            return success
        except Exception:
            return False
