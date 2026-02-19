# Healthcare Management Platform

A comprehensive, scalable healthcare management platform with React frontend and Python FastAPI backend.

## Features

### Core Modules
- **User Management**: Patient, Doctor, and Admin roles with RBAC
- **Doctor Discovery**: Search and filter doctors by specialization, availability, charges
- **Appointment System**: Book, reschedule, cancel appointments
- **Medical History**: Centralized patient medical records
- **Consultations & Prescriptions**: Digital prescription management
- **Billing & Payments**: Automated billing with tax calculation
- **Medical Reports**: Upload and manage diagnostic reports
- **Notifications**: Email, SMS, and in-app notifications
- **Dashboards**: Role-specific dashboards with analytics

## Technology Stack

### Frontend
- React 18
- Material-UI (MUI)
- Redux Toolkit
- React Router v6
- Axios

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 15+
- SQLAlchemy (Async ORM)
- JWT Authentication
- Redis (Caching & Task Queue)
- Celery (Background Jobs)

### Infrastructure
- Docker & Docker Compose
- Nginx (Reverse Proxy)

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd friendlyhealthy
```

2. **Create environment file**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Local Development Setup

#### Backend

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
# Start PostgreSQL (via Docker or local installation)
psql -U postgres -d healthcare_db -f ../DATABASE_SCHEMA.sql
```

4. **Run the server**
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Run development server**
```bash
npm run dev
```

## Project Structure

```
friendlyhealthy/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/          # API endpoints
│   │   │   └── dependencies.py  # Auth & RBAC middleware
│   │   ├── core/
│   │   │   ├── config.py        # Configuration
│   │   │   ├── database.py      # Database setup
│   │   │   └── security.py      # JWT & security utilities
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Utilities
│   │   └── main.py              # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── store/               # Redux store
│   │   ├── utils/               # Utilities
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Entry point
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── DATABASE_SCHEMA.sql          # Complete database schema
└── ARCHITECTURE.md              # System architecture documentation
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user

### Doctors
- `GET /api/v1/doctors` - Get all doctors
- `GET /api/v1/doctors/{id}` - Get doctor by ID
- `GET /api/v1/doctors/search` - Search doctors
- `GET /api/v1/doctors/{id}/availability` - Get doctor availability

### Appointments
- `POST /api/v1/appointments` - Create appointment
- `GET /api/v1/appointments` - Get user appointments
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PUT /api/v1/appointments/{id}` - Update appointment
- `PATCH /api/v1/appointments/{id}/status` - Update status
- `POST /api/v1/appointments/{id}/cancel` - Cancel appointment

### Medical History
- `GET /api/v1/medical-history/patient/{id}` - Get patient history
- `POST /api/v1/medical-history` - Add medical history
- `PUT /api/v1/medical-history/{id}` - Update history

### Prescriptions
- `GET /api/v1/prescriptions` - Get prescriptions
- `GET /api/v1/prescriptions/{id}` - Get prescription details
- `POST /api/v1/prescriptions` - Create prescription
- `GET /api/v1/prescriptions/{id}/pdf` - Download PDF

### Reports
- `POST /api/v1/reports` - Upload medical report
- `GET /api/v1/reports` - Get all reports
- `GET /api/v1/reports/{id}/download` - Download report

### Billing
- `GET /api/v1/bills` - Get all bills
- `GET /api/v1/bills/{id}` - Get bill details
- `POST /api/v1/bills` - Create bill
- `PATCH /api/v1/bills/{id}/payment` - Update payment status

## Database Schema

The complete database schema includes:
- 20+ tables with proper relationships
- ENUM types for statuses
- Indexes for performance
- Stored procedures for business logic
- Triggers for audit trails
- Views for common queries

See [DATABASE_SCHEMA.sql](DATABASE_SCHEMA.sql) for details.

## Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Refresh token rotation
- CORS protection
- SQL injection prevention
- XSS protection
- Rate limiting
- Audit logging

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build

1. **Build Docker images**
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Deploy to production**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `backend/.env.example` for required environment variables.

**Important**: Change the `SECRET_KEY` in production!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under me.

## Support

For issues and questions, please open a GitHub issue.
