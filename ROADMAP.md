# Roadmap — The Vanishing Village (Vertical Slice)

Status legend: ☐ pending · ◐ in progress · ✅ done

## Vision update (2026-07-16): "Inunaki Veil — Mirror of the Forgotten Son"
Setting is now Inunaki Village; protagonist Hiroshi; the **Mirror of Passing** flips between Past (ritual day, living village) and Present (cursed ruins). The existing loop machinery maps directly: Echo-villager day == Past, vengeful-yōkai night == Present; `bIsAfterMidnight` doubles as the era flag so every era-reactive system reuses midnight plumbing. The externally-numbered "M7: Mirror of Passing" milestone is tagged `M8-MirrorOfPassing-Complete` here (M7 tag was already taken by the horror-polish pass). Sensitive themes (suicide, cult trauma) are handled through the "village won't let him die" curse framing — death redirects into the Past, toward memory and redemption, never depicted as goal.

## M8 — Mirror of Passing & Time Flip ✅ (M8-MirrorOfPassing-Complete)
- ✅ FlipEra()/FlipToEra(bool) on the time subsystem: CurrentEra tag, WorldState World.Past/World.Present flags, OnEraFlipped dispatcher, bIsAfterMidnight alias
- ✅ Mirror of Passing: persistent inventory item (shrine pickup), AC_Mirror UseMirror (item-gated, 5 s cooldown), M key
- ✅ Veil Erosion: 1.5/s while in Past; at 100 the Veil tears — forced flip to Present, erosion resets (verified 40 s → exactly 60; 70 s → forced flip)
- ✅ Auto-flip on near-death: vengeful catch throws Hiroshi into the Past (+25 pressure) instead of restarting the night
- ✅ Era world state: villagers Echo↔Vengeful, era-tagged props (PastOnly market life / PresentOnly overgrowth+debris), lighting interpolates warm-morning↔ruin-twilight, ambience beds swap — all PIE-verified both directions
- ✅ Object persistence across flips: inventory + world pickups exist in both eras by design
- ✅ Fixed: missing OnEraFlipped broadcast exec link; era binds wired to tick-chain GetTimeLoop (null at BeginPlay); AC_Interaction trace-miss AccessNone spam (1600+/min since M3) — guarded, 0 in verified run
- Emergent kept: ghosts camping recorded routes + catch-flip = involuntary era thrashing when cornered — reads as the curse fighting back
- Next milestones (external numbering): M8-Expanded village/yōkai skins → M9 pressure polish (largely shipped already) → M10 memory subplots/endings → M11 shipping prep

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
- ✅ M5.5 input fix: all IMC modifiers had been silently lost (map_key returns a struct copy — mutations discarded); mappings rebuilt with Swizzle/Negate, mouse Y-invert now standard FPS
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

## M4 — World & Narrative ✅ (M5-VillageAndEcho-Complete)
- ✅ District in Lvl_Sandbox: shrine (fence ring, offering table, time machine), marketplace (stalls/crates/tables), school cabin + porch (doll on rocking chair), 3 houses (abandoned-dinner tableau, woodcutting site, boat/outhouse), perimeter pines, street fences — 104 actors, all vendor meshes
- ✅ 5 residents (PDA-driven, DT_Residents): Monk Sougen, Teacher Aiko, Grandmother Ume, Child Kenta, Merchant Ichiro — secrets/tragedies authored
- ✅ Routines: AC_Routine follows loop-time fractions, spectral glide (no skeletal assets in project — villagers are translucent Reference_man figures; asset limitation folded into the vanished-villagers fiction); BP_VillageDirector spawns from data, despawns at midnight
- Deferred: dialogue system (AC_Dialogue stub), Smart Objects, letters/photos props (needs suitable assets)

## M5.5 — Audit & Controls Fix ✅ (M5.5-Audit-And-Controls-Fixed)
- ✅ Input mappings rebuilt (all modifiers had been lost — W/S/A/D all strafed right, mouse Y inverted); now Epic-standard FPS feel, verified by asset re-read + full mapping audit
- ✅ 8-agent parallel audit (compile / input / placed actors / asset refs), findings adversarially re-verified:
  - 49 Blueprints compile clean, 0 errors 0 warnings
  - all placed actors valid (121: transforms, collision, marker data, prompts)
  - 3 confirmed hard vendor-mesh refs (BP_TimeMachine, BP_MemoryEchoTrigger, BP_EchoFigure) → converted to MeshPath soft refs loaded at BeginPlay; hard-dependency query now clean
  - DT_Items: MerchantLedger row added (6 rows; table = design-time index, no runtime referencer by intent)
- ✅ PIE regression: runtime mesh loads, pickup→clue, examine overlay, echo scene, loop reset/persistence all pass
- Known limitations: no skeletal meshes/animations in project (villagers = spectral static figures by design); Icon/PickupSound empty on item PDAs (no suitable vendor assets); scaffold assets for M6-M8 (ghost/pressure/dialogue/save subsystems, interfaces, PDA definitions) intentionally unreferenced until their milestones; keyboard/mouse feel needs a human hands-on pass (structural verification only — no input-injection API exposed)

## M5 — Investigation & Memory Echoes ◐ (first scene shipped)
- ✅ Echo mechanic: BP_MemoryEchoTrigger (knowledge-gated, pre-midnight only, once/loop) spawns BP_EchoFigure translucent replay actors — glide + timed speech lines, free player movement, self-expire
- ✅ Marketplace quarrel scene: ledger evidence pickup unlocks clue tag -> echo replays Ichiro/Aiko argument -> unlocks Knowledge.Resident.MerchantDebt
- ✅ Evidence items teach clues via PDA_Item.KnowledgeTag (data-driven)
- Remaining: Codex UI, 3-4 more echo scenes, echo-gated puzzles

## M6 — Ghost AI ✅ (M6-GhostAI-Complete)
- ✅ Four-state escalation on all 5 residents: Echo (day routine) → Distorted at midnight warning (routine halts, glitch jitter, whispers) → Vengeful at midnight (per-resident vengeful mesh + hunt speed + cry line) → Released (weakness knowledge + interact; gives hint, drifts slow)
- ✅ Senses: sight = 900uu + clear LOS trace; hearing = sprinting player within 1500uu; caught (<130uu) = the night restarts (StartNewLoop)
- ✅ "Village Remembers You": BPS_GhostSubsystem records player route (5 s samples, 60-pt ring, persists across loops); unsensed vengeful ghosts patrol/camp recorded positions; Toggle Adaptive in Dev Hub
- ✅ Data-driven per resident (PDA: behavior tag hunter/warden, hunt speed 160-280, vengeful mesh, cry, weakness, hint)
- ✅ Dev Hub: Force All Vengeful / Force All Released / Toggle Adaptive Memory
- ✅ PIE-verified: full state chain, per-resident transforms, live catch→loop-reset, release-with-hint vs stays-vengeful-without-knowledge, adaptive camping of player routes
- Implementation note: tag-driven FSM + trace senses instead of State Tree/EQS/AIPerception (those assets aren't authorable via the python pipeline) — swap-in candidates for an interactive-editor polish pass; name whispers + light-exposure stealth deferred to M7 pressure/audio work

## M7 — Horror Systems ✅ (M7-HorrorPolish-Complete)
- ✅ AC_Pressure (player): 0-100, thresholds 30/60/80 (CDO-tunable); sources: after-midnight +2/s, dusk +0.5/s, vengeful proximity up to +4/s; relief: shrine radius -6/s, knowledge unlock -10, baseline decay
- ✅ Effects: camera breathing (sin pitch, scales 30→100), post-process distortion blend (vignette/grain/chromatic fringe/desaturation, 20→100), fake-ghost apparitions (10 s cadence at 60+), prop nudges at 80+, HUD clock blood-red tint + scrambled time ("??:33") at 80+
- ✅ Adaptive layered ambience from existing WAVs: day fades with pressure; deja_vu under midnight; echoes 30+ / whisper monologue 60+ / simulation drone 80+ (volume-crossfaded AudioComponents)
- ✅ Smooth lighting: morning/dusk/midnight presets now interpolate (FInterpTo/CInterpTo) — no pops
- ✅ Dev Hub: Set Pressure 90/0, Trigger Hallucination
- ✅ PIE-verified end-to-end incl. emergent scare: vengeful ghosts camping the player's recorded position ring at ~300uu and red-line pressure; shrine is an uneasy sanctuary after midnight (-6/s barely beats sources) — kept as design
- Deferred: MetaSound assets + Niagara particles (no such assets in project; not authorable via python pipeline), charm/seal resource loop (M8 with endings economy), camera-shake asset (breathing via pitch osc)

## M8 — Divergence & Endings ☐
- 3 timeline divergences, resident fate changes, 2–3 endings
- Ending flow + statistics screen

## M9 — Polish & Optimization ☐
- Developer Hub complete, data validation, perf pass, full playthrough QA
