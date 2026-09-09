"""Activity changes habitat within fixed visual limits."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pond import habitat
class PondTests(unittest.TestCase):
    def test_empty_and_busy_habitats(self):
        self.assertEqual(habitat([{'count':0}]*365),(0,0))
        self.assertEqual(habitat([{'count':100}]*365),(12,20))
    def test_older_activity_does_not_create_fireflies(self):
        self.assertEqual(habitat([{'count':3}]*358+[{'count':0}]*7),(12,0))
