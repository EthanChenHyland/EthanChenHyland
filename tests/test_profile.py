"""Edge cases that could silently misrepresent real activity."""
from datetime import date,timedelta
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generate_profile import featured_repos, language_totals, render, recent_repos, streaks, validate_data, weekly
from make_ascii import prepare, render_ascii
from PIL import Image


def days(counts):
    return [{'date':str(date(2026,1,1)+timedelta(days=i)),'count':count} for i,count in enumerate(counts)]


class ActivityTests(unittest.TestCase):
    def test_today_can_be_in_progress(self):
        current,longest = streaks(days([0,1,2,3,0]))
        self.assertEqual((len(current),len(longest)),(3,3))

    def test_streak_expired(self):
        current,longest = streaks(days([2,1,0,0]))
        self.assertEqual((len(current),len(longest)),(0,2))

    def test_streak_today_and_longer_history(self):
        current,longest = streaks(days([1,1,1,0,1]))
        self.assertEqual((len(current),len(longest)),(1,3))

    def test_zero_and_full_window(self):
        self.assertEqual(streaks(days([0]*365)),([],[]))
        self.assertEqual(tuple(map(len,streaks(days([1]*365)))),(365,365))

    def test_week_buckets_are_sunday_based(self):
        self.assertEqual(weekly(days([1]*8)),[('2025-12-28',3),('2026-01-04',5)])

    def test_language_presence_is_not_primary_language_count(self):
        sizes,counts = language_totals([{'languages':{'Python':10,'Rust':0}}, {'languages':{'Python':20,'Rust':5}}])
        self.assertEqual(dict(sizes),{'Python':30,'Rust':5})
        self.assertEqual(dict(counts),{'Python':2,'Rust':1})

    def test_featured_order_survives_new_repositories(self):
        repos = [{'name': 'New'}, {'name': 'B'}, {'name': 'A'}]
        self.assertEqual([r['name'] for r in featured_repos(repos, ['A', 'B'])], ['A', 'B'])

    def test_featured_missing_and_duplicate_names_do_not_get_replacements(self):
        repos = [{'name': 'A'}, {'name': 'New'}]
        self.assertEqual([r['name'] for r in featured_repos(repos, ['Missing', 'a', 'A'])], ['A'])

    def test_recent_pushes_keep_time_of_day(self):
        repos = [dict(name='Z',pushed='2026-01-01',pushed_at='2026-01-01T01:00:00Z',archived=False),
                 dict(name='A',pushed='2026-01-01',pushed_at='2026-01-01T23:00:00Z',archived=False)]
        self.assertEqual(recent_repos(repos)[0]['name'],'A')

    def test_missing_days_rejected(self):
        with self.assertRaises(ValueError):
            validate_data({'as_of':'2026-01-02','days':days([1,2])})

    def test_leap_day_window(self):
        end = date(2024,3,1)
        data = {'as_of':str(end),'days':[{'date':str(end-timedelta(days=i)),'count':0} for i in range(364,-1,-1)]}
        self.assertEqual(validate_data(data),end)

    def test_empty_account_and_untrusted_description_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = {'as_of':days([0]*365)[-1]['date'],'login':'Example','days':days([0]*365),'repositories':[]}
            render(data,tmp)
            data['repositories']=[{'name':'A&B<repo>','primary':'Python','description':'<script> & "quoted"\x01',
                                   'url':'https://github.com/Example/example','pushed':'2026-01-01','archived':False,'languages':{'Python':1}}]
            data['repositories'].append(dict(data['repositories'][0], name='FunChessEngine'))
            render(data,tmp)
            for path in Path(tmp).glob('*.svg'):
                ET.parse(path)
            self.assertIn('&lt;script&gt;', (Path(tmp)/'recent.svg').read_text())


class AsciiTests(unittest.TestCase):
    def test_luminance_and_geometry(self):
        # Synthetic fixtures test conversion only; never become profile assets.
        image = Image.new('RGB',(200,100),'white')
        for x in range(100):
            for y in range(100):
                image.putpixel((x,y),(0,0,0))
        rows = prepare(image,crop=(0,0,200,100),columns=100)
        self.assertEqual(len(rows),26)
        self.assertIn('@',rows[10])
        self.assertTrue(rows[10].endswith(' '))
        with tempfile.TemporaryDirectory() as tmp:
            render_ascii(rows,tmp,'Test & detail')
            for path in Path(tmp).glob('*.svg'):
                root = ET.parse(path).getroot()
                animate = root.find('.//{http://www.w3.org/2000/svg}animate')
                self.assertEqual(animate.attrib['repeatCount'],'1')

    def test_dark_tones_preserve_pupil_and_transparency(self):
        image = Image.new('RGBA',(200,100),(255,255,255,255))
        for x in range(100):
            for y in range(100):
                image.putpixel((x,y),(0,0,0,255))
        for x in range(180,200):
            for y in range(100):
                image.putpixel((x,y),(255,255,255,0))
        light = prepare(image,crop=(0,0,200,100),columns=100,theme='light')
        dark = prepare(image,crop=(0,0,200,100),columns=100,theme='dark')
        self.assertEqual(light[10][20],'@')
        self.assertEqual(dark[10][20],' ')
        self.assertEqual(dark[10][70],'@')
        self.assertEqual(dark[10][97],' ')

    def test_transparent_image_and_invalid_crop_rejected(self):
        with self.assertRaises(ValueError):
            prepare(Image.new('RGBA',(10,10),(0,0,0,0)))
        with self.assertRaises(ValueError):
            prepare(Image.new('RGB',(10,10)),crop=(0,0,20,20))


if __name__ == '__main__':
    unittest.main()
