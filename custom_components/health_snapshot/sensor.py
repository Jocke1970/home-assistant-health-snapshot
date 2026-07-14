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

    # Garmin readiness / recovery
    training_readiness = f(hass, "sensor.garmin_connect_training_readiness")
    morning_readiness = f(hass, "sensor.garmin_connect_morning_training_readiness")
    recovery_time_h = f(hass, "sensor.garmin_connect_recovery_time")
    training_status = text(hass, "sensor.garmin_connect_training_status")

    # Garmin Body Battery / HR / stress, using fallback names from different integration versions.
    body_battery = f_any(hass, ["sensor.body_battery_most_recent", "sensor.garmin_connect_body_battery"])
    body_battery_highest = f_any(hass, ["sensor.body_battery_highest", "sensor.garmin_connect_body_battery_highest"])
    body_battery_lowest = f_any(hass, ["sensor.body_battery_lowest", "sensor.garmin_connect_body_battery_lowest"])
    body_battery_charged = f_any(hass, ["sensor.body_battery_charged", "sensor.garmin_connect_body_battery_charged"])
    body_battery_drained = f_any(hass, ["sensor.body_battery_drained", "sensor.garmin_connect_body_battery_drained"])

    resting_heart_rate = f_any(hass, ["sensor.resting_heart_rate", "sensor.garmin_connect_resting_heart_rate"])
    avg_7d_resting_heart_rate = f_any(hass, ["sensor.last_7_days_avg_heart_rate", "sensor.garmin_connect_7_day_average_resting_heart_rate"])
    max_heart_rate = f_any(hass, ["sensor.max_heart_rate", "sensor.garmin_connect_max_heart_rate"])
    min_heart_rate = f_any(hass, ["sensor.min_heart_rate", "sensor.garmin_connect_min_heart_rate"])

    stress_level = f_any(hass, ["sensor.avg_stress_level", "sensor.garmin_connect_average_stress_level"])
    max_stress_level = f_any(hass, ["sensor.max_stress_level", "sensor.garmin_connect_max_stress_level"])
    stress_percentage = f_any(hass, ["sensor.stress_percentage", "sensor.garmin_connect_stress_percentage"])
    high_stress_percentage = f_any(hass, ["sensor.high_stress_percentage", "sensor.garmin_connect_high_stress_percentage"])
    stress_qualifier = text_any(hass, ["sensor.stress_qualifier", "sensor.garmin_connect_stress_qualifier"])
    stress_score = calc_stress_score(stress_level)

    # Garmin sleep
    sleep_need = f(hass, "sensor.garmin_connect_sleep_need")
    deep = f(hass, "sensor.garmin_connect_deep_sleep")
    light = f(hass, "sensor.garmin_connect_light_sleep")
    rem = f(hass, "sensor.garmin_connect_rem_sleep")
    awake = f(hass, "sensor.garmin_connect_awake_time")
    nap = f(hass, "sensor.garmin_connect_nap_time")
    total_sleep = sum_known([deep, light, rem])

    # Garmin SpO2, using names exposed by the Garmin integration.
    average_spo2 = f_any(hass, ["sensor.average_spo2", "sensor.garmin_connect_average_spo2"])
    latest_spo2 = f_any(hass, ["sensor.latest_spo2", "sensor.garmin_connect_latest_spo2"])
    latest_spo2_time = text_any(hass, ["sensor.latest_spo2_time", "sensor.garmin_connect_latest_spo2_time"])
    lowest_spo2 = f_any(hass, ["sensor.lowest_spo2", "sensor.garmin_connect_lowest_spo2"])
    oxygen_score = calc_oxygen_score(average_spo2, lowest_spo2)
    oxygen_status = calc_oxygen_status(average_spo2, lowest_spo2)

    # Garmin HRV / fitness / hydration / blood pressure
    hrv_weekly = f(hass, "sensor.garmin_connect_hrv_weekly_average")
    hrv_last = f(hass, "sensor.garmin_connect_hrv_last_night_average")
    hrv_high = f(hass, "sensor.garmin_connect_hrv_last_night_5_min_high")
    hrv_base = f(hass, "sensor.garmin_connect_hrv_baseline")

    vo2_max = f(hass, "sensor.garmin_connect_vo2_max")
    endurance_score = f(hass, "sensor.garmin_connect_endurance_score")
    chronological_age = f(hass, "sensor.garmin_connect_chronological_age")
    fitness_age = f(hass, "sensor.garmin_connect_fitness_age")
    achievable_fitness_age = f(hass, "sensor.garmin_connect_achievable_fitness_age")
    previous_fitness_age = f(hass, "sensor.garmin_connect_previous_fitness_age")
    fitness_age_delta = diff_or_none(chronological_age, fitness_age)

    hydration = f(hass, "sensor.garmin_connect_hydration")
    hydration_goal = f(hass, "sensor.garmin_connect_hydration_goal")
    hydration_sweat_loss = f(hass, "sensor.garmin_connect_hydration_sweat_loss")
    hydration_score = calc_hydration_score(hydration, hydration_goal)

    bp_systolic = f(hass, "sensor.garmin_connect_blood_pressure_systolic")
    bp_diastolic = f(hass, "sensor.garmin_connect_blood_pressure_diastolic")
    bp_pulse = f(hass, "sensor.garmin_connect_blood_pressure_pulse")
    bp_category = text(hass, "sensor.garmin_connect_blood_pressure_category")
    bp_measurement_time = text(hass, "sensor.garmin_connect_blood_pressure_measurement_time")
    bp_score = calc_blood_pressure_score(bp_systolic, bp_diastolic, bp_category)

    # Garmin activity
    yesterday_steps = f(hass, "sensor.garmin_connect_yesterday_steps")
    weekly_steps = f(hass, "sensor.garmin_connect_weekly_step_average")
    intensity = f(hass, "sensor.garmin_connect_intensity_minutes")
    yesterday_distance = f(hass, "sensor.garmin_connect_yesterday_distance")
    weekly_distance = f(hass, "sensor.garmin_connect_weekly_distance_average")
    power_to_weight = f(hass, "sensor.garmin_connect_power_to_weight_cycling")
    ftp_cycling = f(hass, "sensor.garmin_connect_ftp_cycling")

    # Withings body metrics
    weight = f(hass, "sensor.withings_vikt")
    weight_goal = f(hass, "sensor.withings_viktmal")
    fat = f(hass, "sensor.withings_fettforhallande")
    visceral = f(hass, "sensor.withings_visceral_fat_index")
    pwv = f(hass, "sensor.withings_pulsvagens_hastighet")
    vascular_age = f(hass, "sensor.withings_vaskular_alder")
    withings_pulse = f(hass, "sensor.withings_hjartpuls")
    step_goal = f(hass, "sensor.withings_stegmal") or 5000

    sleep_score = calc_sleep_score(total_sleep, sleep_need, awake, lowest_spo2)
    hrv_score = calc_hrv_score(hrv_last, hrv_base)
    readiness = first([morning_readiness, training_readiness])
    recovery_time_score = calc_recovery_time_score(recovery_time_h)

    recovery_score = avg([
        (body_battery, 0.22),
        (readiness, 0.22),
        (sleep_score, 0.17),
        (hrv_score, 0.13),
        (stress_score, 0.10),
        (oxygen_score, 0.07),
        (recovery_time_score, 0.06),
        (hydration_score, 0.03),
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

    body_score = calc_body_score(
        weight,
        weight_goal,
        fat,
        visceral,
        pwv,
        vascular_age,
        bp_score,
        hydration_score,
    )

    overall_score = avg([(recovery_score, 0.48), (activity_score, 0.27), (body_score, 0.25)])
    hrv_status = calc_hrv_status(hrv_last, hrv_base)
    status = calc_status(overall_score, recovery_score, sleep_score, hrv_score, recovery_time_h, oxygen_score, bp_score)
    summary = build_summary(
        status,
        overall_score,
        recovery_score,
        activity_score,
        body_score,
        sleep_score,
        total_sleep,
        sleep_need,
        hrv_status,
        training_status,
        lowest_spo2,
        oxygen_status,
        body_battery,
        stress_level,
        bp_systolic,
        bp_diastolic,
        hydration_score,
    )

    attributes = {
        "body_battery": r(body_battery),
        "body_battery_highest": r(body_battery_highest),
        "body_battery_lowest": r(body_battery_lowest),
        "body_battery_charged": r(body_battery_charged),
        "body_battery_drained": r(body_battery_drained),
        "training_readiness": r(training_readiness),
        "morning_training_readiness": r(morning_readiness),
        "recovery_time_h": r(recovery_time_h, 1),
        "training_status": training_status,
        "sleep_score": r(sleep_score),
        "sleep_score_source": "calculated_from_sleep_need_spo2_adjusted",
        "sleep_need_min": r(sleep_need),
        "total_sleep_min": r(total_sleep),
        "deep_sleep_min": r(deep),
        "light_sleep_min": r(light),
        "rem_sleep_min": r(rem),
        "awake_time_min": r(awake),
        "nap_time_min": r(nap),
        "oxygen_score": r(oxygen_score),
        "oxygen_status": oxygen_status,
        "average_spo2": r(average_spo2, 1),
        "latest_spo2": r(latest_spo2, 1),
        "latest_spo2_time": latest_spo2_time,
        "lowest_spo2": r(lowest_spo2, 1),
        "hrv_status": hrv_status,
        "hrv_weekly_average_ms": r(hrv_weekly),
        "hrv_last_night_ms": r(hrv_last),
        "hrv_last_night_5_min_high_ms": r(hrv_high),
        "hrv_baseline_ms": r(hrv_base),
        "resting_heart_rate": r(resting_heart_rate),
        "avg_7d_resting_heart_rate": r(avg_7d_resting_heart_rate),
        "max_heart_rate": r(max_heart_rate),
        "min_heart_rate": r(min_heart_rate),
        "stress_level": r(stress_level),
        "max_stress_level": r(max_stress_level),
        "stress_score": r(stress_score),
        "stress_percentage": r(stress_percentage, 1),
        "high_stress_percentage": r(high_stress_percentage, 1),
        "stress_qualifier": stress_qualifier,
        "hydration": r(hydration),
        "hydration_goal": r(hydration_goal),
        "hydration_sweat_loss": r(hydration_sweat_loss),
        "hydration_score": r(hydration_score),
        "blood_pressure_systolic": r(bp_systolic),
        "blood_pressure_diastolic": r(bp_diastolic),
        "blood_pressure_pulse": r(bp_pulse),
        "blood_pressure_category": bp_category,
        "blood_pressure_measurement_time": bp_measurement_time,
        "blood_pressure_score": r(bp_score),
        "vo2_max": r(vo2_max, 1),
        "endurance_score": r(endurance_score),
        "chronological_age": r(chronological_age, 1),
        "fitness_age": r(fitness_age, 1),
        "achievable_fitness_age": r(achievable_fitness_age, 1),
        "previous_fitness_age": r(previous_fitness_age, 1),
        "fitness_age_delta": r(fitness_age_delta, 1),
        "yesterday_steps": r(yesterday_steps),
        "weekly_step_average": r(weekly_steps),
        "yesterday_distance_m": r(yesterday_distance),
        "weekly_distance_average_m": r(weekly_distance),
        "intensity_minutes": r(intensity),
        "power_to_weight_cycling": r(power_to_weight, 2),
        "ftp_cycling": r(ftp_cycling),
        "withings_weight": r(weight, 1),
        "withings_fat_percentage": r(fat, 1),
        "withings_visceral_fat": r(visceral, 1),
        "withings_pwv": r(pwv, 2),
        "withings_vascular_age": r(vascular_age, 1),
        "withings_heart_pulse": r(withings_pulse),
        "data_quality": data_quality([
            training_readiness, morning_readiness, recovery_time_h, body_battery,
            resting_heart_rate, stress_level, sleep_need, total_sleep, average_spo2,
            latest_spo2, lowest_spo2, hrv_last, hrv_base, yesterday_steps,
            weekly_steps, weight, fat, visceral, pwv, vascular_age, bp_systolic,
            bp_diastolic, hydration, hydration_goal, vo2_max, fitness_age,
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


def f_any(hass: HomeAssistant, entity_ids: list[str]) -> float | None:
    for entity_id in entity_ids:
        value = f(hass, entity_id)
        if value is not None:
            return value
    return None


def text(hass: HomeAssistant, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in INVALID:
        return None
    return str(state.state)


def text_any(hass: HomeAssistant, entity_ids: list[str]) -> str | None:
    for entity_id in entity_ids:
        value = text(hass, entity_id)
        if value is not None:
            return value
    return None


def first(values: list[float | None]) -> float | None:
    return next((value for value in values if value is not None), None)


def sum_known(values: list[float | None]) -> float | None:
    known = [value for value in values if value is not None]
    return sum(known) if known else None


def diff_or_none(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return a - b


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


def calc_sleep_score(total_sleep: float | None, sleep_need: float | None, awake: float | None, lowest_spo2: float | None) -> float | None:
    if total_sleep is None or sleep_need is None or sleep_need <= 0:
        return None
    score = clamp((total_sleep / sleep_need) * 100)
    if awake is not None and awake > 45:
        score -= 10
    elif awake is not None and awake > 25:
        score -= 5
    if lowest_spo2 is not None:
        if lowest_spo2 < 88:
            score -= 15
        elif lowest_spo2 < 90:
            score -= 10
        elif lowest_spo2 < 92:
            score -= 5
    return clamp(score)


def calc_oxygen_score(average_spo2: float | None, lowest_spo2: float | None) -> float | None:
    scores = []
    if average_spo2 is not None:
        if average_spo2 >= 96:
            scores.append((95, 0.55))
        elif average_spo2 >= 94:
            scores.append((84, 0.55))
        elif average_spo2 >= 92:
            scores.append((68, 0.55))
        elif average_spo2 >= 90:
            scores.append((52, 0.55))
        else:
            scores.append((35, 0.55))
    if lowest_spo2 is not None:
        if lowest_spo2 >= 94:
            scores.append((94, 0.45))
        elif lowest_spo2 >= 92:
            scores.append((82, 0.45))
        elif lowest_spo2 >= 90:
            scores.append((66, 0.45))
        elif lowest_spo2 >= 88:
            scores.append((48, 0.45))
        else:
            scores.append((30, 0.45))
    return avg(scores)


def calc_oxygen_status(average_spo2: float | None, lowest_spo2: float | None) -> str:
    if average_spo2 is None and lowest_spo2 is None:
        return "Saknas"
    if lowest_spo2 is not None and lowest_spo2 < 90:
        return "Låg lägstanivå"
    if average_spo2 is not None and average_spo2 < 92:
        return "Låg snittnivå"
    if lowest_spo2 is not None and lowest_spo2 < 92:
        return "Något låg lägstanivå"
    if average_spo2 is not None and average_spo2 >= 96:
        return "Bra"
    return "Okej"


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


def calc_stress_score(stress_level: float | None) -> float | None:
    if stress_level is None:
        return None
    if stress_level <= 15:
        return 94
    if stress_level <= 25:
        return 84
    if stress_level <= 35:
        return 70
    if stress_level <= 50:
        return 52
    return 35


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


def calc_hydration_score(hydration: float | None, goal: float | None) -> float | None:
    if hydration is None or goal is None or goal <= 0:
        return None
    return clamp((hydration / goal) * 100)


def calc_blood_pressure_score(systolic: float | None, diastolic: float | None, category: str | None) -> float | None:
    if category:
        category_upper = category.upper()
        if "NORMAL" in category_upper:
            return 92
        if "ELEVATED" in category_upper:
            return 76
        if "HIGH" in category_upper or "HYPERTENSION" in category_upper:
            return 55
        if "LOW" in category_upper:
            return 65
    if systolic is None or diastolic is None:
        return None
    if systolic < 120 and diastolic < 80:
        return 92
    if systolic < 130 and diastolic < 80:
        return 76
    if systolic < 140 or diastolic < 90:
        return 62
    return 45


def calc_activity_score(steps, weekly_steps, step_goal, intensity, distance, weekly_distance, training_status) -> float | None:
    step_score = clamp((steps / step_goal) * 100) if steps is not None and step_goal else None
    trend_score = clamp((steps / weekly_steps) * 85) if steps is not None and weekly_steps else None
    intensity_score = clamp((intensity / 30) * 100) if intensity is not None else None
    distance_score = clamp((distance / weekly_distance) * 85) if distance is not None and weekly_distance else None
    score = avg([(step_score, 0.48), (trend_score, 0.22), (intensity_score, 0.15), (distance_score, 0.15)])
    if score is None:
        return None
    if training_status:
        status = training_status.lower()
        if "detraining" in status:
            score -= 6
        elif "productive" in status:
            score += 5
        elif "peaking" in status:
            score += 4
        elif "strained" in status:
            score -= 8
    return clamp(score)


def calc_body_score(weight, goal, fat, visceral, pwv, vascular_age, bp_score, hydration_score) -> float | None:
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
    return avg([
        (weight_score, 0.18),
        (fat_score, 0.22),
        (visceral_score, 0.22),
        (pwv_score, 0.12),
        (vascular_score, 0.12),
        (bp_score, 0.09),
        (hydration_score, 0.05),
    ])


def calc_status(overall, recovery, sleep, hrv, recovery_time, oxygen, bp_score) -> str:
    if overall is None:
        return "Unknown"
    if sleep is not None and sleep < 55:
        return "Poor sleep"
    if oxygen is not None and oxygen < 50:
        return "Recovery needed"
    if recovery is not None and recovery < 50:
        return "Recovery needed"
    if hrv is not None and hrv < 50:
        return "Recovery needed"
    if recovery_time is not None and recovery_time >= 36:
        return "Recovery needed"
    if bp_score is not None and bp_score < 55:
        return "Low"
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


def build_summary(status, overall, recovery, activity, body, sleep, total_sleep, sleep_need, hrv_status, training_status, lowest_spo2, oxygen_status, body_battery, stress_level, bp_systolic, bp_diastolic, hydration_score) -> str:
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
    if body_battery is not None:
        parts.append(f"Body Battery {round(body_battery)}%")
    if stress_level is not None:
        parts.append(f"stress {round(stress_level)}")
    if sleep is not None and total_sleep is not None and sleep_need is not None:
        parts.append(f"sömn {round(total_sleep)}/{round(sleep_need)} min")
    parts.append(f"HRV: {hrv_status.lower()}")
    if lowest_spo2 is not None:
        parts.append(f"SpO2 lägst {round(lowest_spo2)}% ({oxygen_status.lower()})")
    if bp_systolic is not None and bp_diastolic is not None:
        parts.append(f"BT {round(bp_systolic)}/{round(bp_diastolic)}")
    if hydration_score is not None:
        parts.append(f"hydrering {round(hydration_score)}%")
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
