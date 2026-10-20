from scanner import scanner
from store import store
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo
from monitor_type import monitor_type

DNS_DOMAIN = 'google.com'
STATIC_IP = '8.8.8.8'
SLEEP_SEC = 5

def main():
    s_dns = scanner(DNS_DOMAIN)
    s_static = scanner(STATIC_IP)
    db = store('scan_results')
    while True:
        dns_scan_result = s_dns.scan(25)
        static_scan_result = s_static.scan(25)
        time = datetime.now(tz=ZoneInfo('America/Los_Angeles')).isoformat()

        db.add_observation(dns_scan_result, monitor_type.DNS, time)
        db.add_observation(static_scan_result, monitor_type.STATIC_IP, time)
        sleep(SLEEP_SEC)

if __name__ == '__main__':
    main()