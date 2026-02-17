---
title: List Datapoint Access Events by date range
url: https://docs.daloopa.com/reference/list_datapoint_access_events-1
path: /reference/list_datapoint_access_events-1
---

# List Datapoint Access Events by date range

# List Datapoint Access Events by date range

Ask AI

get

https://app.daloopa.com/api/v2/consumption/events

Return the individual datapoint access events for the authenticated user within a date window.

**Inputs**

  * `start_at` and `end_at` are **dates** (`YYYY-MM-DD`).
  * Internally, `start_at` expands to the start of that day in the current Django timezone; `end_at` expands to the end of that day in the current Django timezone.



**Defaults**

  * If `start_at` is omitted, it defaults to the **first day of the current month** at 00:00:00 (current timezone).
  * If `end_at` is omitted, it defaults to **now** (current datetime in the current timezone).



**Behavior**

  * The window is **inclusive** : `start_at ≤ timestamp ≤ end_at`.
  * Results are ordered by `timestamp` ascending.



**Response**

  * A paginated list of datapoint access events.



