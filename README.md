# Cloud Cost Optimizer Dashboard

A comprehensive cloud cost monitoring and optimization dashboard that helps users track, analyze, and optimize their cloud spending across AWS, GCP, and Azure.

## Features

### Core Functionality
- **Multi-Cloud Support**: Connect to AWS Cost Explorer, GCP Billing, and Azure Cost Management APIs
- **Real-time Cost Tracking**: Daily cost data collection and visualization
- **Anomaly Detection**: Identify unusual spending patterns and cost spikes
- **Smart Recommendations**: Automated suggestions for cost optimization (reserved instances, spot instances, rightsizing)
- **Interactive Dashboard**: Modern React frontend with Chart.js visualizations

### Technical Features
- **Authentication**: JWT-based user authentication with secure API access
- **Background Jobs**: Automated daily data fetching using APScheduler
- **Database**: SQLite with SQLAlchemy ORM for data persistence
- **API**: FastAPI backend with automatic OpenAPI documentation
- **Testing**: Comprehensive unit and integration tests with pytest

## Architecture

```
├── src/
│   ├── api/              # API routes and endpoints
│   ├── models/           # Database models
│   ├── services/         # Business logic services
│   ├── jobs/             # Background jobs and schedulers
│   └── main.py           # FastAPI application entry point
├── frontend/             # React dashboard application
├── tests/                # Unit and integration tests
└── requirements.txt      # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- AWS/GCP/Azure cloud account with billing access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cloud-dashboard
   ```

2. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Run the backend
   python -m uvicorn src.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend Dashboard: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/token` - User login (OAuth2)

### Cost Management
- `GET /costs/daily` - Get daily cost data
- `POST /costs/fetch` - Trigger manual cost data fetch
- `GET /recommendations` - Get cost optimization recommendations

### System
- `GET /` - Root endpoint
- `GET /health` - Health check

## Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: JWT secret key (auto-generated if not set)
- `AWS_ACCESS_KEY_ID`: AWS credentials for Cost Explorer
- `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `GOOGLE_APPLICATION_CREDENTIALS`: GCP service account key path

### Cloud Provider Setup

#### AWS
1. Enable Cost Explorer in AWS Console
2. Create IAM user with Cost Explorer read access
3. Set AWS credentials in environment or AWS CLI

#### GCP
1. Enable Cloud Billing API
2. Create service account with billing viewer role
3. Download JSON key file and set GOOGLE_APPLICATION_CREDENTIALS

#### Azure
1. Enable Cost Management API
2. Create service principal with cost management reader role
3. Set Azure credentials in environment

## Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Development

### Project Structure
- **Phase 1**: Planning and Research ✅
- **Phase 2**: Setup and Infrastructure ✅
- **Phase 3**: Backend Core Development ✅
- **Phase 4**: Automation and Alerts ✅
- **Phase 5**: Frontend Dashboard ✅
- **Phase 6**: Testing and Deployment ✅
- **Phase 7**: Bonus Features (Multi-cloud, AI recommendations)
- **Phase 8**: Documentation and Portfolio

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, APScheduler
- **Frontend**: React, Chart.js, Axios
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **Authentication**: JWT with OAuth2
- **Testing**: pytest, requests
- **Deployment**: Docker, docker-compose

## Cost Optimization Features

### Anomaly Detection
- Statistical analysis of daily spending patterns
- Alert thresholds for cost spikes
- Historical trend analysis

### Recommendations Engine
- Reserved Instance recommendations
- Spot Instance opportunities
- Resource rightsizing suggestions
- Idle resource detection

### Dashboard Visualizations
- Cost trend charts (line/bar graphs)
- Service breakdown analysis
- Monthly spending summaries
- Recommendation impact projections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS Cost Explorer API documentation
- FastAPI framework
- React and Chart.js communities
- Open source contributors

---

**Built with ❤️ for cloud cost optimization**
