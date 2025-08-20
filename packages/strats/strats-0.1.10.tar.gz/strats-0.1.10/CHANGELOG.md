# Changelog

## 0.1.10

Released 2025-08-19

- Features
  - Add /livez, /readyz endpoint
  - Return ASGI app, not serve the app
  - Add runserver command in CLI
  - Update logging system
- Fix
  - Fix Metrics implementation, now user can handle registry

## 0.1.9

Released 2025-08-04

- Features
  - Make dedup-check configurable
  - add `started_at` and `details` for Strategy and Monitor
- Refactoring
  - Silence access log to `/metrics`
  - make `cron_job` function asyncronous

## 0.1.8

Released 2025-07-22

- Refactoring
  - Remove prepare method in Strategy, and pass State as an argument
  - Fix the name handling in Monitor class
  - Give initial Data instance, not Data class
  - Remove unnecessary id function for `source_to_data` in E2E tests

## 0.1.7

Released 2025-07-19

- Features
  - Remove ClockMonitor and improve CronMonitor using croniter
  - Refactor Monitors
  - Embed clock in strats kernel and update API & CLI
- Test
  - Refactor E2E test using conftest.py
  - Re-design E2E test directory, filename and function name
- Misc
  - Add CONTRIBUTING.md

## 0.1.6

Released 2025-05-04

- Rename util module to internal module
- Re-create util module
- Add Unix Domain Socket Clock server & client for backtest
- Move exchange.StreamClient to monitor.StreamClient

## 0.1.5

Released 2025-05-02

- Add monitor's name, again
- Add `start_delay_seconds` in StreamMonitor
- Add CronMonitor
- Wrap Strategy and Monitors by global error handler
- Define QueueMsg type and dedup them
- Give state to Strategy as its member
- Delete `source_class` from Data descriptor
- Flush queue before Strategy starts
- Add an argument `current_data` for `source_to_data` function

## 0.1.4

Released 2025-04-15

- Fix signal handling
- Update Monitor IF
- Improve log readability
- Use cancel method instead of stop event

## 0.1.3

Released 2025-04-11

- Command Line Tool

## 0.1.2

Released 2025-04-10

- Make Srategy, State and Monitors optional
- Enhance PyPI project details
- E2E Test

## 0.1.1

Released 2025-04-05

- Set up CI using GitHub Actions:
  - Run tests
  - Publish to PyPI

## 0.1.0

Released 2025-04-02

- Core Components (Kernel, Data descriptor, State)
- REST API
- StreamMonitor
- Prices, Clock models
- Backtest Exchange for clock handling
- Example usage code
- Project Settings (tox, mypy, ruff)
