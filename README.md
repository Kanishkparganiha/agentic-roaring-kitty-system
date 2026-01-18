# Agentic Stock Analysis System

AI-powered stock screening platform combining multi-agent orchestration, real-time data processing, and advanced financial analytics.

## Overview

A microservices-based system designed to analyze thousands of stocks using autonomous AI agents, fundamental analysis algorithms, and real-time market data processing. The platform identifies undervalued opportunities through multi-factor scoring and generates detailed research reports.

## Architecture

**Backend Services:**
- Data Ingestion - Real-time market data collection with rate limiting
- Analysis Engine - Financial metrics calculation and scoring algorithms
- Agent Coordinator - LLM-based multi-agent orchestration
- Web API - RESTful endpoints with FastAPI
- WebSocket Service - Real-time updates and notifications

**Infrastructure:**
- PostgreSQL - Primary data store with TimescaleDB for time-series
- Redis - Multi-tier caching and session management
- RabbitMQ - Asynchronous task queue
- Docker Compose - Local development orchestration

**AI/ML Stack:**
- OpenAI GPT-4 / Anthropic Claude for analysis
- LangChain for agent orchestration
- Vector embeddings for semantic caching
- Custom scoring algorithms

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL 15
- Redis 7
- Docker
- Prometheus + Grafana

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### Installation

1. Clone repository
```bash
git clone https://github.com/yourusername/agentic-stock-analysis.git
cd agentic-stock-analysis
```

2. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start infrastructure
```bash
docker compose up -d postgres redis
```

4. Setup Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Verify installation
```bash
python health_check.py
```

Expected output:
```
Running System check for external services connection
PostgreSQL connected: postgresql://rkuser:***@localhost:5432/roaring_kitty
Redis connected: redis://localhost:6379/0
Run complete
```

## Project Structure

```
├── config.py              # Configuration management
├── health_check.py        # Infrastructure health checks
├── docker-compose.yml     # Service orchestration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── services/             # Microservices
│   ├── data_ingestion/
│   ├── analysis_engine/
│   ├── agent_coordinator/
│   ├── web_api/
│   └── websocket_service/
├── shared/               # Shared components
│   ├── models/          # SQLAlchemy ORM
│   ├── utils/
│   └── config/
├── tests/
└── infrastructure/
```

## Configuration

Key environment variables:

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

See `.env.example` for complete configuration options.

## Development

### Running Services

```bash
# Start all infrastructure
docker compose up -d

# Run API server (when implemented)
uvicorn services.web_api.main:app --reload

# Run tests
pytest

# Code formatting
black . && flake8 .
```

### Database Migrations

```bash
# Create migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Key Features

**Data Processing**
- Rate-limited API integration with major financial data providers
- Real-time price updates and fundamental data ingestion
- Efficient batch processing for historical data

## Data Ingestion Service

The data ingestion service handles fetching stock data from external APIs with production-grade reliability patterns.

### Components

```
services/data_ingestion/
├── rate_limiter.py   # Token Bucket rate limiting
├── fetcher.py        # HTTP client with retry logic
└── pipeline.py       # ETL orchestration
```

### Rate Limiter (Token Bucket Algorithm)

Implements the Token Bucket algorithm for API rate limiting:

```
Bucket Capacity: N tokens
Refill Rate: R tokens/second

Token Calculation: T = min(M, T + elapsed_time × R)
```

**Why Token Bucket?**
- Allows controlled bursts (e.g., loading a dashboard)
- Smooths requests to steady rate over time
- Industry standard for API rate limiting

### HTTP Fetcher with Exponential Backoff

Smart retry logic that backs off exponentially on failures:

```
Attempt 1: Wait 1 sec  → Retry
Attempt 2: Wait 2 sec  → Retry
Attempt 3: Wait 4 sec  → Retry
Attempt 4: Wait 8 sec  → Retry
Attempt 5: Wait 16 sec → Retry

Formula: delay = base_delay × 2^attempt
```

**Benefits:**
- Prevents overwhelming struggling servers
- Gives external services time to recover
- Standard pattern in distributed systems

### ETL Pipeline

```
┌──────────┐    ┌───────────┐    ┌──────────┐
│ EXTRACT  │ →  │ TRANSFORM │ →  │   LOAD   │
│          │    │           │    │          │
│ Fetch    │    │ Clean     │    │ Save to  │
│ from API │    │ & Format  │    │ Database │
└──────────┘    └───────────┘    └──────────┘
```

**Pipeline Features:**
- Upsert logic (insert or update existing records)
- Transaction management with rollback on failure
- Structured logging for debugging
- Support for batch processing multiple symbols

**Analysis Engine**
- Multi-factor scoring system
- Financial metrics calculation (P/E, P/B, ROE, debt ratios)
- Momentum and trend analysis
- Sector-relative scoring

**Agent System**
- Autonomous LLM agents for fundamental analysis
- Multi-agent collaboration with dependency management
- Semantic caching to reduce API costs
- Structured report generation

**Performance**
- Sub-200ms API response times with caching
- Horizontal scaling support
- Async processing for long-running tasks
- Connection pooling and query optimization

## API Documentation

Once services are running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Monitoring

Access dashboards:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## System Design Highlights

**Scalability**
- Stateless services for horizontal scaling
- Message queue for decoupled async processing
- Multi-tier caching strategy

**Reliability**
- Health checks for all services
- Circuit breakers for external API calls
- Retry logic with exponential backoff
- Database connection pooling

**Performance**
- Indexed database queries
- Redis caching with intelligent invalidation
- Async I/O for external API calls
- Batch processing for bulk operations

## Contributing

This is a personal project portfolio. Feedback and suggestions are welcome through issues.

## License

MIT License

## Contact

GitHub: @yourusername
