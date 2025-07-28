# Stock Simulator

This project is a microservices-based application for backtesting stock trading strategies on historical and generated future data.

## Architecture

The project consists of the following microservices:

- **Main App**: Orchestrates the workflow by calling other services.
- **Historical Data Fetcher**: Fetches historical stock data from Yahoo Finance.
- **Data Generator**: Generates future stock data using a Monte Carlo simulation.
- **Backtester**: Backtests a trading strategy on given data.

## How to Run

1. **Prerequisites**:
   - Docker
   - Docker Compose

2. **Build and Run the Services**:
   Navigate to the `stock_simulator` directory and run:
   ```bash
   docker-compose up --build
   ```

3. **Use the API**:
   Send a POST request to the main application to run a simulation.

   **URL**: `http://localhost:5000/run_simulation`

   **Method**: `POST`

   **Body** (JSON):
   ```json
   {
       "ticker": "AAPL",
       "start_date": "2020-01-01",
       "end_date": "2023-01-01",
       "future_days": 252
   }
   ```

   **Example using curl**:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{
       "ticker": "AAPL",
       "start_date": "2020-01-01",
       "end_date": "2023-01-01",
       "future_days": 252
   }' http://localhost:5000/run_simulation
   ```

## Services

- **Main App**: `http://localhost:5000`
- **Historical Data Fetcher**: `http://localhost:5001`
- **Data Generator**: `http://localhost:5002`
- **Backtester**: `http://localhost:5003`
