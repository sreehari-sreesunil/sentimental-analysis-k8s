# Sentiment Analysis Microservices Platform

Transformer-based sentiment analysis system deployed with containerized microservices architecture.  
Exposes a REST API for sentiment prediction, uses asynchronous logging via RabbitMQ, and includes Prometheus observability + Streamlit frontend for interactive testing.

This project showcases practical **MLOps** patterns: service isolation, containerization, monitoring, async processing, and Kubernetes orchestration.

## Tech Stack

- **API**          : FastAPI  
- **Model**        : Hugging Face Transformers (DistilBERT fine-tuned on SST-2)  
- **Messaging**    : RabbitMQ  
- **Monitoring**   : Prometheus  
- **Frontend**     : Streamlit  
- **Containerization** : Docker  
- **Orchestration**    : Kubernetes  

## Architecture
Streamlit UI ──→ API Gateway ──→ Inference Service
│               │
└─→ RabbitMQ ──→ Logger (async file logging)
│
└─→ Prometheus (metrics scraping)


## Request Flow

1. User submits text (via Streamlit or direct REST call)  
2. API Gateway validates → forwards to Inference service  
3. Inference service runs transformer prediction  
4. Metrics are exposed via `/metrics` (Prometheus format)  
5. Prediction metadata published to RabbitMQ  
6. Logger consumes message → writes structured log to file  
7. API Gateway returns result immediately  

## Services & Ports

| Service       | Port  | Purpose                              |
|---------------|-------|--------------------------------------|
| api-gateway   | 8000  | Public API endpoint                  |
| inference     | 8001  | Internal ML prediction service       |
| rabbitmq      | 5672  | AMQP messaging                       |
| rabbitmq UI   | 15672 | RabbitMQ management dashboard        |
| prometheus    | 9090  | Metrics dashboard                    |
| streamlit     | 8501  | Interactive web frontend             |

## API Endpoints

### Public – API Gateway

```http
POST /analyze

### Request Flow

{
  "text": "Kerala is beautiful!"
}

### Internal – Inference Service

POST /predict
GET /metrics (Prometheus scraping endpoint)

### Project Structure

.
├── api-gateway/            # FastAPI entrypoint service
├── inference/              # Model loading & prediction logic
├── logger/                 # RabbitMQ consumer → file logger
├── streamlit/              # Streamlit frontend
├── sentiment-app.yaml      # Kubernetes manifests (all-in-one or multi-file)
├── prometheus.yaml         # Prometheus scrape config
├── docker-compose.yml      # Local development compose file
└── README.md

## Running the Project

### Option 1: Docker Compose (recommended for local dev)

# Build images
docker build -t inference:latest ./inference
docker build -t api-gateway:latest ./api-gateway
docker build -t logger:latest ./logger

# Or use docker-compose build if you have it configured

# Start everything
docker compose up -d

## Access:

API           http://localhost:8000/docs
Streamlit     http://localhost:8501
RabbitMQ UI   http://localhost:15672  (guest/guest)
Prometheus    http://localhost:9090

## Kubernetes (Minikube / kind / cluster)

# Build images into Minikube VM (or use your registry)
minikube image build -t inference:latest ./inference
minikube image build -t api-gateway:latest ./api-gateway
minikube image build -t logger:latest ./logger

# Apply manifests
kubectl apply -f sentiment-app.yaml

# Check status
kubectl get pods,svc -n sentiment

## Monitoring

Prometheus collects:
sentiment_requests_total (counter)
sentiment_request_latency_seconds (histogram/summary)

RabbitMQ management UI → queue depth, message rates, consumer status

# Conclusion
This project demonstrates production-grade deployment of a transformer NLP model using modern MLOps tooling: FastAPI serving, async messaging, Prometheus monitoring, and Kubernetes orchestration — all in a clean microservices design.