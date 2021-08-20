# stock-market-dash-plotly

## Description

Stock market dashboard to analyze stock performance and apply backtesting strategies.

Strategy currently being used is Simple Moving Average (SMA) and user can test many different values in 1st and 2nd moving average.

## Requirements

Python3.9.5 installed (for data download)
Docker and Docker-compose

## Authentication

user: any_user

password: any_password

## Usage

1. Download data
2. Run docker-compose
3. Access [dash.localhost](dash.localhost)

### 1. Downloading data

```bash
# 1. First, go into ./data folder
cd data
# 2. Create a venv
python3 -m venv venv
# 3. Activate venv
source venv/bin/activate
# 4. Install requirements
pip install -r requirements
# 5. Download data
python download_stocks.py AMZN AAPL MSFT NVDA TSLA BTC-USD
```

### 2. Running docker-compose

```bash
docker swarm init
docker-compose up --build
```

### 3. Access [dash.localhost](dash.localhost)

## Inspiration sources

- [Architecture based on following medium article](https://towardsdatascience.com/clean-architecture-for-ai-ml-applications-using-dash-and-plotly-with-docker-42a3eeba6233)
- [Github associated with architecture above](https://github.com/CzakoZoltan08/dash-clean-architecture-template)
