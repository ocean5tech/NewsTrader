# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-29

### Added
- Initial project structure and architecture
- FastAPI backend with async support
- PostgreSQL database integration with SQLAlchemy
- Redis caching and task queue support
- Claude AI integration for news analysis
- News scraping system with RSS feed support
- React frontend with TypeScript and Ant Design
- Real-time dashboard with data visualization
- Backtesting system for prediction validation
- Docker/Podman containerization support
- Celery background task processing
- RESTful API endpoints for all core functionality
- Sample data and test interface
- Comprehensive documentation

### Backend Features
- News article analysis with impact scoring (0-10 scale)
- Sentiment analysis (-1 to +1 scale)
- Symbol-specific market impact predictions
- Confidence scoring for AI predictions
- Historical data storage and retrieval
- Async task processing with Celery
- Database migrations with Alembic

### Frontend Features
- Modern React 18 with TypeScript
- Ant Design component library
- Real-time data visualization with Recharts
- News management interface
- Market analysis dashboard
- Backtesting results visualization
- Responsive design for all devices

### Infrastructure
- PostgreSQL 15 for data persistence
- Redis 7 for caching and task queues
- Docker/Podman containerization
- Environment-based configuration
- Production-ready deployment setup

### API Endpoints
- `/api/v1/news/articles` - News article management
- `/api/v1/news/trending` - High-impact news retrieval
- `/api/v1/analysis/market-sentiment` - Market sentiment analysis
- `/api/v1/analysis/impact-summary` - Symbol impact summaries
- `/api/v1/analysis/keyword-trends` - Trending keyword analysis
- `/api/v1/backtest/run/{symbol}` - Backtesting execution
- `/api/v1/backtest/results/{symbol}` - Historical backtest results

### Documentation
- Comprehensive README with setup instructions
- PROJECT_OVERVIEW.md with architecture details
- API documentation with OpenAPI/Swagger
- Development and deployment guides
- Contributing guidelines

### Known Issues
- Requires Claude AI API key for full functionality
- Frontend requires compilation for production use
- Some advanced features need additional configuration

### Dependencies
- Python 3.11+ with FastAPI, SQLAlchemy, Celery
- Node.js 16+ with React 18, TypeScript, Ant Design
- PostgreSQL 15, Redis 7
- Docker/Podman for containerization