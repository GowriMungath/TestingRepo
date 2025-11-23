import os
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import issue_creation_trend_analysis as mod


class DummyIssue:
    def __init__(self, created_date):
        self.created_date = created_date


class TestIssueCreationTrendAnalysis(unittest.TestCase):
    def _make_analysis(self):
        with patch.object(mod, "config") as mock_config:
            mock_config.get_parameter.return_value = "test_charts"
            analysis = mod.IssueCreationTrendAnalysis()
        return analysis

    def test_monthly_trend_for_specific_year_and_save_chart(self):
        dummy_issues = [
            DummyIssue("2024-01-10"),
            DummyIssue("2024-01-15"),
            DummyIssue("2024-03-05"),
            DummyIssue("2023-12-30"), 
        ]

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show") as mock_show, \
             patch.object(mod.plt, "savefig") as mock_savefig, \
             patch("builtins.input", side_effect=["2024", "y"]):

            MockLoader.return_value.get_issues.return_value = dummy_issues

            analysis = self._make_analysis()

            buf = io.StringIO()
            with redirect_stdout(buf):
                analysis.run()

            output = buf.getvalue()

            self.assertIn("Showing monthly issue trend for year 2024", output)
            self.assertIn("Summary for 2024", output)
            self.assertIn("Most active month:", output)

            mock_savefig.assert_called_once()
            save_args, _ = mock_savefig.call_args
            saved_path = save_args[0]
            
            self.assertIn("issue_analysis_2024_", os.path.basename(saved_path))

            mock_show.assert_called_once()

    def test_yearly_trend_for_all_years_without_saving(self):
        dummy_issues = [
            DummyIssue("2022-05-01"),
            DummyIssue("2022-07-15"),
            DummyIssue("2023-01-20"),
            DummyIssue("2023-03-10"),
        ]

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show") as mock_show, \
             patch.object(mod.plt, "savefig") as mock_savefig, \
             patch("builtins.input", side_effect=["", "n"]):

            MockLoader.return_value.get_issues.return_value = dummy_issues

            analysis = self._make_analysis()

            buf = io.StringIO()
            with redirect_stdout(buf):
                analysis.run()

            output = buf.getvalue()

            self.assertIn("Showing yearly issue creation trend", output)
            self.assertIn("Overall Summary (All Years)", output)
            self.assertIn("Most active year:", output)

            mock_savefig.assert_not_called()
            mock_show.assert_called_once()

    def test_no_issues_found_for_selected_year(self):
        dummy_issues = [
            DummyIssue("2023-01-01"),
            DummyIssue("2023-02-01"),
        ]

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show") as mock_show, \
             patch.object(mod.plt, "savefig") as mock_savefig, \
             patch("builtins.input", return_value="2024"):

            MockLoader.return_value.get_issues.return_value = dummy_issues

            analysis = self._make_analysis()

            buf = io.StringIO()
            with redirect_stdout(buf):
                analysis.run()

            output = buf.getvalue()

            self.assertIn("No issues found for year 2024.", output)
            mock_savefig.assert_not_called()
            mock_show.assert_not_called()


    def test_invalid_year_input(self):
        """
        BUG 1: Non-numeric year input.
        Currently: int('abcd') raises ValueError and crashes.

        Expected (what this test encodes):
        - run() should handle non-numeric input gracefully instead of crashing.
        """
        dummy_issues = [DummyIssue("2023-01-01")]

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show"), \
             patch("builtins.input", side_effect=["abcd", "n"]):

            MockLoader.return_value.get_issues.return_value = dummy_issues
            analysis = self._make_analysis()

            try:
                analysis.run()
            except ValueError as e:
                self.fail(
                    "run() should handle non-numeric year input gracefully, "
                    f"but ValueError was raised: {e}"
                )

    def test_no_issues_loaded(self):
        """
        BUG 2: DataLoader returns no issues.
        Currently: df has no 'created_date', so df['created_date'] raises KeyError.

        Expected:
        - run() should handle an empty issue list without crashing.
        """
        dummy_issues = []  

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show"), \
             patch("builtins.input", side_effect=["", "n"]):

            MockLoader.return_value.get_issues.return_value = dummy_issues
            analysis = self._make_analysis()

            try:
                analysis.run()
            except KeyError as e:
                self.fail(
                    "run() should handle an empty issue list without crashing, "
                    f"but KeyError was raised: {e}"
                )

    def test_all_invalid_dates(self):
        """
        BUG 3: All created_date values are invalid and get dropped.
        Currently: trend is empty and idxmax() raises ValueError.

        Expected:
        - run() should handle the case where all rows are dropped (no valid dates)
          without raising ValueError.
        """
        dummy_issues = [
            DummyIssue("not-a-date"),
            DummyIssue("totally-invalid"),
        ]

        with patch.object(mod, "DataLoader") as MockLoader, \
             patch.object(mod.plt, "show"), \
             patch("builtins.input", side_effect=["", "n"]):

            MockLoader.return_value.get_issues.return_value = dummy_issues
            analysis = self._make_analysis()

            try:
                analysis.run()
            except ValueError as e:
                self.fail(
                    "run() should handle the case where all created_date "
                    "values are invalid (df becomes empty) without raising "
                    f"ValueError, but got: {e}"
                )

if __name__ == "__main__":
    unittest.main()