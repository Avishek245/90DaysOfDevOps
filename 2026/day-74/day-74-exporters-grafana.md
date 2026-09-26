# Day 74 -- Node Exporter, cAdvisor, and Grafana Dashboards

## Task 1: Node Exporter for host metrics

Added Node Exporter as a container reading `/proc`, `/sys`, and `/` from the host (all read-only). It exposes host-level metrics under the `node_*` prefix.

### Updated prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "notes-app"
    static_configs:
      - targets: ["notes-app:8000"]

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
```

### docker-compose.yml (node-exporter service)
```yaml
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
```

### Queries run
| Query | Result |
|---|---|
| `node_memory_MemTotal_bytes` | 998,219,776 (~952 MiB) |
| `node_memory_MemAvailable_bytes` | 484,061,184 |
| `(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100` | 51.49% |
| `(1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100` (mountpoint `/`) | 38.16% |
| `rate(node_network_receive_bytes_total[5m])` | Only `eth0`/`lo`, no host interfaces |

**Note on network:** Node Exporter runs inside its own container network namespace, so `node_network_*` metrics only see the container's virtual interface, not the host's real NICs. CPU, memory and disk are genuinely host-level because `/proc`, `/sys` and `/` are bind-mounted directly; network is the one exception with this setup.

## Task 2: cAdvisor for container metrics

### docker-compose.yml (cadvisor service)
```yaml
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
```

### The Docker 29 problem
On first setup (using only the assignment's stock config, mounting `docker.sock` alone), cAdvisor's Docker factory failed to register:
```
Registration of the docker container factory failed: unable to create containerd client: containerd: cannot unix dial containerd api service: dial unix /run/containerd/containerd.sock: connect: no such file or directory
```
Docker 29 runs containers through containerd internally, so cAdvisor needs direct access to the **containerd socket**, not just `docker.sock`. Fixed by mounting `/run/containerd/containerd.sock` and adding `--containerd-namespace=moby` (Docker creates containers under the `moby` containerd namespace, not cAdvisor's default `k8s.io`). After the fix, the log showed: `Registration of the docker container factory successfully`.

### Container memory (topk)
| Container | Memory |
|---|---|
| cadvisor | 178.6 MB |
| prometheus | 66.6 MB |
| notes-app | 24.6 MB |
| node-exporter | 14.7 MB |

**Node Exporter vs cAdvisor:** Node Exporter reports on the **host machine** -- CPU, memory, disk, network at the OS level (`node_*` metrics). cAdvisor reports on **individual containers** -- CPU, memory, network per container (`container_*` metrics). Use Node Exporter to know if the server itself is under strain; use cAdvisor to know which container is causing it.

**Limitation found:** `container_network_receive_bytes_total` returns no data. cAdvisor reads a container's network stats by entering its namespace through the host's `/proc`, which isn't mounted into the cAdvisor container in this setup. CPU and memory work because those come from cgroups directly; network needs the extra mount, which conflicts with cAdvisor's own process view. This is a widely known limitation of this setup, not a misconfiguration.

## Task 3: Grafana setup

Deployed `grafana/grafana-enterprise:latest`, exposed on port 3000, logged in with `admin`/`admin123`. Added Prometheus as a datasource with URL `http://prometheus:9090` (the container name -- Grafana and Prometheus share the same Docker network, so `localhost` would point at Grafana's own container instead). Save & Test returned "Successfully queried the Prometheus API".

![Grafana dashboard after login](<Screenshot (1129).png>)

## Task 4: Custom dashboard -- "DevOps Observability Overview"

Five panels:
- **CPU Usage %** (Gauge) -- `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
- **Memory Usage %** (Gauge) -- `(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100`
- **Container CPU Usage** (Time series) -- `rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100`, legend `{{name}}`
- **Container Memory (MB)** (Bar chart) -- `container_memory_usage_bytes{name!=""} / 1024 / 1024`, legend `{{name}}`
- **Disk Usage %** (Stat) -- `(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100`

![Completed DevOps Observability Overview dashboard](<Screenshot (1130).png>)

## Task 5: Provisioning datasources via YAML

### grafana/provisioning/datasources/datasources.yml
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

### docker-compose.yml (grafana service, final)
```yaml
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
```

Mounted into the Grafana container at `/etc/grafana/provisioning`. After restarting Grafana, the Prometheus datasource appeared automatically, no manual clicking required. A duplicate datasource briefly appeared from an earlier manual add -- deleted it, keeping only the provisioned, default one.

**Why provision via YAML instead of the UI?** It's repeatable -- if the Grafana container is destroyed and recreated, the datasource comes back automatically instead of needing to be re-added by hand. It's version-controlled -- the config lives in a file in the repo, not hidden in a database. And it avoids drift -- a manually-added datasource and a provisioned one can silently duplicate or diverge, which is exactly what happened here until it was cleaned up.

## Task 6: Community dashboards

### 1860 -- Node Exporter Full
Imported via JSON (the ID-lookup field returned "Could not find a valid Grafana.com ID" from the browser -- worked around by downloading the JSON with `curl https://grafana.com/api/dashboards/1860/revisions/latest/download` and pasting it directly into the Import screen). Fully populated: CPU Busy 7.9%, RAM Used 61.8%, SWAP Used 24.1%, Root FS Used 51.1%, plus full CPU/Memory/Network/Disk time series.

![Grafana dashboard import with ID 1860](<Screenshot (1133).png>)
![Node Exporter Full dashboard](<Screenshot (1137).png>)

### 193 -- Docker monitoring via cAdvisor
Imported the same way. Several panels initially showed "No data" -- fixed most by editing their queries to add the `{name!=""}` filter this cAdvisor/Docker version needs, e.g.:
- Running containers: `count(container_last_seen{name!=""})`
- Total Memory Usage: `sum(container_memory_usage_bytes{name!=""})`
- Total CPU Usage: `sum(rate(container_cpu_usage_seconds_total{name!=""}[5m])) * 100`

Running Containers (6), Total Memory Usage (616 MiB), Total CPU Usage (3.64%), and the per-container CPU/Memory gauges all now work. Network Rx and Network Tx remain "No data" -- same `/proc` limitation noted in Task 2.

![Docker monitoring dashboard with corrected metrics](<Screenshot (1143).png>)

## Verifying all targets

`prometheus`, `node-exporter`, and `cadvisor` all show UP. `notes-app` remains DOWN, unchanged from Day 73 -- it's a plain Django demo app with no `/metrics` endpoint.

## Key learnings
- Docker 29's containerd-backed storage broke cAdvisor's default Docker detection; fixing it needed the containerd socket mount and the `moby` namespace flag, not just `docker.sock`.
- Node Exporter's network metrics are container-namespace-scoped unless run with `network_mode: host`, so CPU/memory/disk being "host-level" doesn't automatically mean network is too.
- Community dashboards can go stale -- older label conventions stop matching newer exporter versions, and fixing them is a matter of adjusting label filters, not rebuilding from scratch.
- Provisioning via YAML is what prevents the datasource duplication/drift problem I hit firsthand.
- On a 1 GB (t2.micro) instance, five containers plus Grafana push memory close to its limit -- adding 2 GB of swap kept the stack stable throughout.