# Technologies
This project is made by using Python Flask and are currently deployed in railway using docker image from this repo's package. For more detailed libraries used in this project please see the project's [requirements.txt](https://github.com/azaria-fairuz/broiler-prediction/blob/main/requirements.txt) file.

# Usage
To access this project through this link below:
```bash
https://broiler-prediction-production.up.railway.app/
```

To access this project's API, please use the provided [postman for production documentation](https://github.com/azaria-fairuz/broiler-prediction/blob/main/postman_production.json) or access it manually by using the /api prefix:
```bash
https://broiler-prediction-production.up.railway.app/api
```

For more detailed description of the API endpoints, use the provided [postman for production documentation](https://github.com/azaria-fairuz/broiler-prediction/blob/main/postman_production.json). Here are some of the current available API endpoints:
```bash
# check API
https://broiler-prediction-production.up.railway.app/api

# perform prediction
https://broiler-prediction-production.up.railway.app/api/predict

# get prediction data
https://broiler-prediction-production.up.railway.app/api/get_prediction_data
```

# Requirements
If you want to run this project in your local machine, there are a few things that you need to have before proceeding
- Has docker installed on the local machine
- Has internet connection
- Has Access to the current database

# Installation

1. Run docker engine
2. Open terminal and pull docker image:
```bash
docker pull ghcr.io/azaria-fairuz/azaria-fairuz/broiler-prediction:latest
```

3. From the same terminal, run docker image:
```bash
docker run -d -p 5000:5000 -e PYTHONUNBUFFERED=1 --name broiler-prediction ghcr.io/azaria-fairuz/azaria-fairuz/broiler-prediction:latest
```
