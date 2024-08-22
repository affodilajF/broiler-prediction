# Requirements
- Has docker installed on the local machine
- Has internet connection

# Installation

1. Run docker
2. Pull docker image
```bash
docker pull ghcr.io/azaria-fairuz/azaria-fairuz/broiler-prediction:latest
```

3. Run docker image
```bash
docker run -d -p 5000:5000 -e PYTHONUNBUFFERED=1 --name broiler-prediction ghcr.io/azaria-fairuz/azaria-fairuz/broiler-prediction:latest
```
