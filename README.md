# SlotWeave

Invited wallets submit plain-language availability for fixed candidate times; the contract tallies normalized choices and finalizes a meeting slot.

## Why this is an intelligent contract

A multi-member preference ledger and deterministic tally with rotating tie-breaks and owner cancellation. The source interpretation runs inside GenLayer consensus; the stored result and read methods are on-chain.

## Scope

Only invited wallet submissions count. The contract does not check external calendars or promise attendance.

## Verify

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/slot_weave.py
genvm-lint typecheck contracts/slot_weave.py
pytest tests/direct -q
gltest tests/integration/test_studionet.py --network studionet -v -s
```

Live tests submit permanent public StudioNet test transactions; use a fresh test wallet. See EVIDENCE.md for the completed run and explorer links.
