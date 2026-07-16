"""Driver: run interaction then player scripts in one editor session."""
import os

base = os.path.dirname(os.path.abspath(__file__))
for name in ("tvv_m2_cleanup.py", "tvv_m2_player.py"):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        exec(compile(f.read(), name, "exec"), {"__name__": "__main__", "__file__": os.path.join(base, name)})
