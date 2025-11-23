import sys
import unittest
import importlib
from unittest.mock import patch


class TestRunModule(unittest.TestCase):
    def _import_run_with_args(self, argv):
        if "run" in sys.modules:
            del sys.modules["run"]

        with patch("sys.argv", argv), \
             patch("config.overwrite_from_args") as mock_overwrite, \
             patch("example_analysis.ExampleAnalysis") as MockExample, \
             patch("contributor_activity_analysis.ContributorActivityAnalysis") as MockContributor, \
             patch("reopened_closed_analysis.ReopenedClosedAnalysis") as MockReopened, \
             patch("issue_creation_trend_analysis.IssueCreationTrendAnalysis") as MockTrend:

            run_module = importlib.import_module("run")

        return (
            run_module,
            mock_overwrite,
            MockExample,
            MockContributor,
            MockReopened,
            MockTrend,
        )

    def test_parse_args_with_required_and_optional_parameters(self):
        """
        Ensure parse_args correctly parses feature, user, and label.
        """
        argv = ["run.py", "--feature", "1", "--user", "alice", "--label", "bug"]

        run_module, _, _, _, _, _ = self._import_run_with_args(argv)

        with patch("sys.argv", argv):
            args = run_module.parse_args()

        self.assertEqual(args.feature, 1)
        self.assertEqual(args.user, "alice")
        self.assertEqual(args.label, "bug")

    def test_parse_args_with_only_required_feature(self):
        """
        Ensure parse_args works with just the required --feature flag.
        """
        argv = ["run.py", "-f", "2"]

        run_module, _, _, _, _, _ = self._import_run_with_args(argv)

        with patch("sys.argv", argv):
            args = run_module.parse_args()

        self.assertEqual(args.feature, 2)
        self.assertIsNone(args.user)
        self.assertIsNone(args.label)

    def test_feature_0_triggers_example_analysis(self):
        """
        For --feature 0, ExampleAnalysis().run() should be called.
        """
        argv = ["run.py", "--feature", "0"]
        _, mock_overwrite, MockExample, MockContributor, MockReopened, MockTrend = (
            self._import_run_with_args(argv)
        )

        mock_overwrite.assert_called_once()
        MockExample.assert_called_once()
        MockExample.return_value.run.assert_called_once()

        MockContributor.assert_not_called()
        MockReopened.assert_not_called()
        MockTrend.assert_not_called()

    def test_feature_1_triggers_contributor_activity_analysis(self):
        """
        For --feature 1, ContributorActivityAnalysis().run() should be called.
        """
        argv = ["run.py", "-f", "1"]
        _, mock_overwrite, MockExample, MockContributor, MockReopened, MockTrend = (
            self._import_run_with_args(argv)
        )

        mock_overwrite.assert_called_once()
        MockContributor.assert_called_once()
        MockContributor.return_value.run.assert_called_once()

        MockExample.assert_not_called()
        MockReopened.assert_not_called()
        MockTrend.assert_not_called()

    def test_feature_2_triggers_reopened_closed_analysis(self):
        """
        For --feature 2, ReopenedClosedAnalysis().run() should be called.
        """
        argv = ["run.py", "--feature", "2"]
        _, mock_overwrite, MockExample, MockContributor, MockReopened, MockTrend = (
            self._import_run_with_args(argv)
        )

        mock_overwrite.assert_called_once()
        MockReopened.assert_called_once()
        MockReopened.return_value.run.assert_called_once()

        MockExample.assert_not_called()
        MockContributor.assert_not_called()
        MockTrend.assert_not_called()

    def test_feature_3_triggers_issue_creation_trend_analysis(self):
        """
        For --feature 3, IssueCreationTrendAnalysis().run() should be called.
        """
        argv = ["run.py", "-f", "3"]
        _, mock_overwrite, MockExample, MockContributor, MockReopened, MockTrend = (
            self._import_run_with_args(argv)
        )

        mock_overwrite.assert_called_once()
        MockTrend.assert_called_once()
        MockTrend.return_value.run.assert_called_once()

        MockExample.assert_not_called()
        MockContributor.assert_not_called()
        MockReopened.assert_not_called()

    def test_invalid_feature_prints_message(self):
        """
        For an invalid feature (e.g., 99), none of the analyses should run,
        and the error message should be printed.
        """
        argv = ["run.py", "--feature", "99"]

        if "run" in sys.modules:
            del sys.modules["run"]

        with patch("sys.argv", argv), \
             patch("config.overwrite_from_args") as mock_overwrite, \
             patch("example_analysis.ExampleAnalysis") as MockExample, \
             patch("contributor_activity_analysis.ContributorActivityAnalysis") as MockContributor, \
             patch("reopened_closed_analysis.ReopenedClosedAnalysis") as MockReopened, \
             patch("issue_creation_trend_analysis.IssueCreationTrendAnalysis") as MockTrend, \
             patch("builtins.print") as mock_print:

            importlib.import_module("run")

        mock_overwrite.assert_called_once()

        MockExample.assert_not_called()
        MockContributor.assert_not_called()
        MockReopened.assert_not_called()
        MockTrend.assert_not_called()

        mock_print.assert_called_once()
        printed_msg = mock_print.call_args.args[0]
        self.assertIn("Need to specify which feature to run", printed_msg)

if __name__ == "__main__":
    unittest.main()