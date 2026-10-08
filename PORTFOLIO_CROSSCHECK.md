# Cross-contract architecture check

This check compares the eight contracts with each other and with the twelve
GenLayer contracts inspected in `stephengerald`'s account. It is a scoped
originality check, not a claim of worldwide novelty.

| Contract | Primary input | Consensus task | Persistent form | Output / state effect |
| --- | --- | --- | --- | --- |
| RateScript | Tariff prose | Extract exact rate tiers | Immutable formula | Reusable usage-price calculator |
| SplitSlip | Receipt image | Transcribe balanced line items | Assignment ledger | Per-diner exact shares |
| SlotWeave | Invited members' availability prose | Normalize fixed-slot indices | Member-to-slot votes | Best slot and fairness tie rotation |
| FloorFlow | Labeled floor-plan image | Extract direct room edges | Undirected spatial graph | Shortest route between rooms |
| MuseumLabel | Curator fact list | Select audience-relevant fact IDs | Revisioned fact publications | Source-exact public label |
| UnitCraft | Measurement table headings | Infer supported unit symbols | Typed numeric matrix | Canonical base-unit table |
| InvariantHunter | Bounded expression tree | Propose any valid counterexample | AST and proof witness | Machine-verified broken claim |
| CutPlan | Cut-list prose | Extract lengths and quantities | Board bins | Reproducible allocation and waste |

## State-machine fingerprints

| Contract | State transitions | Principal rights | Read model |
| --- | --- | --- | --- |
| RateScript | absent → immutable tariff | publisher | formula + arbitrary usage quote |
| SplitSlip | absent → assigning → finalized | organizer assigns | receipt + per-diner shares |
| SlotWeave | absent → open → finalized/cancelled | invited members vote; owner closes | poll + per-member preference |
| FloorFlow | absent → immutable map | publisher | graph + shortest route |
| MuseumLabel | exhibit revisions; immutable labels per revision | curator edits and publishes | exhibit + provenance-preserving label |
| UnitCraft | absent → immutable normalized table | table publisher | typed source and base-unit rows |
| InvariantHunter | absent → open → counterexample found | any caller hunts | challenge + machine-checked witness |
| CutPlan | absent → immutable plan | order publisher | piece allocation + waste |

No pair shares the same combination of state transitions, caller rights,
persistent shape, and read model. Four contracts have a generic publish-once
transition, and RateScript, UnitCraft, and CutPlan all use a
language-to-structure-to-calculation pipeline. Those are genuine high-level
similarities; the domain schema, algorithm, and lasting capability differ.

## Pairwise near-neighbor review

RateScript, UnitCraft, and CutPlan all normalize unstructured input, which is a
GenLayer capability rather than their product architecture. RateScript stores
a reusable price formula and answers arbitrary future usage queries; UnitCraft
stores a one-off typed matrix with exact unit conversion; CutPlan runs an
ordered stock-allocation algorithm and stores a physical piece-to-board plan.
They have different data models, algorithms, and user-visible outcomes.

SplitSlip and FloorFlow both use images. SplitSlip creates a multi-wallet
assignment/finalization ledger from OCR data; FloorFlow stores an immutable
spatial graph and answers path queries. Their states and transitions differ.

SlotWeave and SplitSlip both involve multiple people. SlotWeave requires each
invited wallet to make a consensus-normalized availability submission before
deterministic selection. SplitSlip has one organizer assign OCR line items to
diners before balancing a tab. Neither is a work-approval or claims review.

MuseumLabel and InvariantHunter are structurally unlike every other member:
the former publishes exact-source, revisioned excerpts selected for an
audience; the latter treats the model as a candidate generator and admits
results only through deterministic proof checking. The InvariantHunter
validator need not reproduce an arbitrary LLM answer.

## Check against the twelve prior account contracts

None of these eight implements a claim/challenge/appeal loop, a prize contest,
an insurance tier, contributor-role credit, quote selection, household chore
approval, translation grading, prediction scoring, flight coverage, SLA
assessment, study-deviation judgment, or lost-property matching. The closest
abstract overlap is that all use ordinary GenLayer authorization, bounded
storage, and a consensus rule for non-deterministic work. Those are platform
primitives, not copied domain architectures.

## Residual originality limit

This audit only compares designs we can inspect. A portal or ecosystem reviewer
may know other projects not present in the inspected account. Before each
individual submission, check its title, description, methods, and state
machine against that broader catalog.
