import os
import yfinance as yf
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data = request.get_json()
    ticker = data.get('ticker')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([ticker, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            return jsonify({'error': 'No data found for the given parameters'}), 404

        # Save data to a CSV file
        output_dir = '/app/data'
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'{ticker}_{start_date}_{end_date}.csv')
        stock_data.to_csv(file_path)

        return jsonify({'message': f'Data for {ticker} saved to {file_path}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
