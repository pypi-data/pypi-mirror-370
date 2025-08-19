# Docker Prune CLI
# Docker Prune CLI  
**A flexible, safe, and automated CLI for cleaning unused Docker containers, images, volumes, and networks.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/t4skforce/docker-prune/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/docker-prune?color=blue&label=PyPI)](https://pypi.org/project/docker-prune/)
[![Docker Hub](https://img.shields.io/docker/pulls/t4skforce/docker-prune?logo=docker&label=Docker%20Hub)](https://hub.docker.com/r/t4skforce/docker-prune)
[![Docker Image Size](https://img.shields.io/docker/image-size/t4skforce/docker-prune/latest?logo=docker)](https://hub.docker.com/r/t4skforce/docker-prune/tags)
[![GHCR](https://img.shields.io/badge/GHCR-ghcr.io%2Ft4skforce%2Fdocker--prune-blue?logo=github)](https://ghcr.io/t4skforce/docker-prune)
[![Podman](https://img.shields.io/badge/Run%20with-Podman-892CA0?logo=podman)](https://podman.io/)
[![Rootless](https://img.shields.io/badge/Container-Rootless-brightgreen)](https://docs.docker.com/engine/security/rootless/)
[![Read-Only FS](https://img.shields.io/badge/Filesystem-Read--Only-lightgrey)](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user)

[![Profile: Conservative](https://img.shields.io/badge/Profile-Conservative-green)](https://github.com/t4skforce/blob/main/docker/config-conservative.yaml)
[![Profile: Default](https://img.shields.io/badge/Profile-Default-blue)](https://github.com/t4skforce/blob/main/docker/config-default.yaml)
[![Profile: Act](https://img.shields.io/badge/Profile-Act-orange)](https://github.com/t4skforce/blob/main/docker/config-act.yaml)
[![Profile: Aggressive](https://img.shields.io/badge/Profile-Aggressive-red)](https://github.com/t4skforce/blob/main/docker/config-aggressive.yaml)

`docker-prune` is a **powerful and flexible CLI tool** for managing and cleaning up unused Docker resources — including containers, images, volumes, and networks. Unlike basic `docker system prune`, this tool allows you to define **complex, fine‑grained cleanup rules** via filters, labels, regex patterns, and YAML configuration files.

This makes it ideal for:
- **Homelab environments** — keep your systems clean and healthy without manual intervention.
- **Production & CI/CD** — automate safe cleanup policies to prevent disk bloat.
- **Developers** — quickly reclaim space while keeping important resources intact.

With semantic versioned Docker images, built‑in cleanup profiles, and a cron‑based scheduler, `docker-prune` can run **fully automated** in the background, tailored to your needs — all inside a **rootless container** for improved security.

---

## Features

- **Container Management**: Stop and remove containers based on age, name, labels, and restart count.
- **Image Cleanup**: Remove unused images with filters for age, tags, and labels.
- **Volume Pruning**: Delete unused volumes with label-based filters and age-based rules.
- **Network Pruning**: Remove unused Docker networks, excluding built-in networks (`bridge`, `host`, `none`) and custom exclusions.
- **Detailed Storage Info**: View disk usage statistics for Docker images and volumes.
- **Configurable**: Load cleanup configurations via YAML files.
- **Rootless by Default**: The official Docker image runs as a non-root user (`app`) with configurable UID/GID for enhanced security.

---

## Installation

To install the `docker-prune` binary, run:

```bash
pip install docker-prune
```

This will make the `docker-prune` command available in your system's PATH.

---

## Using the Docker Image

In addition to installing via `pip`, you can run **docker-prune** directly from its published Docker image. Images are available from:

- **GitHub Container Registry (GHCR)**: `ghcr.io/t4skforce/docker-prune`
- **Docker Hub**: `t4skforce/docker-prune`


> **Security:** Runs as rootless `app` user by default (`UID=1000`, `GID=967`) for improved security.


### Pull Image
```bash
docker pull ghcr.io/t4skforce/docker-prune:latest
docker pull t4skforce/docker-prune:latest
```

### Version Tags

The images follow [Semantic Versioning (SemVer)](https://semver.org/) and multiple tags are published for each release:

| Tag example | Description |
|-------------|-------------|
| `latest`    | Always points to the latest stable release |
| `v1.0.4`    | Full SemVer – pinned to an exact release |
| `v1.0`      | Minor version – receives updates for all `v1.0.x` releases |
| `v1`        | Major version – receives updates for all `v1.x.x` releases |

This allows you to:
- **Track the latest release:** use `latest`
- **Stay on a major release line:** use `v1`
- **Stay on a specific minor line:** use `v1.0`
- **Pin to an exact release:** use `v1.0.4`

Examples:

```bash
# Always get latest v1.x.x release
docker pull ghcr.io/t4skforce/docker-prune:v1

# Pin to a specific version
docker pull t4skforce/docker-prune:v1.0.4
```

### Running the Container

Run `docker-prune` from the container:

```bash
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/t4skforce/docker-prune:latest --help
```

Run with a specific profile and schedule:

```bash
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_PRUNE_PROFILE=aggressive \
  -e DOCKER_PRUNE_SCHEDULE="0 */6 * * *" \
  t4skforce/docker-prune:v1
```

Run with a custom configuration file:

```bash
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /path/to/config.yml:/config/config.yml \
  -e DOCKER_PRUNE_CONFIG_FILE=/config/config.yml \
  ghcr.io/t4skforce/docker-prune:v1.0.4
```

---

### Using docker-compose for Scheduled Cleanup

You can also run `docker-prune` as a **scheduled cleanup service** using Docker Compose.  
This is ideal for **homelab** or **server environments** where you want regular automated pruning without manual runs.

**Example: daily cleanup at 3 AM using the `default` profile**

```yaml
version: "3.8"

services:
  docker-prune:
    image: ghcr.io/t4skforce/docker-prune:v1
    container_name: docker-prune
    restart: unless-stopped
    environment:
      # Choose one of: default, aggressive, conservative
      DOCKER_PRUNE_PROFILE: default
      
      # Optional: change the schedule (default is 0 2 * * *)
      DOCKER_PRUNE_SCHEDULE: "0 3 * * *"
      
      # Optional: set timezone
      TZ: Europe/Berlin
    volumes:
      # Mount Docker socket to control Docker on the host
      - /var/run/docker.sock:/var/run/docker.sock:ro
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=1024
      - /home/app/.docker:rw,noexec,nosuid,size=1024
    security_opt:
      - no-new-privileges:true
    network_mode: none
```

**Example: aggressive cleanup every 6 hours**

```yaml
version: "3.8"

services:
  docker-prune:
    image: ghcr.io/t4skforce/docker-prune:v1
    restart: unless-stopped
    environment:
      DOCKER_PRUNE_PROFILE: aggressive
      DOCKER_PRUNE_SCHEDULE: "0 */6 * * *"
      TZ: UTC
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=1024
      - /home/app/.docker:rw,noexec,nosuid,size=1024
    security_opt:
      - no-new-privileges:true
    network_mode: none
```

**Deploy**:

```bash
docker compose up -d
```

Check logs:

```bash
docker compose logs -f docker-prune
```

---

## Usage

### Get Info

```bash
docker-prune info
```

Displays storage usage information for Docker images and volumes.

Example Output:

```plaintext
INFO - Overall usage Images: 732.91MB Volumes: 1.31MB
INFO - Total reclaimed space: 0.00B
```

---

### Run Cleanup Configurations

```bash
docker-prune run cleanup-config.yml
```

Runs cleanup commands from a YAML configuration file.

**Additional options:**
- `--validate`: Validate the configuration file and exit without running any commands.
- `--exit` / `--no-exit`: Exit immediately if a command exits with a non-zero status (default: `--no-exit`).

---

### Manage Containers

The `docker-prune containers` command group lets you **stop** running containers or **remove** stopped containers using multiple filters.  
All filters are combined with **AND** logic — only containers matching **all** specified filters are affected.

**Notes:**
- The `stop` command affects **running** containers.
- The `rm` command affects **stopped** containers only.
- You can combine multiple filters to precisely target which containers to affect.
- The `--not-*` filters are useful for protecting important containers from cleanup runs.

---

#### Stop Containers

`docker-prune containers stop` stops running containers that match your criteria.

**Defaults:**
- `--restart`: `100` (stop containers restarted more than 100 times by default)
- `--not-label`: Excludes containers with labels matching:
  - `^(com.docker|io.podman).keep=(1|true|yes)?$`

**Examples:**
```bash
# Stop containers older than 1 week
docker-prune containers stop --age "1w"

# Stop containers with more than 50 restarts
docker-prune containers stop --restart 50

# Stop containers named like 'test-*' except those with 'keep' in the name
docker-prune containers stop --name "^test-.*" --not-name "keep"
```

---

#### Remove Containers

`docker-prune containers rm` removes **stopped** containers that match your criteria.

**Supported filters:**
- `--age` / `-a`: Remove stopped containers older than the given age (default: `1w`).
- `--name`: Include only containers with names matching a regex.
- `--not-name`: Exclude containers with names matching a regex.
- `--label`: Include only containers with labels matching a regex.
- `--not-label`: Exclude containers with labels matching a regex.
  **Default exclusions**:
  - `^(com.docker|io.podman).keep=(1|true|yes)?$`

**Examples:**
```bash
# Remove stopped containers older than 2 weeks
docker-prune containers rm --age "2w"

# Remove stopped containers with label 'env=dev'
docker-prune containers rm --label "^env=dev$"

# Remove stopped containers with 'temp' in their name, except those with label 'keep=true'
docker-prune containers rm --name "temp" --not-label "^keep=true$"
```

---

### Clean Docker Images

The `docker-prune images` command removes unused Docker images according to the filters you specify, and **also** performs additional automatic cleanup to reclaim disk space.

By default, it will:

1. **Remove images matching your filters**, such as:
   - `--age`: Remove images older than the given age (default: `90d`)
   - `--tag` / `--not-tag`: Include or exclude images by tag regex
   - `--label` / `--not-label`: Include or exclude images by label regex

2. **Prune dangling images** (untagged images that are not used by any container).

3. **Prune the Docker build cache**, optionally keeping a certain amount of build cache space using `--keep-builds`.

**Examples:**

Remove images older than 90 days (default):
```bash
docker-prune images --age "90d"
```

Remove images older than 30 days but exclude the `latest` tag:
```bash
docker-prune images --age "30d" --not-tag "^latest$"
```

Remove all unused images and keep only 500MB of build cache:
```bash
docker-prune images --keep-builds 500MB
```

---

### Prune Volumes

The `docker-prune volumes` command removes **unused** Docker volumes based on filters you specify.  
By default, it:

1. Targets only **dangling volumes** (not referenced by any container).
2. Applies your filters to decide which volumes to delete.
3. Excludes common volumes used by Docker Compose and Podman unless you override the exclusions.
4. After filtered deletion, also runs a **volume prune** to remove any remaining anonymous volumes.

**Default `--not-label` exclusions:**
- `^(com.docker|io.podman).compose.(project|volume)`
- `^(com.docker|io.podman).keep=(1|true|yes)?$`

**Examples:**

Remove dangling volumes older than 30 days (default):
```bash
docker-prune volumes
```

Remove dangling volumes older than 7 days:
```bash
docker-prune volumes --age "7d"
```

Remove volumes with names starting with `temp_`:
```bash
docker-prune volumes --name "^temp_"
```

Remove volumes except those matching `important` in the name:
```bash
docker-prune volumes --not-name "important"
```

Remove all unused volumes, ignoring default label exclusions:
```bash
docker-prune volumes --not-label ""
```

---

### Delete Networks

The `docker-prune networks` command removes **unused custom Docker networks** based on filters you specify.

By default, it:

1. Targets only **custom networks** that are not currently attached to any container.
2. Applies your filters to decide which networks to delete.
3. Excludes built-in networks (`bridge`, `host`, `none`) automatically.
4. Excludes common Compose/Podman networks and networks explicitly marked to keep, unless you override the exclusions.

**Examples:**

Remove unused custom networks older than 15 days:
```bash
docker-prune networks --age "15d"
```

Remove unused networks with names starting with `temp_`:
```bash
docker-prune networks --name "^temp_"
```

Remove unused networks except those matching `important` in the name:
```bash
docker-prune networks --not-name "important"
```

Remove all unused networks, ignoring default label exclusions:
```bash
docker-prune networks --not-label ""
```

**Note**:
- Built-in networks (`bridge`, `host`, `none`) are **always excluded** from pruning and cannot be included.
- The default `--not-label` option excludes networks commonly associated with `docker-compose` or `Podman` projects, such as:
  - `^(com.docker|io.podman).compose.(project|network)`
  - `^(com.docker|io.podman).keep=(1|true|yes)?$`

---

### Debug Mode

Enable detailed logging for debugging:

```bash
docker-prune --debug containers stop --age "2d"
```

---

## YAML Configuration Example

You can specify cleanup rules in a YAML file:

```yaml
- docker-prune containers stop --age "7d"
- docker-prune containers rm --age "30d"
- docker-prune images --age "90d" --not-tag "^latest$"
- docker-prune volumes --age "30d" --not-label "^com.docker.compose.project"
- docker-prune networks --age "15d"
```

Run the configuration:

```bash
docker-prune run config.yml
```

---

## Profiles & Configuration

`docker-prune` comes with several **built‑in cleanup profiles** — pre‑defined YAML configuration files (`config-*.yaml`) baked into the container image.  
These let you run cleanup tasks without writing your own config from scratch.

You can select a profile using the `DOCKER_PRUNE_PROFILE` environment variable, or override it entirely with a custom config via `DOCKER_PRUNE_CONFIG_FILE`.

### Available Profiles

| Profile          | Purpose |
|------------------|---------|
| **default**      | Balanced cleanup — safe for most environments. (see. [config-default.yml](https://github.com/t4skforce/blob/main/docker/config-default.yml)) |
| **aggressive**   | Faster and more frequent cleanup — best when disk space is critical. (see. [config-aggressive.yml](https://github.com/t4skforce/blob/main/docker/config-aggressive.yml)) |
| **conservative** | Minimal cleanup — prioritizes safety, good for production. (see. [config-conservative.yml](https://github.com/t4skforce/blob/main/docker/config-conservative.yml)) |
| **act**          | Optimized for **self‑hosted GitHub Actions runners** using [nektos/act](https://nektosact.com/usage/runners.html). Cleans up aggressively between CI jobs to free space, while keeping commonly reused CI images cached to **minimize registry pulls** and speed up builds. (see. [config-act.yml](https://github.com/t4skforce/blob/main/docker/config-act.yml)) |

---

### Default Cronjob Scheduler

The Docker container for `docker-prune` starts a cronjob scheduler by default. The cleanup tasks are executed based on the selected profile (`default`, `aggressive`, `conservative`, `act`) and are scheduled to run at `0 2 * * *` (every day at 2:00 AM). Profiles act as shorthand for built-in configuration files, but users can provide a fully custom configuration file if needed.

---

### Environment Variables

**`DOCKER_PRUNE_PROFILE`**:
   - Selects one of the built-in profiles (`default`, `aggressive`, `conservative`, `act`).
   - Example:
     ```bash
     -e DOCKER_PRUNE_PROFILE=aggressive
     ```

**`DOCKER_PRUNE_CONFIG_FILE`**:
   - Specifies the path to a custom configuration file. If provided, it overrides the profile-based default file.
   - Example:
     ```bash
     -e DOCKER_PRUNE_CONFIG_FILE=/path/to/custom-config.yaml
     ```

**`DOCKER_PRUNE_SCHEDULE`**:
   - Defines a custom cron schedule for the cleanup tasks. Accepts values supported by the [Supercronic](https://github.com/aptible/supercronic) project.
   - Example:
     ```bash
     -e DOCKER_PRUNE_SCHEDULE="*/10 * * * *"  # Runs every 10 minutes
     ```

---

### Docker Connection

Since `docker-prune` uses the [Python Docker SDK](https://docker-py.readthedocs.io/en/stable/), you can configure how it connects to the Docker daemon using the standard environment variables supported by the SDK.

If not set, the SDK defaults to:
- **Unix socket**: `/var/run/docker.sock` on Linux/macOS
- **Named pipe**: `//./pipe/docker_engine` on Windows

You can override this behavior using:

| Variable | Description | Example |
|----------|-------------|---------|
| `DOCKER_HOST` | URL to the Docker host. Use `unix:///var/run/docker.sock` for local or `tcp://host:port` for remote. | `tcp://192.168.1.50:2376` |
| `DOCKER_TLS_VERIFY` | Set to `1` to enable TLS verification. | `1` |
| `DOCKER_CERT_PATH` | Path to the directory containing TLS certificates (`ca.pem`, `cert.pem`, `key.pem`). Required if `DOCKER_TLS_VERIFY=1`. | `/home/app/.docker` |
| `DOCKER_CONFIG` | Path to the Docker CLI config directory (used for authentication, etc.). | `/home/app/.docker` |

**Example – connect to a remote Docker host with TLS:**
```bash
export DOCKER_HOST=tcp://192.168.1.50:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=$HOME/.docker/certs
docker-prune info
```

**Example – run container with remote Docker host:**
```bash
docker run -it \
  -e DOCKER_HOST=tcp://192.168.1.50:2376 \
  -e DOCKER_TLS_VERIFY=1 \
  -e DOCKER_CERT_PATH=/certs \
  -v /path/to/certs:/certs:ro \
  ghcr.io/t4skforce/docker-prune:latest info
```

For more details, see the [Docker SDK for Python documentation on environment variables](https://docker-py.readthedocs.io/en/stable/client.html#docker.client.DockerClient).


---

### Docker Example Command

<details>
<summary>Run the Docker container with a custom profile (`aggressive`) and schedule</summary>

```bash
docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_PRUNE_PROFILE=aggressive \
  -e DOCKER_PRUNE_SCHEDULE="0 */6 * * *" \
  -e TZ=Europe/Berlin \
  docker-prune:latest
```
</details>

<details>
<summary>Run the Docker container with a fully custom configuration file</summary>

```bash
docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_PRUNE_CONFIG_FILE=/path/to/custom-config.yaml \
  -e DOCKER_PRUNE_SCHEDULE="0 */6 * * *" \
  -e TZ=Europe/Berlin \
  docker-prune:latest
```
</details>

---

### Supported Custom Schedule

The `DOCKER_PRUNE_SCHEDULE` environment variable uses cron-style expressions for scheduling cleanup tasks. Below are a few examples:

| **Schedule**          | **Description**                     |
|------------------------|-------------------------------------|
| `0 2 * * *`           | Every day at 2:00 AM (default).     |
| `*/10 * * * *`        | Every 10 minutes.                   |
| `0 */6 * * *`         | Every 6 hours.                      |
| `0 3 * * 1`           | Every Monday at 3:00 AM.            |
| `30 1 1 * *`          | On the first day of every month at 1:30 AM. |

For more advanced scheduling options, refer to the [Supercronic documentation](https://github.com/aptible/supercronic).

---

### Default Parameter Values

Many commands come with default values for parameters. Below are some commonly used defaults:

- **Containers**:
  - `--age`: `1w` (1 week) for `rm` command
  - `--timeout`: `60` (60 seconds before forcing stop)
  - `--restart`: `100` (only for `stop` command)
  - `--not-label`: By default, both `stop` and `rm` exclude containers with labels:
    - `^(com.docker|io.podman).keep=(1|true|yes)?$`

- **Images**:
  - `--age`: `90d` (90 days)

- **Volumes**:
  - `--age`: `30d` (30 days)
  - `--not-label`: Excludes common `docker-compose` and `Podman` volume labels, plus keep-labels:
    - `^(com.docker|io.podman).compose.(project|volume)`
    - `^(com.docker|io.podman).keep=(1|true|yes)?$`

- **Networks**:
  - `--age`: None (manual configuration required)
  - `--not-name`: Excludes `bridge`, `host`, `none`.
  - `--not-label`: By default excludes common Docker Compose / Podman network labels and keep-labels.
    - `^(com.docker|io.podman).compose.(project|network)`
    - `^(com.docker|io.podman).keep=(1|true|yes)?$`

---

## Development

### Requirements

- Python 3.10 or higher
- Docker Python SDK
- Click library
- JSON Schema validation library
- PyYAML for YAML parsing

---

### Setup with Pipenv

Clone the repository:

```bash
git clone https://github.com/t4skforce/docker-prune.git
cd docker-prune
```

Install dependencies using `pipenv`:

```bash
pip install pipenv
pipenv install --dev
```

Activate the virtual environment:

```bash
pipenv shell
```

Run the tool locally:

```bash
python -m docker_prune.cli --help
```

---

### Run Locally with Docker

You can build and run the tool using Docker for testing in an isolated environment.

#### Build the Docker Image

```bash
docker build -t docker-prune:latest -f docker/Dockerfile .
```

#### Run the Docker Container

```bash
docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e TZ=Europe/Berlin \
  -e DOCKER_PRUNE_SCHEDULE='*/10 * * * *' \
  -e DOCKER_PRUNE_DEBUG=false \
  docker-prune:latest
```

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

### Reporting Issues

If you encounter any bugs or have feature requests, please open an issue on the [GitHub repository](https://github.com/t4skforce/docker-prune).

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/t4skforce/blob/main/LICENSE) file for details.
