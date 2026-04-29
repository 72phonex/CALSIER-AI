# tests/test_core.py
import unittest
from calsifer import CalsiferCore

class TestCalsiferCore(unittest.TestCase):
    def test_memory(self):
        core = CalsiferCore("testuser")
        reply = core.chat("Hello?")
        self.assertIn("Calsifer", reply)
        episodes = core.recall()
        self.assertTrue(len(episodes) > 0)

    def test_patch_suggestion(self):
        core = CalsiferCore("testuser")
        core.chat("Please improve response")
        conn = core.conn
        cur = conn.execute("SELECT suggestion FROM patches")
        rows = cur.fetchall()
        self.assertTrue(len(rows) > 0)

if __name__ == "__main__":
    unittest.main()
