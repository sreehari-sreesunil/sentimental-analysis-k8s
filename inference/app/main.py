from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from prometheus_client import Counter, Histogram, make_asgi_app
import time

app = FastAPI(title="Sentiment Inference Service")

# Load model once at startup (simple, no separate file)
predictor = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

REQUESTS = Counter('sentiment_requests_total', 'Total sentiment analysis requests')
LATENCY = Histogram('sentiment_request_latency_seconds', 'Request latency')

class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input: TextInput):
    start = time.time()
    REQUESTS.inc()

    with LATENCY.time():
        result = predictor(input.text)[0]

    latency = time.time() - start

    return {
        "sentiment": result["label"],
        "score": round(float(result["score"]), 4),
        "latency_seconds": round(latency, 3)
    }

app.mount("/metrics", make_asgi_app())