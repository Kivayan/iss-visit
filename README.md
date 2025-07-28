# ISS Country Visit Tracker

Track which countries the International Space Station (ISS) visits most frequently using real-time position data.

## Features

- 🛰️ Real-time ISS position tracking
- 🌍 Country detection using reverse geocoding
- 📊 SQLite database for persistent visit tracking
- 🐳 Docker support with volume mounting
- 📈 Visit statistics and analytics

## Database Schema

The application uses SQLite with three main tables:

- **visits**: Records each country entry with coordinates and timestamp
- **country_stats**: Aggregated visit counts per country
- **app_state**: Tracks last known position to detect country changes

## Quick Start

### Local Development

```bash
# Install dependencies
uv sync

# Run single check
uv run python main.py

# Run continuous tracking (checks every 5 minutes)
uv run python continuous_tracker.py
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or run manually with volume mount
docker build -t iss-tracker .
docker run -v ${PWD}/data:/data iss-tracker
```

## Usage

### Single Position Check
```python
from main import ISSTracker

tracker = ISSTracker()
result = tracker.track_iss_position()
print(f"ISS is over: {result['current_country']}")
```

### View Statistics
```python
stats = tracker.get_visit_stats()
for country, visits, first, last in stats:
    print(f"{country}: {visits} visits")
```

## Database Location

When running in Docker, the SQLite database is stored at `/data/iss_visits.db` inside the container. Mount a volume to persist data:

```bash
docker run -v /host/path/data:/data iss-tracker
```

## Environment Variables

- `TZ`: Timezone for logging (default: UTC)

## API Endpoints Used

- **ISS Position**: `http://api.open-notify.org/iss-now.json`
- **Reverse Geocoding**: Local `reverse_geocoder` library

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request