# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

import hashlib
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from dependamerge.cli import _generate_override_sha, _validate_override_sha, app
from dependamerge.models import PullRequestInfo


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    @patch("dependamerge.cli.GitHubClient")
    @patch("dependamerge.cli.PRComparator")
    def test_merge_command_dry_run(self, mock_comparator_class, mock_client_class):
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_comparator = Mock()
        mock_comparator_class.return_value = mock_comparator

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = True

        # Mock a repository with a similar PR
        mock_repo = Mock()
        mock_repo.full_name = "owner/other-repo"
        mock_client.get_organization_repositories.return_value = [mock_repo]

        # Mock a similar PR
        mock_open_pr = Mock()
        mock_open_pr.number = 5
        mock_open_pr.user.login = "dependabot[bot]"
        mock_client.get_open_pull_requests.return_value = [mock_open_pr]

        # Mock the similar PR info
        similar_pr = PullRequestInfo(
            number=5,
            title="Bump requests from 2.28.0 to 2.28.1",
            body="Test body",
            author="dependabot[bot]",
            head_sha="def456",
            base_branch="main",
            head_branch="dependabot/pip/requests-2.28.1",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/other-repo",
            html_url="https://github.com/owner/other-repo/pull/5",
        )

        mock_pr = PullRequestInfo(
            number=22,
            title="Bump requests from 2.28.0 to 2.28.1",
            body="Test body",
            author="dependabot[bot]",
            head_sha="abc123",
            base_branch="main",
            head_branch="dependabot/pip/requests-2.28.1",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )

        def get_pr_info_side_effect(owner, repo, pr_number):
            if pr_number == 22:
                return mock_pr
            elif pr_number == 5:
                return similar_pr

        mock_client.get_pull_request_info.side_effect = get_pr_info_side_effect
        mock_client.get_pr_status_details.return_value = "Ready to merge"

        # Mock comparison result
        from dependamerge.models import ComparisonResult

        comparison_result = ComparisonResult(
            is_similar=True,
            confidence_score=0.95,
            reasons=["Same title pattern", "Same author"],
        )
        mock_comparator.compare_pull_requests.return_value = comparison_result

        result = self.runner.invoke(
            app,
            [
                "https://github.com/owner/repo/pull/22",
                "--dry-run",
                "--token",
                "test_token",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.stdout

    @patch("dependamerge.cli.GitHubClient")
    def test_merge_command_invalid_url(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.parse_pr_url.side_effect = ValueError("Invalid GitHub PR URL")

        result = self.runner.invoke(
            app, ["https://invalid-url.com", "--token", "test_token"]
        )

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("dependamerge.cli.GitHubClient")
    def test_merge_command_non_automation_pr(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = False

        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )
        mock_client.get_pull_request_info.return_value = mock_pr
        mock_client.get_pull_request_commits.return_value = [
            "Fix bug\n\nDetailed description"
        ]
        mock_client.get_pr_status_details.return_value = "Ready to merge"

        result = self.runner.invoke(
            app, ["https://github.com/owner/repo/pull/22", "--token", "test_token"]
        )

        assert result.exit_code == 0
        assert "not from a recognized automation tool" in result.stdout

    @patch("dependamerge.cli.GitHubClient")
    @patch("dependamerge.cli.PRComparator")
    def test_merge_command_no_similar_prs_merges_source(
        self, mock_comparator_class, mock_client_class
    ):
        """Test that when no similar PRs are found, the source PR is still merged."""
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_comparator = Mock()
        mock_comparator_class.return_value = mock_comparator

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = True

        # Mock repository with no similar PRs
        mock_repo = Mock()
        mock_repo.full_name = "owner/other-repo"
        mock_repo.owner.login = "owner"
        mock_repo.name = "other-repo"
        mock_client.get_organization_repositories.return_value = [mock_repo]

        # Mock no open PRs (or none that are similar)
        mock_client.get_open_pull_requests.return_value = []

        # Mock the source PR
        mock_pr = PullRequestInfo(
            number=22,
            title="pre-commit autoupdate",
            body="Update pre-commit hooks",
            author="pre-commit-ci[bot]",
            head_sha="abc123",
            base_branch="main",
            head_branch="pre-commit-ci-update-config",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )
        mock_client.get_pull_request_info.return_value = mock_pr
        mock_client.get_pr_status_details.return_value = "Ready to merge"

        # Mock approve and merge methods
        mock_client.approve_pull_request.return_value = True
        mock_client.merge_pull_request.return_value = True
        mock_client.fix_out_of_date_pr.return_value = True

        result = self.runner.invoke(
            app,
            [
                "https://github.com/owner/repo/pull/22",
                "--token",
                "test_token",
            ],
        )

        # Debug output
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Stdout: {result.stdout}")
            if result.exception:
                print(f"Exception: {result.exception}")
                import traceback

                print(
                    f"Traceback: {traceback.format_exception(type(result.exception), result.exception, result.exception.__traceback__)}"
                )

        assert result.exit_code == 0
        assert "No similar PRs found" in result.stdout
        # Check for merge message (may include Rich color codes)
        assert "Merging source PR" in result.stdout and "22" in result.stdout
        assert "Successfully merged 1/1 PRs" in result.stdout

        # Verify the source PR was approved and merged
        mock_client.approve_pull_request.assert_called_once_with("owner", "repo", 22)
        mock_client.merge_pull_request.assert_called_once_with(
            "owner", "repo", 22, "merge"
        )

    @patch("dependamerge.cli.GitHubClient")
    def test_merge_command_non_automation_pr_no_override(self, mock_client_class):
        """Test that non-automation PR without override shows SHA and exits."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = False

        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug in authentication",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )
        mock_client.get_pull_request_info.return_value = mock_pr
        mock_client.get_pull_request_commits.return_value = [
            "Fix bug in authentication\n\nDetailed description"
        ]
        mock_client.get_pr_status_details.return_value = "Ready to merge"

        result = self.runner.invoke(
            app, ["https://github.com/owner/repo/pull/22", "--token", "test_token"]
        )

        assert result.exit_code == 0
        assert "not from a recognized automation tool" in result.stdout
        assert "--override" in result.stdout
        assert "human-user" in result.stdout

    @patch("dependamerge.cli.GitHubClient")
    def test_merge_command_non_automation_pr_invalid_override(self, mock_client_class):
        """Test that non-automation PR with invalid override SHA fails."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = False

        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug in authentication",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )
        mock_client.get_pull_request_info.return_value = mock_pr
        mock_client.get_pull_request_commits.return_value = [
            "Fix bug in authentication\n\nDetailed description"
        ]
        mock_client.get_pr_status_details.return_value = "Ready to merge"

        result = self.runner.invoke(
            app,
            [
                "https://github.com/owner/repo/pull/22",
                "--token",
                "test_token",
                "--override",
                "invalid_sha",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid override SHA" in result.stdout

    @patch("dependamerge.cli.GitHubClient")
    @patch("dependamerge.cli.PRComparator")
    def test_merge_command_non_automation_pr_valid_override(
        self, mock_comparator_class, mock_client_class
    ):
        """Test that non-automation PR with valid override SHA proceeds."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_comparator = Mock()
        mock_comparator_class.return_value = mock_comparator

        mock_client.parse_pr_url.return_value = ("owner", "repo", 22)
        mock_client.is_automation_author.return_value = False

        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug in authentication",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )

        mock_client.get_pull_request_info.return_value = mock_pr
        mock_client.get_pull_request_commits.return_value = [
            "Fix bug in authentication\n\nDetailed description"
        ]
        mock_client.get_organization_repositories.return_value = []
        mock_client.get_pr_status_details.return_value = "Ready to merge"
        mock_client.approve_pull_request.return_value = True
        mock_client.merge_pull_request.return_value = True

        # Calculate the expected SHA for this test case
        combined_data = "human-user:Fix bug in authentication"
        expected_sha = hashlib.sha256(combined_data.encode("utf-8")).hexdigest()[:16]

        result = self.runner.invoke(
            app,
            [
                "https://github.com/owner/repo/pull/22",
                "--token",
                "test_token",
                "--override",
                expected_sha,
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Override SHA validated" in result.stdout

    def test_generate_override_sha(self):
        """Test SHA generation functionality."""
        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug in authentication",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )

        commit_message = "Fix bug in authentication"
        sha = _generate_override_sha(mock_pr, commit_message)

        # Check that SHA is generated and has expected length
        assert len(sha) == 16
        assert isinstance(sha, str)

        # Check that same inputs generate same SHA
        sha2 = _generate_override_sha(mock_pr, commit_message)
        assert sha == sha2

        # Check that different inputs generate different SHA
        mock_pr2 = mock_pr.model_copy()
        mock_pr2.author = "different-user"
        sha3 = _generate_override_sha(mock_pr2, commit_message)
        assert sha != sha3

    def test_validate_override_sha(self):
        """Test SHA validation functionality."""
        mock_pr = PullRequestInfo(
            number=22,
            title="Fix bug in authentication",
            body="Test body",
            author="human-user",
            head_sha="abc123",
            base_branch="main",
            head_branch="fix-bug",
            state="open",
            mergeable=True,
            mergeable_state="clean",
            behind_by=0,
            files_changed=[],
            repository_full_name="owner/repo",
            html_url="https://github.com/owner/repo/pull/22",
        )

        commit_message = "Fix bug in authentication"
        correct_sha = _generate_override_sha(mock_pr, commit_message)

        # Valid SHA should validate successfully
        assert _validate_override_sha(correct_sha, mock_pr, commit_message) is True

        # Invalid SHA should fail validation
        assert _validate_override_sha("invalid_sha", mock_pr, commit_message) is False
        assert _validate_override_sha("", mock_pr, commit_message) is False
