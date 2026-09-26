# Day 75 — Log Management with Loki and Promtail

Environment: AWS EC2 (Ubuntu 24.04, t2.micro, 951 MB RAM + 2 GB swap), continuing the stack built on Day 73 (Prometheus) and Day 74 (Exporters + Grafana).

---

## 1. Architecture

```
[Docker Containers]
       |
       | write JSON logs to /var/lib/docker/containers/<id>/<id>-json.log
       v
  [Promtail]  --- discovers containers via Docker API (unix:///var/run/docker.sock)
       |          attaches labels: job, container, logstream
       | pushes to Loki over HTTP
       v
    [Loki]  --- indexes only labels; stores compressed log chunks on local disk
       |
       | queried via LogQL
       v
   [Grafana]  --- Explore + dashboard panel, Loki datasource
       |
       v
   [You]
```

### Why Loki indexes only labels, not full text

Elasticsearch-style engines (the "L" in ELK) build a full inverted index over every word in every log line. That gives powerful free-text search but is expensive to run — large index, high memory/CPU/disk cost, and real operational overhead (shard management, etc.).

Loki instead treats labels (`container`, `job`, `logstream`) the same way Prometheus treats metric labels: it builds a small index over just those, and stores the actual log content compressed in chunks on disk. A query uses labels to narrow down which chunks to look at, then scans the raw text within those chunks for anything like `|= "error"`.

**Trade-off:**
- Cheap to run — small index footprint, which matters a lot on a t2.micro with under 1 GB RAM.
- Operationally simple — no index management overhead.
- Free-text search without a label filter is slower, since it's a scan rather than an index lookup.
- Query performance depends on keeping label cardinality low. Container name and job are good labels; something like a request ID or user ID as a label would make Loki's index blow up the same way it would in Prometheus.

This is a deliberate "index less, scan more" trade that works well under tight resource constraints.

---

## 2. Configuration Files

### `loki/loki-config.yml`

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory
  replication_factor: 1
  path_prefix: /loki

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

storage_config:
  filesystem:
    directory: /loki/chunks

limits_config:
  retention_period: 168h
```

**Deviation from the base assignment:** added `limits_config.retention_period: 168h` (7 days). On a t2.micro with limited disk, unbounded log retention isn't practical — this caps it the same way Prometheus's `--storage.tsdb.retention.size=1GB` caps metrics storage.

- `auth_enabled: false` — single-tenant mode, no auth needed for this setup.
- `store: tsdb` — Loki's time-series index format.
- `object_store: filesystem` — log chunks stored on local disk rather than S3/GCS.
- `replication_factor: 1` — single instance, no replication (fine for a learning setup).

### `promtail/promtail-config.yml`

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'logstream'
    pipeline_stages:
      - docker: {}
```

**Deviation from the base assignment (important):** the assignment's original config uses a `static_configs` block with a file glob (`__path__: /var/lib/docker/containers/*/*-json.log`). That approach only parses the JSON log *content* (timestamp, stream, message) — it does **not** know which container each file belongs to, because the file path is just a container ID hash, not a name. Using that config, every log line only carried the labels `job=docker` and `service_name=docker`, with no way to filter by container.

Switched to **Docker service discovery** (`docker_sd_configs`) instead, which queries the Docker API directly for container metadata and lets `relabel_configs` turn `__meta_docker_container_name` into a clean `container` label (stripping the leading `/` Docker adds to container names), plus a `logstream` label for stdout/stderr. This is what makes `{container="notes-app"}`-style queries actually work.

- `positions` — bookmark file tracking which log lines have already been shipped.
- `clients` — Loki push endpoint.
- `docker_sd_configs` — service discovery against the Docker socket.
- `pipeline_stages: docker: {}` — parses the Docker JSON log wrapper to extract the real message.

---

## 3. Full `docker-compose.yml`

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
      - '--storage.tsdb.retention.size=1GB'
    restart: unless-stopped

  notes-app:
    image: trainwithshubham/notes-app:latest
    container_name: notes-app
    ports:
      - "8000:8000"
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /run/containerd/containerd.sock:/run/containerd/containerd.sock:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    command:
      - '--containerd-namespace=moby'
    restart: unless-stopped

  grafana:
    image: grafana/grafana-enterprise:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yml:/etc/loki/loki-config.yml
      - loki_data:/loki
    command: -config.file=/etc/loki/loki-config.yml
    restart: unless-stopped
    mem_limit: 256m

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    ports:
      - "9080:9080"
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/promtail-config.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: -config.file=/etc/promtail/promtail-config.yml
    restart: unless-stopped
    mem_limit: 128m

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

**Other deviations:**
- Added `mem_limit: 256m` (Loki) and `mem_limit: 128m` (Promtail) to keep both services bounded on a t2.micro (951 MB RAM, 2 GB swap). Neither hit an OOM kill during this session (`dmesg` checked clean).
- Mounted `/var/run/docker.sock` as `:ro` for Promtail, since it only needs to read container metadata.
- Exposed Promtail's port `9080:9080` explicitly (missed on the first pass — had to add it after finding the targets page unreachable both locally and via the EC2 security group).

### Grafana datasource provisioning — `grafana/provisioning/datasources/datasources.yml`

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
```

---

## 4. LogQL Queries Run

| # | Query | Result |
|---|-------|--------|
| 1 | `{job="docker"}` | All Docker container logs. ~1000 lines shown, 1.97K info / 494 unknown / 7 warning over the sampled window. |
| 2 | `{container="notes-app"}` | Filtered to notes-app only, once the Promtail relabeling fix landed. Common labels: `container=notes-app logstream=stderr service_name=notes-app`. |
| 3 | `{job="docker"} \|= "error"` | Keyword search. 22 error lines found — mostly from Grafana's own plugin API (`grafana-assistant-app`, unrelated to the observability stack itself). |
| 4 | `{job="docker"} != "health"` | Negative filter. 1480 lines shown, excluding anything containing "health". |
| 5 | `{job="docker"} \|~ "status=[45]\\d{2}"` | Regex for HTTP 4xx/5xx. Matched 6 error, 2 info, 1 warning lines. |
| 6 | `count_over_time({job="docker"}[5m])` | Count of log lines per 5-minute window, broken out per container/level. |
| 7 | `rate({job="docker"}[5m])` | Rate of log lines per second, clearly showing spikes matching test traffic bursts. |
| 8 | `topk(5, sum by (container) (rate({job="docker"}[5m])))` | Top log-volume containers — notes-app dominant during the test window. |

**Exercise — errors from notes-app in the last hour:**

```logql
{container="notes-app"} |= "error"
```

This returned **zero** matches. Notable finding: notes-app doesn't log the literal string "error" — its failed requests appear as HTTP access-log lines (`"GET /metrics HTTP/1.1" 404`) rather than an `error`-labeled message. Adjusted to match the app's actual log format:

```logql
{container="notes-app"} |= "404"
```

This matched 720 of 744 lines in the sampled window — largely repeated `GET /metrics` 404s, which is expected since notes-app has no `/metrics` endpoint (documented on Day 74).

**Exercise — error lines per minute:**

```logql
count_over_time({container="notes-app"} |= "404" [1m])
```

Returned a per-minute count series (e.g. 4 matching lines in the 16:47 minute during the sampled window).

**Takeaway for the doc:** keyword filters in LogQL only work if they match your application's actual log format — assuming a keyword like "error" exists is a common mistake; check real log output first.

---

## 5. Correlating Metrics and Logs

### Adding notes-app to metrics correlation — a labeling gotcha

cAdvisor labels containers by their raw hex container ID (`name="a009a8d5c87ad..."`), not by a human-readable name, which matches the `{name!=""}` filter workaround already noted from Day 74's dashboard 193 import. This meant the assignment's suggested query:

```promql
rate(container_cpu_usage_seconds_total{name="notes-app"}[5m])
```

returned **no data**. Debugged by querying Prometheus directly:

```bash
curl -sG 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=count by (name) (container_cpu_usage_seconds_total)'
```

This confirmed every `name` label was a raw container ID hash with no compose-service label attached (`container_label_com_docker_compose_service` wasn't present). The reliable, restart-safe alternative is filtering on the `image` label instead:

```promql
rate(container_cpu_usage_seconds_total{image=~".*notes-app.*"}[5m])
```

This is worth using for any per-container CPU/memory query going forward on this setup, since container IDs change on every recreate but the image name doesn't.

### Explore split view

Left pane (Prometheus): `rate(container_cpu_usage_seconds_total{image=~".*notes-app.*"}[5m])`
Right pane (Loki): `{container="notes-app"}`

Generated a burst of test traffic and observed a clear CPU spike in the left panel matched by a simultaneous log-volume spike in the right panel, in the same time window — confirming the correlation workflow: see a metric anomaly, immediately check logs from that exact moment.

### Dashboard panel

Added a "Container Logs" panel (Loki, query `{job="docker"}`, Logs visualization) to the existing "DevOps Observability Overview" dashboard from Day 74, alongside the CPU/Memory gauges, Container CPU/Memory time series, and Disk Usage panel — giving one screen with metrics and logs together.

**Known limitation carried over:** the Container CPU/Memory panel legends still show raw container ID hashes rather than names, same root cause as above (cAdvisor's default `name` label). Left as-is for this task, same category as the Day 74 Network Rx/Tx "No data" limitation — both are documented rather than fixed, since fixing them isn't required by the assignment.

### Why metrics + logs in one tool helps incident response

Compared to checking Prometheus/Grafana for metrics and a separate log viewer (or SSH + `docker logs`) for context, having both in Grafana means:
- One time range selection applies to both — no manually aligning timestamps across two different tools/timezones.
- Clicking a spike zooms both panels to that exact window, so cause (log errors) and effect (CPU/memory spike) are visible together without needing to remember or copy over a timestamp.
- Reduces context-switching during an actual incident, when speed matters and jumping between disconnected tools costs time and increases the chance of missing the relevant log lines.

---

## 6. Loki vs ELK — When to Use Each

| | Loki | ELK (Elasticsearch/Logstash/Kibana) |
|---|---|---|
| Indexing | Labels only | Full text, every field |
| Resource cost | Low — small index | High — large index, more CPU/RAM |
| Free-text search | Slower (scans chunks) | Fast (index lookup) |
| Operational complexity | Simple, few moving parts | Complex — shards, replicas, index lifecycle |
| Best fit | Cost-conscious setups, Kubernetes/container environments already using Prometheus-style labels, teams that mostly filter by known dimensions (service, pod, level) | Environments needing deep free-text search across unstructured logs, security/audit log analysis, larger teams/budgets that can run a heavier stack |

For this project — a single t2.micro instance already running Prometheus, Grafana, and several exporters — Loki was the only realistic option. Running Elasticsearch here likely wouldn't have fit in the available RAM.

---

![alt text](<Screenshot (1179).png>) ![alt text](<Screenshot (1154).png>) ![alt text](<Screenshot (1155).png>) ![alt text](<Screenshot (1156).png>) ![alt text](<Screenshot (1157).png>) ![alt text](<Screenshot (1158).png>) ![alt text](<Screenshot (1159).png>) ![alt text](<Screenshot (1160).png>) ![alt text](<Screenshot (1161).png>) ![alt text](<Screenshot (1162).png>) ![alt text](<Screenshot (1163).png>) ![alt text](<Screenshot (1164).png>) ![alt text](<Screenshot (1165).png>) ![alt text](<Screenshot (1166).png>) ![alt text](<Screenshot (1167).png>) ![alt text](<Screenshot (1168).png>) ![alt text](<Screenshot (1169).png>) ![alt text](<Screenshot (1170).png>) ![alt text](<Screenshot (1171).png>) ![alt text](<Screenshot (1172).png>) ![alt text](<Screenshot (1173).png>) ![alt text](<Screenshot (1174).png>) ![alt text](<Screenshot (1175).png>) ![alt text](<Screenshot (1176).png>) ![alt text](<Screenshot (1177).png>) ![alt text](<Screenshot (1178).png>)
