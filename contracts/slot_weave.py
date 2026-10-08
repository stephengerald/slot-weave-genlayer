# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""A bounded multi-person schedule with consensus-normalized preferences."""

from genlayer import *
import json


def _fail(code: str) -> None:
    raise gl.vm.UserError("[EXPECTED] " + code)


def _bad(code: str) -> None:
    raise gl.vm.UserError("[LLM_ERROR] " + code)


def _array(raw: str, label: str) -> list:
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        _fail("invalid_" + label + "_json")
    if not isinstance(data, list):
        _fail("invalid_" + label)
    return data


class SlotWeave(gl.Contract):
    polls: TreeMap[str, str]
    votes: TreeMap[str, str]
    rotation: u256

    def __init__(self):
        self.rotation = u256(0)

    @gl.public.write
    def open_poll(self, key: str, topic: str, slots_json: str, members_json: str) -> str:
        clean_key = key.strip().lower()
        if not 1 <= len(clean_key) <= 40 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in clean_key):
            _fail("invalid_key")
        poll_id = str(gl.message.sender_address).lower() + ":" + clean_key
        if self.polls.get(poll_id, ""):
            _fail("poll_exists")
        if not 8 <= len(topic.strip()) <= 200:
            _fail("invalid_topic")
        slots = _array(slots_json, "slots")
        members = _array(members_json, "members")
        if not 2 <= len(slots) <= 8 or not 2 <= len(members) <= 8:
            _fail("invalid_count")
        if any(not isinstance(slot, str) or not 5 <= len(slot.strip()) <= 100 for slot in slots):
            _fail("invalid_slot")
        if len({slot.lower() for slot in slots}) != len(slots):
            _fail("duplicate_slot")
        clean_members = []
        for member in members:
            if not isinstance(member, str):
                _fail("invalid_member")
            address = member.lower()
            if len(address) != 42 or not address.startswith("0x") or any(c not in "0123456789abcdef" for c in address[2:]):
                _fail("invalid_member")
            if address == "0x" + "0" * 40 or address in clean_members:
                _fail("duplicate_or_zero_member")
            clean_members.append(address)
        self.polls[poll_id] = json.dumps(
            {"owner": str(gl.message.sender_address).lower(), "topic": topic.strip(),
             "slots": slots, "members": clean_members, "submitted": 0, "status": "OPEN",
             "winner": -1, "counts": []},
            sort_keys=True, separators=(",", ":"),
        )
        return poll_id

    @gl.public.write
    def submit_preference(self, poll_id: str, preference_text: str) -> None:
        raw = self.polls.get(poll_id, "")
        if not raw:
            _fail("poll_missing")
        poll = json.loads(raw)
        if poll["status"] != "OPEN":
            _fail("poll_closed")
        sender = str(gl.message.sender_address).lower()
        if sender not in poll["members"]:
            _fail("not_invited")
        vote_key = poll_id + ":" + sender
        if self.votes.get(vote_key, ""):
            _fail("already_submitted")
        text = preference_text.strip()
        if not 8 <= len(text) <= 500:
            _fail("invalid_preference")
        slots = poll["slots"]
        prompt = (
            "Given these FIXED candidate slots, extract the indices the speaker explicitly says "
            "they can attend. Return JSON exactly {\"available\":[integer indices]}. "
            "Use zero-based indices and an empty list if none are clearly available. "
            "Do not invent availability. Slots: " + json.dumps(slots) + "\nPREFERENCE: " + text
        )

        def parse(value):
            if not isinstance(value, dict) or set(value) != {"available"} or not isinstance(value["available"], list):
                _bad("available_shape")
            indices = value["available"]
            if any(type(i) is not int or i < 0 or i >= len(slots) for i in indices):
                _bad("invalid_slot_index")
            if indices != sorted(set(indices)):
                _bad("indices_not_unique_sorted")
            return indices

        def leader_fn():
            return parse(gl.nondet.exec_prompt(prompt, response_format="json"))

        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                candidate = leader_result.calldata
                return parse({"available": candidate}) == leader_fn()
            except Exception:
                return False

        available = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        self.votes[vote_key] = json.dumps({"text": text, "available": available}, sort_keys=True)
        poll["submitted"] += 1
        self.polls[poll_id] = json.dumps(poll, sort_keys=True, separators=(",", ":"))

    @gl.public.write
    def finalize(self, poll_id: str) -> u256:
        raw = self.polls.get(poll_id, "")
        if not raw:
            _fail("poll_missing")
        poll = json.loads(raw)
        if poll["owner"] != str(gl.message.sender_address).lower():
            _fail("only_owner")
        if poll["status"] != "OPEN" or poll["submitted"] != len(poll["members"]):
            _fail("poll_incomplete_or_closed")
        counts = [0] * len(poll["slots"])
        for member in poll["members"]:
            vote = json.loads(self.votes[poll_id + ":" + member])
            for index in vote["available"]:
                counts[index] += 1
        best = max(counts)
        if best == 0:
            _fail("no_available_slot")
        tied = [index for index, count in enumerate(counts) if count == best]
        chosen = tied[int(self.rotation) % len(tied)]
        self.rotation = u256(int(self.rotation) + 1)
        poll["winner"] = chosen
        poll["counts"] = counts
        poll["status"] = "FINALIZED"
        self.polls[poll_id] = json.dumps(poll, sort_keys=True, separators=(",", ":"))
        return u256(chosen)

    @gl.public.write
    def cancel_poll(self, poll_id: str) -> None:
        raw = self.polls.get(poll_id, "")
        if not raw:
            _fail("poll_missing")
        poll = json.loads(raw)
        if poll["owner"] != str(gl.message.sender_address).lower():
            _fail("only_owner")
        if poll["status"] != "OPEN":
            _fail("poll_not_open")
        poll["status"] = "CANCELLED"
        self.polls[poll_id] = json.dumps(poll, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_poll(self, poll_id: str) -> dict:
        raw = self.polls.get(poll_id, "")
        if not raw:
            _fail("poll_missing")
        return json.loads(raw)

    @gl.public.view
    def get_preference(self, poll_id: str, member: str) -> dict:
        raw = self.votes.get(poll_id + ":" + member.lower(), "")
        if not raw:
            _fail("preference_missing")
        return json.loads(raw)
