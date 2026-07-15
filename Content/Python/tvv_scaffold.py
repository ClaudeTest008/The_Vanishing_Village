"""TVV foundation scaffold.

Creates the Content/TVV folder tree and skeleton Blueprint assets:
subsystem objects, actor components, interfaces, PDA definition classes,
function library, game framework classes, Developer Hub widget.

Run inside the editor (or headless):
  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="Content/Python/tvv_scaffold.py"

Idempotent: existing assets are skipped, never overwritten.
"""
import unreal

ROOT = "/Game/TVV"

FOLDERS = [
    "Blueprints/Core", "Blueprints/Core/Subsystems", "Blueprints/Player",
    "Blueprints/Ghosts", "Blueprints/Residents", "Blueprints/Interactables",
    "Blueprints/Components", "Blueprints/Interfaces", "Blueprints/Libraries",
    "Data/Definitions", "Data/Residents", "Data/Ghosts", "Data/Memories",
    "Data/Items", "Data/Puzzles", "Data/Dialogues", "Data/Endings",
    "Data/Routines", "Data/Tables",
    "UI/HUD", "UI/Menus", "UI/Codex", "UI/Echo", "UI/Developer",
    "Input", "Maps", "Audio", "VFX", "Materials",
]

# (name, package_path, parent_class)
BLUEPRINTS = [
    # Game framework
    ("BP_TVVGameInstance", "Blueprints/Core", unreal.GameInstance),
    ("BP_TVVGameMode", "Blueprints/Core", unreal.GameModeBase),
    ("BP_TVVPlayerController", "Blueprints/Core", unreal.PlayerController),
    ("BP_TVVHUD", "Blueprints/Core", unreal.HUD),
    ("BP_PlayerCharacter", "Blueprints/Player", unreal.Character),
    # Subsystem-pattern manager objects (see docs/ARCHITECTURE.md)
    ("BPS_TimeLoopSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_MemorySubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_GhostSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_WorldStateSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_AudioSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_SaveSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("BPS_DeveloperSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    # Actor components
    ("AC_Pressure", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Inventory", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Interaction", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Ghost", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Memory", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Routine", "Blueprints/Components", unreal.ActorComponent),
    ("AC_Dialogue", "Blueprints/Components", unreal.ActorComponent),
    # PDA definition classes
    ("PDA_Resident", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Ghost", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Routine", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Memory", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Item", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Puzzle", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Dialogue", "Data/Definitions", unreal.PrimaryDataAsset),
    ("PDA_Ending", "Data/Definitions", unreal.PrimaryDataAsset),
    # SaveGame
    ("SG_TVVSave", "Blueprints/Core", unreal.SaveGame),
]

INTERFACES = [
    ("BPI_Interactable", "Blueprints/Interfaces"),
    ("BPI_TimeAware", "Blueprints/Interfaces"),
    ("BPI_Saveable", "Blueprints/Interfaces"),
    ("BPI_GhostReaction", "Blueprints/Interfaces"),
    ("BPI_MemoryProvider", "Blueprints/Interfaces"),
    ("BPI_LoopReset", "Blueprints/Interfaces"),
]

FUNCTION_LIBRARIES = [("BFL_TVV", "Blueprints/Libraries")]

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
created, skipped, failed = [], [], []


def ensure_folders():
    for f in FOLDERS:
        path = f"{ROOT}/{f}"
        if not eal.does_directory_exist(path):
            eal.make_directory(path)


def make_asset(name, subpath, factory):
    path = f"{ROOT}/{subpath}"
    full = f"{path}/{name}"
    if eal.does_asset_exist(full):
        skipped.append(full)
        return
    try:
        asset = asset_tools.create_asset(name, path, None, factory)
        if asset:
            eal.save_asset(full, only_if_is_dirty=False)
            created.append(full)
        else:
            failed.append(full)
    except Exception as e:  # log and continue — partial scaffold still useful
        failed.append(f"{full} ({e})")


def main():
    ensure_folders()

    for name, subpath, parent in BLUEPRINTS:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent)
        make_asset(name, subpath, factory)

    for name, subpath in INTERFACES:
        try:
            factory = unreal.BlueprintInterfaceFactory()
        except AttributeError:
            factory = None
        if factory:
            make_asset(name, subpath, factory)
        else:
            failed.append(f"{ROOT}/{subpath}/{name} (BlueprintInterfaceFactory unavailable)")

    for name, subpath in FUNCTION_LIBRARIES:
        try:
            factory = unreal.BlueprintFunctionLibraryFactory()
        except AttributeError:
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", unreal.BlueprintFunctionLibrary)
        make_asset(name, subpath, factory)

    # Developer Hub — Editor Utility Widget
    try:
        factory = unreal.EditorUtilityWidgetBlueprintFactory()
        make_asset("EUW_DeveloperHub", "UI/Developer", factory)
    except AttributeError:
        failed.append("EUW_DeveloperHub (EditorUtilityWidgetBlueprintFactory unavailable)")

    unreal.log("=== TVV SCAFFOLD RESULT ===")
    unreal.log(f"created={len(created)} skipped={len(skipped)} failed={len(failed)}")
    for a in created:
        unreal.log(f"[CREATED] {a}")
    for a in skipped:
        unreal.log(f"[SKIPPED] {a}")
    for a in failed:
        unreal.log_error(f"[FAILED] {a}")


main()
