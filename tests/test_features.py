"""Guard activity-window boundaries and public metadata rendering."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from features import activity_windows, project_notes


class FeatureTests(unittest.TestCase):
    def test_recent_windows_do_not_overlap_previous_week(self):
        days = [{'count':0}]*16 + [{'count':2}]*7 + [{'count':3}]*7
        self.assertEqual(activity_windows(days),{'week':21,'previous_week':14,'month':35,'active_month':14})

    def test_project_notes_escape_text_and_encode_branch(self):
        repo = {'name':'sample','url':'https://github.com/test/sample','branch':'feature/new',
                'languages':{'Python':20},'issues_enabled':True,
                'latest_commit':{'headline':'<script> & text','url':'https://github.com/test/sample/commit/123','date':'2026-09-08'},
                'release':{'tag':'v1.0','url':'https://github.com/test/sample/releases/tag/v1.0','date':'2026-09-07'}}
        html = project_notes(repo,'Useful <tool>')
        self.assertIn('/commits/feature%2Fnew',html)
        self.assertIn('&lt;script&gt; &amp; text',html)
        self.assertNotIn('<script>',html)
        self.assertIn('Latest release:',html)
        repo['release']=None
        self.assertNotIn('Latest release:',project_notes(repo,'Useful'))


if __name__ == '__main__':
    unittest.main()
