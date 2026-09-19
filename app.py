import streamlit as st
import requests

st.set_page_config(page_title="Smart Calculator & Currency Converter", page_icon="🧮", layout="centered")
st.title("🧮 Smart Calculator")
st.caption("Basic calculator + PKR currency converter")

st.header("➕ Basic Calculator")
col1, col2 = st.columns(2)
with col1:
    num1 = st.number_input("First number", value=0.0)
with col2:
    num2 = st.number_input("Second number", value=0.0)

operation = st.selectbox("Choose operation", ["Addition (+)", "Subtraction (-)", "Multiplication (×)", "Division (÷)"])

if st.button("Calculate", type="primary"):
    if operation == "Addition (+)":
        result, symbol = num1 + num2, "+"
    elif operation == "Subtraction (-)":
        result, symbol = num1 - num2, "-"
    elif operation == "Multiplication (×)":
        result, symbol = num1 * num2, "×"
    else:
        if num2 == 0:
            st.error("❌ Division by zero is not allowed.")
            result = None
        else:
            result, symbol = num1 / num2, "÷"
    if result is not None:
        st.success(f"Result: {num1:g} {symbol} {num2:g} = {result:g}")

st.divider()
st.header("💱 Currency Converter")
st.write("Convert PKR to supported world currencies and supported currencies to PKR.")

API_URL = "https://open.er-api.com/v6/latest/USD"
CURRENCIES = {
    "PKR": "Pakistani Rupee", "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
    "AED": "UAE Dirham", "SAR": "Saudi Riyal", "QAR": "Qatari Riyal", "KWD": "Kuwaiti Dinar",
    "BHD": "Bahraini Dinar", "OMR": "Omani Rial", "INR": "Indian Rupee", "CNY": "Chinese Yuan",
    "JPY": "Japanese Yen", "KRW": "South Korean Won", "CAD": "Canadian Dollar", "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar", "CHF": "Swiss Franc", "TRY": "Turkish Lira", "MYR": "Malaysian Ringgit",
    "SGD": "Singapore Dollar", "THB": "Thai Baht", "RUB": "Russian Ruble", "ZAR": "South African Rand",
    "BRL": "Brazilian Real", "MXN": "Mexican Peso", "NOK": "Norwegian Krone", "SEK": "Swedish Krona",
    "DKK": "Danish Krone", "PLN": "Polish Zloty", "HKD": "Hong Kong Dollar", "IDR": "Indonesian Rupiah",
    "VND": "Vietnamese Dong"
}

@st.cache_data(ttl=3600)
def get_exchange_rates():
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
    data = response.json()
    if data.get("result") != "success":
        raise RuntimeError("Exchange-rate service did not return successful data.")
    return data["rates"], data.get("time_last_update_utc", "Unknown")

try:
    rates, update_time = get_exchange_rates()
    direction = st.radio("Conversion direction", ["PKR → Foreign Currency", "Foreign Currency → PKR"], horizontal=True)

    choices = [code for code in CURRENCIES if code != "PKR"]
    if direction == "PKR → Foreign Currency":
        from_currency = "PKR"
        to_currency = st.selectbox("Convert PKR to", choices, format_func=lambda code: f"{code} — {CURRENCIES[code]}")
    else:
        to_currency = "PKR"
        from_currency = st.selectbox("Convert from", choices, format_func=lambda code: f"{code} — {CURRENCIES[code]}")

    amount = st.number_input(f"Amount in {from_currency}", min_value=0.01, value=100.00, step=1.00)

    if st.button("Convert Currency", type="primary"):
        if from_currency not in rates or to_currency not in rates:
            st.error("❌ The selected currency is not currently available from the exchange-rate service.")
        else:
            source_rate = float(rates[from_currency])
            target_rate = float(rates[to_currency])
            conversion_rate = target_rate / source_rate
            converted_amount = amount * conversion_rate
            st.success(f"{amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}")
            st.info(f"1 {from_currency} = {conversion_rate:,.6f} {to_currency}")
            st.caption(f"Last API update: {update_time}")
except requests.exceptions.RequestException:
    st.error("❌ Could not connect to the exchange-rate service. Please check your internet connection and try again.")
except Exception as e:
    st.error(f"❌ Could not initialize currency converter: {e}")

st.divider()
st.caption("Currency rates are reference rates from an online exchange-rate service. Bank, card, or exchange-counter rates may be different.")
