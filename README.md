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

For dashboard-only 30/90-day deltas, the bundled `dashboards/bodyfit_card.yaml` uses Home Assistant's native **Statistic card** directly against long-term statistics, so no extra helper entities are required. The same card includes 30-day daily trend graphs and 12-month monthly trend graphs. Create Statistics helpers only if you later need the rolling deltas as reusable entities for automations or other dashboards.

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


## BodyFit dashboard

A complete BodyFit dashboard card is available at:

```text
dashboards/bodyfit_card.yaml
```

It uses:

- the eight BodyFit proxy entities for current values and long-term statistics
- native Statistic cards for rolling 30-day and 90-day change
- native Statistics Graph cards for 30-day and 12-month trends
- the existing segmental muscle entities from Withings
- the existing uploaded body image media-source reference used by the current dashboard

The clean BodyFit trend history starts on 2026-10-03, so rolling windows initially represent the available post-migration history until the full 30/90-day windows have elapsed.


## Withings health metrics dashboard

A separate Withings health metrics card is available at:

```text
dashboards/withings_health_card.yaml
```

This card intentionally complements rather than duplicates the BodyFit body-composition card. It includes:

- vascular age, pulse wave velocity (PWV) and Withings pulse
- 30-day and 12-month cardiovascular trend graphs
- total body water, intracellular water (ICW) and extracellular water (ECW)
- latest Withings workout details
- weight/step goals
- BodyFit and Body Comp battery/maintenance status

The card follows the active Home Assistant theme and uses the same collapsible section pattern as the BodyFit dashboard.
