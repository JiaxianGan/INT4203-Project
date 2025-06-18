import mysql.connector
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from mysql.connector import Error

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'Xian0703',  # Replace with your MySQL password
    'database': 'stock_advisor_db'
}

# List of stock symbols to fetch
stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

def connect_to_db():
    """Establish connection to MySQL database."""
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Successfully connected to MySQL database")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def insert_stock_info(conn, symbol, company_name, sector, industry, exchange):
    """Insert stock metadata into the stocks table."""
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO stocks (symbol, company_name, sector, industry, exchange)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company_name = VALUES(company_name),
            sector = VALUES(sector),
            industry = VALUES(industry),
            exchange = VALUES(exchange),
            updated_at = CURRENT_TIMESTAMP
        """
        cursor.execute(query, (symbol, company_name, sector, industry, exchange))
        conn.commit()
        print(f"Inserted/Updated stock info for {symbol}")
    except Error as e:
        print(f"Error inserting stock info for {symbol}: {e}")

def insert_stock_prices(conn, stock_id, data):
    """Insert historical stock prices into the stock_prices table."""
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO stock_prices (stock_id, date, open_price, close_price, high_price, low_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            close_price = VALUES(close_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            volume = VALUES(volume),
            updated_at = CURRENT_TIMESTAMP
        """
        for _, row in data.iterrows():
            cursor.execute(query, (
                stock_id,
                row['Date'].date(),
                row['Open'],
                row['Close'],
                row['High'],
                row['Low'],
                int(row['Volume'])
            ))
        conn.commit()
        print(f"Inserted/Updated stock prices for stock_id {stock_id}")
    except Error as e:
        print(f"Error inserting stock prices for stock_id {stock_id}: {e}")

def get_stock_id(conn, symbol):
    """Retrieve stock_id for a given symbol."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT stock_id FROM stocks WHERE symbol = %s", (symbol,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error retrieving stock_id for {symbol}: {e}")
        return None

def fetch_yahoo_finance_data(symbol, start_date, end_date):
    """Fetch stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        info = stock.info
        return {
            'history': hist,
            'company_name': info.get('longName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'exchange': info.get('exchange', 'Unknown')
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def main():
    # Connect to the database
    conn = connect_to_db()
    if not conn:
        return

    # Define date range for historical data (e.g., last 1 year)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)

    try:
        for symbol in stock_symbols:
            # Fetch data from Yahoo Finance
            data = fetch_yahoo_finance_data(symbol, start_date, end_date)
            if not data:
                continue

            # Insert stock metadata
            insert_stock_info(
                conn,
                symbol,
                data['company_name'],
                data['sector'],
                data['industry'],
                data['exchange']
            )

            # Get stock_id
            stock_id = get_stock_id(conn, symbol)
            if not stock_id:
                print(f"Could not find stock_id for {symbol}")
                continue

            # Insert historical price data
            insert_stock_prices(conn, stock_id, data['history'])

    except Exception as e:
        print(f"Error in main process: {e}")
    finally:
        if conn.is_connected():
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()