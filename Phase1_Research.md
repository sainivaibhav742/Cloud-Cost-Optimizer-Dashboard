# Phase 1: Planning and Research - Cloud Cost Optimizer Dashboard

## 1. AWS Cost Explorer API, GCP, and Azure Billing APIs

### AWS Cost Explorer API
- **Overview**: AWS Cost Explorer is a service that enables you to visualize, understand, and manage your AWS costs and usage over time. The API allows programmatic access to cost and usage data.
- **Key Features**:
  - Retrieve cost and usage data for the last 13 months.
  - Group data by dimensions like service, availability zone, instance type.
  - Metrics include blended costs, unblended costs, usage quantities.
  - Supports filters for specific accounts, services, etc.
- **API Endpoints**:
  - `GetCostAndUsage`: Main endpoint for retrieving cost and usage data.
  - `GetReservationCoverage`: For reserved instance coverage.
  - `GetReservationPurchaseRecommendation`: For RI recommendations.
- **Authentication**: Requires AWS credentials (access key, secret key) or IAM roles.
- **Limitations**: Data is available with a 24-hour delay; API calls are rate-limited.

### GCP Billing APIs
- **Overview**: Google Cloud Billing API provides programmatic access to billing data, budgets, and cost management.
- **Key Features**:
  - Export billing data to BigQuery for analysis.
  - Create budgets and alerts via API.
  - Retrieve cost breakdowns by project, service, SKU.
- **API Endpoints**:
  - `projects.billingInfo`: Get billing info for projects.
  - `billingAccounts.budgets`: Manage budgets.
  - BigQuery exports for detailed data.
- **Authentication**: OAuth 2.0 or service account keys.
- **Limitations**: Real-time data not available; exports are daily.

### Azure Billing APIs
- **Overview**: Azure Cost Management and Billing APIs allow access to cost and usage data.
- **Key Features**:
  - Query cost data using REST APIs.
  - Support for dimensions like resource group, service, meter.
  - Forecasting and budgeting.
- **API Endpoints**:
  - `providers/Microsoft.CostManagement/query`: Query cost data.
  - `providers/Microsoft.Billing/billingAccounts`: Billing account info.
- **Authentication**: Azure AD authentication with tokens.
- **Limitations**: Data latency of 24-48 hours; complex query syntax.

## 2. PostgreSQL Analytics Queries and MongoDB Alternatives

### PostgreSQL Analytics Queries
- **Overview**: PostgreSQL supports advanced analytics with window functions, CTEs, and extensions like TimescaleDB for time-series data.
- **Key Features for Analytics**:
  - Window functions: `ROW_NUMBER()`, `RANK()`, `SUM() OVER()`.
  - Common Table Expressions (CTEs): For complex queries.
  - Aggregations: `GROUP BY`, `HAVING`, subqueries.
  - Extensions: PostGIS for spatial, pg_stat_statements for query stats.
- **Example Queries**:
  - Trend analysis: `SELECT date, SUM(cost) OVER (ORDER BY date) FROM costs;`
  - Anomalies: `SELECT * FROM costs WHERE cost > AVG(cost) OVER (PARTITION BY service);`
- **Advantages**: ACID compliance, rich data types, performance for complex queries.
- **Disadvantages**: Less scalable for very large datasets compared to NoSQL.

### MongoDB Alternatives
- **Overview**: MongoDB is a NoSQL document database suitable for flexible schemas and large-scale data.
- **Key Features**:
  - Document-based storage (JSON-like).
  - Aggregation pipeline for analytics: `$group`, `$match`, `$project`.
  - Sharding for horizontal scaling.
  - Time-series collections (MongoDB 5.0+).
- **Comparison to PostgreSQL**:
  - Better for unstructured data and rapid schema changes.
  - Faster writes, but eventual consistency.
  - Analytics via aggregation framework, but less SQL-like.
- **When to Use**: For cost data with varying structures or high write loads.

## 3. Cron Jobs, Schedulers (node-cron, Celery), and Background Workers

### Cron Jobs
- **Overview**: Cron is a time-based job scheduler in Unix-like systems.
- **Usage**: Schedule scripts to run at specific times (e.g., daily at 2 AM).
- **Syntax**: `0 2 * * * /path/to/script` (minute hour day month day-of-week).
- **Advantages**: Simple, built-in to most systems.
- **Disadvantages**: Limited error handling, no distributed execution.

### Node-cron (for Node.js)
- **Overview**: A Node.js library for scheduling tasks.
- **Usage**: `cron.schedule('0 2 * * *', () => { fetchData(); });`
- **Features**: Supports cron expressions, time zones, job management.
- **Advantages**: Easy integration with Node.js apps.
- **Disadvantages**: Single-threaded, not for heavy workloads.

### Celery (for Python)
- **Overview**: Distributed task queue for Python, with scheduling via Celery Beat.
- **Usage**: Define tasks as functions, schedule with beat.
- **Features**: Asynchronous execution, retries, monitoring (Flower).
- **Advantages**: Scalable, supports multiple brokers (Redis, RabbitMQ).
- **Disadvantages**: More complex setup.

### Background Workers
- **General Concept**: Processes that run tasks asynchronously, separate from the main application.
- **Examples**: Celery workers, Node.js worker threads, Python multiprocessing.
- **Use in Project**: For daily data fetching without blocking the API.

## 4. Data Visualization Best Practices (Chart.js, Recharts)

### Best Practices
- **Choose Appropriate Charts**: Line charts for trends, bar charts for comparisons, pie for proportions.
- **Data Preparation**: Aggregate data on backend to reduce frontend load.
- **Interactivity**: Tooltips, zooming, filtering.
- **Accessibility**: Alt text, color-blind friendly palettes.
- **Performance**: Limit data points, use lazy loading.
- **Consistency**: Standard colors, fonts across charts.

### Chart.js
- **Overview**: JavaScript library for responsive charts.
- **Features**: Line, bar, pie, radar charts; plugins for advanced features.
- **Usage**: Register components, pass data objects.
- **Advantages**: Lightweight, customizable.
- **Disadvantages**: Requires manual setup.

### Recharts
- **Overview**: React-based charting library built on D3.
- **Features**: Declarative API, composable components.
- **Usage**: `<LineChart data={data}><Line dataKey="cost" /></LineChart>`
- **Advantages**: React-native, easy integration.
- **Disadvantages**: Dependent on React.

## 5. OAuth and JWT for Authentication with Cloud APIs

### JWT (JSON Web Tokens)
- **Overview**: Compact, URL-safe tokens for claims transmission.
- **Structure**: Header, payload, signature.
- **Usage**: Issued by auth server, verified by API.
- **Advantages**: Stateless, scalable.
- **Disadvantages**: No revocation without blacklist.

### OAuth for Cloud APIs
- **Overview**: Authorization framework for delegated access.
- **Flow**: Client requests access, user grants, token issued.
- **Cloud Integration**:
  - AWS: IAM roles, temporary credentials.
  - GCP: Service accounts, OAuth 2.0.
  - Azure: Managed identities, OAuth.
- **Best Practices**: Use refresh tokens, secure storage, short-lived tokens.

## 6. Project Scope, Tech Stack Choice, and Development Environment Setup

### Project Scope
- **Core Features**: Daily cost fetching, anomaly detection, recommendations, dashboard visualization.
- **Boundaries**: Start with AWS, add multi-cloud later; mock data for initial testing.
- **MVP**: Backend API with basic auth, frontend charts, daily cron job.

### Tech Stack Choice
- **Backend**: FastAPI (Python) - Fast, async, auto-docs.
- **Database**: PostgreSQL for structured data, MongoDB if needed for flexibility.
- **Frontend**: React + Chart.js for visualization.
- **Scheduler**: Celery for background jobs.
- **Auth**: JWT with FastAPI's security.

### Development Environment Setup
- **Tools**: Python 3.8+, Node.js 16+, PostgreSQL.
- **Virtual Environment**: Use venv or conda for Python.
- **Dependencies**: Install via pip (requirements.txt), npm (package.json).
- **IDE**: VS Code with extensions for Python, React.
- **Version Control**: Git, GitHub for repo.
- **Testing**: Pytest for backend, Jest for frontend.

This research provides the foundation for implementing the Cloud Cost Optimizer Dashboard. All key topics have been covered to inform the design and development decisions.
