from pythonping import ping
from dataclasses import dataclass
from typing import Optional

@dataclass
class scan_result:
    loss_pct: float
    average: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None

class scanner:
    def __init__(self, test_url):
        self.test_url = test_url

    def scan(self, count) -> int:
        try:
            res_list = ping(self.test_url, count=count)
        except:
            return scan_result(loss_pct=100)

        latencies = [res.time_elapsed_ms for res in res_list if res.success]
        if len(latencies) == 0:
            return scan_result(loss_pct=100)

        average_ms = sum(latencies) / len(latencies)
        loss_pct = (1 - sum([1 if res.success else 0 for res in res_list]) / len(res_list)) * 100

        return scan_result(loss_pct, average_ms, min(latencies), max(latencies))