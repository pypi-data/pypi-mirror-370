import json

import requests
import time
from typing import Optional, Callable


class GjqClientError(Exception):
    """Custom exception class for TgqClient errors."""
    pass

class GjqClient:
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 10, max_retries: int = 3,
                 failure_callback: Optional[Callable[[str, Exception], None]] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.failure_callback = failure_callback
        self.session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers.update(headers)

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if 400 <= response.status_code < 500:
                    raise GjqClientError(f"Client error {response.status_code}: {response.text}")
                response.raise_for_status()
                result = response.json()
                return result
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == self.max_retries:
                    if self.failure_callback:
                        self.failure_callback(url, e)
                    raise GjqClientError(f"Timeout/ConnectionError requesting {url} after {self.max_retries} attempts.") from e
                time.sleep(2 ** attempt)
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    if self.failure_callback:
                        self.failure_callback(url, e)
                    raise GjqClientError(f"RequestException requesting {url} after {self.max_retries} attempts.") from e
                time.sleep(2 ** attempt)

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def set_max_retries(self, max_retries: int):
        self.max_retries = max_retries

    def set_failure_callback(self, callback: Callable[[str, Exception], None]):
        self.failure_callback = callback

    def get_cluster_list(self):
        return self._request("GET", "/cluster/id-list")

    def get_cluster_info(self, cluster_id: str):
        return self._request("GET", f"/cluster/select/{cluster_id}")

    def get_least_busy_device_info(self, device_type: int):
        return self._request("POST", f"/cluster/least-busy-device", json={"deviceType": device_type})['data']

    def get_available_backends(self):
        """获取可用的后端设备，这里不按设备类型过滤"""
        list_of_available_backends = []
        clusterIdList = self.get_cluster_list()['data']
        for clusterId in clusterIdList:
            deviceDOList = self.get_cluster_info(clusterId)['data']['deviceDOList']
            for deviceDO in deviceDOList:
                # 设备状态，MAINTENANCE = 0;IDLE = 1;RUNNING = 2;
                if deviceDO['deviceState'] != 0:
                    list_of_available_backends.append(deviceDO)
        return list_of_available_backends

    def submit_task(self, payload: dict):
        return self._request("POST", "/task/create/device", json=payload)

    def get_task_info(self, job_id: str):
        return self._request("GET", f"/task/info", params={"jobId": job_id})

    def cancel_task(self, job_id: str):
        return self._request("GET", f"/task/cancel", params={"jobId": job_id})

    def close(self):
        self.session.close()

# Example usage
def main():
    # client = TgqClient(base_url="http://192.168.12.134:9998/scheduler/api/v1", api_key="your_api_key_here")
    client = GjqClient(base_url="http://localhost:9998/scheduler/api/v1", api_key="your_api_key_here")
    # client.set_timeout(20)
    # client.set_max_retries(5)

    try:
        # # 获取least_busy设备信息
        # cluster_list = client.get_least_busy_device_info()
        # print(json.dumps(cluster_list, indent=4, ensure_ascii=False))

        # # 获取集群列表
        # cluster_list = client.get_cluster_list()
        # print(json.dumps(cluster_list, indent=4, ensure_ascii=False))

        # 获取集群信息
        cluster_info = client.get_cluster_info("tgq-0001")
        print(json.dumps(cluster_info, indent=4, ensure_ascii=False))

        # # 提交任务
        # payload = {
        #     "userId": "qiskit_user",
        #     "jobName": "qiskit_test_0427",
        #     "account": "account",
        #     "qos": "normal", # 可空
        #     "timeLimit": 60,
        #     "needQubit": 20,
        #     "repetitions": 1000,
        #     "taskDesc": "TgqClient_test", # 可空
        #     "reqDeviceType": 1,
        #     "clusterId": "tgq-0001",
        #     "taskCode": "OPENQASM 2.0;\n qreg q[2];\n h q[0];\n cx q[0],q[1];\n measure q[0];\n measure q[1];"
        # }
        # task = client.submit_task(payload)
        # print(json.dumps(task, indent=4, ensure_ascii=False))

        # # 获取任务信息
        # task_info = client.get_task_info(job_id="100000157")
        # print(json.dumps(task_info, indent=4, ensure_ascii=False))

        # # 取消任务
        # cancel = client.cancel_task(job_id="100000156")
        # print(json.dumps(cancel, indent=4, ensure_ascii=False))

    except GjqClientError as e:
        raise GjqClientError(f"TgqClient error: {e}") from e

    finally:
        client.close()

if __name__ == "__main__":
    main()
