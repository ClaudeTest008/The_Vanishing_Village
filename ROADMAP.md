# Roadmap — The Vanishing Village (Vertical Slice)

Status legend: ☐ pending · ◐ in progress · ✅ done

## M1 — Project Foundation ✅
- ✅ Git repository, .gitignore, GitHub remote
- ✅ Plugin enablement (StateTree, SmartObjects, CommonUI, MetaSound, Python/EditorScripting)
- ✅ Gameplay tag tree (`Config/DefaultGameplayTags.ini`)
- ✅ Architecture doc, asset audit doc
- ✅ Editor scaffold script (`Content/Python/tvv_scaffold.py`)
- ✅ Scaffolded `Content/TVV` folder tree + 36 skeleton assets (subsystems, components, interfaces, PDA classes, function library, SaveGame, Developer Hub widget)
- ➡ Graph logic in subsystem skeletons → M2/M3 (in-editor work)

## M2 — Core Gameplay ◐
- ✅ Enhanced Input assets: IA_Move/Look/Sprint/Crouch/Interact/Lean/Lantern/Codex/Pause + IMC_Default (WASD, mouse, E/F/Q/R/Tab/Esc)
- ✅ BP_TVVGameMode defaults: pawn=BP_PlayerCharacter, PC=BP_TVVPlayerController, HUD=BP_TVVHUD
- ✅ PDA data schemas: 67 member variables across all 9 definition classes (`Content/Python/tvv_m2_pda_vars.py`); added missing PDA_LoopEvent, BPS_NarrativeSubsystem, AC_Health
- ✅ Engine MCP server plugin enabled (ModelContextProtocol + MCPClientToolset, autostart on port 8000; `.mcp.json` wires Claude Code)
- ✅ First-person character: camera, move/look/crouch/sprint (WalkSpeed/SprintSpeed vars 220/450), Enhanced Input wiring (`Content/Python/tvv_m2_player.py`)
- ✅ Interaction system: `AC_Interactable` marker component (PromptText + OnInteracted event), `AC_Interaction` camera line trace → CurrentInteractable, `IA_Interact` → TryInteract (`Content/Python/tvv_m2_interaction.py`). BPI_Interactable kept as editor-time contract — interface message nodes not creatable headless.
- ✅ Template content removed (ThirdPerson, Variant_Combat, Characters, LevelPrototyping, Input — 446 files); `Lvl_Sandbox` test map; defaults → Lvl_Sandbox + BP_TVVGameMode (`Content/Python/tvv_m2_cleanup.py`)
- ◐ Prompt UI widget (needs UMG pass, with M7 UI work or earlier)
- `AC_Inventory` + `PDA_Item` + pickup/examine flow
- PIE smoke test (needs interactive editor or automation test)

## M3 — Time Loop ☐
- Loop clock, time segments, phase corruption
- Time Loom actor in shrine + reset sequence
- `BPI_LoopReset`/`BPI_TimeAware` propagation; persistent vs reset state via WorldStateSubsystem
- Save system v1 (codex, loop stats)

## M4 — World & Narrative ☐
- `L_Village` World Partition map: Shrine, Marketplace, School, River, paths
- 4–5 residents: PDA definitions, routines (Smart Objects), dialogue
- Environmental storytelling pass (letters, photos, altars)

## M5 — Investigation & Memory Echoes ☐
- Evidence gathering → Codex UI
- Echo reconstruction: translucent interactive replay volume, 30–60 s, free player movement
- Echo-gated puzzles (4–5, interconnected)

## M6 — Ghost AI ☐
- 3–4 ghosts: State Tree brains, EQS hunt/search/ambush, four-state escalation
- Cross-loop learning ledger (route prediction, shortcut blocking, name whispers)
- Stealth model: sound events, light exposure, line of sight

## M7 — Horror Systems ☐
- Pressure component + hallucination events + post-process/audio distortion
- Dynamic lighting/audio corruption toward midnight
- Charms/seals resource loop

## M8 — Divergence & Endings ☐
- 3 timeline divergences, resident fate changes, 2–3 endings
- Ending flow + statistics screen

## M9 — Polish & Optimization ☐
- Developer Hub complete, data validation, perf pass, full playthrough QA
