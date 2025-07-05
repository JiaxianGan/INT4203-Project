import pandas as pd
import numpy as np
import google.generativeai as genai

# Load Gemini Flash
genai.configure(api_key="AIzaSyD7x0Qa3OixdUBqWhPn8W2glp0OhKZXIxI")
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Step 1: Load price trend data ---
price_data = pd.read_csv("klci_20250704_close_prices.csv", index_col=0, parse_dates=True)

summary = {}
for ticker in price_data.columns:
    prices = price_data[ticker].dropna()
    if len(prices) < 2:
        continue

    latest = prices[-1]
    prev = prices[-2]
    pct_change = ((latest - prev) / prev) * 100

    try:
        monthly_change = ((latest - prices[-21]) / prices[-21]) * 100
    except:
        monthly_change = np.nan

    trend = "up" if monthly_change > 0 else "down" if monthly_change < 0 else "flat"

    summary[ticker] = {
        "latest": round(latest, 2),
        "change": round(pct_change, 2),
        "1M_trend": trend,
        "1M_change": round(monthly_change, 2)
    }

# --- Step 2: Load fundamental data from CSV ---
fundamentals_df = pd.read_csv("fundamentals.csv", index_col="Ticker")

# --- Step 3: Get fundamentals from loaded CSV ---
def get_fundamental_metrics(ticker):
    try:
        row = fundamentals_df.loc[ticker]
        return {
            "Price": f"RM {row['Price']}",
            "EPS": row['EPS'],
            "PE Ratio": row['PE'],
            "ROE": f"{row['ROE']}%",
            "P/B Ratio": row['PB'],
            "Dividend Yield": f"{row['DividendYield']}%",
            "Market Cap": f"{row['MarketCap']}"
        }
    except KeyError:
        return {"Note": "No fundamental data found for this ticker."}

# --- Step 4: Generate full prompt ---
def generate_prompt(user_question, summary):
    stock_info_text = ""
    for ticker, info in summary.items():
        stock_info_text += (
            f"{ticker}: RM{info['latest']} ({info['change']}% today, "
            f"{info['1M_change']}% over 1M, trend: {info['1M_trend']})\n"
        )

    # Try to find mentioned ticker
    first_ticker = None
    for code in summary.keys():
        if code in user_question:
            first_ticker = code
            break

    metrics_text = ""
    if first_ticker:
        metrics = get_fundamental_metrics(first_ticker)
        metrics_text += f"\n📊 Value Investing Metrics for {first_ticker}:\n"
        for k, v in metrics.items():
            metrics_text += f"- {k}: {v}\n"

    prompt = (
        "You are a financial assistant helping with Malaysian KLCI stocks.\n"
        "Use the price trend and fundamental data to provide clear analysis.\n\n"
        "📉 Price Summary:\n"
        f"{stock_info_text}\n"
        f"{metrics_text}\n"
        f"User asked: {user_question}\n"
        "Provide value-investing-based insights, and help the user decide based on metrics like PE, ROE, EPS."
    )
    return prompt

# --- Step 5: Chatbot function ---
def stock_llm_chatbot(user_input):
    prompt = generate_prompt(user_input, summary)
    response = model.generate_content(prompt)
    return response.text.strip()

# --- Step 6: Terminal interface ---
if __name__ == "__main__":
    print("📈 Gemini Flash Stock ChatBot (with fundamental data)")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting...")
                break
            answer = stock_llm_chatbot(user_input)
            print("Bot:", answer, "\n")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
