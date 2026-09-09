"""Boundary cases for checkpoints and deterministic daily discovery."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from observatory import next_target, spotlight, comparison


class ObservatoryTests(unittest.TestCase):
    def test_checkpoint_always_advances(self):
        self.assertEqual(next_target(0,100),100)
        self.assertEqual(next_target(99,100),100)
        self.assertEqual(next_target(100,100),200)

    def test_daily_pick_rotates_and_ignores_order_and_archives(self):
        repos=[{'name':'B','archived':False},{'name':'A','archived':False},{'name':'C','archived':True}]
        first=spotlight(repos,'2026-09-08')
        self.assertEqual(first,spotlight(list(reversed(repos)),'2026-09-08'))
        self.assertNotEqual(first,spotlight(repos,'2026-09-09'))
        self.assertIsNone(spotlight([],'2026-09-08'))
        self.assertIsNone(spotlight([repos[2]],'2026-09-08'))

    def test_comparison_escapes_api_values(self):
        result=comparison([{'name':'<img>','url':'https://github.com/a/b','languages':{'A&B':1},'archived':True,'pushed':'2026-09-08'}])
        self.assertIn('&lt;img&gt;',result)
        self.assertIn('A&amp;B',result)
        self.assertIn('Archived',result)


if __name__ == '__main__':
    unittest.main()
