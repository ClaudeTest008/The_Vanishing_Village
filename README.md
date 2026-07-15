# The Vanishing Village

First-person psychological survival horror. Unreal Engine 5.8, Blueprint-only.

A mountain village in rural Japan vanished in one tragic night. The player finds the **Time Loom** — an ancient Shinto ritual device in the shrine — and rewinds to the morning of the final day. The goal is not escape: it is to **rewrite the village's final day**, loop after loop, using permanent knowledge of the residents' routines, secrets, and regrets. Ghosts remember previous loops and evolve into an escalating psychological duel.

## Pillars
- Psychological horror through memory and regret
- Exploration and environmental storytelling
- Knowledge-based time-loop investigation (rewriting history)
- Memory Echoes — walkable, interactive reconstructions of the past
- Resource and stealth management
- Emergent ghost encounters and moral choices
- Replayability through diverging timelines

## Vertical Slice
One interconnected district: Shrine + Marketplace + School + River. 60–90 minutes of gameplay, ~25–35 minutes per loop, 4–5 residents, 3–4 evolving ghosts, 3 timeline divergences, 2–3 endings.

## Repository Layout
| Path | Purpose |
|---|---|
| `Content/TVV/` | All game systems, data, UI, maps (feature-based) |
| `Content/Fab/`, `Content/Modular_Rural_Cabin/`, etc. | Licensed art/audio packs (see [docs/ASSET_AUDIT.md](docs/ASSET_AUDIT.md)) |
| `Content/Python/` | Editor automation (scaffolding, validation) |
| `docs/` | Architecture, roadmap, milestone notes |
| `Config/DefaultGameplayTags.ini` | Full gameplay tag tree |

## Docs
- [ROADMAP.md](ROADMAP.md) — milestone plan and status
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — subsystems, components, interfaces, data model
- [docs/ASSET_AUDIT.md](docs/ASSET_AUDIT.md) — audit of existing content packs

## Requirements
Unreal Engine 5.8 (Epic Launcher build). Open `TheVanishingVillage.uproject`.
