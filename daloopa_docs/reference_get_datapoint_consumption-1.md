---
title: Get Datapoint Consumption by date range
url: https://docs.daloopa.com/reference/get_datapoint_consumption-1
path: /reference/get_datapoint_consumption-1
---

# Get Datapoint Consumption by date range

# Get Datapoint Consumption by date range

Ask AI

get

https://app.daloopa.com/api/v2/consumption

Return the user's datapoint consumption within a date window and the user's effective monthly datapoint limit.

**Inputs**

  * `start_at` and `end_at` are both dates (in format `YYYY-MM-DD`).
  * Internally, `start_at` is expanded to the start of the day of that date in the current Django timezone; `end_at` is expanded to the end of the day of that date in the current Django timezone.



**Defaults**

  * If `start_at` is omitted, it defaults to the first day of the current month at 00:00:00 (current timezone).
  * If `end_at` is omitted, it defaults to now (the current datetime in the current timezone).



**Behavior**

  * The window is inclusive: `start_at ≤ timestamp ≤ end_at`.



**Response**

  * `monthly_limit` (string): `'Unlimited'` if there is no limit for the user, the numeric limit as a string otherwise.
  * `consumption` (integer): total datapoints accessed in the window.
  * `initial_date` / `final_date` (date): the date components of the resolved `start_at` and `end_at` values for the windows



