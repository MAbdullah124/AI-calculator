import streamlit as st
import requests
from decimal import Decimal, InvalidOperation

st.set_page_config(page_title="Smart Calculator & Currency Converter", page_icon="🧮", layout="centered")

st.title("🧮 Smart Calculator & Currency Converter")
st.caption("Basic arithmetic + PKR ↔ worldwide currency conversion")

# ---------------- Calculator ----------------
st.header("🧮 Calculator")
col1, col2 = st.columns(2)
with col1:
    num1 = st.number_input("First number", value=0.0, format="%.10f")
with col2:
    num2 = st.number_input("Second number", value=0.0, format="%.10f")

operation = st.selectbox("Operation", ["Addition (+)", "Subtraction (-)", "Multiplication (×)", "Division (÷)"])

if st.button("Calculate", type="primary"):
    if operation == "Addition (+)":
        result = num1 + num2
        expression = f"{num1:g} + {num2:g}"
    elif operation == "Subtraction (-)":
        result = num1 - num2
        expression = f"{num1:g} - {num2:g}"
    elif operation == "Multiplication (×)":
        result = num1 * num2
        expression = f"{num1:g} × {num2:g}"
    else:
        if num2 == 0:
            st.error("❌ Division by zero is not allowed.")
            st.stop()
        result = num1 / num2
        expression = f"{num1:g} ÷ {num2:g}"
    st.success(f"Result: {expression} = {result:g}")

# ---------------- Currency Converter ----------------
st.divider()
st.header("💱 Currency Converter")
st.write("Convert PKR to another currency or another supported currency to PKR.")

# Frankfurter is a free exchange-rate API and does not require an API key.
API_BASE = "https://api.frankfurter.dev/v2"

@st.cache_data(ttl=3600)
def get_currencies():
    r = requests.get(f"{API_BASE}/currencies", timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=3600)
def get_rate(base, quote):
    r = requests.get(f"{API_BASE}/rate/{base}/{quote}", timeout=10)
    r.raise_for_status()
    data = r.json()
    return Decimal(str(data["rate"])), data.get("date", "Unknown")

try:
    currencies = get_currencies()
    codes = sorted(currencies.keys())

    if "PKR" not in codes:
        st.error("PKR is not currently available from the exchange-rate service.")
        st.stop()

    direction = st.radio("Conversion direction", ["PKR → Foreign Currency", "Foreign Currency → PKR"], horizontal=True)
    amount_text = st.text_input("Amount", value="100")

    if direction == "PKR → Foreign Currency":
        foreign_codes = [c for c in codes if c != "PKR"]
        target = st.selectbox("Convert PKR to", foreign_codes, format_func=lambda c: f"{c} — {currencies[c]}")
        base = "PKR"
        quote = target
    else:
        foreign_codes = [c for c in codes if c != "PKR"]
        source = st.selectbox("Convert from", foreign_codes, format_func=lambda c: f"{c} — {currencies[c]}")
        base = source
        quote = "PKR"

    if st.button("Convert Currency", type="primary"):
        try:
            amount = Decimal(amount_text.strip())
            if amount < 0:
                st.error("❌ Please enter a positive amount.")
                st.stop()

            rate, rate_date = get_rate(base, quote)
            converted = amount * rate

            st.success(f"{amount:,.2f} {base} = {converted:,.2f} {quote}")
            st.info(f"Exchange rate: 1 {base} = {rate:,.8f} {quote}\n\nRate date: {rate_date}")
        except InvalidOperation:
            st.error("❌ Please enter a valid number.")
        except requests.exceptions.RequestException:
            st.error("❌ Could not retrieve the exchange rate. Check your internet connection and try again.")
        except Exception as e:
            st.error(f"❌ Currency conversion error: {e}")

except requests.exceptions.RequestException:
    st.error("❌ Could not load currencies. Check your internet connection and refresh the app.")
except Exception as e:
    st.error(f"❌ Could not initialize currency converter: {e}")

st.divider()
st.caption("Exchange-rate data: Frankfurter API. Rates are reference rates and may differ from bank or exchange-counter rates.")
