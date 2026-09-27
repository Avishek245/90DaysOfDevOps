# Day 76 — OpenTelemetry and Alerting

Part of the #90DaysOfDevOps observability series. Environment: AWS EC2, Ubuntu 24.04, t2.micro (951 MB RAM, 2 GB swap), 8 Docker containers.

---

## 1. Understanding OpenTelemetry

**OpenTelemetry (OTel)** is a vendor-neutral, open-source framework for generating, collecting, and exporting telemetry data — metrics, logs, and traces. It is not a storage backend; it ships data to backends like Prometheus, Loki, Jaeger, or Tempo.

**OTel Collector** is a standalone service with a three-stage pipeline:
- **Receivers** — accept incoming data (OTLP, Prometheus, Jaeger formats)
- **Processors** — transform data in flight (batching, filtering, memory limiting, sampling)
- **Exporters** — send data onward to a backend (Prometheus, debug console, Jaeger)

**OTLP (OpenTelemetry Protocol)** is the standard wire format for telemetry, available over:
- gRPC — port `4317`
- HTTP — port `4318`

**Distributed traces** track a single request as it moves through multiple services. Each step is a **span**, and spans carry a trace ID, span ID, parent span ID, start time, duration, and attributes. Example: `User request → API Gateway (span 1) → Auth Service (span 2) → Database (span 3)`.

---

## 2. OpenTelemetry Collector Setup

### `otel-collector/otel-collector-config.yml`

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 5s
    limit_mib: 90
    spike_limit_mib: 20
  batch:

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  debug:
    verbosity: detailed

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
```

**Notes:**
- `memory_limiter` was added beyond the base assignment template. On a 951 MB t2.micro running 8 containers, the collector is also capped with a hard `mem_limit: 128m` in Docker Compose. Without `memory_limiter`, the collector doesn't self-regulate against that cap and can get ungracefully OOM-killed by the container runtime instead of shedding load gracefully. `limit_mib: 90` keeps it under the 128 MB hard limit with headroom.
- Metrics go to the Prometheus exporter on `8889` (scraped by Prometheus). Traces and logs go to the `debug` exporter (console output) — in production these would go to Jaeger/Tempo/Loki instead.

### `docker-compose.yml` — otel-collector service

```yaml
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: otel-collector
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus exporter
    volumes:
      - ./otel-collector/otel-collector-config.yml:/etc/otelcol-contrib/config.yaml
    mem_limit: 128m
    restart: unless-stopped
```

### `prometheus.yml` — scrape target added

```yaml
  - job_name: "otel-collector"
    static_configs:
      - targets: ["otel-collector:8889"]
```

### Memory footprint on startup

Checked with `docker stats --no-stream` right after bringing the collector up alongside the other 7 containers:

| Container | Memory used | Limit |
|---|---|---|
| otel-collector | 33.67 MiB | 128 MiB |
| promtail | 23.64 MiB | 128 MiB |
| loki | 73.61 MiB | 256 MiB |
| grafana | 192 MiB | 951.9 MiB |
| cadvisor | 54.38 MiB | 951.9 MiB |
| node-exporter | 13.91 MiB | 951.9 MiB |
| prometheus | 41.08 MiB | 951.9 MiB |
| notes-app | 18.43 MiB | 951.9 MiB |

System memory at the time: `951Mi total / 658Mi used / 293Mi available`. The collector started cleanly with no OOM kills or restart loops (`Everything is ready. Begin running and processing data.` in logs).

---

## 3. Test OTLP Traces and Metrics

### Trace sent via curl

```bash
curl -X POST http://localhost:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{
    "resourceSpans": [{
      "resource": { "attributes": [{ "key": "service.name", "value": { "stringValue": "my-test-service" } }] },
      "scopeSpans": [{
        "spans": [{
          "traceId": "5b8efff798038103d269b633813fc60c",
          "spanId": "eee19b7ec3c1b174",
          "name": "test-span",
          "kind": 1,
          "startTimeUnixNano": "1544712660000000000",
          "endTimeUnixNano": "1544712661000000000",
          "attributes": [
            { "key": "http.method", "value": { "stringValue": "GET" } },
            { "key": "http.status_code", "value": { "intValue": "200" } }
          ]
        }]
      }]
    }]
  }'
```

Response: `{"partialSuccess":{}}` (empty object = fully accepted).

Verified in collector debug output:

```
Name           : test-span
Kind           : Internal
Start time     : 2018-12-13 14:51:00 +0000 UTC
End time       : 2018-12-13 14:51:01 +0000 UTC
Attributes:
     -> http.method: Str(GET)
```

### Metric sent via curl

```bash
curl -X POST http://localhost:4318/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "resourceMetrics": [{
      "resource": { "attributes": [{ "key": "service.name", "value": { "stringValue": "my-test-service" } }] },
      "scopeMetrics": [{
        "metrics": [{
          "name": "test_requests_total",
          "sum": {
            "dataPoints": [{ "asInt": "42", "startTimeUnixNano": "1544712660000000000", "timeUnixNano": "1544712661000000000" }],
            "aggregationTemporality": 2,
            "isMonotonic": true
          }
        }]
      }]
    }]
  }'
```

Queried in Prometheus: `test_requests_total` → returned `42`, confirming the full path: **curl → OTLP receiver → Prometheus exporter → Prometheus scrape → query result.**

---

## 4. Prometheus Alerting Rules

### `alert-rules.yml`

```yaml
groups:
  - name: system-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage has been above 80% for more than 2 minutes. Current value: {{ $value }}%"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 85
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85%. Current value: {{ $value }}%"

      - alert: ContainerDown
        expr: absent(container_last_seen{image=~".*notes-app.*"})
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container is down"
          description: "The notes-app container has not been seen for over 1 minute"

      - alert: TargetDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Scrape target is down"
          description: "{{ $labels.job }} target {{ $labels.instance }} is unreachable"

      - alert: HighDiskUsage
        expr: (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space running low"
          description: "Root filesystem usage is above 90%. Current value: {{ $value }}%"
```

> **Note on `ContainerDown`:** the assignment template uses `container_last_seen{name="notes-app"}`. On this setup, cAdvisor is run with `--containerd-namespace=moby`, which makes it read containers via the containerd API rather than Docker's naming layer. As a result, the `name` label on cAdvisor-discovered containers is the raw container ID hash, not the friendly Docker name — so `name="notes-app"` never matches. Fixed by matching on the `image` label instead, which stays human-readable: `image=~".*notes-app.*"`. Confirmed directly on the cAdvisor metrics endpoint:
> ```
> curl -s http://localhost:8080/metrics | grep container_last_seen | grep notes
> ```
> returned a result keyed by `name="<container-id-hash>"` and `image="docker.io/trainwithshubham/notes-app:latest"` — confirming the label mismatch, not a missing/dead container.

### `prometheus.yml` — rule_files added

```yaml
rule_files:
  - /etc/prometheus/alert-rules.yml
```

### `docker-compose.yml` — Prometheus volume mount added

```yaml
  prometheus:
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert-rules.yml:/etc/prometheus/alert-rules.yml
      - prometheus_data:/prometheus
```

### Verified rule lifecycle

All 5 rules loaded and healthy (`Status → Rules`, all showing `OK`). On the Alerts page, observed the full state lifecycle without needing the assignment's manual "stop notes-app" test — a genuine issue (notes-app's `/metrics` endpoint returning 404) already triggered a real firing sequence:

- `HighCPUUsage`, `HighMemoryUsage`, `HighDiskUsage` → inactive (system healthy)
- `TargetDown` → **pending → firing** (notes-app `/metrics` scrape genuinely returns 404 — a real, pre-existing limitation of the notes-app image, not an OTel-related issue)
- `ContainerDown` → initially pending → firing due to the label mismatch above; resolved to **inactive** after the `image` label fix, since notes-app is actually running

**Screenshots:**
- Status → Rules: all 5 rules `OK`
- Alerts page: `PENDING (2)` state
- Alerts page: `FIRING (2)` state — `ContainerDown` and `TargetDown`

**Known limitation (documented, not fixed today):** the `notes-app` container image does not expose a Prometheus-compatible `/metrics` endpoint, so its dedicated scrape job in `prometheus.yml` will remain permanently down. This is unrelated to the OTel/alerting work and would require changes to the notes-app image itself.

---

## 5. Grafana Alerting

### Contact point

- Name: `DevOps Team`
- Integration: Email
- Address: configured to personal email

> SMTP is not configured in this Grafana instance's environment variables, so the contact point saves successfully but will not actually deliver email unless SMTP settings are added to the `grafana` service in `docker-compose.yml`. Sufficient for this assignment's scope (rule + contact point wiring), noted as a follow-up for real notification delivery.

### Alert rule: "High Container Memory"

- Folder: `observability-alerts`
- Evaluation group: `system-alerts-group`, every `1m`
- Query: `container_memory_usage_bytes{image=~".*notes-app.*"} / 1024 / 1024`
- Condition: **IS ABOVE** `100`
- Pending period: `2m`
- Label: `severity=warning`
- Contact point: `DevOps Team`

> Same cAdvisor `containerd-namespace` label issue as Task 4 applied here — original query used `name="notes-app"`, which returned `No data`. Fixed the same way, matching on `image` instead of `name`. After the fix, the rule evaluates cleanly, showing live memory usage (~17.1–17.4 MB), well under the 100 MB threshold, with state `Normal`.

**Screenshots:**
- New alert rule form, fully configured
- Rule detail page with live graph and `Normal` state after the label fix

### Prometheus alerts vs. Grafana alerts

| | Prometheus Alerting | Grafana Alerting |
|---|---|---|
| Where rules live | `alert-rules.yml`, version-controlled, PromQL only | UI-managed (or provisioned), can query multiple data sources |
| Data sources | Prometheus only | Prometheus, Loki, and any other configured data source |
| Notifications | Requires a separate Alertmanager to route/send notifications | Built-in contact points and notification policies — no extra component needed |
| Best for | Infrastructure-level rules tightly coupled to metrics already in Prometheus, GitOps-style rule management | Cross-source alerting (e.g., combining metrics + logs), quick setup without standing up Alertmanager |

**When to use each:** Prometheus alerting rules are a good fit when the whole team already manages Prometheus config as code and wants alert definitions to live next to the scrape config. Grafana alerting is simpler to get notifications working quickly (no Alertmanager needed) and is the better choice once alerts need to span multiple backends — e.g., a rule that correlates a Loki log pattern with a Prometheus metric.

---

## 6. Full Observability Architecture

```
                    METRICS PIPELINE
[Node Exporter] -----> [Prometheus] -----> [Grafana Dashboards]
[cAdvisor] ----------> [Prometheus] -----> [Grafana Dashboards]
[OTEL Collector:8889]> [Prometheus] -----> [Grafana Dashboards]
                                    -----> [Alert Rules -> Alerts Page]

                    LOGS PIPELINE
[Docker Containers] -> [Promtail] -> [Loki] -> [Grafana Explore/Dashboards]

                    TRACES PIPELINE
[curl/App OTLP] -----> [OTEL Collector] -> [Debug Output / Future: Jaeger/Tempo]

                    ALERTING
[Prometheus Rules] --> [Alerts UI] (no Alertmanager configured — UI only, no notifications)
[Grafana Rules] -----> [Contact Points] -> [Email (SMTP not yet configured)]
```

### Services running

| Service | Port | Purpose | Memory limit |
|---|---|---|---|
| Prometheus | 9090 | Metrics storage and querying | — |
| Node Exporter | 9100 | Host system metrics | — |
| cAdvisor | 8080 | Container metrics | — |
| Grafana | 3000 | Visualization and alerting | — |
| Loki | 3100 | Log storage | 256m |
| Promtail | 9080 | Log collection agent | 128m |
| OTEL Collector | 4317 / 4318 / 8889 | Telemetry collection | 128m |
| Notes App | 8000 | Sample application | — |

All 8 containers running (`docker compose ps`).

### Key learnings from today

1. **Resource-constrained OTel deployment:** on a t2.micro, the collector's `memory_limiter` processor paired with a Docker `mem_limit` prevents an ungraceful OOM kill under load — the collector sheds data gracefully instead of the container dying outright.
2. **cAdvisor label behavior with `--containerd-namespace=moby`:** container-identifying labels (`name`) on cAdvisor metrics can resolve to raw container ID hashes instead of Docker container names, depending on how cAdvisor discovers the container. The `image` label is more reliable for matching a specific service in PromQL when this is the case.
3. **A genuine failure is a better alert-firing demo than a synthetic one:** the `notes-app` `/metrics` 404 gave a real end-to-end proof of the `TargetDown` alert's full pending → firing lifecycle without needing to manually stop a container.

---

## Submission
![OTel collector config](<Screenshot (1182).png>)
![Prometheus targets page](<Screenshot (1183).png>)
![Prometheus test_requests_total metric](<Screenshot (1184).png>)
![Prometheus rules page](<Screenshot (1185).png>)
![Prometheus alert lifecycle](<Screenshot (1186).png>)
![Prometheus firing alerts](<Screenshot (1187).png>)
![Grafana alert rule normal state](<Screenshot (1194).png>)