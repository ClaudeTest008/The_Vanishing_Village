"""TVV M2/M3 prep: PDA data schemas.

1. Creates skeletons missed in the first scaffold pass:
   PDA_LoopEvent, BPS_NarrativeSubsystem, AC_Health.
2. Adds member variables to all nine PDA definition Blueprints via
   BlueprintEditorLibrary.add_member_variable, then compiles and saves.

Run headless:
  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="Content/Python/tvv_m2_pda_vars.py"

Idempotent: existing assets/variables are skipped.
"""
import unreal

ROOT = "/Game/TVV"
DEFS = f"{ROOT}/Data/Definitions"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
bel = unreal.BlueprintEditorLibrary

created, skipped, failed = [], [], []
vars_added, vars_skipped, vars_failed = [], [], []


# ---------- missing skeletons ----------

MISSING = [
    ("PDA_LoopEvent", "Data/Definitions", unreal.PrimaryDataAsset),
    ("BPS_NarrativeSubsystem", "Blueprints/Core/Subsystems", unreal.Object),
    ("AC_Health", "Blueprints/Components", unreal.ActorComponent),
]


def make_missing():
    for name, subpath, parent in MISSING:
        full = f"{ROOT}/{subpath}/{name}"
        if eal.does_asset_exist(full):
            skipped.append(full)
            continue
        try:
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", parent)
            asset = asset_tools.create_asset(name, f"{ROOT}/{subpath}", None, factory)
            if asset:
                eal.save_asset(full, only_if_is_dirty=False)
                created.append(full)
            else:
                failed.append(full)
        except Exception as e:
            failed.append(f"{full} ({e})")


# ---------- pin type helpers ----------
# EdGraphPinType exposes no properties to Python; build types via
# BlueprintEditorLibrary factory functions only.
# ponytail: soft asset refs are untyped FSoftObjectPath — no Python helper for
# TSoftObjectPtr<T>; retype in editor (ChangeMemberVariableType) if the type
# filter is ever missed in practice.

def T_TEXT(): return bel.get_basic_type_by_name("text")
def T_BOOL(): return bel.get_basic_type_by_name("bool")
def T_INT(): return bel.get_basic_type_by_name("int")
def T_FLOAT(): return bel.get_basic_type_by_name("real")
def T_TAG(): return bel.get_struct_type(unreal.GameplayTag.static_struct())
def T_TAGS(): return bel.get_struct_type(unreal.GameplayTagContainer.static_struct())
def T_SOFT(): return bel.get_struct_type(unreal.SoftObjectPath.static_struct())
def A(t): return bel.get_array_type(t)


# ---------- schemas ----------

def build_schemas():
    return {
        "PDA_Resident": [
            ("DisplayName", T_TEXT()),
            ("ResidentTag", T_TAG()),
            ("Portrait", T_SOFT()),
            ("Occupation", T_TEXT()),
            ("HomeLocationTag", T_TAG()),
            ("Routine", T_SOFT()),
            ("Ghost", T_SOFT()),
            ("RelationshipTags", T_TAGS()),
            ("Secrets", A(T_TEXT())),
            ("TragedySummary", T_TEXT()),
            ("Dialogues", A(T_SOFT())),
            ("Memories", A(T_SOFT())),
        ],
        "PDA_Ghost": [
            ("DisplayName", T_TEXT()),
            ("GhostTag", T_TAG()),
            ("LinkedResidentTag", T_TAG()),
            ("InitialStateTag", T_TAG()),
            ("HostilityLevel", T_FLOAT()),
            ("SightRadius", T_FLOAT()),
            ("HearingRadius", T_FLOAT()),
            ("PatrolSpeed", T_FLOAT()),
            ("ChaseSpeed", T_FLOAT()),
            ("RemembersPlayer", T_BOOL()),
            ("Mesh", T_SOFT()),
            ("AppearSound", T_SOFT()),
        ],
        # ponytail: parallel arrays for routine entries; upgrade to a
        # UserDefinedStruct (S_RoutineEntry) once created in-editor.
        "PDA_Routine": [
            ("OwnerResidentTag", T_TAG()),
            ("EntryTimes", A(T_FLOAT())),
            ("EntryLocationTags", A(T_TAG())),
            ("EntryActivities", A(T_TEXT())),
        ],
        "PDA_Memory": [
            ("MemoryTag", T_TAG()),
            ("Title", T_TEXT()),
            ("Description", T_TEXT()),
            ("LinkedResidentTag", T_TAG()),
            ("LocationTag", T_TAG()),
            ("RequiredClueTags", T_TAGS()),
            ("UnlocksTags", T_TAGS()),
            ("EchoDuration", T_FLOAT()),
        ],
        "PDA_Item": [
            ("ItemTag", T_TAG()),
            ("DisplayName", T_TEXT()),
            ("Description", T_TEXT()),
            ("Icon", T_SOFT()),
            ("WorldMesh", T_SOFT()),
            ("MaxStack", T_INT()),
            ("Consumable", T_BOOL()),
            ("UseEffectTag", T_TAG()),
        ],
        "PDA_Puzzle": [
            ("PuzzleTag", T_TAG()),
            ("Title", T_TEXT()),
            ("LocationTag", T_TAG()),
            ("RequiredItemTags", T_TAGS()),
            ("RequiredKnowledgeTags", T_TAGS()),
            ("RewardTags", T_TAGS()),
        ],
        "PDA_Dialogue": [
            ("DialogueTag", T_TAG()),
            ("SpeakerResidentTag", T_TAG()),
            ("Lines", A(T_TEXT())),
            ("RequiredTags", T_TAGS()),
            ("GrantsKnowledgeTags", T_TAGS()),
        ],
        "PDA_Ending": [
            ("EndingTag", T_TAG()),
            ("Title", T_TEXT()),
            ("Description", T_TEXT()),
            ("RequiredWorldStateTags", T_TAGS()),
            ("Priority", T_INT()),
        ],
        "PDA_LoopEvent": [
            ("EventTag", T_TAG()),
            ("TriggerTime", T_FLOAT()),
            ("LocationTag", T_TAG()),
            ("InvolvedResidentTags", T_TAGS()),
            ("Description", T_TEXT()),
            ("CanBePrevented", T_BOOL()),
            ("PreventedByTags", T_TAGS()),
        ],
    }


def add_vars():
    schemas = build_schemas()
    for bp_name, fields in schemas.items():
        path = f"{DEFS}/{bp_name}"
        bp = unreal.load_asset(path)
        if not bp:
            vars_failed.append(f"{path} (asset not found)")
            continue
        try:
            existing = list(bel.list_member_variable_names(bp, include_inherited_members=False))
        except Exception:
            existing = []
        dirty = False
        for var_name, pin_type in fields:
            if var_name in existing:
                vars_skipped.append(f"{bp_name}.{var_name}")
                continue
            try:
                if bel.add_member_variable(bp, var_name, pin_type):
                    vars_added.append(f"{bp_name}.{var_name}")
                    dirty = True
                else:
                    vars_failed.append(f"{bp_name}.{var_name}")
            except Exception as e:
                vars_failed.append(f"{bp_name}.{var_name} ({e})")
        if dirty:
            bel.compile_blueprint(bp)
            eal.save_asset(path, only_if_is_dirty=False)


def main():
    make_missing()
    add_vars()
    unreal.log("=== TVV PDA VARS RESULT ===")
    unreal.log(f"assets: created={len(created)} skipped={len(skipped)} failed={len(failed)}")
    unreal.log(f"vars: added={len(vars_added)} skipped={len(vars_skipped)} failed={len(vars_failed)}")
    for a in created:
        unreal.log(f"[CREATED] {a}")
    for v in vars_added:
        unreal.log(f"[VAR] {v}")
    for x in failed + vars_failed:
        unreal.log_error(f"[FAILED] {x}")


main()
