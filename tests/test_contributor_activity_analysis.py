import unittest
from unittest.mock import patch
from contributor_activity_analysis import ContributorActivityAnalysis


class DummyIssue:
    def __init__(self, creator, created_date):
        self.creator = creator
        self.created_date = created_date


class TestContributorActivityAnalysis(unittest.TestCase):

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    def test_no_issues(self, mock_show, mock_dataloader):
        mock_dataloader.return_value.get_issues.return_value = []
        analysis = ContributorActivityAnalysis()
        analysis.run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", return_value="")
    def test_basic_run(self, mock_input, mock_show, mock_dataloader):
        issues = [
            DummyIssue("alice", "2025-01-01T12:00:00Z"),
            DummyIssue("bob", "2025-01-02T12:00:00Z"),
            DummyIssue("alice", "2025-02-01T12:00:00Z"),
        ]
        mock_dataloader.return_value.get_issues.return_value = issues
        analysis = ContributorActivityAnalysis()
        analysis.run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", side_effect=["2025", "n"])
    def test_year_filter_no_save(self, mock_input, mock_show, mock_dataloader):
        issues = [
            DummyIssue("alice", "2024-12-31T12:00:00Z"),
            DummyIssue("bob", "2025-01-01T12:00:00Z"),
            DummyIssue("alice", "2025-02-01T12:00:00Z"),
        ]
        mock_dataloader.return_value.get_issues.return_value = issues
        analysis = ContributorActivityAnalysis()
        analysis.run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", side_effect=["", "y"])
    @patch("os.makedirs")
    @patch("matplotlib.pyplot.Figure.savefig")
    def test_save_chart(self, mock_savefig, mock_makedirs, mock_input, mock_show, mock_dataloader):
        issues = [
            DummyIssue("alice", "2025-01-01T12:00:00Z"),
            DummyIssue("bob", "2025-01-02T12:00:00Z"),
        ]
        mock_dataloader.return_value.get_issues.return_value = issues
        analysis = ContributorActivityAnalysis()
        analysis.run()

        self.assertTrue(mock_savefig.called)
        self.assertTrue(mock_makedirs.called)

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", return_value="")
    def test_invalid_date_entries(self, mock_input, mock_show, mock_dataloader):
        issues = [
            DummyIssue("alice", "not-a-date"),
            DummyIssue("bob", "2025-01-02T12:00:00Z"),
        ]
        mock_dataloader.return_value.get_issues.return_value = issues
        analysis = ContributorActivityAnalysis()
        analysis.run()

    @patch("builtins.input", return_value="")
    def test_no_usernames(self, mock_input):
        issues = [DummyIssue("", "2025-01-01T12:00:00Z")]
        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()

        import matplotlib
        matplotlib.use("Agg")

        analysis.run()

    @patch("builtins.input", return_value="2024")
    def test_year_filter_no_data(self, mock_input):
        issues = [DummyIssue("alice", "2025-01-01T12:00:00Z")]
        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()

        import matplotlib
        matplotlib.use("Agg")

        analysis.run()

    @patch("builtins.input", side_effect=["", "y"])
    def test_save_chart_path(self, mock_input):
        import tempfile
        issues = [DummyIssue("alice", "2025-01-01T12:00:00Z")]

        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()

        import matplotlib
        matplotlib.use("Agg")

        analysis.output_dir = tempfile.TemporaryDirectory().name
        analysis.run()

    @patch("builtins.input", return_value="")
    @patch("contributor_activity_analysis.plt.show")
    def test_all_invalid_dates(self, mock_show, mock_input):
        issues = [
            DummyIssue("alice", "invalid-date"),
            DummyIssue("bob", "not-a-date"),
        ]
        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()
        analysis.run()

    @patch("builtins.input", return_value="")
    @patch("contributor_activity_analysis.plt.show")
    def test_no_years_detected(self, mock_show, mock_input):
        issues = [
            DummyIssue("alice", None),
            DummyIssue("bob", None),
        ]
        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()
        analysis.run()

    @patch("builtins.input", side_effect=["2030", "n"])
    @patch("contributor_activity_analysis.plt.show")
    def test_year_filter_not_found(self, mock_show, mock_input):
        issues = [
            DummyIssue("alice", "2025-01-01T12:00:00Z"),
            DummyIssue("bob", "2025-01-02T12:00:00Z"),
        ]
        analysis = ContributorActivityAnalysis()
        analysis.loader = type("", (), {"get_issues": lambda self: issues})()
        analysis.run()

    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", return_value="abc")
    def test_invalid_year_input_causes_crash(self, mock_input, mock_show, mock_dataloader):
        """
        BUG: No validation for year input. Non-numeric input causes ValueError.
        Expected: Should handle gracefully or show error message.
        Actual: Crashes with ValueError - this test will fail with ValueError.
        """
        issues = [DummyIssue("alice", "2025-01-01T12:00:00Z")]
        mock_dataloader.return_value.get_issues.return_value = issues
        
        analysis = ContributorActivityAnalysis()
        with self.assertRaises(ValueError):
            analysis.run()
        self.fail("Program should handle invalid year input gracefully, not raise ValueError")
    
    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", return_value="")
    def test_case_sensitive_usernames_counted_separately(self, mock_input, mock_show, mock_dataloader):
        """
        BUG: Usernames are case-sensitive. "Alice" and "alice" count as different users.
        Expected: Should normalize to lowercase for counting.
        Actual: Treats them as separate contributors.
        """
        issues = [
            DummyIssue("Alice", "2025-01-01T12:00:00Z"),
            DummyIssue("alice", "2025-01-02T12:00:00Z"),
            DummyIssue("ALICE", "2025-01-03T12:00:00Z"),
        ]
        mock_dataloader.return_value.get_issues.return_value = issues
        
        analysis = ContributorActivityAnalysis()
        analysis.run()
        usernames = [issue.creator for issue in issues]
        unique_users = len(set(u.lower() for u in usernames))
        actual_unique = len(set(usernames))
        
        self.assertEqual(actual_unique, unique_users, 
                        f"Expected {unique_users} unique user, got {actual_unique}")
        
    @patch("contributor_activity_analysis.DataLoader")
    @patch("contributor_activity_analysis.plt.show")
    @patch("builtins.input", side_effect=["-1", "n"])
    def test_negative_year_accepted(self, mock_input, mock_show, mock_dataloader):
        """
        BUG: Negative year input is accepted without validation.
        Expected: Should reject negative years.
        Actual: Accepts -1, -2024, etc.
        """
        issues = [DummyIssue("alice", "2025-01-01T12:00:00Z")]
        mock_dataloader.return_value.get_issues.return_value = issues
        
        analysis = ContributorActivityAnalysis()
        error_raised = False
        try:
            analysis.run()
        except ValueError:
            error_raised = True
        self.assertTrue(error_raised, "Program should reject negative year input, not accept it")

if __name__ == "__main__":
    unittest.main()