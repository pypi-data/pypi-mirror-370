from unittest.mock import patch

import pytest

from src.version_builder.constants import INITIAL_VERSION
from src.version_builder.exceptions import BadChoiceError
from src.version_builder.git import GitHelper


class TestGit:
    @patch("src.version_builder.git.Repo.init")
    @patch("src.version_builder.git.logger.info")
    def test_get_last_tag_empty(self, mock_logger, mock_repo):
        mock_repo.return_value.tags = []

        GitHelper().get_last_tag()
        assert mock_logger.call_count == 1
        assert mock_logger.mock_calls[0].args[0] == "No tags found"

    @patch("src.version_builder.git.Repo.init")
    @patch("src.version_builder.git.logger.info")
    def test_get_last_tag_not_empty(self, mock_logger, mock_repo):
        class MockTag:
            def __init__(self, name):
                self.name = name

        mock_repo.return_value.tags = [MockTag(name="1.0.0"), MockTag(name="1.0.1")]

        GitHelper().get_last_tag()
        assert mock_logger.call_count == 1
        assert mock_logger.mock_calls[0].args[1] == "1.0.1"

    @patch("src.version_builder.git.Repo.init")
    @patch("src.version_builder.git.logger.info")
    def test_create_tag(self, mock_logger, mock_repo):
        tag = "1.2.0"
        GitHelper().create_tag(tag=tag)

        mock_repo.return_value.create_tag.assert_called_once_with(tag)
        mock_logger.assert_called_once_with("Created tag %s", tag)

    @pytest.mark.parametrize(
        "last_tag, choice, expected",
        [
            ("1.2.3", "major", "2.0.0"),
            ("1.2.3", "minor", "1.3.0"),
            ("1.2.3", "patch", "1.2.4"),
        ],
    )
    def test_generate_tag_name(self, last_tag, choice, expected):
        helper = GitHelper()
        result = helper._generate_tag_name(last_tag=last_tag, choice=choice)
        assert result == expected

    def test_generate_tag_name_invalid_choice(self):
        helper = GitHelper()

        with pytest.raises(BadChoiceError, match="Invalid choice for bump version"):
            helper._generate_tag_name(last_tag="1.2.3", choice="invalid")

    @pytest.mark.parametrize(
        "last_tag_return, choice, expected_tag",
        [
            (None, "major", INITIAL_VERSION),
            (None, "minor", INITIAL_VERSION),
            (None, "patch", INITIAL_VERSION),
            ("1.2.3", "major", "2.0.0"),
            ("1.2.3", "minor", "1.3.0"),
            ("1.2.3", "patch", "1.2.4"),
        ],
    )
    @patch("src.version_builder.git.GitHelper.get_last_tag")
    @patch("src.version_builder.git.GitHelper.create_tag")
    def test_bump(
        self,
        mock_create_tag,
        mock_get_last_tag,
        last_tag_return,
        choice,
        expected_tag,
    ):
        helper = GitHelper()
        mock_get_last_tag.return_value = last_tag_return

        helper.bump(choice=choice)

        mock_get_last_tag.assert_called_once()
        mock_create_tag.assert_called_once_with(tag=expected_tag)
