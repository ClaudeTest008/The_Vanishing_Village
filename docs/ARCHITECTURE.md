# Architecture — The Vanishing Village

Blueprint-only UE 5.8 project. Everything data-driven, gameplay decoupled from art via soft references and gameplay tags.

## Core pattern: Blueprint "subsystems"

`UGameInstanceSubsystem` is not Blueprint-subclassable without C++. In a Blueprint-only project the equivalent pattern is:

- `BP_TVVGameInstance` (parent: `GameInstance`) owns one instance of each manager object, created in `Init` and exposed through pure getters.
- Each manager is a Blueprint of parent class `Object` (Blueprintable), named `BPS_<Name>Subsystem`, living in `Content/TVV/Blueprints/Core/Subsystems/`.
- A Blueprint Function Library `BFL_TVV` provides static `GetTimeLoopSubsystem(WorldContext)` etc., so call sites read exactly like engine subsystem access.

This preserves the subsystem architecture (single instance, game-instance lifetime, global access) and ports to C++ `UGameInstanceSubsystem` classes 1:1 if the project later adds a C++ module.

### Subsystems
| Blueprint | Responsibility |
|---|---|
| `BPS_TimeLoopSubsystem` | Loop clock (06:00 → midnight, ~25–35 real minutes), phase tags (`World.Phase.*`, `World.Time.*`), Time Loom reset, loop counter, broadcast `OnLoopStarted/OnTimeSegmentChanged/OnLoopReset`. Notifies all `BPI_LoopReset` / `BPI_TimeAware` actors. |
| `BPS_MemorySubsystem` | Knowledge Codex. Evidence registration, memory completion state (`Memory.*` tags), Memory Echo eligibility + activation, resident profiles. Knowledge is permanent across loops. |
| `BPS_GhostSubsystem` | Ghost registry, cross-loop ghost learning ledger (routes seen, hiding spots used, shortcuts taken), state escalation Echo→Distorted→Vengeful→Released, spawn/despawn orchestration. |
| `BPS_WorldStateSubsystem` | Timeline divergence flags (`History.*`), resident fates, unlocked shortcuts, door/world object state per loop, applies changed history at loop start. |
| `BPS_AudioSubsystem` | Audio state machine (`Audio.State.*`), MetaSound parameter routing, pressure-driven mix, stingers. |
| `BPS_SaveSubsystem` | SaveGame read/write: codex, profiles, solved memories, changed history, shortcuts, loop statistics, endings seen. Implements the persistence contract for `BPI_Saveable`. |
| `BPS_DeveloperSubsystem` | Debug flags consumed by the Developer Hub (Editor Utility Widget `EUW_DeveloperHub`): spawn ghost, jump loop time, force echo, dump state, validate data. |

## Actor Components (`Content/TVV/Blueprints/Components/`)
| Component | Attached to | Responsibility |
|---|---|---|
| `AC_Pressure` | Player | Pressure 0–100 from darkness/ghost proximity/trauma/supernatural; drives hallucination + post-process + UI glitch events; decays at shrines/safe rooms. |
| `AC_Inventory` | Player | Slot-limited inventory of `PDA_Item`; loop-reset policy honors `Item.Persistent`. |
| `AC_Interaction` | Player | Trace + focus management, drives interact prompt, routes to `BPI_Interactable`. |
| `AC_Ghost` | Ghost pawns | State (`Ghost.State.*`), awareness, per-loop memory hooks into `BPS_GhostSubsystem`. |
| `AC_Memory` | Echo actors / evidence | Links actor to a `PDA_Memory`, reports evidence pickup. |
| `AC_Routine` | Resident echo pawns | Executes `PDA_Routine` schedule entries against loop clock. |
| `AC_Dialogue` | Residents/ghosts | Runs `PDA_Dialogue` trees, gated by knowledge/trust tags. |

## Blueprint Interfaces (`Content/TVV/Blueprints/Interfaces/`)
`BPI_Interactable` (GetInteractionType/CanInteract/Interact/GetPrompt), `BPI_TimeAware` (OnTimeSegmentChanged/OnPhaseChanged), `BPI_Saveable` (CaptureState/RestoreState), `BPI_GhostReaction` (OnGhostNear/OnGhostStateChanged), `BPI_MemoryProvider` (GetMemoryId/GetEvidenceTags), `BPI_LoopReset` (OnLoopWillReset/OnLoopStarted).

## Data model (`Content/TVV/Data/`)
Primary Data Assets (one Blueprint class per type, parent `PrimaryDataAsset`):
`PDA_Resident`, `PDA_Ghost`, `PDA_Routine`, `PDA_Memory` (with echo trigger evidence-tag requirements), `PDA_Item`, `PDA_Puzzle`, `PDA_Dialogue`, `PDA_Ending`.

Data Tables for tabular data: routine schedules, loot placement, pressure tuning curves, loc strings. All asset references inside definitions are **soft** (TSoftObjectPtr) — gameplay never hard-references art.

## Gameplay Tags
Declared centrally in `Config/DefaultGameplayTags.ini`. Namespaces: `Ghost.*`, `World.*`, `Loop.*`, `Memory.*`, `Player.*`, `Pressure.*`, `Item.*`, `Interaction.*`, `Resident.*`, `History.*`, `Puzzle.*`, `Ending.*`, `UI.Layer.*`, `Audio.State.*`.

## AI
Ghost behavior: **State Tree** (GameplayStateTree plugin) per ghost archetype with shared sub-trees; **EQS** for search/ambush/route-prediction queries; **Smart Objects** for resident echo routines (pray, shop, teach, fish). Cross-loop learning: `BPS_GhostSubsystem` ledger biases EQS scoring (weight previously used player routes/hiding spots) and unlocks State Tree branches (block shortcut, whisper name).

## UI
CommonUI layer stack (`UI.Layer.*` tags): HUD (prompt, pressure vignette—no numeric bars), Codex screen, dialogue, echo overlay, menus. `EUW_DeveloperHub` is an Editor Utility Widget, never cooked.

## Maps
World Partition single persistent level `L_Village` with districts as data layers; `L_MainMenu` separate. Corruption phase swaps handled via data layers + MPC-driven material corruption, not duplicate maps.

## Folder layout (`Content/TVV/`)
```
Blueprints/{Core,Core/Subsystems,Player,Ghosts,Residents,Interactables,Components,Interfaces,Libraries}
Data/{Definitions,Residents,Ghosts,Memories,Items,Puzzles,Dialogues,Endings,Routines,Tables}
UI/{HUD,Menus,Codex,Echo,Developer}
Input/  Maps/  Audio/  VFX/  Materials/
```
Licensed packs stay in their vendor folders (`Fab/`, `Modular_Rural_Cabin/`, `ENTROPYSTARTER/`); game code references them only via soft references inside data assets.
