"""TVV M2: Enhanced Input assets + game framework class defaults.

Creates IA_* input actions and IMC_Default with key mappings under
/Game/TVV/Input, and wires BP_TVVGameMode CDO defaults (pawn, PC, HUD).
Idempotent.
"""
import unreal

ROOT = "/Game/TVV/Input"
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
log, err = unreal.log, unreal.log_error

AXIS2D = unreal.InputActionValueType.AXIS2D
AXIS1D = unreal.InputActionValueType.AXIS1D
BOOL = unreal.InputActionValueType.BOOLEAN

# name -> value type
ACTIONS = {
    "IA_Move": AXIS2D,
    "IA_Look": AXIS2D,
    "IA_Sprint": BOOL,
    "IA_Crouch": BOOL,
    "IA_Interact": BOOL,
    "IA_Lean": AXIS1D,
    "IA_Lantern": BOOL,
    "IA_Codex": BOOL,
    "IA_Pause": BOOL,
}


def get_or_create(name, klass):
    full = f"{ROOT}/{name}"
    if eal.does_asset_exist(full):
        return eal.load_asset(full)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", klass)
    asset = asset_tools.create_asset(name, ROOT, klass, factory)
    if asset:
        log(f"[CREATED] {full}")
    else:
        err(f"[FAILED] {full}")
    return asset


def new_modifier(cls, imc, **props):
    m = unreal.new_object(cls, outer=imc)
    for k, v in props.items():
        m.set_editor_property(k, v)
    return m


def map_key(imc, action, key_name, modifiers=(), triggers=()):
    key = unreal.Key()
    key.set_editor_property("key_name", key_name)
    mapping = imc.map_key(action, key)
    if modifiers:
        mapping.set_editor_property("modifiers", list(modifiers))
    if triggers:
        mapping.set_editor_property("triggers", list(triggers))


def main():
    actions = {}
    for name, vtype in ACTIONS.items():
        ia = get_or_create(name, unreal.InputAction)
        if ia:
            ia.set_editor_property("value_type", vtype)
            actions[name] = ia

    imc = get_or_create("IMC_Default", unreal.InputMappingContext)
    if imc and actions:
        # rebuild mappings from scratch each run (idempotent)
        try:
            imc.set_editor_property("mappings", [])
        except Exception:
            for ia in actions.values():
                imc.unmap_all_keys_from_action(ia)
        swizzle = lambda: new_modifier(unreal.InputModifierSwizzleAxis, imc)
        negate = lambda: new_modifier(unreal.InputModifierNegate, imc)

        # Move: WASD -> Axis2D (X=right, Y=forward)
        map_key(imc, actions["IA_Move"], "W", modifiers=[swizzle()])
        map_key(imc, actions["IA_Move"], "S", modifiers=[swizzle(), negate()])
        map_key(imc, actions["IA_Move"], "D")
        map_key(imc, actions["IA_Move"], "A", modifiers=[negate()])
        # Look: mouse
        map_key(imc, actions["IA_Look"], "Mouse2D")
        map_key(imc, actions["IA_Sprint"], "LeftShift")
        map_key(imc, actions["IA_Crouch"], "LeftControl")
        map_key(imc, actions["IA_Crouch"], "C")
        map_key(imc, actions["IA_Interact"], "E")
        map_key(imc, actions["IA_Lean"], "Q", modifiers=[negate()])
        map_key(imc, actions["IA_Lean"], "R")
        map_key(imc, actions["IA_Lantern"], "F")
        map_key(imc, actions["IA_Codex"], "Tab")
        map_key(imc, actions["IA_Pause"], "Escape")

    # Game framework defaults on BP_TVVGameMode CDO
    gm_class = unreal.load_object(None, "/Game/TVV/Blueprints/Core/BP_TVVGameMode.BP_TVVGameMode_C")
    pawn_class = unreal.load_object(None, "/Game/TVV/Blueprints/Player/BP_PlayerCharacter.BP_PlayerCharacter_C")
    pc_class = unreal.load_object(None, "/Game/TVV/Blueprints/Core/BP_TVVPlayerController.BP_TVVPlayerController_C")
    hud_class = unreal.load_object(None, "/Game/TVV/Blueprints/Core/BP_TVVHUD.BP_TVVHUD_C")
    if gm_class and pawn_class and pc_class and hud_class:
        cdo = unreal.get_default_object(gm_class)
        cdo.set_editor_property("default_pawn_class", pawn_class)
        cdo.set_editor_property("player_controller_class", pc_class)
        cdo.set_editor_property("hud_class", hud_class)
        log("[OK] BP_TVVGameMode defaults wired")
    else:
        err("[FAILED] loading framework classes for GameMode defaults")

    saved = 0
    for name in list(ACTIONS) + ["IMC_Default"]:
        if eal.does_asset_exist(f"{ROOT}/{name}"):
            eal.save_asset(f"{ROOT}/{name}", only_if_is_dirty=False)
            saved += 1
    eal.save_asset("/Game/TVV/Blueprints/Core/BP_TVVGameMode", only_if_is_dirty=False)
    log(f"=== TVV M2 INPUT RESULT === saved={saved}")


main()
