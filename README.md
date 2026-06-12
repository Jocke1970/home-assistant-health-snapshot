# Home Assistant Health Snapshot

Python-based Garmin + Withings health snapshot sensor platform for Home Assistant.

This custom component creates a small set of calculated health snapshot sensors from existing Garmin Connect and Withings entities.

## Created entities

```yaml
sensor.health_snapshot_overall_score
sensor.health_snapshot_recovery_score
sensor.health_snapshot_activity_score
sensor.health_snapshot_body_score
sensor.health_snapshot_status
sensor.health_snapshot_summary
```

The summary sensor exposes card-friendly attributes, including Garmin readiness, sleep, HRV, SpO2 and Withings body metrics.

## Installation

Copy this folder into Home Assistant:

```text
custom_components/health_snapshot/
```

Then add this to `configuration.yaml` or a package file:

```yaml
sensor:
  - platform: health_snapshot
```

Restart Home Assistant.

## Important

Disable/remove any old template sensors using the same names before restart, otherwise Home Assistant may create `_2` entity IDs for the Python sensors.

## Current data sources

Garmin:

- training readiness
- morning training readiness
- recovery time
- sleep need
- deep/light/REM/awake sleep
- average/latest/lowest SpO2
- HRV last night + baseline
- steps and distance
- intensity minutes
- training status

Withings:

- weight
- weight goal
- body fat percentage
- visceral fat index
- pulse wave velocity
- vascular age
- heart pulse
- step goal

## Notes

This is an early v0.1 backend. It is intentionally local, lightweight and YAML-platform based for easy Home Assistant testing.
