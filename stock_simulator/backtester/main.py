import pandas as pd
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def simple_moving_average_strategy(data, short_window=40, long_window=100):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    signals['short_mavg'] = data['Adj Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Adj Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['signal'][short_window:] = \
        pd.np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)

    signals['positions'] = signals['signal'].diff()
    return signals

@app.route('/backtest', methods=['POST'])
def backtest():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'Missing file_path parameter'}), 400

    try:
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found at {file_path}'}), 404

        stock_data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        signals = simple_moving_average_strategy(stock_data)

        # Calculate portfolio performance
        initial_capital = float(100000.0)
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions['stock'] = 100 * signals['signal']

        portfolio = positions.multiply(stock_data['Adj Close'], axis=0)
        pos_diff = positions.diff()

        portfolio['holdings'] = (positions.multiply(stock_data['Adj Close'], axis=0)).sum(axis=1)
        portfolio['cash'] = initial_capital - (pos_diff.multiply(stock_data['Adj Close'], axis=0)).sum(axis=1).cumsum()
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()

        return jsonify(portfolio.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
