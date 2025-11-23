import unittest
from unittest.mock import patch, mock_open
from types import SimpleNamespace
import data_loader

sample_issues_json = [
    {"id": 1, "title": "Issue 1"},
    {"id": 2, "title": "Issue 2"}
]

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        data_loader._ISSUES = None

    def tearDown(self):
        data_loader._ISSUES = None

    def test_data_loader_initialization(self):
        with patch('config.get_parameter', return_value='dummy_path.json'):
            loader = data_loader.DataLoader()
            self.assertEqual(loader.data_path, 'dummy_path.json')

    def test_load_reads_file_and_creates_issues(self):
        with patch('config.get_parameter', return_value='dummy_path.json'), \
             patch('builtins.open', mock_open(read_data='[{"id":1},{"id":2}]')), \
             patch('data_loader.Issue', side_effect=lambda x: f"Issue-{x['id']}") as mock_issue:

            loader = data_loader.DataLoader()
            issues = loader._load()
            self.assertEqual(issues, ["Issue-1", "Issue-2"])
            self.assertEqual(mock_issue.call_count, 2)

    def test_get_issues_loads_only_once(self):
        with patch('config.get_parameter', return_value='dummy_path.json'), \
             patch('builtins.open', mock_open(read_data='[{"id":1},{"id":2}]')), \
             patch('data_loader.Issue', side_effect=lambda x: f"Issue-{x['id']}"):

            loader = data_loader.DataLoader()
            issues_first = loader.get_issues()
            self.assertEqual(issues_first, ["Issue-1", "Issue-2"])

            issues_second = loader.get_issues()
            self.assertIs(issues_second, issues_first)

    def test_get_issues_prints_message(self):
        with patch('config.get_parameter', return_value='dummy_path.json'), \
             patch('builtins.open', mock_open(read_data='[{"id":1}]')), \
             patch('data_loader.Issue', side_effect=lambda x: f"Issue-{x['id']}"):

            loader = data_loader.DataLoader()
            with patch('builtins.print') as mock_print:
                _ = loader.get_issues()
                mock_print.assert_any_call("Loaded 1 issues from dummy_path.json.")

    def test_singleton_behavior_across_load_calls(self):
        with patch('config.get_parameter', return_value='dummy_path.json'), \
             patch('builtins.open', mock_open(read_data='[{"id":1}]')), \
             patch('data_loader.Issue', side_effect=lambda x: f"Issue-{x['id']}"):

            loader1 = data_loader.DataLoader()
            issues1 = loader1.get_issues()

            loader2 = data_loader.DataLoader()
            issues2 = loader2.get_issues()

            self.assertIs(issues1, issues2)


if __name__ == "__main__":
    unittest.main()