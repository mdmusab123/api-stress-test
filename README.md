# API Stress Test — Locust Load Testing Suite

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Locust](https://img.shields.io/badge/Locust-Load%20Testing-00A86B?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

A configurable API load testing suite built with [Locust](https://locust.io/). Designed to benchmark REST APIs under realistic traffic conditions — with zero hardcoded configuration. All settings (host, API key, endpoints, payload size, wait times) are controlled via the Locust Web UI or CLI flags, making it easy to reuse across different projects and environments.

---

## What This Does

Most load testing scripts are throwaway — hardcoded URLs, fixed user counts, no flexibility. This one is built to be reused:

- **No code changes needed** to test a different API — just change the host in the UI
- **Three task types** with weighted distribution to simulate real-world traffic patterns
- **Dynamic payloads** (small / medium / large) to test how a server handles JSON parsing under load
- **Cache-busting** on GET requests so CDN/edge caches don't skew results
- **Custom failure logic** — treats expected 404s as success so they don't pollute your crash stats
- **10-second SLA threshold** — any request taking longer is automatically marked as a failure

---

## How It Works

```
Locust spawns N virtual users
        ↓
Each user runs tasks based on weighted distribution:
  POST /primary   → 5x  (core write traffic)
  GET  /secondary → 3x  (data fetching / polling)
  POST /tertiary  → 1x  (infrequent edge actions)
        ↓
Results stream to Web UI in real time
(RPS, latency percentiles, failure rate)
```

---

## Quick Start

**1. Install Locust**
```bash
pip install locust
```

**2. Run with Web UI**
```bash
locust -f locustfile.py
```
Open [http://localhost:8089](http://localhost:8089) in your browser.

Fill in the form:
- **Host** — your target API base URL (e.g. `https://api.example.com`)
- **Number of users** — concurrent virtual users to simulate
- **Spawn rate** — users added per second
- **API Key** — passed as `X-API-KEY` header (marked secret, not logged)
- **Payload size** — `small`, `medium` (~1KB metadata), or `large` (~10KB + bulk array)

**3. Run Headless (CLI / CI pipeline)**
```bash
locust -f locustfile.py \
  --headless \
  -u 500 \
  -r 50 \
  --run-time 5m \
  --host https://api.example.com \
  --api-key YOUR_SECRET_KEY \
  --payload-size large
```

**4. Run Specific Task Types Only**
```bash
# Test only read endpoints (GET requests)
locust -f locustfile.py --tags read

# Test only write endpoints (POST requests)
locust -f locustfile.py --tags write

# Test only core traffic (excludes edge cases)
locust -f locustfile.py --tags core
```

---

## Task Breakdown

| Task | Method | Weight | Tags | Purpose |
|------|--------|--------|------|---------|
| `test_primary_post_endpoint` | POST | 5 | `core, post, write` | Simulates heavy write traffic |
| `test_secondary_get_endpoint` | GET | 3 | `core, get, read` | Simulates data fetching / polling |
| `test_tertiary_post_endpoint` | POST | 1 | `edge, post` | Simulates infrequent complex actions |

Weight `5:3:1` means for every 9 requests, 5 go to the primary endpoint, 3 to secondary, 1 to tertiary — a realistic distribution for most SaaS APIs.

---

## Reading the Results

While the test runs, focus on these metrics in the Locust UI:

| Metric | What it means | Warning threshold |
|--------|--------------|-------------------|
| **95th percentile (ms)** | 95% of requests finish within this time | > 1000ms = server struggling |
| **Failures/s** | Requests returning unexpected errors | Any spike = investigate |
| **RPS** | Requests per second the server handles | Drops under load = bottleneck |

**Common failure patterns:**
- `502 Bad Gateway` — app server crashed, proxy returning error
- `504 Gateway Timeout` — request queue backed up
- `401 Unauthorized` — API key not passed correctly
- `Timeout SLA Breached (>10s)` — custom threshold, server too slow

---

## Project Structure

```
api-stress-test/
├── locustfile.py    # Main test file — all logic lives here
└── README.md
```

---

## Key Implementation Details

**Dynamic wait time** — instead of a fixed `between(1, 3)`, wait time reads from UI input at runtime so you can simulate both casual users and aggressive traffic without restarting.

**Cache busting** — GET requests append a random `?cb=` query parameter to prevent CDN/edge caches from returning cached responses, ensuring each request actually hits the origin server.

**Smart failure handling** — a `404` on a randomly generated resource ID is a valid business response, not a server crash. Marking it as success keeps failure stats meaningful and focused on real errors.

**Event hook logging** — a global `request` event listener logs full tracebacks on failures, which is critical when running in headless/CI mode where you can't see the UI.

---

## Author

**Musab Ahmed**
- GitHub: [@mdmusab123](https://github.com/mdmusab123)
- Email: mdmusab207@gmail.com

---

## Disclaimer

Only use this tool against servers you own or have explicit written permission to test. High-concurrency load testing mimics DDoS behavior and can take down production environments or trigger automated security blocks.

---

## License

MIT License
