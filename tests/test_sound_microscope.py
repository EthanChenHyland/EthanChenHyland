from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sound_microscope import sample_frame, strongest, PITCHES

class MicroscopeTests(unittest.TestCase):
    def test_selects_nearest_recorded_frame(self):
        frames=[{'time_seconds':'2.98'},{'time_seconds':'3.004'},{'time_seconds':'3.025'}]
        self.assertIs(sample_frame(frames,3),frames[1])

    def test_ties_and_silence_do_not_invent_unique_winner(self):
        row={'audio_'+p:0 for p in PITCHES}
        self.assertEqual(strongest(row),[])
        row.update(audio_Cs=0.8,audio_F=0.8)
        self.assertEqual(strongest(row),['C#','F'])
