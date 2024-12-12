import unittest
from unittest.mock import patch, mock_open

from main import *


class TestGitDependencyGraph(unittest.TestCase):

    def setUp(self):
        self.repo_path = "/path/to/repo"
        self.test_commit_hash_1 = "abcdef1234567890"
        self.test_commit_hash_2 = "123456abcdef7890"
        self.cutoff_date = datetime.datetime(2023, 1, 1)

    @patch('main.open', new_callable=mock_open, read_data='abcdef1234567890\n')
    def test_resolve_head_commit(self, mock_open):
        head_commit = resolve_head_commit(self.repo_path)
        self.assertEqual(head_commit, 'abcdef1234567890')

    @patch('builtins.open', new_callable=mock_open)
    @patch('zlib.decompress',
           return_value=b'commit 123\x00parent abcdef1234567890\ncommitter John Doe <john@example.com> 1700000000 +0000\n\nCommit message')
    def test_read_git_object(self, mock_zlib, mock_open):
        obj_type, data = read_git_object(self.repo_path, self.test_commit_hash_1)
        self.assertEqual(obj_type, 'commit')
        self.assertIn(b'parent abcdef1234567890', data)

    @patch('main.read_git_object')
    def test_parse_commit(self, mock_read_git_object):
        mock_read_git_object.side_effect = [
            ('commit',
             b'parent 123456abcdef7890\ncommitter John Doe <john@example.com> 1700000000 +0000\n\nCommit message'),
            ('commit',
             b'committer Jane Doe <jane@example.com> 1600000000 +0000\n\nInitial commit')
        ]

        commits = []
        parse_commit(self.repo_path, self.test_commit_hash_1, commits)

        self.assertEqual(len(commits), 2)

        self.assertEqual(commits[0]['id'], 'abcdef1234567890')
        self.assertEqual(commits[0]['date'], datetime.datetime.fromtimestamp(1700000000))
        self.assertEqual(commits[0]['parents'], ['123456abcdef7890'])

        self.assertEqual(commits[1]['id'], '123456abcdef7890')
        self.assertEqual(commits[1]['date'], datetime.datetime.fromtimestamp(1600000000))
        self.assertEqual(commits[1]['parents'], [])

    def test_filter_commits_by_date(self):
        commits = [
            {'id': '123', 'date': datetime.datetime(2022, 12, 31)},
            {'id': '456', 'date': datetime.datetime(2023, 1, 2)}
        ]
        filtered_commits = filter_commits_by_date(commits, self.cutoff_date)
        self.assertEqual(len(filtered_commits), 1)
        self.assertEqual(filtered_commits[0]['id'], '123')

    def test_build_dependency_graph(self):
        commits = [
            {'id': '123', 'date': datetime.datetime(2022, 12, 31), 'parents': []},
            {'id': '456', 'date': datetime.datetime(2023, 1, 1), 'parents': ['123']}
        ]
        graph = build_dependency_graph(commits)
        self.assertIn('123 -> 456', graph.source)
        self.assertIn('rankdir=BT', graph.source)


if __name__ == '__main__':
    unittest.main()
