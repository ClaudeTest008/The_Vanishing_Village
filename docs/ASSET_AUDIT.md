# Asset Audit — 2026-07-15

Total Content: ~3.4 GB, largest single file 59 MB (safe for GitHub without LFS).

## Packs (keep in vendor folders, reference via soft refs only)

| Folder | Size | Files | Verdict / Use |
|---|---|---|---|
| `Fab/Horror_themed_Forest` | part of 1.4 GB Fab | — | **Core environment**: village surroundings, river area foliage, paths. |
| `Fab/Ghost` + `Fab/Free_Ghost👻` | — | — | **Ghost pawns**. Two ghost meshes → two archetypes. ⚠ Rename `Free_Ghost👻` → `Free_Ghost` (emoji in path risks cooker/platform issues). |
| `Fab/Possessed_Doll` | — | — | Marketplace/school scare prop + Distorted Memory ghost variant. |
| `Fab/Zombie` | — | — | Base for Vengeful Spirit (corrupted resident) with material work. |
| `Fab/Old_Furniture_Set` | — | — | Interiors: school, homes, shrine office. |
| `Fab/Eastern_European_Low_Poly_Garage_Props_Pack` | — | — | Generic clutter (crates, buckets, shelves) for marketplace stalls/storage. Low-poly — background/dark areas only. |
| `Fab/FREE_Post_Apocalypse_Survivor_Environment_Kitbash_set` | — | — | Corrupted-phase set dressing (midnight decay). |
| `Modular_Rural_Cabin` | 1.6 GB | 587 | **Primary building kit**: village houses, school, shrine outbuildings. |
| `ENTROPYSTARTER` | 274 MB | 10 | Horror audio (cues + wavs) → feed MetaSounds via AudioSubsystem. |
| `Characters/Mannequins` | 125 MB | 128 | Resident echo pawns (translucent echo material hides mannequin look); anims incl. Death set. |
| `LevelPrototyping` | 3 MB | 29 | Blockout only; must not ship in final slice lighting passes. |
| `Variant_Combat` | 4 MB | 49 | Template leftovers — **audit for deletion** after confirming no anim reuse. |
| `ThirdPerson` | ~0 | 5 | Template. Replace as default map/gamemode, then **delete**. |
| `Input` | ~0 | 9 | Template Enhanced Input assets — rebuild as first-person set under `TVV/Input`. |

## Gaps (no suitable existing asset)
- Japanese shrine/torii/villager-specific meshes — cabin kit is western rural; slice art direction: remote mountain village with rustic cabins, shrine built from kit + custom trim materials, torii from modeling tools or future Fab acquisition.
- First-person arms — not required (no weapons; interaction is trace-based).

## Actions
1. Rename `Fab/Free_Ghost👻` (redirector-safe rename in editor).
2. New game content lives under `Content/TVV/` only.
3. Delete `ThirdPerson`/`Variant_Combat` once foundation replaces defaults (milestone 2).
4. `__ExternalActors__`/`__ExternalObjects__` belong to existing maps — will regenerate for `L_Village` (World Partition).
