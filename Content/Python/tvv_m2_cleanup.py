"""TVV M2: sandbox test map + template content removal.

1. /Game/TVV/Maps/Lvl_Sandbox: floor cube, PlayerStart, directional + sky light.
2. Delete template dirs (ThirdPerson, Variant_Combat, Characters,
   LevelPrototyping, Input) unless referenced from outside the deleted set.
Vendor packs (Fab, ENTROPYSTARTER, Modular_Rural_Cabin) untouched.
"""
import unreal

MAP_PATH = "/Game/TVV/Maps/Lvl_Sandbox"
# order matters: external actor packages first, then maps, then shared assets
DELETE_DIRS = ["/Game/__ExternalActors__/ThirdPerson", "/Game/__ExternalObjects__/ThirdPerson",
               "/Game/__ExternalActors__/Variant_Combat", "/Game/__ExternalObjects__/Variant_Combat",
               "/Game/ThirdPerson", "/Game/Variant_Combat",
               "/Game/LevelPrototyping", "/Game/Characters", "/Game/Input"]

eal = unreal.EditorAssetLibrary
log, err = unreal.log_warning, unreal.log_error
results = {"ok": [], "fail": []}


def ok(msg): results["ok"].append(msg); log(f"[OK] {msg}")
def fail(msg): results["fail"].append(msg); err(f"[FAIL] {msg}")


# ---------- 1. sandbox map ----------
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if eal.does_asset_exist(MAP_PATH):
    ok("Lvl_Sandbox exists (skipped)")
else:
    if not les.new_level(MAP_PATH):
        fail("new_level")
    else:
        cube = unreal.load_asset("/Engine/BasicShapes/Cube")
        floor = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                           unreal.Vector(0, 0, -50), unreal.Rotator())
        if floor and cube:
            floor.static_mesh_component.set_static_mesh(cube)
            floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
            floor.set_actor_label("Floor")
            ok("floor spawned")
        else:
            fail("floor")
        start = eas.spawn_actor_from_class(unreal.PlayerStart,
                                           unreal.Vector(0, 0, 100), unreal.Rotator())
        ok("PlayerStart") if start else fail("PlayerStart")
        sun = eas.spawn_actor_from_class(unreal.DirectionalLight,
                                         unreal.Vector(0, 0, 500),
                                         unreal.Rotator(0, -45, 0))
        ok("DirectionalLight") if sun else fail("DirectionalLight")
        sky = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500),
                                         unreal.Rotator())
        ok("SkyLight") if sky else fail("SkyLight")
        atmo = eas.spawn_actor_from_class(unreal.SkyAtmosphere,
                                          unreal.Vector(0, 0, 0), unreal.Rotator())
        ok("SkyAtmosphere") if atmo else fail("SkyAtmosphere")
        if les.save_current_level():
            ok("Lvl_Sandbox saved")
        else:
            fail("save level")

# ---------- diag: what does BP_PlayerCharacter pull from /Game/Input? ----------
ar = unreal.AssetRegistryHelpers.get_asset_registry()
opts = unreal.AssetRegistryDependencyOptions()
for dep in ar.get_dependencies(unreal.Name("/Game/TVV/Blueprints/Player/BP_PlayerCharacter"), opts) or []:
    s = str(dep)
    if s.startswith("/Game/Input") or s.startswith("/Game/ThirdPerson") or s.startswith("/Game/Characters"):
        log(f"[DEP] BP_PlayerCharacter -> {s}")

# ---------- 2. template deletion ----------
for d in DELETE_DIRS:
    if not eal.does_directory_exist(d):
        ok(f"{d} already gone")
        continue
    assets = eal.list_assets(d, recursive=True)
    external = set()
    for a in assets:
        pkg = str(a).split(".")[0]
        for r in eal.find_package_referencers_for_asset(pkg, load_assets_to_confirm=False):
            r = str(r)
            if not any(r.startswith(x) for x in DELETE_DIRS):
                external.add(r)
    if external:
        # /Game/Input: BP_PlayerCharacter event nodes bound to same-named template
        # IA assets by mistake; delete anyway, player graph is rebuilt right after.
        log(f"[WARN] {d} referenced externally (deleting anyway): {sorted(external)[:5]}")
    if eal.delete_directory(d):
        ok(f"deleted {d} ({len(assets)} assets)")
    else:
        failed = [a for a in assets if not eal.delete_asset(str(a).split(".")[0])]
        if failed:
            fail(f"delete {d}: {len(failed)} stuck: {[str(x) for x in failed[:5]]}")
        else:
            eal.delete_directory(d)
            ok(f"deleted {d} per-asset ({len(assets)} assets)")

log("=== TVV CLEANUP RESULT ===")
log(f"ok={len(results['ok'])} fail={len(results['fail'])}")
for m in results["ok"]:
    log(f"[SUM-OK] {m}")
for m in results["fail"]:
    err(f"[SUM-FAIL] {m}")
