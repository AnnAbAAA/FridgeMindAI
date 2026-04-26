# import streamlit as st
# from datetime import date, datetime
# import json
# import os
# # from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

DATA_FILE = "fridge.json"

st.set_page_config(page_title="FridgeMind AI", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f8f9fb;
}

.title {
    font-size: 42px;
    font-weight: 800;
    color: #1f2937;
}
.subtitle {
    color: #6b7280;
    margin-bottom: 20px;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 12px;
}

.urgent {
    border-left: 6px solid #ef4444;
}
.soon {
    border-left: 6px solid #f59e0b;
}
.safe {
    border-left: 6px solid #10b981;
}

.ai-box {
    background: #111827;
    color: white;
    padding: 20px;
    border-radius: 18px;
}

.metric {
    background: white;
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def days_left(exp):
    d = datetime.strptime(exp, "%Y-%m-%d").date()
    return (d - date.today()).days

def generate_meal_plan(items):
    if not items:
        return "No food available."

    sorted_items = sorted(items, key=lambda x: days_left(x["expiry"]))
    urgent = [i for i in sorted_items if days_left(i["expiry"]) <= 2]
    all_names = [i["name"] for i in sorted_items]

    prompt = f"""
You are a smart food assistant.

User has these ingredients:
{all_names}

These ingredients are urgent and must be used first:
{[i["name"] for i in urgent]}

Generate:
1. What they should eat RIGHT NOW
2. 2 meal ideas using urgent ingredients
3. Health score (1-10)
4. Eco impact explanation (short)
5. Very simple steps (max 4 steps)

Keep it short, structured, and practical.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

st.title("FridgeMind AI 🧠🥗")
st.caption("Eat smarter. Waste less. Powered by AI.")

data = load_data()

with st.sidebar:
    st.header("Add product")

    name = st.text_input("Product")
    expiry = st.date_input("Expiry date", min_value=date.today())

    if st.button("Add"):
        if name:
            data.append({
                "name": name.lower(),
                "expiry": expiry.strftime("%Y-%m-%d")
            })
            save_data(data)
            st.success("Added")

    if st.button("Clear"):
        data = []
        save_data(data)
        st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your fridge")

    if not data:
        st.info("Empty fridge")
    else:
        sorted_data = sorted(data, key=lambda x: days_left(x["expiry"]))

        for idx, item in enumerate(sorted_data):
            d = days_left(item["expiry"])

            if d <= 1:
                color = "🔴"
            elif d <= 3:
                color = "🟠"
            else:
                color = "🟢"

            col_item, col_btn = st.columns([4, 1])

            with col_item:
                st.write(f"{color} **{item['name']}** — {d} days left")

            with col_btn:
                if st.button("❌", key=f"del_{idx}", help="Delete item"):
                    data.remove(item)
                    save_data(data)
                    st.rerun()

with col2:
    st.subheader("AI suggestions")

    if st.button("What should I eat?"):
        with st.spinner("Thinking..."):
            result = generate_meal_plan(data)
            st.markdown(result)

st.divider()

urgent_count = sum(1 for i in data if days_left(i["expiry"]) <= 2)

st.subheader("Impact")

st.write(f"⚠️ Urgent items: {urgent_count}")
st.write(f"🌍 Estimated CO₂ saved: {round(urgent_count * 0.6, 2)} kg")
