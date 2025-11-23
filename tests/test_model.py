import unittest
from datetime import datetime

import model as mod

class TestUser(unittest.TestCase):
    def test_user_basic_fields_and_default_site_admin(self):
        data = {
            "id": 123,
            "login": "alice",
            "type": "User",
        }
        user = mod.User(data)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.login, "alice")
        self.assertEqual(user.type, "User")
        self.assertFalse(user.site_admin)

    def test_user_site_admin_true(self):
        data = {"id": 1, "login": "root", "site_admin": True}
        user = mod.User(data)
        self.assertTrue(user.site_admin)


class TestLabel(unittest.TestCase):
    def test_label_from_dict(self):
        label = mod.Label({"name": "bug"})
        self.assertEqual(label.name, "bug")

    def test_label_from_string(self):
        label = mod.Label("feature")
        self.assertEqual(label.name, "feature")

    def test_label_from_unsupported_type(self):
        label = mod.Label(42)
        self.assertIsNone(label.name)


class TestComment(unittest.TestCase):
    def test_comment_with_nested_author_and_valid_date(self):
        data = {
            "id": 1,
            "issue_id": 10,
            "event_id": 100,
            "author": {"id": 7, "login": "bob"},
            "body": "This is a comment",
            "created_at": "2024-01-01T10:00:00Z",
        }
        comment = mod.Comment(data)
        self.assertEqual(comment.id, 1)
        self.assertEqual(comment.issue_id, 10)
        self.assertEqual(comment.event_id, 100)
        self.assertEqual(comment.author_id, 7)
        self.assertEqual(comment.author_login, "bob")
        self.assertEqual(comment.comment, "This is a comment")
        self.assertIsInstance(comment.created_date, datetime)
        self.assertEqual(comment.created_date.year, 2024)

    def test_comment_with_flat_author_and_invalid_date_and_comment_field(self):
        data = {
            "id": 2,
            "issue_id": 20,
            "event_id": 200,
            "author": "flat-author",
            "author_id": 99,
            "comment": "Fallback comment",
            "created_at": "not-a-date",
        }
        comment = mod.Comment(data)
        self.assertEqual(comment.author_id, 99)
        self.assertIsNone(comment.author_login)
        self.assertEqual(comment.comment, "Fallback comment")
        self.assertIsNone(comment.created_date)

class TestEvent(unittest.TestCase):
    def test_event_with_actor_label_and_valid_date(self):
        data = {
            "id": 11,
            "event": "closed",
            "issue_id": 101,
            "comment_id": 1001,
            "actor": {"id": 5, "login": "charlie"},
            "label": {"name": "bug"},
            "created_at": "2023-12-31T23:59:59Z",
        }
        event = mod.Event(data)
        self.assertEqual(event.id, 11)
        self.assertEqual(event.event_type, "closed")
        self.assertEqual(event.issue_id, 101)
        self.assertEqual(event.comment_id, 1001)
        self.assertEqual(event.author_id, 5)
        self.assertEqual(event.author_login, "charlie")
        self.assertEqual(event.label_name, "bug")
        self.assertIsInstance(event.event_date, datetime)
        self.assertEqual(event.event_date.year, 2023)

    def test_event_with_author_fallback_and_event_type_field(self):
        data = {
            "id": 22,
            "event_type": "reopened",
            "issue_id": 202,
            "author": {"id": 8, "login": "dana"},
        }
        event = mod.Event(data)
        self.assertEqual(event.event_type, "reopened")
        self.assertEqual(event.author_id, 8)
        self.assertEqual(event.author_login, "dana")
        self.assertIsNone(event.label_name)
        self.assertIsNone(event.event_date)

    def test_event_with_flat_author_and_invalid_date(self):
        data = {
            "id": 33,
            "event": "assigned",
            "issue_id": 303,
            "author": "flat-author",
            "author_id": 123,
            "created_at": "definitely-not-a-date",
        }
        event = mod.Event(data)
        self.assertEqual(event.author_id, 123)
        self.assertIsNone(event.author_login)
        self.assertIsNone(event.event_date)

class TestIssueLabelAndAssignee(unittest.TestCase):
    def test_issue_label_simple(self):
        il = mod.IssueLabel(issue_number=42, label_name="bug")
        self.assertEqual(il.issue_number, 42)
        self.assertEqual(il.label_name, "bug")

    def test_issue_assignee_simple(self):
        ia = mod.IssueAssignee(issue_number=7, assignee_id=999)
        self.assertEqual(ia.issue_number, 7)
        self.assertEqual(ia.assignee_id, 999)


class TestIssue(unittest.TestCase):
    def test_issue_with_nested_user_and_valid_dates_and_children(self):
        data = {
            "number": 101,
            "title": "Test issue",
            "state": "open",
            "url": "https://example.com/issues/101",
            "timeline_url": "https://example.com/issues/101/timeline",
            "body": "Issue body text",
            "user": {"id": 1, "login": "owner"},
            "created_at": "2024-02-01T12:00:00Z",
            "updated_at": "2024-02-02T13:30:00Z",
            "comments": [
                {
                    "id": 1,
                    "issue_id": 101,
                    "author": {"id": 2, "login": "commenter"},
                    "body": "comment text",
                    "created_at": "2024-02-01T13:00:00Z",
                }
            ],
            "events": [
                {
                    "id": 10,
                    "event": "labeled",
                    "issue_id": 101,
                    "actor": {"id": 3, "login": "bot"},
                    "label": {"name": "bug"},
                    "created_at": "2024-02-01T14:00:00Z",
                }
            ],
            "labels": [
                {"name": "bug"},
                "help wanted",
                123, 
            ],
        }
        issue = mod.Issue(data)

        # Basic fields
        self.assertEqual(issue.number, 101)
        self.assertEqual(issue.title, "Test issue")
        self.assertEqual(issue.state, "open")
        self.assertEqual(issue.url, "https://example.com/issues/101")
        self.assertEqual(issue.timeline_url, "https://example.com/issues/101/timeline")
        self.assertEqual(issue.text, "Issue body text")

        self.assertEqual(issue.creator_id, 1)
        self.assertEqual(issue.creator_login, "owner")

        self.assertEqual(issue.creator, "owner")

        self.assertIsInstance(issue.created_date, datetime)
        self.assertIsInstance(issue.updated_date, datetime)
        self.assertEqual(issue.created_date.year, 2024)
        self.assertEqual(issue.updated_date.year, 2024)

        self.assertEqual(len(issue.comments), 1)
        self.assertIsInstance(issue.comments[0], mod.Comment)
        self.assertEqual(issue.comments[0].comment, "comment text")

        self.assertEqual(len(issue.events), 1)
        self.assertIsInstance(issue.events[0], mod.Event)
        self.assertEqual(issue.events[0].event_type, "labeled")

        self.assertEqual(len(issue.labels), 3)
        self.assertIsInstance(issue.labels[0], mod.Label)
        self.assertEqual(issue.labels[0].name, "bug")
        self.assertEqual(issue.labels[1].name, "help wanted")
        self.assertIsNone(issue.labels[2].name)

    def test_issue_with_string_creator_and_created_date_field(self):
        data = {
            "number": 202,
            "title": "String creator test",
            "creator": "string-user",
            "created_date": "2023-05-10T09:00:00Z",
            "updated_date": "not-a-date",
        }
        issue = mod.Issue(data)

        # Creator is a plain string
        self.assertIsNone(issue.creator_id)
        self.assertEqual(issue.creator_login, "string-user")
        self.assertEqual(issue.creator, "string-user")

        self.assertIsInstance(issue.created_date, datetime)
        self.assertEqual(issue.created_date.year, 2023)
        self.assertIsNone(issue.updated_date)

    def test_issue_with_missing_creator_and_no_children(self):
        data = {
            "number": 303,
            "title": "No creator or children",
        }
        issue = mod.Issue(data)

        self.assertIsNone(issue.creator_id)
        self.assertIsNone(issue.creator_login)
        self.assertIsNone(issue.creator)

        self.assertEqual(issue.comments, [])
        self.assertEqual(issue.events, [])
        self.assertEqual(issue.labels, [])


class TestAllExport(unittest.TestCase):
    def test_all_contains_expected_symbols(self):
        expected = {
            "Issue",
            "User",
            "Comment",
            "Event",
            "Label",
            "IssueLabel",
            "IssueAssignee",
        }
        self.assertTrue(hasattr(mod, "__all__"))
        self.assertEqual(set(mod.__all__), expected)

if __name__ == "__main__":
    unittest.main()