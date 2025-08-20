from qiskit.providers import JobStatus

from guojiqe_sdk.runtime_service import GjqRuntimeService

# 创建服务实例
service = GjqRuntimeService(channel="CPU_FULL_AMPLITUDE_SIMULATOR")
# 获取后端
# 方式1：自动选择最空闲的后端
backend1 = service.least_busy()

# 方式2：为用户提供指定类型的可用后端设备列表，用户通过查看这些信息，选择后端设备
# backends = service.backends()
# for backend in backends:
#     print("名称:", backend.name, "量子比特数:", backend.num_qubits, "设备ID:", backend.device_id)
#
#
# # 可以不指定device_id，默认返回第一个可用的设备
# backend2 = service.backend()
# # backend2 = service.backend("tgq-super-0001")
# print(backend2.num_qubits)
# sim_target = backend2.target
# # print(sim_target)
# # 获取拓扑
# coupling_map = sim_target.build_coupling_map()
# print(coupling_map.get_edges())
#
#
target = backend1.target
print(target)
print("后端:", backend1.name)


# 创建电路
# from qiskit import QuantumCircuit
# circuit = QuantumCircuit(2)
# circuit.x(range(2))
# circuit.cz(0, 1)
# circuit.measure_all()  # measurement!
# #
# # 方式1: 通过后端运行
# job = backend1.run(circuit)
# while job.status() not in [JobStatus.DONE, JobStatus.CANCELLED, JobStatus.ERROR]:
#     print("作业状态:", job.status())
#     import time
#     time.sleep(2)  # 等待2秒后再检查状态
# result = job.result().results[0].data.to_dict()
# print("后端运行结果:", result)

