from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, Measure
from qiskit.providers import Options
from typing import Optional
from qiskit.transpiler import Target, InstructionProperties
from qiskit.circuit.library import (
    HGate, XGate, YGate, ZGate, RXGate, RYGate, RZGate, SGate, SdgGate, TGate, TdgGate, SXGate,  # 单比特门
    CXGate, SwapGate, iSwapGate, CZGate, CPhaseGate, RXXGate, RYYGate, RZZGate,  # 双比特门 SycamoreGate这里会报错
    CCXGate, CSwapGate,  # 三比特门
)
from base import BackendBase
from qiskit_ibm_runtime.models import BackendStatus
from itertools import combinations
from device_types import DeviceType
from noise_model import NoiseModel


class GjqBackend(BackendBase):
    """连接到公司量子计算机的自定义后端"""

    def __init__(self, service, name: str, num_qubits: int, device_id: str):
        """
        初始化后端

        Args:
            service: 关联的RuntimeService实例
            name: 后端名称
        """
        self._service = service
        self._name = name
        self._num_qubits = num_qubits
        self._device_id = device_id
        self._version = "0.1.0"
        self._target = self._build_target()

    def _build_target(self) -> Target:
        """构建量子计算机的 Target 对象，描述支持的门和耦合关系"""
        """参考：https://docs.quantum.ibm.com/api/qiskit/qiskit.transpiler.Target"""
        if self._service.channel == DeviceType.SUPERCONDUCTING_QUANTUM_COMPUTER.name:
            target = Target(num_qubits=self._num_qubits, description=f"{self.name} Target")

            # 单比特门列表（使用门类和属性）
            single_qubit_gates = [
                (XGate, {"duration": 50e-9, "error": 0.001}),  # X 门
                (SXGate, {"duration": 50e-9, "error": 0.001}),  # SX 门
                (YGate, {"duration": 50e-9, "error": 0.001}),  # Y 门
                (RXGate, {"duration": 60e-9, "error": 0.0015}, Parameter('theta')),  # RX 门（参数化）
                (RYGate, {"duration": 60e-9, "error": 0.0015}, Parameter('theta')),  # RY 门（参数化）
                (RZGate, {"duration": 60e-9, "error": 0.0015}, Parameter('theta')),  # RZ 门（参数化）
            ]

            # 为每个单比特门添加指令，一次性指定所有量子比特的属性
            for gate_class, props, *param in single_qubit_gates:
                # 如果有参数（如 RX、RY、RZ），使用参数化门
                gate = gate_class(param[0]) if param else gate_class()
                # 构建所有量子比特的属性字典
                qubit_properties = {
                    (qubit,): InstructionProperties(
                        duration=props["duration"],
                        error=props["error"]
                    ) for qubit in range(self._num_qubits)
                }
                # 一次性添加指令
                target.add_instruction(gate, qubit_properties)

            # 双比特门：CZ 门（仅 Q0 和 Q1）
            cz_props = {"duration": 200e-9, "error": 0.01}
            target.add_instruction(
                CZGate(),
                {(0, 1): InstructionProperties(
                    duration=cz_props["duration"],
                    error=cz_props["error"]
                )}
            )

            # 测量指令（所有量子比特）
            measure_properties = {
                (qubit,): InstructionProperties(
                    duration=1000e-9,  # 测量耗时较长
                    error=0.05  # 测量误差较高
                ) for qubit in range(self._num_qubits)
            }
            target.add_instruction(Measure(), measure_properties)

            return target

        # 除了含噪声模拟器外，其余不同振幅模拟器错误率为0，含噪声模拟器模拟真机，有错误率或者噪声模型
        elif "NOISY_SIMULATOR" not in self._service.channel:
            target = Target(num_qubits=self._num_qubits, description=f"{self.name} Target")

            # 单比特门列表（使用门类和属性）
            single_qubit_gates = [
                (HGate, {"duration": 50e-9, "error": 0}),  # H 门
                (XGate, {"duration": 50e-9, "error": 0}),  # X 门
                (YGate, {"duration": 50e-9, "error": 0}),  # Y 门
                (ZGate, {"duration": 50e-9, "error": 0}),  # Z 门
                (RXGate, {"duration": 60e-9, "error": 0}, Parameter('theta')),  # RX 门（参数化）
                (RYGate, {"duration": 60e-9, "error": 0}, Parameter('theta')),  # RY 门（参数化）
                (RZGate, {"duration": 60e-9, "error": 0}, Parameter('theta')),  # RZ 门（参数化）
                (SGate, {"duration": 50e-9, "error": 0}),  # S 门
                (SdgGate, {"duration": 50e-9, "error": 0}),  # SDG 门
                (TGate, {"duration": 50e-9, "error": 0}),  # T 门
                (TdgGate, {"duration": 50e-9, "error": 0}),  # TDG 门
            ]

            # 为每个单比特门添加指令，一次性指定所有量子比特的属性
            for gate_class, props, *param in single_qubit_gates:
                gate = gate_class(param[0]) if param else gate_class()
                qubit_properties = {
                    (qubit,): InstructionProperties(
                        duration=props["duration"],
                        error=props["error"]
                    ) for qubit in range(self._num_qubits)
                }
                target.add_instruction(gate, qubit_properties)

            # 双比特门列表（支持任意耦合）
            two_qubit_gates = [
                (CXGate, {"duration": 200e-9, "error": 0}),  # CX 门
                (SwapGate, {"duration": 200e-9, "error": 0}),  # SWAP 门
                (iSwapGate, {"duration": 200e-9, "error": 0}),  # iSWAP 门
                (CZGate, {"duration": 200e-9, "error": 0}),  # CZ 门
                (CPhaseGate, {"duration": 200e-9, "error": 0}, Parameter('theta')),  # CP 门（参数化）
                (RXXGate, {"duration": 200e-9, "error": 0}, Parameter('theta')),  # RXX 门（参数化）
                (RYYGate, {"duration": 200e-9, "error": 0}, Parameter('theta')),  # RYY 门（参数化）
                (RZZGate, {"duration": 200e-9, "error": 0}, Parameter('theta')),  # RZZ 门（参数化）
                # (SycamoreGate, {"duration": 200e-9, "error": 0.01}),  # SYC 门：有报错
            ]

            # 为每个双比特门添加指令，支持任意量子比特对
            for gate_class, props, *param in two_qubit_gates:
                gate = gate_class(param[0]) if param else gate_class()
                # 生成所有可能的量子比特对 (i, j)，i != j
                qubit_pairs = list(combinations(range(self._num_qubits), 2))
                pair_properties = {
                    (i, j): InstructionProperties(
                        duration=props["duration"],
                        error=props["error"]
                    ) for i, j in qubit_pairs
                }
                target.add_instruction(gate, pair_properties)

            # 三比特门列表（支持任意三量子比特组合）
            three_qubit_gates = [
                (CCXGate, {"duration": 300e-9, "error": 0}),  # CCX 门
                (CSwapGate, {"duration": 300e-9, "error": 0}),  # CSWAP 门
            ]

            # 为每个三比特门添加指令，支持任意三量子比特组合
            for gate_class, props in three_qubit_gates:
                gate = gate_class()
                # 生成所有可能的三量子比特组合 (i, j, k)，i != j != k
                qubit_triples = list(combinations(range(self._num_qubits), 3))
                triple_properties = {
                    (i, j, k): InstructionProperties(
                        duration=props["duration"],
                        error=props["error"]
                    ) for i, j, k in qubit_triples
                }
                target.add_instruction(gate, triple_properties)

            # 测量指令（所有量子比特）
            measure_properties = {
                (qubit,): InstructionProperties(
                    duration=1000e-9,  # 测量耗时较长
                    error=0.05  # 测量误差较高
                ) for qubit in range(self._num_qubits)
            }
            target.add_instruction(Measure(), measure_properties)

            return target

    def run(self, circuit: QuantumCircuit, **options):
        """
        组织量子电路提交接口

        Args:
            circuit: 要运行的量子电路
            **options: 运行选项

        Returns:
            表示提交任务的Job对象
        """
        from job import GjqJob  # 延迟导入
        # options = {
        #     'job_name': options.get('job_name', 'test'),
        #     'qos': options.get('qos', 'normal'),
        #     'time_limit': options.get('time_limit', 60),
        #     'repetitions': options.get('repetitions', 1000),
        #     'task_desc': options.get('task_desc', 'Qiskit Job'),
        #     'req_device_type': options.get('req_device_type', 1)
        # }

        # 创建并返回GjqJob实例
        return GjqJob(backend=self, service=self._service, circuit=circuit)

    @property
    def name(self) -> str:
        """返回后端名称"""
        return self._name

    @property
    def version(self) -> str:
        """返回后端版本"""
        return self._version

    @property
    def target(self) -> Target:
        """返回后端的Target对象"""
        return self._target

    @property
    def max_circuits(self) -> int:
        """单次执行支持的最大电路数量"""
        return 1000  # 根据实际情况调整

    @property
    def service(self):
        """返回关联的服务实例"""
        return self._service

    @property
    def device_id(self):
        """返回backend的设备ID"""
        return self._device_id

    @property
    def num_qubits(self):
        """返回backend的设备ID"""
        return self._num_qubits
