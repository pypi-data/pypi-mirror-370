Cyberwave SDK (MVP)

This package exposes a minimal, synchronous facade for Missions and Runs to enable quick demos and developer onboarding.

Quickstart

```python
from cyberwave import Cyberwave, Mission

cw = Cyberwave(base_url="http://localhost:8000", token="<TOKEN>")

mission = Mission(key="so101/PickOrange", version=1, name="Pick Orange into Bin")
(mission.world()
  .asset("props/table-simple", alias="table")
  .asset("props/bin", alias="bin")
  .asset("props/orange", alias="orange1")
  .place("table",   [0,0,0, 1,0,0,0])
  .place("bin",     [0.6,0,0.8, 1,0,0,0])
  .place("orange1", [0.1,0,0.8, 1,0,0,0])
)
mission.parameters["seed"] = 42
mission.goal_object_in_zone("orange1", "bin", tolerance_m=0.05, hold_s=2.0)

cw.missions.register(mission)
run = cw.runs.start(environment_uuid="<ENV_UUID>", mission_key=mission.key, mission_version=mission.version, parameters=mission.parameters, mode="virtual")
print("run:", run["uuid"]) 
```

See `examples/quickstart_mvp.py` for a complete script with teleop and command calls.

