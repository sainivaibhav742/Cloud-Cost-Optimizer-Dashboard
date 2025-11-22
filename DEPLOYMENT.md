# Deployment Guide

This guide explains how to deploy the Cloud Cost Optimizer Dashboard in various environments.

## Quick Start with Docker Compose (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd Cloud-Cost-Optimizer-Dashboard

# Copy environment file
cp .env.example .env

# Edit .env and configure your settings (optional for demo)
nano .env

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Demo Mode

The application comes with demo data seeding:

1. Access http://localhost:3000
2. Use demo credentials:
   - Username: `demo`
   - Password: `demo123`

## Local Development Setup

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database initialization and seed demo data
python -c "from src.services.demo_data_service import seed_demo_data; seed_demo_data()"

# Start the backend server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

## Production Deployment

### Environment Variables

Create a `.env` file with production values:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cloud_cost_db

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
ENABLE_DEMO_MODE=false

# AWS (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_DEFAULT_REGION=us-east-1

# OpenAI (Optional)
OPENAI_API_KEY=sk-your-key

# Email Alerts (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
```

### Docker Compose Production

```bash
# Build and start services
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Production Deployment

#### Backend

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn src.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Frontend

```bash
cd frontend

# Build for production
npm run build

# Start production server
npm start
```

## Cloud Provider Deployment

### AWS EC2

1. Launch an EC2 instance (t3.medium or larger recommended)
2. Install Docker and Docker Compose
3. Clone the repository
4. Configure `.env` file
5. Run `docker-compose up -d`
6. Configure security groups to allow ports 80, 443, 3000, 8000

### Google Cloud Run

```bash
# Build and push backend
gcloud builds submit --tag gcr.io/PROJECT_ID/cloud-cost-backend
gcloud run deploy cloud-cost-backend \
  --image gcr.io/PROJECT_ID/cloud-cost-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and push frontend
cd frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/cloud-cost-frontend
gcloud run deploy cloud-cost-frontend \
  --image gcr.io/PROJECT_ID/cloud-cost-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Create resource group
az group create --name cloud-cost-rg --location eastus

# Deploy backend
az container create \
  --resource-group cloud-cost-rg \
  --name cloud-cost-backend \
  --image your-registry/cloud-cost-backend \
  --dns-name-label cloud-cost-backend \
  --ports 8000

# Deploy frontend
az container create \
  --resource-group cloud-cost-rg \
  --name cloud-cost-frontend \
  --image your-registry/cloud-cost-frontend \
  --dns-name-label cloud-cost-frontend \
  --ports 3000
```

## Database Setup

### PostgreSQL (Production Recommended)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE cloud_cost_db;
CREATE USER cloud_user WITH ENCRYPTED PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE cloud_cost_db TO cloud_user;

# Update .env
DATABASE_URL=postgresql://cloud_user:your-password@localhost:5432/cloud_cost_db
```

### Database Migrations (Optional with Alembic)

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Application Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# All logs
docker-compose logs -f
```

### Health Checks

- Backend health: http://localhost:8000/health
- System health: http://localhost:8000/monitoring/health

## Backup and Recovery

### Database Backup

```bash
# SQLite backup
cp cloud_cost_db.db cloud_cost_db.backup.$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump cloud_cost_db > backup_$(date +%Y%m%d).sql
```

### Restore

```bash
# SQLite restore
cp cloud_cost_db.backup.20240101.db cloud_cost_db.db

# PostgreSQL restore
psql cloud_cost_db < backup_20240101.sql
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify database connection in `.env`
- Check logs: `docker-compose logs backend`

### Frontend won't connect to backend
- Verify `NEXT_PUBLIC_API_URL` in frontend environment
- Check CORS settings in backend
- Ensure backend is running

### Database errors
- Check database URL format
- Verify database service is running
- Check file permissions for SQLite

### Authentication issues
- Verify `SECRET_KEY` is set
- Check token expiration settings
- Clear browser localStorage and try again

## Performance Optimization

### Backend
- Use gunicorn with multiple workers
- Enable caching for frequently accessed data
- Use connection pooling for database

### Frontend
- Build with `npm run build` for production
- Enable CDN for static assets
- Use image optimization

### Database
- Add indexes on frequently queried columns
- Regular VACUUM for SQLite
- Enable query caching

## Security Best Practices

1. **Change default secrets**: Update `SECRET_KEY` in production
2. **Use HTTPS**: Always use SSL/TLS in production
3. **Secure database**: Use strong passwords and restrict access
4. **Regular updates**: Keep dependencies up to date
5. **Environment isolation**: Never commit `.env` files
6. **API rate limiting**: Implement rate limiting for production
7. **Input validation**: Validate all user inputs
8. **CORS configuration**: Restrict allowed origins in production

## Support and Maintenance

### Regular Tasks
- Monitor application logs
- Check disk space
- Review security alerts
- Update dependencies monthly
- Backup database weekly
- Review and rotate credentials quarterly

### Scaling
- Horizontal: Add more backend workers
- Vertical: Increase container resources
- Database: Consider managed database services
- Caching: Add Redis for session/data caching

For issues and feature requests, please use the GitHub issue tracker.
