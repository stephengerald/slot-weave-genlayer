"""Direct behavior and edge tests for this contract."""

import json
import pytest

def address(value):
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()
    return str(value)

def mock(direct_vm, result, pattern=r".*"):
    direct_vm.clear_mocks()
    direct_vm.mock_llm(pattern, json.dumps(result))

def _address(value):
    return "0x" + bytes(value).hex() if isinstance(value, (bytes, bytearray)) else str(value)

def _mock(vm, answer):
    vm.clear_mocks()
    vm.mock_llm(r".*", json.dumps(answer))

def test_slot_weave_invitation_consensus_and_finalization(deploy, direct_vm, direct_alice, direct_bob, direct_charlie):
    contract = deploy("slot_weave.py")
    members = json.dumps([address(direct_bob), address(direct_charlie)])
    poll_id = contract.open_poll("meeting", "Choose our planning meeting", '["Monday 10:00 UTC", "Tuesday 11:00 UTC"]', members)
    with direct_vm.expect_revert("not_invited"):
        contract.submit_preference(poll_id, "I can attend the Monday session")
    direct_vm.sender = direct_bob
    mock(direct_vm, {"available": [0, 1]})
    contract.submit_preference(poll_id, "I can attend Monday or Tuesday")
    with direct_vm.expect_revert("already_submitted"):
        contract.submit_preference(poll_id, "I can attend Monday or Tuesday")
    direct_vm.sender = direct_charlie
    mock(direct_vm, {"available": [1]})
    contract.submit_preference(poll_id, "I can only attend the Tuesday time")
    direct_vm.sender = direct_alice
    assert contract.finalize(poll_id) == 1
    assert contract.get_poll(poll_id)["counts"] == [1, 2]

def test_slot_weave_cancel_unusable_poll(deploy, direct_vm, direct_alice, direct_bob, direct_charlie):
    contract = deploy("slot_weave.py")
    poll_id = contract.open_poll("bad-time", "A hard-to-attend meeting", '["Monday 10:00 UTC", "Tuesday 11:00 UTC"]',
                                 json.dumps([_address(direct_bob), _address(direct_charlie)]))
    direct_vm.sender = direct_bob
    _mock(direct_vm, {"available": []})
    contract.submit_preference(poll_id, "I cannot attend any listed slot")
    direct_vm.sender = direct_charlie
    _mock(direct_vm, {"available": []})
    contract.submit_preference(poll_id, "I cannot attend either listed slot")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("no_available_slot"):
        contract.finalize(poll_id)
    contract.cancel_poll(poll_id)
    assert contract.get_poll(poll_id)["status"] == "CANCELLED"
    with direct_vm.expect_revert("poll_incomplete_or_closed"):
        contract.finalize(poll_id)
