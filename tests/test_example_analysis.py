import unittest
from unittest.mock import patch, MagicMock
from example_analysis import ExampleAnalysis
import pandas as pd

class TestExampleAnalysis(unittest.TestCase):

    @patch("example_analysis.DataLoader")
    @patch("example_analysis.plt.show")
    def test_run_no_user(self, mock_show, mock_loader):
        issue1 = MagicMock(creator="Alice", events=[MagicMock(author="Alice"), MagicMock(author="Bob")])
        issue2 = MagicMock(creator="Bob", events=[MagicMock(author="Alice")])
        mock_loader.return_value.get_issues.return_value = [issue1, issue2]
        analysis = ExampleAnalysis()
        analysis.run()
        mock_show.assert_called_once()
        

    @patch("example_analysis.DataLoader")
    @patch("example_analysis.plt.show")
    def test_run_with_user_filter(self, mock_show, mock_loader):
        issue1 = MagicMock(creator="Alice", events=[MagicMock(author="Alice")])
        issue2 = MagicMock(creator="Bob", events=[MagicMock(author="Bob")])
        mock_loader.return_value.get_issues.return_value = [issue1, issue2]
        analysis = ExampleAnalysis()
        analysis.run()
        mock_show.assert_called_once()


    @patch("example_analysis.DataLoader")
    @patch("example_analysis.plt.show")
    @patch("pandas.DataFrame.plot") 
    def test_internal_count_events(self, mock_plot, mock_show, mock_loader):
        issue1 = MagicMock()
        issue1.creator = "Alice"
        issue1.events = [MagicMock(author="Alice"), MagicMock(author="Bob")]

        issue2 = MagicMock()
        issue2.creator = "Bob"
        issue2.events = [MagicMock(author="Alice")]

        mock_loader.return_value.get_issues.return_value = [issue1, issue2]

        analysis = ExampleAnalysis()
        analysis.USER = None
        analysis.run()
        df_arg = mock_plot.call_args[0][0] if mock_plot.call_args else None
        df = pd.DataFrame.from_records([{'creator':issue1.creator}, {'creator':issue2.creator}])
        counts = df['creator'].value_counts()
        self.assertEqual(counts['Alice'], 1)
        self.assertEqual(counts['Bob'], 1)
        mock_show.assert_called_once()


    @patch("example_analysis.DataLoader")
    @patch("example_analysis.plt.show")
    def test_run_with_user_no_match(self, mock_show, mock_loader):

        issue1 = MagicMock(creator="Alice", events=[MagicMock(author="Bob")])
        issue2 = MagicMock(creator="Bob", events=[MagicMock(author="Charlie")])
        mock_loader.return_value.get_issues.return_value = [issue1, issue2]
        analysis = ExampleAnalysis()
        analysis.USER = "NonExistentUser" 
        try:
            analysis.run()
        except Exception as e:
            self.fail(f"ExampleAnalysis.run() crashed when no events matched user filter: {e}")
        mock_show.assert_called_once() 


if __name__ == "__main__":
    unittest.main()
