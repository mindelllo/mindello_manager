"""Tests for mindello_manager.main module."""

import os
import platform
import sys
from contextlib import suppress
from unittest import mock

import pytest

import mindello_manager.main as main_mod

MonkeyPatch = pytest.MonkeyPatch


class ExecvpCalledError(Exception):
    """Custom error to simulate os.execvp call in tests."""


def test_main_runs_as_root(monkeypatch: MonkeyPatch) -> None:
    """Test main runs as root/admin without privilege escalation."""
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    with (
        mock.patch.object(main_mod, "Zeroconf"),
        mock.patch.object(main_mod, "ServiceBrowser"),
        mock.patch.object(main_mod, "MatterListener"),
        mock.patch("builtins.input", side_effect=KeyboardInterrupt),
    ):
        main_mod.main()


def test_main_escalates_privileges_linux(monkeypatch: MonkeyPatch) -> None:
    """Test main escalates privileges on Linux if not root."""
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "geteuid", lambda: 1)

    def fake_execvp(*_args: object, **_kwargs: object) -> None:
        raise ExecvpCalledError

    monkeypatch.setattr(os, "execvp", fake_execvp)
    with suppress(ExecvpCalledError), pytest.raises(SystemExit):
        main_mod.main()


def test_main_escalates_privileges_windows(monkeypatch: MonkeyPatch) -> None:
    """Test main escalates privileges on Windows if not admin."""
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    fake_ctypes = mock.MagicMock()
    fake_ctypes.windll.shell32.IsUserAnAdmin.return_value = 0
    fake_ctypes.windll.shell32.ShellExecuteW.side_effect = ExecvpCalledError
    monkeypatch.setitem(sys.modules, "ctypes", fake_ctypes)
    with suppress(ExecvpCalledError), pytest.raises(SystemExit):
        main_mod.main()
    assert fake_ctypes.windll.shell32.ShellExecuteW.called


def test_main_keyboard_interrupt(monkeypatch: MonkeyPatch) -> None:
    """Test main handles KeyboardInterrupt gracefully."""
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    with (
        mock.patch.object(main_mod, "Zeroconf"),
        mock.patch.object(main_mod, "ServiceBrowser"),
        mock.patch.object(main_mod, "MatterListener"),
        mock.patch("builtins.input", side_effect=KeyboardInterrupt),
    ):
        main_mod.main()


def test_main_normal_exit(monkeypatch: MonkeyPatch) -> None:
    """Test main exits normally when Enter is pressed."""
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    with (
        mock.patch.object(main_mod, "Zeroconf"),
        mock.patch.object(main_mod, "ServiceBrowser"),
        mock.patch.object(main_mod, "MatterListener"),
        mock.patch("builtins.input", return_value=""),
    ):
        main_mod.main()
