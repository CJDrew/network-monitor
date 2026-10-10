from scanner import scanner
from store import store
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo

def main():
    s = scanner('google.com')
    db = store('scan_results')
    while True:
        scan_result = s.scan(25)
        time = datetime.now(tz=ZoneInfo('America/Los_Angeles')).isoformat()
        db.add_observation(scan_result, time)
        print(scan_result)
        sleep(30)

if __name__ == '__main__':
    main()