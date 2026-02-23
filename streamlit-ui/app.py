import streamlit as st
import requests
import json
from datetime import datetime

# Config
API_URL = "http://127.0.0.1:62612/analyze"   # your api-gateway endpoint
st.set_page_config(page_title="Sentiment Analyzer", layout="centered")

# Title & description
st.title("😊 Sentiment Analysis Demo")
st.markdown("""
This app uses a **microservices backend** (FastAPI + Hugging Face model + RabbitMQ logging)  
to analyze text sentiment in real-time.
""")

# Input
text_input = st.text_area(
    "Enter some text to analyze:",
    placeholder="Kerala is beautiful and microservices rock!",
    height=120,
    max_chars=500
)

# Button to trigger analysis
if st.button("Analyze Sentiment", type="primary", use_container_width=True):
    if not text_input.strip():
        st.error("Please enter some text!")
    else:
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"text": text_input},
                    timeout=15
                )
                response.raise_for_status()  # raise error if not 2xx
                result = response.json()

                # Display result nicely
                sentiment = result.get("sentiment", "UNKNOWN")
                score = result.get("score", 0.0)
                latency = result.get("latency_seconds", 0.0)

                if sentiment == "POSITIVE":
                    color = "green"
                    emoji = "😊👍"
                elif sentiment == "NEGATIVE":
                    color = "red"
                    emoji = "😔👎"
                else:
                    color = "orange"
                    emoji = "🤔"

                st.success(f"**{sentiment}** {emoji}")
                st.metric("Confidence Score", f"{score:.4f}")
                st.metric("Inference Latency", f"{latency:.3f} seconds")

                # Optional: show raw response
                with st.expander("Raw API Response"):
                    st.json(result)

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {str(e)}")
                st.info("Make sure docker compose is running and api-gateway is healthy.")

# Footer / info
st.markdown("---")
st.caption(f"Built with Streamlit + FastAPI microservices • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.caption("Backend services must be running via `docker compose up -d`")