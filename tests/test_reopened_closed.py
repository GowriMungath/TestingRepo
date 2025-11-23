import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from reopened_closed_analysis import ReopenedClosedAnalysis

class TestReopenedClosedAnalysis(unittest.TestCase):

    @patch("builtins.input", side_effect=["", "", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    @patch("reopened_closed_analysis.plt.show")
    def test_internal_computation(self, mock_show, mock_loader, mock_input):
        from datetime import datetime
        issue1 = MagicMock(state="closed", events=[], created_date=datetime(2024,1,1))
        issue2 = MagicMock(state="closed", events=[MagicMock(event_type="reopened")], created_date=datetime(2024,2,1))
        issue3 = MagicMock(state="open", events=[MagicMock(event_type="reopened")], created_date=datetime(2024,3,1))
        mock_loader.return_value.get_issues.return_value = [issue1, issue2, issue3]
        analysis = ReopenedClosedAnalysis()
        analysis.run()
        reopened_count = sum(
            len([e for e in issue.events if e.event_type == "reopened"])
            for issue in [issue1, issue2, issue3]
        )
        self.assertEqual(reopened_count, 2)
        self.assertTrue(mock_show.called)


    @patch("builtins.input", side_effect=["", "", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    @patch("reopened_closed_analysis.plt.show")
    @patch("reopened_closed_analysis.pd.to_datetime")
    def test_reopened_analysis_no_save(self, mock_to_datetime, mock_show, mock_loader, mock_input):
        mock_to_datetime.side_effect = lambda x, utc=True: pd.Timestamp(datetime(2024, 1, 1), tz='UTC')
        fake_issues = [
            MagicMock(number=1, state='open', created_date='2024-01-01', events=[]),
            MagicMock(number=2, state='closed', created_date='2024-02-01', events=[]),
            MagicMock(number=3, state='closed', created_date='2024-03-01', events=[MagicMock(event_type='reopened')]),
        ]
        mock_loader.return_value.get_issues.return_value = fake_issues
        analysis = ReopenedClosedAnalysis()
        analysis.run()
        mock_show.assert_called_once()


    @patch("builtins.input", side_effect=["", "", "y"])
    @patch("reopened_closed_analysis.DataLoader")
    @patch("reopened_closed_analysis.plt.savefig")
    @patch("reopened_closed_analysis.datetime")
    @patch("reopened_closed_analysis.pd.to_datetime")
    def test_reopened_analysis_saves_chart(self, mock_to_datetime, mock_dt, mock_savefig, mock_loader, mock_input):
        mock_to_datetime.side_effect = lambda x, utc=True: pd.Timestamp(datetime(2024, 1, 1), tz='UTC')
        mock_dt.now.return_value.strftime.return_value = "20240101-121200"

        fake_issues = [
            MagicMock(number=1, state='open', created_date='2024-01-01', events=[]),
            MagicMock(number=2, state='closed', created_date='2024-02-01', events=[]),
            MagicMock(number=3, state='closed', created_date='2024-03-01', events=[MagicMock(event_type='reopened')]),
        ]
        mock_loader.return_value.get_issues.return_value = fake_issues
        analysis = ReopenedClosedAnalysis()
        analysis.run()
        mock_savefig.assert_called_once()  


    @patch("builtins.input", side_effect=["", "", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    @patch("builtins.print")
    def test_reopened_analysis_empty_issues(self, mock_print, mock_loader, mock_input):
        mock_loader.return_value.get_issues.return_value = []  
        analysis = ReopenedClosedAnalysis()
        analysis.run()
        printed = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("No issues found in the specified range.", printed)


    @patch("builtins.input", side_effect=["2024-01-01", "", "n"]) 
    @patch("reopened_closed_analysis.DataLoader")
    @patch("reopened_closed_analysis.plt.show")
    def test_start_date_filter(self, mock_show, mock_loader, _):
        fake_issues = [
            MagicMock(number=1, state='open', created_date='2023-12-31', events=[]), 
            MagicMock(number=2, state='open', created_date='2024-01-02', events=[]),
        ]
        mock_loader.return_value.get_issues.return_value = fake_issues
        analysis = ReopenedClosedAnalysis()
        analysis.run()


    @patch("builtins.input", side_effect=["", "2024-01-01", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    @patch("reopened_closed_analysis.plt.show")
    def test_end_date_filter(self, mock_show, mock_loader, _):
        fake_issues = [
            MagicMock(number=1, state='open', created_date='2024-01-02', events=[]),
            MagicMock(number=2, state='open', created_date='2023-12-31', events=[]),
        ]
        mock_loader.return_value.get_issues.return_value = fake_issues
        analysis = ReopenedClosedAnalysis()
        analysis.run()


    # This test case is expected to fail
    @patch("builtins.input", side_effect=["abc", "", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    def test_invalid_date_input_failure(self, mock_loader, mock_input):
        from reopened_closed_analysis import ReopenedClosedAnalysis
        mock_loader.return_value.get_issues.return_value = [
            MagicMock(number=1, state="open", created_date="2024-02-01", events=[])
        ]
        analysis = ReopenedClosedAnalysis()
        try:
            analysis.run()
        except Exception:
            self.fail("Expected failure due to invalid date input") 


    # This test case is expected to fail
    @patch("builtins.input", side_effect=["", "", "n"])
    @patch("reopened_closed_analysis.DataLoader")
    def test_events_none_failure(self, mock_loader, mock_input):
        from reopened_closed_analysis import ReopenedClosedAnalysis
        mock_loader.return_value.get_issues.return_value = [
            MagicMock(number=1, state="closed", created_date="2024-01-01", events=None)
        ]
        analysis = ReopenedClosedAnalysis()
        try:
            analysis.run()
        except TypeError:
            self.fail("Expected failure when issue.events is None")


if __name__ == "__main__":
    unittest.main()
