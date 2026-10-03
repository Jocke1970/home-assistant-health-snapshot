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

From version `2026.10.0b1`, the integration also exposes fresh BodyFit-only proxy sensors. These intentionally start a new recorder/long-term-statistics history after the Body Comp → BodyFit migration, so composition graphs are not polluted by the instrument change.

## Installation

Copy this folder into Home Assistant:

```text
custom_components/health_snapshot/
```

Then add the platform to your normal sensor configuration (directly in `configuration.yaml` or your existing split sensor include):

```yaml
sensor:
  - platform: health_snapshot
```

No Home Assistant package is required for Health Snapshot.

Restart Home Assistant.

## Important

Disable/remove any old template sensors using the same names before restart, otherwise Home Assistant may create `_2` entity IDs for the Python sensors.

## BodyFit trend entities

```text
sensor.health_snapshot_bodyfit_weight
sensor.health_snapshot_bodyfit_fat_percentage
sensor.health_snapshot_bodyfit_muscle_mass
sensor.health_snapshot_bodyfit_fat_mass
sensor.health_snapshot_bodyfit_fat_free_mass
sensor.health_snapshot_bodyfit_bone_mass
sensor.health_snapshot_bodyfit_water_percentage
sensor.health_snapshot_bodyfit_visceral_fat
```

The water percentage entity is calculated as Withings hydration mass divided by current Withings body weight. All BodyFit proxy entities use `state_class: measurement` so Home Assistant can build long-term statistics for month/year graphs.

For rolling 30/90-day change sensors, use Home Assistant's native **Statistics helper** against these BodyFit proxy entities. This keeps recorder/statistics logic in Home Assistant instead of duplicating it in the custom integration.

## Branch / release SOP

Long-lived branches are strictly:

```text
dev → beta → main
```

- `dev`: active development only
- `beta`: latest verified prerelease
- `main`: stable only
- no direct feature work on `beta` or `main`
- beta tags use calendar versions such as `v2026.10.0b1`, `v2026.10.0b2`

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

The backend is intentionally local and lightweight. Version `2026.10.0b1` begins the BodyFit trend-history migration while retaining the existing YAML sensor-platform setup.
