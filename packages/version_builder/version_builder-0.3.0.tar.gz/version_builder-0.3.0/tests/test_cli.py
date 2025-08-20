from unittest.mock import patch

from src.version_builder.cli import CLI


class TestCLI:
    @patch("src.version_builder.cli.CLI.version")
    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_without_arguments(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
        mock_version,
    ):
        mock_parse_args.return_value.show = False
        mock_parse_args.return_value.bump = None
        mock_parse_args.return_value.version = False

        cli = CLI()
        cli()

        mock_help.assert_called_once()
        mock_show_last_tag.assert_not_called()
        mock_bump.assert_not_called()
        mock_version.assert_not_called()

    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_with_last_tag_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
    ):
        mock_parse_args.return_value.show = True

        cli = CLI()
        cli()

        mock_show_last_tag.assert_called_once()
        mock_help.assert_not_called()

    @patch("src.version_builder.cli.CLI.version")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_with_version_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_version,
    ):
        mock_parse_args.return_value.show = False
        mock_parse_args.return_value.bump = None
        mock_parse_args.return_value.version = True

        cli = CLI()
        cli()

        mock_version.assert_called_once()
        mock_help.assert_not_called()

    @patch("src.version_builder.cli.CLI.bump")
    @patch("src.version_builder.cli.CLI.show")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_with_bump_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
        mock_bump,
    ):
        mock_parse_args.return_value.bump = "patch"
        mock_parse_args.return_value.show = False

        cli = CLI()
        cli()

        mock_bump.assert_called_once()
        mock_show_last_tag.assert_not_called()
        mock_help.assert_not_called()

    @patch("src.version_builder.cli.GitHelper.get_last_tag")
    def test_show_last_tag_calls_git_method(self, mock_get_last_tag):
        cli = CLI()
        cli.show()
        mock_get_last_tag.assert_called_once()

    @patch("src.version_builder.cli.GitHelper.bump")
    def test_bump_calls_git_method(self, mock_bump):
        cli = CLI()
        cli.bump(choice="patch")
        mock_bump.assert_called_once()
