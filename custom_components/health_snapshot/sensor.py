"""Health Snapshot sensors for Home Assistant.

YAML setup:

sensor:
  - platform: health_snapshot
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

SCAN_INTERVAL = timedelta(minutes=15)
INVALID = {"unknown", "unavailable", "none", "None", ""}

SENSORS = {
    "overall_score": ("Health Snapshot Overall Score", "mdi:heart-circle", PERCENTAGE),
    "recovery_score": ("Health Snapshot Recovery Score", "mdi:battery-heart", PERCENTAGE),
    "activity_score": ("Health Snapshot Activity Score", "mdi:run-fast", PERCENTAGE),
    "body_score": ("Health Snapshot Body Score", "mdi:human", PERCENTAGE),
    "status": ("Health Snapshot Status", "mdi:heart-pulse", None),
    "summary": ("Health Snapshot Summary", "mdi:clipboard-pulse", None),
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up Health Snapshot sensors."""
    async_add_entities([HealthSnapshotSensor(hass, key) for key in SENSORS], True)


class HealthSnapshotSensor(SensorEntity):
    """Calculated Health Snapshot sensor."""

    _attr_should_poll = True

    def __init__(self, hass: HomeAssistant, key: str) -> None:
        self.hass = hass
        self.key = key
        name, icon, unit = SENSORS[key]
        self._attr_name = name
        self._attr_unique_id = f"health_snapshot_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._attr_extra_state_attributes: dict[str, Any] = {}

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    def update(self) -> None:
        snapshot = build_snapshot(self.hass)
        self._attr_native_value = snapshot.get(self.key)
        self._attr_extra_state_attributes = snapshot["attributes"] if self.key == "summary" else {}


def build_snapshot(hass: HomeAssistant) -> dict[str, Any]:
    """Build one complete snapshot from Garmin + Withings states."""
    training_readiness = f(hass, "sensor.garmin_connect_training_readiness")
    morning_readiness = f(hass, "sensor.garmin_connect_morning_training_readiness")
    recovery_time_h = f(hass, "sensor.garmin_connect_recovery_time")

    sleep_need = f(hass, "sensor.garmin_connect_sleep_need")
    deep = f(hass, "sensor.garmin_connect_deep_sleep")
    light = f(hass, "sensor.garmin_connect_light_sleep")
    rem = f(hass, "sensor.garmin_connect_rem_sleep")
    awake = f(hass, "sensor.garmin_connect_awake_time")
    total_sleep = sum_known([deep, light, rem])

    hrv_last = f(hass, "sensor.garmin_connect_hrv_last_night_average")
    hrv_base = f(hass, "sensor.garmin_connect_hrv_baseline")

    yesterday_steps = f(hass, "sensor.garmin_connect_yesterday_steps")
    weekly_steps = f(hass, "sensor.garmin_connect_weekly_step_average")
    intensity = f(hass, "sensor.garmin_connect_intensity_minutes")
    yesterday_distance = f(hass, "sensor.garmin_connect_yesterday_distance")
    weekly_distance = f(hass, "sensor.garmin_connect_weekly_distance_average")
    training_status = s(hass, "sensor.garmin_connect_training_status")

    weight = f(hass, "sensor.withings_vikt")
    weight_goal = f(hass, "sensor.withings_viktmal")
    fat = f(hass, "sensor.withings_fettforhallande")
    visceral = f(hass, "sensor.withings_visceral_fat_index")
    pwv = f(hass, "sensor.withings_pulsvagens_hastighet")
    vascular_age = f(hass, "sensor.withings_vaskular_alder")
    withings_pulse = f(hass, "sensor.withings_hjartpuls")
    step_goal = f(hass, "sensor.withings_stegmal") or 5000

    sleep_score = calc_sleep_score(total_sleep, sleep_need, awake)
    hrv_score = calc_hrv_score(hrv_last, hrv_base)
    readiness = first([morning_readiness, training_readiness])
    recovery_time_score = calc_recovery_time_score(recovery_time_h)

    recovery_score = avg([
        (readiness, 0.42),
        (sleep_score, 0.28),
        (hrv_score, 0.20),
        (recovery_time_score, 0.10),
    ])
    activity_score = calc_activity_score(
        yesterday_steps,
        weekly_steps,
        step_goal,
        intensity,
        yesterday_distance,
        weekly_distance,
        training_status,
    )
    body_score = calc_body_score(weight, weight_goal, fat, visceral, pwv, vascular_age)
    overall_score = avg([(recovery_score, 0.48), (activity_score, 0.27), (body_score, 0.25)])
    hrv_status = calc_hrv_status(hrv_last, hrv_base)
    status = calc_status(overall_score, recovery_score, sleep_score, hrv_score, recovery_time_h)
    summary = build_summary(status, overall_score, recovery_score, activity_score, body_score, sleep_score, total_sleep, sleep_need, hrv_status, training_status)

    attributes = {
        "body_battery": None,
        "training_readiness": r(training_readiness),
        "morning_training_readiness": r(morning_readiness),
        "sleep_score": r(sleep_score),
        "sleep_score_source": "calculated_from_sleep_need",
        "hrv_status": hrv_status,
        "resting_heart_rate": None,
        "stress_level": None,
        "withings_weight": r(weight, 1),
        "withings_fat_percentage": r(fat, 1),
        "withings_visceral_fat": r(visceral, 1),
        "withings_pwv": r(pwv, 2),
        "withings_vascular_age": r(vascular_age, 1),
        "withings_heart_pulse": r(withings_pulse),
        "recovery_time_h": r(recovery_time_h, 1),
        "sleep_need_min": r(sleep_need),
        "total_sleep_min": r(total_sleep),
        "deep_sleep_min": r(deep),
        "light_sleep_min": r(light),
        "rem_sleep_min": r(rem),
        "awake_time_min": r(awake),
        "hrv_last_night_ms": r(hrv_last),
        "hrv_baseline_ms": r(hrv_base),
        "yesterday_steps": r(yesterday_steps),
        "weekly_step_average": r(weekly_steps),
        "intensity_minutes": r(intensity),
        "training_status": training_status,
        "data_quality": data_quality([
            training_readiness, morning_readiness, recovery_time_h, sleep_need, total_sleep,
            hrv_last, hrv_base, yesterday_steps, weekly_steps, weight, fat, visceral, pwv, vascular_age,
        ]),
    }

    return {
        "overall_score": r(overall_score),
        "recovery_score": r(recovery_score),
        "activity_score": r(activity_score),
        "body_score": r(body_score),
        "status": status,
        "summary": summary,
        "attributes": attributes,
    }


def f(hass: HomeAssistant, entity_id: str) -> float | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in INVALID:
        return None
    try:
        return float(str(state.state).replace(",", "."))
    except (TypeError, ValueError):
        return None


def s(hass: HomeAssistant, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in INVALID:
        return None
    return str(state.state)


def first(values: list[float | None]) -> float | None:
    return next((value for value in values if value is not None), None)


def sum_known(values: list[float | None]) -> float | None:
    known = [value for value in values if value is not None]
    return sum(known) if known else None


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def r(value: float | None, digits: int = 0):
    if value is None:
        return None
    return int(round(value)) if digits == 0 else round(value, digits)


def avg(items: list[tuple[float | None, float]]) -> float | None:
    usable = [(value, weight) for value, weight in items if value is not None]
    if not usable:
        return None
    total_weight = sum(weight for _, weight in usable)
    return clamp(sum(value * weight for value, weight in usable) / total_weight)


def calc_sleep_score(total_sleep: float | None, sleep_need: float | None, awake: float | None) -> float | None:
    if total_sleep is None or sleep_need is None or sleep_need <= 0:
        return None
    score = clamp((total_sleep / sleep_need) * 100)
    if awake is not None and awake > 45:
        score -= 10
    elif awake is not None and awake > 25:
        score -= 5
    return clamp(score)


def calc_hrv_score(last: float | None, baseline: float | None) -> float | None:
    if last is None or baseline is None or baseline <= 0:
        return None
    ratio = last / baseline
    if ratio >= 1.05:
        return 92
    if ratio >= 0.95:
        return 84
    if ratio >= 0.85:
        return 70
    if ratio >= 0.75:
        return 55
    return 40


def calc_recovery_time_score(hours: float | None) -> float | None:
    if hours is None:
        return None
    if hours <= 4:
        return 95
    if hours <= 12:
        return 82
    if hours <= 24:
        return 65
    if hours <= 48:
        return 45
    return 25


def calc_activity_score(steps, weekly_steps, step_goal, intensity, distance, weekly_distance, training_status) -> float | None:
    step_score = clamp((steps / step_goal) * 100) if steps is not None and step_goal else None
    trend_score = clamp((steps / weekly_steps) * 85) if steps is not None and weekly_steps else None
    intensity_score = clamp((intensity / 30) * 100) if intensity is not None else None
    distance_score = clamp((distance / weekly_distance) * 85) if distance is not None and weekly_distance else None
    score = avg([(step_score, 0.48), (trend_score, 0.22), (intensity_score, 0.15), (distance_score, 0.15)])
    if score is None:
        return None
    if training_status:
        text = training_status.lower()
        if "detraining" in text:
            score -= 6
        elif "productive" in text:
            score += 5
        elif "peaking" in text:
            score += 4
        elif "strained" in text:
            score -= 8
    return clamp(score)


def calc_body_score(weight, goal, fat, visceral, pwv, vascular_age) -> float | None:
    weight_score = clamp(100 - abs(weight - goal) * 8) if weight is not None and goal is not None else None
    fat_score = None
    if fat is not None:
        if 12 <= fat <= 22:
            fat_score = 92
        elif 10 <= fat < 12 or 22 < fat <= 27:
            fat_score = 80
        elif 27 < fat <= 32:
            fat_score = 65
        else:
            fat_score = 50
    visceral_score = None
    if visceral is not None:
        if visceral <= 5:
            visceral_score = 95
        elif visceral <= 9:
            visceral_score = 82
        elif visceral <= 12:
            visceral_score = 65
        else:
            visceral_score = 45
    pwv_score = None
    if pwv is not None:
        if pwv < 7.5:
            pwv_score = 90
        elif pwv < 8.5:
            pwv_score = 78
        elif pwv < 9.5:
            pwv_score = 65
        else:
            pwv_score = 48
    vascular_score = None
    if vascular_age is not None:
        if vascular_age <= 50:
            vascular_score = 90
        elif vascular_age <= 58:
            vascular_score = 76
        elif vascular_age <= 65:
            vascular_score = 62
        else:
            vascular_score = 45
    return avg([(weight_score, 0.20), (fat_score, 0.25), (visceral_score, 0.25), (pwv_score, 0.15), (vascular_score, 0.15)])


def calc_status(overall, recovery, sleep, hrv, recovery_time) -> str:
    if overall is None:
        return "Unknown"
    if sleep is not None and sleep < 55:
        return "Poor sleep"
    if recovery is not None and recovery < 50:
        return "Recovery needed"
    if hrv is not None and hrv < 50:
        return "Recovery needed"
    if recovery_time is not None and recovery_time >= 36:
        return "Recovery needed"
    if overall >= 85:
        return "Excellent"
    if overall >= 70:
        return "Good"
    if overall >= 55:
        return "Okay"
    return "Low"


def calc_hrv_status(last, baseline) -> str:
    if last is None or baseline is None or baseline <= 0:
        return "Saknas"
    ratio = last / baseline
    if ratio >= 1.05:
        return "Över baseline"
    if ratio >= 0.95:
        return "I baseline"
    if ratio >= 0.85:
        return "Något låg"
    if ratio >= 0.75:
        return "Låg"
    return "Mycket låg"


def build_summary(status, overall, recovery, activity, body, sleep, total_sleep, sleep_need, hrv_status, training_status) -> str:
    if overall is None:
        return "Snapshot saknar tillräckligt med data just nu."
    status_sv = {
        "Excellent": "Mycket bra läge",
        "Good": "Bra läge",
        "Okay": "Okej läge",
        "Low": "Låg snapshot",
        "Recovery needed": "Återhämtning behövs",
        "Poor sleep": "Svag sömn",
        "Unknown": "Okänt läge",
    }.get(status, status)
    parts = [f"{status_sv}: overall {round(overall)}%."]
    if recovery is not None:
        parts.append(f"Recovery {round(recovery)}%")
    if sleep is not None and total_sleep is not None and sleep_need is not None:
        parts.append(f"sömn {round(total_sleep)}/{round(sleep_need)} min")
    parts.append(f"HRV: {hrv_status.lower()}")
    if activity is not None:
        parts.append(f"aktivitet {round(activity)}%")
    if body is not None:
        parts.append(f"body {round(body)}%")
    if training_status:
        parts.append(f"status {training_status}")
    return " · ".join(parts) + "."


def data_quality(values: list[float | None]) -> int:
    if not values:
        return 0
    return int(round(len([value for value in values if value is not None]) / len(values) * 100))
