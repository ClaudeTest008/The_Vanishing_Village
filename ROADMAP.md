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
- ✅ Inventory system (M3-Inventory-Complete): PDA_Item extended (Weight/ExamineText/bIsExaminable/PickupSound), FInventoryEntry + FItemTableRow structs, 5 item PDAs from vendor meshes, DT_Items
- ✅ AC_Inventory: stacking AddItem/RemoveItem, HasItem/GetItemCount/GetInventoryContents, UseItem/ExamineItem + OnInventoryChanged/OnItemUsed/OnItemExamined dispatchers (MaxStack clamp deferred)
- ✅ AC_InventoryItemMarker + BP_Pickup_Base (prompt derived from item data at BeginPlay); 5 pickups in Lvl_Sandbox
- ✅ Player: AC_Inventory component, IA_Examine (X) -> AC_Interaction.ExamineCurrent
- ✅ UI: WBP_InteractionPrompt (OnInteractableChanged) + WBP_ExamineOverlay (OnItemExamined, 5 s auto-hide); HUD spawns both. CommonUI deferred (no style assets)
- ✅ Developer Hub: Add Test Herb / Dump Inventory (PIE)
- ✅ PIE smoke test via VibeUE (stacking, pickup e2e, prompt + examine verified live)
- Icons + pickup SFX pending suitable assets; MaxStack clamp with PDA-load strategy

## M3 — Time Loop ✅ (M4-TimeLoop-Complete)
- ✅ BPS_TimeLoopSubsystem: loop clock (AdvanceTime via GameMode tick), LoopDuration 1800 s, midnight warning at 120 s, idempotent TriggerMidnight; dispatchers OnLoopStarted/OnMidnightApproaching/OnMidnightTriggered/OnLoopReset/OnKnowledgeUnlocked
- ✅ Knowledge persistence: KnowledgeCodex (GameplayTagContainer) + WorldState (Map<Tag,bool>) live on GameInstance-owned manager — survive loops; UnlockKnowledge/HasKnowledge/Set+GetWorldStateFlag
- ✅ BP_TimeMachine (shrine monolith, two-stage confirm interact) in Lvl_Sandbox
- ✅ Loop reset: AC_Inventory.ResetForLoop keeps bPersistentThroughLoops items (Ritual Bowl), player respawns at PlayerStart
- ✅ WBP_LoopTimer HUD countdown / AFTER MIDNIGHT state
- ✅ Day/night: GameMode ApplyTimeOfDay — dusk on warning, near-black + dense fog at midnight, morning restore on loop start; World.AfterMidnight tag flag = ghost-shift trigger (consumed in M6)
- ✅ Developer Hub: StartNewLoop / JumpToMidnight / SetLoopTime60 / UnlockKnowledge
- ✅ PIE-verified: 3 loops — persistence vs reset, machine activation, auto-midnight, lighting states
- Deferred: disk SaveGame (SG_TVVSave) for cross-session persistence; smooth lighting lerps (Timeline) with M7 polish; BPI_LoopReset propagation to world actors (needed once village NPCs/props exist, M4-World)

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
