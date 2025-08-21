# """Unit tests for main module."""
# from typing import Tuple
# from unittest.mock import MagicMock

import typer

# from clickpy import BasicClickStrategy
# from clickpy.exception import ClickStrategyNotFound
# from clickpy.strategy import BasicClickStrategy, ClickStrategy
# from pytest_mock import MockerFixture
from typer.testing import CliRunner

import clickpy

# from . import basic_name

app = typer.Typer()
app.command()(clickpy.main)

runner = CliRunner()


# # Helper Functions
# def _make_and_mock_basic_click(
#     mocker: MockerFixture, fast=False, debug=False
# ) -> Tuple[ClickStrategy, MagicMock, MagicMock]:
#     """Create a basic click object and factory mock.

#     Returns:
#         (BasicClickStrategy, Mock for factory, Mock for auto_click)
#     """
#     basic_click = ClickStrategy(name=basic_name, fast=fast, debug=debug)
#     return (
#         basic_click,
#         mocker.patch("clickpy.strategy.ClickStrategy.new", return_value=basic_click),
#         mocker.patch("clickpy.strategy.BasicClickStrategy.click", side_effect=KeyboardInterrupt),
#     )


# # Tests


# def test_main_no_options(mocker: MockerFixture) -> None:  # noqa
#     # Arrange
#     basic_strat, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)

#     # Act
#     result = runner.invoke(app)

#     # Assert
#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Running clickpy. Enter ctrl+c to stop.

# """
#     )
#     mock_factory.assert_called_once_with(click_type=None, fast=False, debug=False)
#     mock_clicker.assert_called_once_with(basic_strat)


# def test_main_fast_click_option(mocker: MockerFixture) -> None:  # noqa
#     # Arrange
#     basic_click, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker, fast=True)

#     # Act
#     # clickpy.main.main(fast=True, debug=False)
#     result = runner.invoke(app, ["-f"])

#     # Assert
#     assert basic_click.sleep_time == 0.5
#     assert basic_click.debug == False
#     mock_factory.assert_called_once_with(click_type=None, fast=True, debug=False)
#     mock_clicker.assert_called_once_with(basic_click)


# def test_print_strategy_names_works_correctly(mocker: MockerFixture):  # noqa
#     _, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)

#     result = runner.invoke(app, ["--list"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Available click types:

# basic
# natural
# """
#     )
#     mock_factory.assert_not_called()
#     mock_clicker.assert_not_called()


# def test_list_output_with_debug_flag(mocker: MockerFixture):  # noqa
#     _, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)
#     result = runner.invoke(app, ["--list", "-d"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=False
# list_clicks=True
# click_type=None

# Available click types:

# basic
# natural
# """
#     )
#     mock_factory.assert_not_called()
#     mock_clicker.assert_not_called()


# def test_list_output_with_debug_and_fast_flags(mocker: MockerFixture):  # noqa
#     _, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)
#     result = runner.invoke(app, ["--list", "-d", "-f"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=True
# list_clicks=True
# click_type=None

# Available click types:

# basic
# natural
# """
#     )
#     mock_factory.assert_not_called()
#     mock_clicker.assert_not_called()


# def test_list_output_with_debug_and_fast_and_click_type_flags(mocker: MockerFixture):  # noqa
#     _, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)
#     result = runner.invoke(app, ["--list", "-d", "-f", "-t", "basic"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=True
# list_clicks=True
# click_type='basic'

# Available click types:

# basic
# natural
# """
#     )
#     mock_factory.assert_not_called()
#     mock_clicker.assert_not_called()


# def test_debug_flag_works_correctly(mocker: MockerFixture):  # noqa
#     basic_click, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker, debug=True)

#     result = runner.invoke(app, ["-d"])

#     assert result.exit_code == 0
#     mock_factory.assert_called_once_with(click_type=None, fast=False, debug=True)
#     mock_clicker.assert_called_once_with(basic_click)

#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=False
# list_clicks=False
# click_type=None

# Using clicker type: basic

# KeyboardInterrupt thrown and caught. Exiting script.
# """
#     )


# def test_fast_flag_gets_passed_in_correctly(mocker: MockerFixture):  # noqa
#     basic_click, mock_factory, mock_click = _make_and_mock_basic_click(
#         mocker, fast=True, debug=True
#     )

#     result = runner.invoke(app, ["--debug", "--fast"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=True
# list_clicks=False
# click_type=None

# Using clicker type: basic

# KeyboardInterrupt thrown and caught. Exiting script.
# """
#     )

#     assert basic_click.sleep_time == 0.5
#     assert basic_click.debug == True
#     mock_factory.assert_called_once_with(click_type=None, fast=True, debug=True)
#     mock_click.assert_called_once_with(basic_click)


# def test_fast_flag_gets_passed_in_correctly_with_click_type_flag(mocker: MockerFixture):  # noqa
#     basic_click, mock_factory, mock_click = _make_and_mock_basic_click(
#         mocker, fast=True, debug=True
#     )

#     result = runner.invoke(app, ["--debug", "--fast", "--type", "basic"])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Argument list:
# debug=True
# fast=True
# list_clicks=False
# click_type='basic'

# Using clicker type: basic

# KeyboardInterrupt thrown and caught. Exiting script.
# """
#     )

#     assert basic_click.sleep_time == 0.5
#     assert basic_click.debug == True
#     mock_factory.assert_called_once_with(click_type="basic", fast=True, debug=True)
#     mock_click.assert_called_once_with(basic_click)


# def test_click_type_works_for_existing_click_strategies(mocker: MockerFixture):  # noqa
#     basic_click, mock_factory, mock_clicker = _make_and_mock_basic_click(mocker)

#     basic = "basic"
#     result = runner.invoke(app, ["--type", basic])

#     assert result.exit_code == 0
#     assert (
#         result.stdout
#         == """Running clickpy. Enter ctrl+c to stop.

# Back to work!
# """
#     )

#     mock_factory.assert_called_once_with(click_type=basic, fast=False, debug=False)
#     mock_clicker.assert_called_once_with(basic_click)


# def test_click_factory_throws_ClickStrategyNotFound_and_stdout_correctly(
#     mocker: MockerFixture,
# ):  # noqa
#     mock_factory = mocker.patch("clickpy.click_strategy_factory", side_effect=ClickStrategyNotFound)
#     mock_clicker = mocker.patch("clickpy.auto_click", side_effect=KeyboardInterrupt)

#     bad_click_type = "something_else"
#     result = runner.invoke(app, ["-t", bad_click_type])

#     assert result.exit_code == 1
#     assert (
#         result.stdout
#         == f"""Argument {bad_click_type!r} is not a valid clicker type.
# Available click types:

# basic
# natural
# """
#     )


# def test_click_factory_throws_ClickStrategyNotFound_and_stdout_correctly_with_debug_flag(
#     mocker: MockerFixture,
# ):  # noqa
#     mock_factory = mocker.patch("clickpy.click_strategy_factory", side_effect=ClickStrategyNotFound)
#     mock_clicker = mocker.patch("clickpy.auto_click", side_effect=KeyboardInterrupt)

#     bad_click_type = "something_else"
#     result = runner.invoke(app, ["-t", bad_click_type, "--debug"])

#     assert result.exit_code == 1
#     assert (
#         result.stdout
#         == f"""Argument list:
# debug=True
# fast=False
# list_clicks=False
# click_type='something_else'

# Argument {bad_click_type!r} is not a valid clicker type.
# Available click types:

# basic
# natural
# """
#     )
