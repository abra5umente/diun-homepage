# DIUN Homepage Widget

A Flask API that receives webhooks from [DIUN](https://crazymax.dev/diun/) and displays container update notifications in [Homepage](https://gethomepage.dev/).

<img width="436" height="110" alt="image" src="https://github.com/user-attachments/assets/9af8a3f4-a6a8-45d2-8795-0be05dbaf85b" />  


## Features

- Receives DIUN webhooks and tracks available container updates
- Displays updates as a dynamic list in Homepage
- Auto-clears stale updates when DIUN runs a new scan cycle
- Persists data through container restarts

## Quick Start

### Build & Run
```bash
docker build -t diun-homepage:latest .
docker run -d \
  --name diun-homepage \
  -p 5000:5000 \
  -v /path/to/data/updates.json:/app/updates.json \
  -e APP_PORT=5000 \
  -e APP_IP=0.0.0.0 \
  diun-homepage:latest
```

### Docker Compose
```yaml
diun-homepage:
  container_name: diun-homepage
  image: your-username/diun-homepage:latest
  ports:
    - "5000:5000"
  networks:
    - docker-network
  volumes:
    - /path/to/data/updates.json:/app/updates.json # Create this file BEFORE starting the container.
  environment:
    - APP_PORT=5000
    - APP_IP=0.0.0.0
  restart: unless-stopped
```

## Configuration

### DIUN Setup

Add webhook notification to your DIUN configuration:
```yaml
- DIUN_NOTIF_WEBHOOK_ENDPOINT=http://your-server-ip:5000/webhook
- DIUN_NOTIF_WEBHOOK_METHOD=POST
```

### Homepage Widget

Add this to your `services.yaml`:
```yaml
- DIUN Updates:
    icon: docker.png
    href: http://your-server-ip:5000/updates/list
    description: Container updates available
    widget:
      type: customapi
      url: http://your-server-ip:5000/updates/list
      method: GET
      display: dynamic-list
      mappings:
        name: image
        label: status
        limit: 10
```

## API Endpoints

- `GET /` - Health check
- `POST /webhook` - Receives DIUN webhooks
- `GET /updates/list` - Returns updates as array (for Homepage)
- `GET /updates/summary` - Returns summary with count

## How It Works

1. DIUN scans your containers and detects updates
2. Sends a webhook for each updated image
3. API stores the update with timestamp
4. When new scan cycle starts (detected by 1+ hour gap), old updates are automatically cleared
5. Homepage displays current list of pending updates

## Environment Variables

- `APP_PORT` - Port to run on (default: 5000)
- `APP_IP` - IP address that the process binds to (default: 0.0.0.0)

## Notes

- Updates auto-clear after 1 hour of no new webhooks (assumes new DIUN scan cycle)
- Only tracks the most recent update per image
- Data persists in `updates.json` file
