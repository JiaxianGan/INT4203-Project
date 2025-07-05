import pandas as pd
import requests
import numpy as np
import json



# --- Step 1: Load stock data CSV ---
data = pd.read_csv("klci_20250704_close_prices.csv", index_col=0, parse_dates=True)

# --- Step 2: Generate summary info ---
summary = {}

for ticker in data.columns:
    prices = data[ticker].dropna()
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

# --- Step 3: Ask Ollama using deepseek-r1 ---
def ask_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1",
                "prompt": prompt,
                "stream": False  # Disable streaming to fix JSON error
            }
        )
        result = response.json()
        return result["response"]
    except json.JSONDecodeError as e:
        print("⚠️ JSON decode error:", e)
        print("Raw response:", response.text)
        return "Sorry, I couldn't understand the response from the LLM."

# --- Step 4: Format stock summary + user input ---
def generate_stock_prompt(user_question, summary):
    stock_info_text = ""
    for ticker, info in summary.items():
        stock_info_text += (
            f"{ticker}: RM{info['latest']} ({info['change']}% today, "
            f"{info['1M_change']}% over 1M, trend: {info['1M_trend']})\n"
        )

    prompt = (
        "You are a helpful financial advisory assistant focused on Malaysian KLCI stocks.\n"
        "Here is the latest stock summary for key tickers:\n\n"
        f"{stock_info_text}\n"
        f"User asked: {user_question}\n"
        "Give a clear and relevant response based on the trend and data above.\n"
    )
    return prompt

# --- Step 5: Complete chatbot function ---
def stock_llm_chatbot(user_input):
    prompt = generate_stock_prompt(user_input, summary)
    response = ask_ollama(prompt)
    return response.strip()

# --- Step 6: Interactive console chatbot ---
if __name__ == "__main__":
    print("💬 Stock Advisory Chatbot (powered by DeepSeek via Ollama)")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            user_question = input("You: ")
            if user_question.lower() in ["exit", "quit"]:
                print("👋 Bye!")
                break
            answer = stock_llm_chatbot(user_question)
            print("Bot:", answer, "\n")
        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
