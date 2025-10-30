# Cloud Cost Optimizer Dashboard

A comprehensive cloud cost monitoring and optimization dashboard that helps users track, analyze, and optimize their cloud spending across AWS, GCP, and Azure.

## Features

- **Multi-Cloud Support**: Connect to AWS Cost Explorer, GCP Billing, and Azure Cost Management APIs
- **Real-time Cost Tracking**: Daily cost data collection and visualization
- **Anomaly Detection**: Identify unusual spending patterns and cost spikes
- **Smart Recommendations**: Automated suggestions for cost optimization (reserved instances, spot instances, rightsizing)
- **Interactive Dashboard**: Modern React frontend with Chart.js visualizations
- **AI-Powered Insights**: OpenAI integration for advanced cost optimization recommendations
- **Budget Management**: Set spending limits and receive alerts when approaching thresholds
- **Cost Forecasting**: Predict future cloud spending based on historical trends
- **Performance Monitoring**: API performance metrics and system health monitoring

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based authentication with OAuth2
- **Background Jobs**: APScheduler for automated data fetching
- **Cloud APIs**: Boto3 (AWS), Google Cloud Client Libraries (GCP), Azure SDK (Azure)
- **AI Integration**: OpenAI API for intelligent recommendations
- **Monitoring**: Custom performance monitoring service
- **Testing**: pytest with async support

### Frontend
- **Framework**: Next.js (React)
- **Styling**: CSS modules
- **Charts**: Chart.js with react-chartjs-2
- **HTTP Client**: Axios
- **State Management**: React hooks

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: SQLite (development), PostgreSQL (production)
- **Message Queue**: Redis (optional, for Celery)
- **Task Queue**: Celery (optional, for background processing)

## Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- AWS/GCP/Azure cloud account with billing access (optional for demo)

## Installation & Setup

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cloud-dashboard
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cloud-dashboard
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run the backend
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=sqlite:///./cloud_cost_db.db

# JWT Authentication
SECRET_KEY=your-secret-key-here

# AWS Configuration (optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# GCP Configuration (optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Azure Configuration (optional)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Redis (optional, for Celery)
REDIS_URL=redis://localhost:6379/0
```

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

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/token` - User login (OAuth2)

### Cost Management
- `GET /costs/daily` - Get daily cost data
- `POST /costs/fetch` - Trigger manual cost data fetch
- `GET /recommendations` - Get cost optimization recommendations
- `GET /ai-recommendations` - Get AI-powered recommendations

### Monitoring & Analytics
- `GET /monitoring/health` - System health metrics
- `GET /monitoring/performance` - API performance metrics
- `GET /monitoring/savings` - Cost savings report

### Budget & Forecasting
- `POST /budget/simulate` - Budget simulation
- `GET /budgets` - Budget management (coming soon)
- `GET /alerts` - Cost alerts (coming soon)
- `GET /forecast` - Cost forecasting (coming soon)

## Project Structure

```
cloud-dashboard/
├── src/                          # Backend source code
│   ├── api/                      # API routes and endpoints
│   │   ├── routes.py            # Main API routes
│   │   └── auth_routes.py       # Authentication routes
│   ├── models/                  # Database models
│   │   ├── database.py          # Database configuration
│   │   ├── cost_model.py        # Cost data model
│   │   └── user_model.py        # User model
│   ├── services/                # Business logic services
│   │   ├── aws_cost_service.py  # AWS cost fetching
│   │   ├── ai_recommendations.py # AI recommendations
│   │   ├── anomaly_detection.py # Cost anomaly detection
│   │   ├── alert_service.py     # Alert management
│   │   └── monitoring_service.py # System monitoring
│   ├── jobs/                    # Background jobs
│   │   ├── scheduler.py         # Job scheduling
│   │   └── daily_cost_fetch.py  # Daily cost fetching
│   └── main.py                  # FastAPI application entry
├── frontend/                     # React frontend
│   ├── components/               # React components
│   ├── pages/                    # Next.js pages
│   ├── styles/                   # CSS styles
│   └── package.json              # Frontend dependencies
├── tests/                        # Unit and integration tests
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Backend container
├── docker-compose.yml            # Multi-container setup
└── README.md                     # This file
```

## Testing

```bash
# Run backend tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run frontend tests (if implemented)
cd frontend
npm test
```

## Development

### Running in Development Mode

```bash
# Backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev
```

### Database Migrations

The application uses SQLAlchemy with automatic table creation on startup. For production deployments, consider using Alembic for proper migration management.

### Adding New Features

1. **Backend**: Add new routes in `src/api/`, services in `src/services/`
2. **Frontend**: Add new components in `frontend/components/`, pages in `frontend/pages/`
3. **Database**: Add new models in `src/models/`
4. **Tests**: Add corresponding tests in `tests/`

## Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export DATABASE_URL=postgresql://user:pass@host:5432/db
   export SECRET_KEY=your-production-secret
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Manual Deployment**
   ```bash
   # Backend
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

   # Frontend
   npm run build && npm start
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS Cost Explorer API
- Google Cloud Billing API
- Azure Cost Management API
- FastAPI framework
- React and Next.js communities
- OpenAI for AI recommendations
- Open source contributors

---

**Built with ❤️ for cloud cost optimization**
