# Changelog

## 2026.10.0b3

- Add a complete premium BodyFit dashboard card.
- Use native Statistic cards for rolling 30-day and 90-day changes, avoiding eight extra helper entities.
- Add 30-day daily and 12-month monthly BodyFit trend graphs.
- Keep the BodyFit instrument-change boundary clean by using only the new proxy entities.
- Keep `beta` on verified `2026.10.0b2` until the dashboard is tested.

## 2026.10.0b2

- Make BodyFit proxy sensors event-driven instead of waiting for the 15-minute platform poll.
- Refresh BodyFit values immediately whenever the corresponding Withings source entity changes.
- Track both weight and hydration changes for the derived body-water percentage sensor.
- Fix BodyFit entities remaining `unknown` after startup when Withings data arrived after Health Snapshot initialized.

## 2026.10.0b1

- Add BodyFit-only proxy sensors for clean post-migration long-term statistics.
- Add derived BodyFit body-water percentage sensor.
- Preserve existing Health Snapshot scoring and summary sensors.
- Document the strict release flow: `dev → beta → main`.
- Keep rolling change calculations in Home Assistant's native Statistics helper rather than YAML packages or custom recorder code.

