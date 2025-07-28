from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HISTORICAL_DATA_FETCHER_URL = "http://historical_data_fetcher:5001"
DATA_GENERATOR_URL = "http://data_generator:5002"
BACKTESTER_URL = "http://backtester:5003"

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.get_json()
    ticker = data.get('ticker')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    future_days = data.get('future_days', 100)

    if not all([ticker, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # 1. Fetch historical data
        fetch_response = requests.post(
            f"{HISTORICAL_DATA_FETCHER_URL}/fetch_data",
            json={'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        )
        fetch_response.raise_for_status()
        historical_data_path = fetch_response.json().get('message').split(' ')[-1]

        # 2. Generate future data
        generate_response = requests.post(
            f"{DATA_GENERATOR_URL}/generate_data",
            json={'file_path': historical_data_path, 'days': future_days}
        )
        generate_response.raise_for_status()
        generated_data_path = generate_response.json().get('message').split(' ')[-1]

        # 3. Backtest on historical data
        backtest_historical_response = requests.post(
            f"{BACKTESTER_URL}/backtest",
            json={'file_path': historical_data_path}
        )
        backtest_historical_response.raise_for_status()
        historical_results = backtest_historical_response.json()

        # 4. Backtest on future data
        backtest_future_response = requests.post(
            f"{BACKTESTER_URL}/backtest",
            json={'file_path': generated_data_path}
        )
        backtest_future_response.raise_for_status()
        future_results = backtest_future_response.json()

        return jsonify({
            'historical_performance': historical_results,
            'future_performance': future_results
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error communicating with a service: {e}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
