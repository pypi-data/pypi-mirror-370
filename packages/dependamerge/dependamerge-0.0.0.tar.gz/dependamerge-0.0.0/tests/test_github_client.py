# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

from unittest.mock import Mock, patch

import pytest

from dependamerge.github_client import GitHubClient
from dependamerge.models import PullRequestInfo


class TestGitHubClient:
    @patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"})
    def test_init_with_env_token(self):
        client = GitHubClient()
        assert client.token == "test_token"

    def test_init_with_explicit_token(self):
        client = GitHubClient(token="explicit_token")
        assert client.token == "explicit_token"

    def test_init_without_token_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubClient()

    def test_parse_pr_url_valid(self):
        client = GitHubClient(token="test_token")
        owner, repo, pr_number = client.parse_pr_url(
            "https://github.com/lfreleng-actions/python-project-name-action/pull/22"
        )
        assert owner == "lfreleng-actions"
        assert repo == "python-project-name-action"
        assert pr_number == 22

    def test_parse_pr_url_with_trailing_slash(self):
        client = GitHubClient(token="test_token")
        owner, repo, pr_number = client.parse_pr_url(
            "https://github.com/owner/repo/pull/123/"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert pr_number == 123

    def test_parse_pr_url_invalid(self):
        client = GitHubClient(token="test_token")
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            client.parse_pr_url("https://invalid-url.com")

    def test_parse_pr_url_with_files_path(self):
        client = GitHubClient(token="test_token")
        owner, repo, pr_number = client.parse_pr_url(
            "https://github.com/lfreleng-actions/python-project-name-action/pull/23/files"
        )
        assert owner == "lfreleng-actions"
        assert repo == "python-project-name-action"
        assert pr_number == 23

    def test_parse_pr_url_with_commits_path(self):
        client = GitHubClient(token="test_token")
        owner, repo, pr_number = client.parse_pr_url(
            "https://github.com/owner/repo/pull/456/commits"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert pr_number == 456

    def test_parse_pr_url_with_multiple_path_segments(self):
        client = GitHubClient(token="test_token")
        owner, repo, pr_number = client.parse_pr_url(
            "https://github.com/org/repository/pull/789/files/diff"
        )
        assert owner == "org"
        assert repo == "repository"
        assert pr_number == 789

    @patch("dependamerge.github_client.Github")
    def test_get_pull_request_info(self, mock_github_class):
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.full_name = "owner/repo"

        mock_pr = Mock()
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.number = 22
        mock_pr.title = "Test PR"
        mock_pr.body = "Test body"
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.head.sha = "abc123"
        mock_pr.base.ref = "main"
        mock_pr.head.ref = "update-deps"
        mock_pr.state = "open"
        mock_pr.mergeable = True
        mock_pr.mergeable_state = "clean"
        mock_pr.behind_by = 0
        mock_pr.html_url = "https://github.com/owner/repo/pull/22"

        mock_file = Mock()
        mock_file.filename = "requirements.txt"
        mock_file.additions = 1
        mock_file.deletions = 1
        mock_file.changes = 2
        mock_file.status = "modified"
        mock_pr.get_files.return_value = [mock_file]

        client = GitHubClient(token="test_token")
        pr_info = client.get_pull_request_info("owner", "repo", 22)

        assert isinstance(pr_info, PullRequestInfo)
        assert pr_info.number == 22
        assert pr_info.title == "Test PR"
        assert pr_info.author == "dependabot[bot]"
        assert len(pr_info.files_changed) == 1
        assert pr_info.files_changed[0].filename == "requirements.txt"

    def test_is_automation_author(self):
        client = GitHubClient(token="test_token")

        assert client.is_automation_author("dependabot[bot]")
        assert client.is_automation_author("pre-commit-ci[bot]")
        assert client.is_automation_author("renovate[bot]")
        assert not client.is_automation_author("human-user")
        assert not client.is_automation_author("random-bot")

    @patch("dependamerge.github_client.Github")
    def test_get_pull_request_commits(self, mock_github_class):
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        # Mock repository and PR
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        mock_pr = Mock()
        mock_repo.get_pull.return_value = mock_pr

        # Mock commits
        mock_commit1 = Mock()
        mock_commit1.commit.message = (
            "Fix bug in authentication\n\nDetailed description"
        )
        mock_commit2 = Mock()
        mock_commit2.commit.message = "Update tests"

        mock_pr.get_commits.return_value = [mock_commit1, mock_commit2]

        client = GitHubClient(token="test_token")
        commits = client.get_pull_request_commits("owner", "repo", 22)

        assert len(commits) == 2
        assert commits[0] == "Fix bug in authentication\n\nDetailed description"
        assert commits[1] == "Update tests"

        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_once_with(22)

    @patch("dependamerge.github_client.Github")
    def test_get_pull_request_commits_empty(self, mock_github_class):
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        mock_pr = Mock()
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_commits.return_value = []

        client = GitHubClient(token="test_token")
        commits = client.get_pull_request_commits("owner", "repo", 22)

        assert commits == []
