import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

def monte_carlo_simulation(data, days):
    log_returns = np.log(1 + data['Adj Close'].pct_change())
    mu = log_returns.mean()
    sigma = log_returns.std()
    daily_returns = np.exp(mu + sigma * np.random.normal(0, 1, days))

    price_list = [data['Adj Close'].iloc[-1]]
    for r in daily_returns:
        price_list.append(price_list[-1] * r)

    return price_list[1:]

@app.route('/generate_data', methods=['POST'])
def generate_data():
    data = request.get_json()
    file_path = data.get('file_path')
    days = data.get('days', 100)

    if not file_path:
        return jsonify({'error': 'Missing file_path parameter'}), 400

    try:
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found at {file_path}'}), 404

        historical_data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        future_prices = monte_carlo_simulation(historical_data, days)

        # Create a new DataFrame for the future data
        last_date = historical_data.index[-1]
        future_dates = pd.to_datetime([last_date + pd.DateOffset(days=i) for i in range(1, days + 1)])
        future_data = pd.DataFrame(future_prices, index=future_dates, columns=['Adj Close'])

        # Save the generated data
        output_dir = '/app/data'
        os.makedirs(output_dir, exist_ok=True)
        generated_file_path = os.path.join(output_dir, f'generated_data_{os.path.basename(file_path)}')
        future_data.to_csv(generated_file_path)

        return jsonify({'message': f'Generated data saved to {generated_file_path}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
