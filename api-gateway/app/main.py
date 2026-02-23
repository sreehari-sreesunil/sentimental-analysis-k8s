from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pika
import json
import os

app = FastAPI(title="Sentiment Analysis API Gateway")

# Config from env
INFERENCE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://inference:8001/predict")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_QUEUE = "sentiment_logs"

class AnalyzeRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze_text(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Call inference
    try:
        resp = requests.post(INFERENCE_URL, json={"text": request.text}, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Inference error: {str(e)}")

    # Send to RabbitMQ (don't fail request if this breaks)
    try:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            )
        )
        ch = conn.channel()
        ch.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        msg = {
            "text": request.text,
            "sentiment": result.get("sentiment"),
            "score": result.get("score"),
            "latency": result.get("latency_seconds")
        }
        ch.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(msg),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conn.close()
    except Exception as e:
        print(f"RabbitMQ publish failed: {e}")

    return result