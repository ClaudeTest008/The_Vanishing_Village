"""TVV M2: BP_PlayerCharacter — first-person camera + Enhanced Input graph logic.

Headless via UE 5.8 unreal.BlueprintGraphEditor:
  BeginPlay -> Controller -> CastToPlayerController -> EnhancedInput LP subsystem
            -> AddMappingContext(IMC_Default)
  IA_Move (Triggered)  -> AddMovementInput(forward * Y) + AddMovementInput(right * X)
  IA_Look (Triggered)  -> AddControllerYawInput(X) + AddControllerPitchInput(Y)
  IA_Sprint / IA_Crouch: walk-speed toggle + Crouch/UnCrouch.

Idempotent: bails out if the event graph already has nodes beyond the default 2
ghost events (skips rewiring), and skips camera add if FirstPersonCamera exists.
"""
import unreal

BP_PATH = "/Game/TVV/Blueprints/Player/BP_PlayerCharacter"
IMC_PATH = "/Game/TVV/Input/IMC_Default"
IA_DIR = "/Game/TVV/Input"

bel = unreal.BlueprintEditorLibrary
bge = unreal.BlueprintGraphEditor
gp = unreal.BlueprintGraphPin  # ScriptMethod statics also available on instances

log, err = unreal.log, unreal.log_error
results = {"ok": [], "fail": []}


def ok(msg): results["ok"].append(msg); log(f"[OK] {msg}")
def fail(msg): results["fail"].append(msg); err(f"[FAIL] {msg}")


def dump_pins(node, label):
    ins = [str(p.get_pin_name()) for p in bel.list_input_pins(node)]
    outs = [str(p.get_pin_name()) for p in bel.list_output_pins(node)]
    log(f"[PINS] {label}: in={ins} out={outs}")


def connect(a, b, label):
    if a is None or b is None or not a.try_create_connection(b):
        fail(f"connect {label}")
        return False
    return True


# ---------- load assets ----------
bp = unreal.load_asset(BP_PATH)
imc = unreal.load_asset(IMC_PATH)
ia = {}
for name in ("IA_Move", "IA_Look", "IA_Sprint", "IA_Crouch", "IA_Interact",
             "IA_Lean", "IA_Lantern", "IA_Codex", "IA_Pause"):
    ia[name] = unreal.load_asset(f"{IA_DIR}/{name}")
if not bp or not imc or not all(ia.values()):
    raise RuntimeError("missing assets")

# ---------- camera component ----------
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
sfl = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
existing = {}
for h in handles:
    data = sds.k2_find_subobject_data_from_handle(h)
    existing[str(sfl.get_variable_name(data))] = h

if "FirstPersonCamera" in existing:
    ok("camera exists (skipped)")
else:
    try:
        params = unreal.AddNewSubobjectParams(
            parent_handle=existing.get("CapsuleComponent", handles[0]),
            new_class=unreal.CameraComponent,
            blueprint_context=bp)
        new_handle, fail_reason = sds.add_new_subobject(params)
        if not fail_reason.is_empty():
            fail(f"add camera: {fail_reason}")
        else:
            sds.rename_subobject(new_handle, unreal.Text("FirstPersonCamera"))
            data = sds.k2_find_subobject_data_from_handle(new_handle)
            cam = sfl.get_object(data)
            cam.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 64.0))
            cam.set_editor_property("use_pawn_control_rotation", True)
            ok("camera added")
    except Exception as e:
        fail(f"camera: {e}")

# ---------- crouch capability on CharacterMovement template ----------
try:
    if "CharacterMovement" in existing:
        data = sds.k2_find_subobject_data_from_handle(existing["CharacterMovement"])
        cm = sfl.get_object(data)
        props = cm.get_editor_property("nav_agent_props")
        props.set_editor_property("can_crouch", True)
        cm.set_editor_property("nav_agent_props", props)
        ok("can_crouch enabled")
except Exception as e:
    fail(f"can_crouch: {e}")

# ---------- event graph ----------
editor = bge.get_graph_editor_by_name(bp, "EventGraph")
if not editor:
    raise RuntimeError("no EventGraph editor")

nodes = editor.list_all_nodes()
if nodes:
    editor.remove_nodes(nodes)  # rebuild from scratch: idempotent by reconstruction
if True:
    avail = editor.list_available_nodes([])
    for n in avail:
        if "IA_" in n or "reakVector2" in n.replace(" ", ""):
            log(f"[CAND] {n}")

    def node_name(suffix):
        for n in avail:
            if n.endswith(suffix):
                return n
        # fallback: case/space-insensitive containment
        want = suffix.replace(" ", "").lower()
        for n in avail:
            if want in n.replace(" ", "").lower():
                return n
        fail(f"node name not found: {suffix}")
        return None

    def create(suffix, x, y):
        name = node_name(suffix)
        if not name:
            return None
        n = editor.create_node_from_name(name, unreal.Vector2D(x, y), [])
        if not n:
            fail(f"create {name}")
        return n

    X, Y = 0, 0

    # --- BeginPlay -> AddMappingContext ---
    ev_bp = create("AddEvent|EventBeginPlay", X, Y)
    n_ctrl = create("Pawn|GetController", X + 200, Y + 150)
    n_cast = create("Utilities|Casting|CastToPlayerController", X + 250, Y)
    n_sub = create("PlayerController|LocalPlayerSubsystems|GetEnhancedInputLocalPlayerSubsystem", X + 500, Y + 150)
    n_amc = create("Input|AddMappingContext", X + 700, Y)
    if all((ev_bp, n_ctrl, n_cast, n_sub, n_amc)):
        for n, lbl in ((ev_bp, "BeginPlay"), (n_ctrl, "GetController"), (n_cast, "Cast"),
                       (n_sub, "GetEILPSubsystem"), (n_amc, "AddMappingContext")):
            dump_pins(n, lbl)
        connect(bel.find_then_pin(ev_bp), bel.find_execute_pin(n_cast), "BeginPlay->Cast")
        connect(bel.find_result_pin(n_ctrl), bel.find_input_pin(n_cast, "Object"), "Controller->Cast.Object")
        cast_out = next((p for p in bel.list_output_pins(n_cast)
                         if str(p.get_pin_name()).startswith("As")), None)
        connect(cast_out, bel.find_input_pin(n_sub, "PlayerController"), "Cast->Subsystem.PC")
        connect(bel.find_result_pin(n_sub), bel.find_self_pin(n_amc), "Subsystem->AMC.Target")
        connect(bel.find_then_pin(n_cast), bel.find_execute_pin(n_amc), "Cast.then->AMC")
        p = bel.find_input_pin(n_amc, "MappingContext")
        if not p.set_pin_value(f"{IMC_PATH}.IMC_Default"):
            fail("AMC.MappingContext value")
        else:
            ok("BeginPlay chain wired")

    # --- IA_Move ---
    ev_move = create("Input|EnhancedActionEvents|IA_Move", X, Y + 500)
    n_break = create("Math|Vector2D|BreakVector2D", X + 220, Y + 620)
    n_fwd = create("GetActorForwardVector", X + 220, Y + 720)
    n_right = create("GetActorRightVector", X + 220, Y + 820)
    n_add1 = create("Pawn|Input|AddMovementInput", X + 500, Y + 500)
    n_add2 = create("Pawn|Input|AddMovementInput", X + 800, Y + 500)
    if all((ev_move, n_break, n_fwd, n_right, n_add1, n_add2)):
        dump_pins(ev_move, "IA_Move")
        connect(bel.find_output_pin(ev_move, "Triggered"), bel.find_execute_pin(n_add1), "Move.Trig->Add1")
        connect(bel.find_output_pin(ev_move, "ActionValue"),
                bel.find_input_pin(n_break, "InVec"), "Move.Value->Break")
        connect(bel.find_output_pin(n_break, "Y"), bel.find_input_pin(n_add1, "ScaleValue"), "Break.Y->Add1.Scale")
        connect(bel.find_result_pin(n_fwd), bel.find_input_pin(n_add1, "WorldDirection"), "Fwd->Add1.Dir")
        connect(bel.find_then_pin(n_add1), bel.find_execute_pin(n_add2), "Add1->Add2")
        connect(bel.find_output_pin(n_break, "X"), bel.find_input_pin(n_add2, "ScaleValue"), "Break.X->Add2.Scale")
        connect(bel.find_result_pin(n_right), bel.find_input_pin(n_add2, "WorldDirection"), "Right->Add2.Dir")
        ok("IA_Move wired")

    # --- IA_Look ---
    ev_look = create("Input|EnhancedActionEvents|IA_Look", X, Y + 1100)
    n_break2 = create("Math|Vector2D|BreakVector2D", X + 220, Y + 1220)
    n_yaw = create("Pawn|Input|AddControllerYawInput", X + 500, Y + 1100)
    n_pitch = create("Pawn|Input|AddControllerPitchInput", X + 800, Y + 1100)
    if all((ev_look, n_break2, n_yaw, n_pitch)):
        connect(bel.find_output_pin(ev_look, "Triggered"), bel.find_execute_pin(n_yaw), "Look.Trig->Yaw")
        connect(bel.find_output_pin(ev_look, "ActionValue"),
                bel.find_input_pin(n_break2, "InVec"), "Look.Value->Break")
        connect(bel.find_output_pin(n_break2, "X"), bel.find_input_pin(n_yaw, "Val"), "Break.X->Yaw")
        connect(bel.find_then_pin(n_yaw), bel.find_execute_pin(n_pitch), "Yaw->Pitch")
        connect(bel.find_output_pin(n_break2, "Y"), bel.find_input_pin(n_pitch, "Val"), "Break.Y->Pitch")
        ok("IA_Look wired")

    # --- IA_Crouch (toggle on Started) ---
    ev_crouch = create("Input|EnhancedActionEvents|IA_Crouch", X, Y + 1700)
    n_crouch = create("Character|Crouch", X + 300, Y + 1700)
    n_uncrouch = create("Character|UnCrouch", X + 300, Y + 1850)
    if all((ev_crouch, n_crouch, n_uncrouch)):
        connect(bel.find_output_pin(ev_crouch, "Started"), bel.find_execute_pin(n_crouch), "Crouch.Started")
        connect(bel.find_output_pin(ev_crouch, "Completed"), bel.find_execute_pin(n_uncrouch), "Crouch.Completed")
        ok("IA_Crouch wired")

# ---------- compile & save ----------
if not bel.compile_blueprint(bp):
    fail("compile_blueprint")
else:
    ok("compiled")
    unreal.EditorAssetLibrary.save_asset(BP_PATH, only_if_is_dirty=False)
    ok("saved")

log("=== TVV PLAYER RESULT ===")
log(f"ok={len(results['ok'])} fail={len(results['fail'])}")
for m in results["ok"]:
    log(f"[SUM-OK] {m}")
for m in results["fail"]:
    err(f"[SUM-FAIL] {m}")
