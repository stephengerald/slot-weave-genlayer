"""Independent direct-test deployment fixture with the Windows stdin workaround."""

from pathlib import Path
import os
import sys
import tempfile

import pytest


def _install_windows_compatibility():
    if sys.platform != "win32":
        return
    from gltest.direct import loader
    from gltest.direct.vm import VMContext

    if getattr(loader, "_original_eight_windows_compat", False):
        return

    def inject_message_to_fd0(vm):
        from genlayer.py import calldata
        from genlayer.py.types import Address

        def address(value):
            return Address(value) if isinstance(value, bytes) else value

        encoded = calldata.encode({
            "contract_address": address(vm._contract_address),
            "sender_address": address(vm.sender),
            "origin_address": address(vm.origin),
            "stack": [],
            "value": vm._value,
            "datetime": vm._datetime,
            "is_init": False,
            "chain_id": vm._chain_id,
            "entry_kind": 0,
            "entry_data": b"",
            "entry_stage_data": None,
        })
        fd, path = tempfile.mkstemp()
        try:
            os.write(fd, encoded)
            os.lseek(fd, 0, os.SEEK_SET)
            vm._original_stdin_fd = os.dup(0)
            os.dup2(fd, 0)
            vm._original_eight_stdin_path = path
        finally:
            os.close(fd)

    original_cleanup = VMContext._cleanup_after_deactivate

    def cleanup_after_deactivate(vm):
        path = getattr(vm, "_original_eight_stdin_path", None)
        try:
            original_cleanup(vm)
        finally:
            if path:
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass
                vm._original_eight_stdin_path = None

    loader._inject_message_to_fd0 = inject_message_to_fd0
    VMContext._cleanup_after_deactivate = cleanup_after_deactivate
    loader._original_eight_windows_compat = True


_install_windows_compatibility()
CONTRACTS = Path(__file__).resolve().parents[1] / "contracts"


@pytest.fixture
def deploy(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-08T12:00:00Z")

    def _deploy(name):
        return direct_deploy(str(CONTRACTS / name), sdk_version="v0.2.16")

    return _deploy
