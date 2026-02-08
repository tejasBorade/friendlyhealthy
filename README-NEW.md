# Healthcare Management Platform - Setup & Run Guide

## Prerequisites
- Node.js 18+ installed
- PostgreSQL 12+ installed and running
- Git (optional)

## Quick Start

### 1. Install Dependencies

**Backend:**
```powershell
cd server
npm install
```

**Frontend:**
```powershell
cd frontend
npm install
```

### 2. Set up PostgreSQL Database

1. Open PostgreSQL command line or pgAdmin
2. Create database:
   ```sql
   CREATE DATABASE healthcare_db;
   ```

3. Run the schema:
   ```powershell
   psql -U postgres -d healthcare_db -f server/database/schema.sql
   ```
   
   Or use pgAdmin to run the SQL file: `server/database/schema.sql`

4. Update `server/.env` with your PostgreSQL credentials if different from defaults

### 3. Start the Application

**Option A: Use the startup script (Recommended)**
```powershell
.\run-app.ps1
```

**Option B: Start manually**

Terminal 1 - Backend:
```powershell
cd server
npm run dev
```

Terminal 2 - Frontend:
```powershell
cd frontend
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

## Default Login

After running the schema, you can register new users or use:
- Email: Any new email
- Password: Must contain uppercase, lowercase, number, special char (e.g., Test@123)

## API Endpoints

- POST /api/auth/register - Register new user
- POST /api/auth/login - Login
- GET /api/auth/me - Get current user
- GET /api/doctors - Get all doctors
- GET /api/doctors/:id - Get doctor by ID
- GET /api/appointments - Get appointments
- POST /api/appointments - Create appointment
- PATCH /api/appointments/:id - Update appointment
- DELETE /api/appointments/:id - Delete appointment

## Project Structure

```
server/
  ├── config/         # Database configuration
  ├── database/       # SQL schema
  ├── middleware/     # Auth middleware
  ├── routes/         # API routes
  ├── .env           # Environment variables
  └── server.js      # Main server file

frontend/
  ├── src/
  │   ├── components/  # React components
  │   ├── pages/       # Page components
  │   ├── services/    # API services
  │   └── store/       # Redux store
  └── .env.local      # Local environment variables
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check credentials in `server/.env`
- Verify database exists: `psql -U postgres -l`

### Port Already in Use
- Backend (5000): `netstat -ano | find ":5000"` then kill process
- Frontend (3000): `netstat -ano | find ":3000"` then kill process

### Module Not Found
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## Technology Stack

**Backend:**
- Node.js + Express.js
- PostgreSQL
- JWT Authentication
- bcryptjs for password hashing

**Frontend:**
- React 18
- Vite
- Material-UI
- Redux Toolkit
- Axios
