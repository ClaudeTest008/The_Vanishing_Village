"""TVV M2: Interaction system (headless-safe, no interface message nodes).

Design: marker component. Interactable actors carry AC_Interactable
(PromptText var + OnInteracted custom event; owner binds via component-bound
event). AC_Interaction on the player line-traces from the camera each tick,
stores GetComponentByClass(AC_Interactable) result in CurrentInteractable
(typed), and TryInteract() fires OnInteracted on it.

Interface message nodes are NOT creatable headless (BP action DB never indexes
BP-asset actions in -run=pythonscript); BPI_Interactable is kept as editor-time
contract only.

Idempotent by reconstruction: graphs wiped and rebuilt each run.
"""
import unreal

BPI_PATH = "/Game/TVV/Blueprints/Interfaces/BPI_Interactable"
AC_PATH = "/Game/TVV/Blueprints/Components/AC_Interaction"
ACI_PATH = "/Game/TVV/Blueprints/Components/AC_Interactable"
ACI_CLASS = f"{ACI_PATH}.AC_Interactable_C"
TRACE_DISTANCE = "300.0"

bel = unreal.BlueprintEditorLibrary
bge = unreal.BlueprintGraphEditor
eal = unreal.EditorAssetLibrary
log, err = unreal.log_warning, unreal.log_error  # plain log invisible in -run=pythonscript
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


def setval(node, pin_name, value, label):
    p = bel.find_input_pin(node, pin_name)
    if p is None:
        dump_pins(node, f"{label}(pin {pin_name} missing)")
        fail(f"set {label}.{pin_name}: pin not found")
        return
    for v in (value, value.rstrip("0").rstrip("."), f"{float(value):f}" if value.replace(".", "").isdigit() else value):
        if p.set_pin_value(v):
            log(f"[OK] set {label}.{pin_name}={v}")
            return
    fail(f"set {label}.{pin_name}={value}")


def compile_save(bp, path, label):
    if not bel.compile_blueprint(bp):
        fail(f"compile {label}")
        return False
    eal.save_asset(path, only_if_is_dirty=False)
    ok(f"{label} compiled+saved")
    return True


# ============ 1. BPI_Interactable (editor-time contract) ============
bpi = unreal.load_asset(BPI_PATH)
actor_ref = bel.get_object_reference_type(unreal.Actor)
text_type = bel.get_basic_type_by_name("text")
if bpi:
    if bge.get_graph_editor_by_name(bpi, "Interact"):
        ok("BPI.Interact exists")
    else:
        g = bge.create_and_edit_function_graph(bpi, "Interact")
        g and g.add_graph_input_parameter("Instigator", actor_ref, "")
        ok("BPI.Interact created") if g else fail("BPI.Interact")
    if bge.get_graph_editor_by_name(bpi, "GetInteractionPrompt"):
        ok("BPI.GetInteractionPrompt exists")
    else:
        g = bge.create_and_edit_function_graph(bpi, "GetInteractionPrompt")
        g and g.add_graph_output_parameter("Prompt", text_type)
        ok("BPI.GetInteractionPrompt created") if g else fail("BPI.GetInteractionPrompt")
    compile_save(bpi, BPI_PATH, "BPI")

# ============ 2. AC_Interactable marker component ============
aci = unreal.load_asset(ACI_PATH)
if not aci:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.ActorComponent)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    aci = at.create_asset("AC_Interactable", "/Game/TVV/Blueprints/Components", None, factory)
    ok("AC_Interactable created") if aci else fail("AC_Interactable create")

if aci:
    if "PromptText" not in [str(v) for v in bel.list_member_variable_names(aci)]:
        if bel.add_member_variable(aci, "PromptText", text_type):
            ok("PromptText var added")
        else:
            fail("PromptText var")
    else:
        ok("PromptText var exists")
    ged = bge.get_graph_editor_by_name(aci, "EventGraph")
    nodes = ged.list_all_nodes()
    if nodes:
        ged.remove_nodes(nodes)
    ev = ged.add_custom_event_node("OnInteracted")
    if ev:
        ok("OnInteracted event added")
    else:
        fail("OnInteracted event")
    compile_save(aci, ACI_PATH, "AC_Interactable")

# ============ 3. AC_Interaction ============
ac = unreal.load_asset(AC_PATH)
if not ac:
    raise RuntimeError("AC_Interaction missing")

aci_class = unreal.load_object(None, ACI_CLASS)
comp_ref = bel.get_object_reference_type(aci_class)
real_type = bel.get_basic_type_by_name("real")
existing_vars = [str(v) for v in bel.list_member_variable_names(ac)]
if "TraceDistance" not in existing_vars:
    if bel.add_member_variable(ac, "TraceDistance", real_type):
        ok("var TraceDistance added")
    else:
        fail("var TraceDistance")
else:
    ok("var TraceDistance exists")
if "CurrentInteractable" in existing_vars:
    # may carry old Actor type from a previous run; remove via graph editor API
    bge.get_graph_editor_by_name(ac, "EventGraph").remove_member_variable("CurrentInteractable")
if bel.add_member_variable(ac, "CurrentInteractable", comp_ref):
    ok("var CurrentInteractable (AC_Interactable ref)")
else:
    fail("var CurrentInteractable")

# ---- EventGraph: tick trace -> GetComponentByClass -> Set ----
editor = bge.get_graph_editor_by_name(ac, "EventGraph")
nodes = editor.list_all_nodes()
if nodes:
    editor.remove_nodes(nodes)

avail = editor.list_available_nodes([])


def node_name(suffix):
    want = suffix.replace(" ", "").lower()
    for n in avail:
        if n.replace(" ", "").lower().endswith(want):
            return n
    for n in avail:
        if want in n.replace(" ", "").lower():
            return n
    fail(f"node name not found: {suffix}")
    return None


def create(suffix, x=0, y=0):
    name = node_name(suffix)
    if not name:
        return None
    n = editor.create_node_from_name(name, unreal.Vector2D(x, y), [])
    if not n:
        fail(f"create {name}")
    return n


def call(path, label):
    n = editor.add_call_function_node(path)
    if not n:
        fail(f"add_call_function_node {label}: {path}")
    return n


ev_tick = create("EventTick")
n_pcm = call("/Script/Engine.GameplayStatics.GetPlayerCameraManager", "GetPCM")
n_camloc = call("/Script/Engine.PlayerCameraManager.GetCameraLocation", "GetCamLoc")
n_fwd = call("/Script/Engine.Actor.GetActorForwardVector", "GetFwd")
n_mul = call("/Script/Engine.KismetMathLibrary.Multiply_VectorFloat", "MulVF")
n_add = call("/Script/Engine.KismetMathLibrary.Add_VectorVector", "AddVV")
n_trace = call("/Script/Engine.KismetSystemLibrary.LineTraceSingle", "Trace")
n_break = call("/Script/Engine.GameplayStatics.BreakHitResult", "BreakHit")
n_getcomp = call("/Script/Engine.Actor.GetComponentByClass", "GetCompByClass")
n_set = editor.add_set_member_variable_node("CurrentInteractable")
n_dist = editor.add_get_member_variable_node("TraceDistance")

phase1 = all((ev_tick, n_pcm, n_camloc, n_fwd, n_mul, n_add, n_trace, n_break, n_getcomp, n_set, n_dist))
if phase1:
    # setting class pin default triggers DeterminesOutputType retype of ReturnValue
    connect(bel.find_output_pin(n_dist, "TraceDistance"), bel.find_input_pin(n_mul, "B"), "Dist->Mul.B")
    setval(n_getcomp, "ComponentClass", ACI_CLASS, "GetCompByClass")
    dump_pins(n_getcomp, "GetCompByClass(after class set)")
    dump_pins(n_set, "SetVar")
    connect(bel.find_output_pin(n_pcm, "ReturnValue"), bel.find_self_pin(n_camloc), "PCM->CamLoc.self")
    connect(bel.find_output_pin(n_pcm, "ReturnValue"), bel.find_self_pin(n_fwd), "PCM->Fwd.self")
    connect(bel.find_output_pin(n_fwd, "ReturnValue"), bel.find_input_pin(n_mul, "A"), "Fwd->Mul.A")
    connect(bel.find_output_pin(n_camloc, "ReturnValue"), bel.find_input_pin(n_add, "A"), "CamLoc->Add.A")
    connect(bel.find_output_pin(n_mul, "ReturnValue"), bel.find_input_pin(n_add, "B"), "Mul->Add.B")
    connect(bel.find_output_pin(ev_tick, "then"), bel.find_execute_pin(n_trace), "Tick->Trace")
    connect(bel.find_output_pin(n_camloc, "ReturnValue"), bel.find_input_pin(n_trace, "Start"), "CamLoc->Trace.Start")
    connect(bel.find_output_pin(n_add, "ReturnValue"), bel.find_input_pin(n_trace, "End"), "Add->Trace.End")
    connect(bel.find_output_pin(n_trace, "OutHit"), bel.find_input_pin(n_break, "Hit"), "Trace->Break")
    connect(bel.find_output_pin(n_break, "HitActor"), bel.find_self_pin(n_getcomp), "HitActor->GetComp.self")
    connect(bel.find_then_pin(n_trace), bel.find_execute_pin(n_set), "Trace->Set")
    connect(bel.find_output_pin(n_getcomp, "ReturnValue"),
            bel.find_input_pin(n_set, "CurrentInteractable"), "GetComp->Set")
    ok("AC tick trace wired")

# ---- TryInteract function ----
fedit = bge.get_graph_editor_by_name(ac, "TryInteract")
if not fedit:
    fedit = bge.create_and_edit_function_graph(ac, "TryInteract")
if fedit:
    fnodes = [n for n in fedit.list_all_nodes()
              if not isinstance(n, unreal.K2Node_FunctionEntry)]
    if fnodes:
        fedit.remove_nodes(fnodes)
    entry_pin = fedit.find_graph_entry_pin()
    n_get = fedit.add_get_member_variable_node("CurrentInteractable")
    n_valid = fedit.add_call_function_node("/Script/Engine.KismetSystemLibrary.IsValid")
    n_fbranch = fedit.add_branch_node()
    n_call = fedit.add_call_function_node(f"{ACI_CLASS}.OnInteracted")
    if all((n_get, n_valid, n_fbranch, n_call)):
        dump_pins(n_call, "OnInteracted")
        var_out = bel.find_output_pin(n_get, "CurrentInteractable")
        connect(var_out, bel.find_input_pin(n_valid, "Object"), "Var->IsValid")
        connect(entry_pin, bel.find_execute_pin(n_fbranch), "Entry->Branch")
        connect(bel.find_output_pin(n_valid, "ReturnValue"), bel.find_input_pin(n_fbranch, "Condition"), "IsValid->Cond")
        connect(bel.find_output_pin(n_fbranch, "then"), bel.find_execute_pin(n_call), "True->OnInteracted")
        connect(var_out, bel.find_self_pin(n_call), "Var->OnInteracted.self")
        ok("TryInteract wired")
    else:
        fail("TryInteract nodes")
else:
    fail("TryInteract graph")

if compile_save(ac, AC_PATH, "AC_Interaction"):
    # float literals rejected by SetPinValue on real pins; defaults go on the CDO instead
    try:
        cdo = unreal.get_default_object(unreal.load_object(None, f"{AC_PATH}.AC_Interaction_C"))
        cdo.set_editor_property("TraceDistance", float(TRACE_DISTANCE))
        eal.save_asset(AC_PATH, only_if_is_dirty=False)
        ok(f"TraceDistance CDO default={TRACE_DISTANCE}")
    except Exception as e:
        fail(f"TraceDistance CDO: {e}")

log("=== TVV INTERACTION RESULT ===")
log(f"ok={len(results['ok'])} fail={len(results['fail'])}")
for m in results["ok"]:
    log(f"[SUM-OK] {m}")
for m in results["fail"]:
    err(f"[SUM-FAIL] {m}")
