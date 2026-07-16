"""Probe: find how BPI_Interactable functions appear in the Blueprint action DB."""
import unreal

BPI_PATH = "/Game/TVV/Blueprints/Interfaces/BPI_Interactable"
AC_PATH = "/Game/TVV/Blueprints/Components/AC_Interaction"
bel = unreal.BlueprintEditorLibrary
bge = unreal.BlueprintGraphEditor
warn = unreal.log_warning

bpi = unreal.load_asset(BPI_PATH)
ac = unreal.load_asset(AC_PATH)
bpi_class = unreal.load_object(None, f"{BPI_PATH}.BPI_Interactable_C")
warn(f"[PROBE] bpi={bpi} class={bpi_class}")

fedit = bge.get_graph_editor_by_name(ac, "TryInteract")
avail = fedit.list_available_nodes([])
warn(f"[PROBE] total avail={len(avail)}")
hits = [n for n in avail if any(k in n.lower() for k in ("bpi", "interactable", "prompt"))]
for n in hits:
    warn(f"[HIT] {n}")

for name in ("Interact", "Interfaces|Interact", "BPI_Interactable|Interact",
             "BPIInteractable|Interact", "Interact(Message)",
             "Interfaces|Interact(Message)", "BPIInteractable|Interact(Message)"):
    for cls in (bpi_class, None):
        n = fedit.create_node_from_name(name, unreal.Vector2D(1200, 600), [], cls)
        warn(f"[TRY] name='{name}' cls={'BPI' if cls else 'None'} -> {n}")
        if n:
            ins = [str(p.get_pin_name()) for p in bel.list_input_pins(n)]
            warn(f"[TRYPINS] in={ins}")
            fedit.remove_nodes([n])
# no save: probe only
