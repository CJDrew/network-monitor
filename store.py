import sqlite3
from scanner import scan_result
from dataclasses import astuple

class store:
    def __init__(self, name: str):
        self.con = sqlite3.connect(f'{name}.db')
        self._init_table()

    def _init_table(self):
        cursor = self.con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scan_results(timestamp, loss_pct, avg_ms, min_ms, max_ms)")
        self.con.commit()

    def add_observation(self, obs: scan_result, time: str):
        cursor = self.con.cursor()
        print(time)
        cursor.execute('INSERT INTO scan_results (timestamp, loss_pct, avg_ms, min_ms, max_ms) VALUES (?, ?, ?, ?, ?)', (time,) + astuple(obs))
        self.con.commit()

    def get_observations(self):
        cursor = self.con.cursor()
        cursor.execute('SELECT * FROM scan_results')
