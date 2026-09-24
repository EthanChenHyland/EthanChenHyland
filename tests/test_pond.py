"""Activity changes habitat within fixed visual limits."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pond import habitat, draw_pond
import tempfile
import xml.etree.ElementTree as ET
class PondTests(unittest.TestCase):
    def test_empty_and_busy_habitats(self):
        self.assertEqual(habitat([{'count':0}]*365),(0,0))
        self.assertEqual(habitat([{'count':100}]*365),(12,20))
    def test_older_activity_does_not_create_fireflies(self):
        self.assertEqual(habitat([{'count':3}]*358+[{'count':0}]*7),(12,0))

    def test_frog_is_inline_visible_artwork_in_both_themes(self):
        with tempfile.TemporaryDirectory() as out:
            draw_pond([{'date':'2026-09-24','count':3}],out)
            ns = {'s':'http://www.w3.org/2000/svg'}
            for name in ('pond.svg','pond-dark.svg'):
                root = ET.parse(Path(out)/name).getroot()
                frog = root.find('.//s:g[@class="pond-frog"]',ns)
                self.assertIsNotNone(frog)
                self.assertTrue(frog.findall('.//s:text',ns))
                self.assertIsNone(frog.find('.//s:image',ns))
                self.assertIsNone(frog.find('.//s:animate',ns))
                self.assertFalse(any('clip-path' in node.attrib for node in frog.iter()))
                self.assertIn('transform',frog.attrib)  # Visible if animation is unsupported.
