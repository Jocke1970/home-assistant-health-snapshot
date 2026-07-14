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

The summary sensor exposes card-friendly attributes, including Garmin readiness, Body Battery, resting heart rate, stress, sleep, HRV, SpO2, blood pressure, hydration, VO2 max, fitness age and Withings body metrics.

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

- Body Battery most recent/highest/lowest/charged/drained
- resting heart rate and 7-day resting heart rate
- average/max stress level and stress percentages
- training readiness and morning training readiness
- recovery time and training status
- sleep need and deep/light/REM/awake sleep
- average/latest/lowest SpO2
- HRV weekly, last night, 5-minute high and baseline
- hydration, hydration goal and sweat loss
- blood pressure systolic/diastolic/pulse/category
- VO2 max, endurance score, fitness age and chronological age
- steps, distance and intensity minutes
- cycling FTP and power-to-weight

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

This is a v0.2 backend. It is intentionally local, lightweight and YAML-platform based for easy Home Assistant testing.
