# Elder Health Monitoring System

This project is a beginner-friendly Elder Health Monitoring System.
It uses a simple HTML, CSS, and JavaScript frontend with a FastAPI and MongoDB backend.
The code is written in a clean and easy-to-explain style.

## Features

- User registration and login
- JWT authentication
- Password hashing with bcrypt
- Role-based authorization
- Care Manager can add patients and health data
- Parent can view data, view alerts, and send emergency alerts
- Child can view health data in read-only mode
- Automatic health alerts for unsafe values
- Simple user codes like `CM001`, `P001`, `C001`, and `PT001`
- Simple frontend with plain HTML, CSS, and JavaScript

## Project Structure

```text
elder-health-system/
|-- backend/
|   |-- main.py
|   |-- config.py
|   |-- database.py
|   |-- models.py
|   |-- auth.py
|   |-- requirements.txt
|   |-- .env
|   |-- .env.example
|   |-- sample_data.json
|   |-- routes/
|   |   |-- auth_routes.py
|   |   |-- health_routes.py
|   |   |-- alert_routes.py
|   |-- utils/
|       |-- jwt_handler.py
|       |-- role_checker.py
|-- frontend/
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- add_health.html
|   |-- alerts.html
|   |-- patient_data.html
|   |-- emergency_button.html
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- app.js
|       |-- auth.js
|-- README.md
```

## Step 1: Backend Setup

### 1. Install Python packages

From the project root run:

```bash
venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 2. Check the .env file

This project now reads settings from:

- [backend/.env](/d:/health_project/backend/.env)

Current values:

```env
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=elder_health_system
SECRET_KEY=replace_this_with_a_strong_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Start MongoDB

Make sure MongoDB is running on:

```text
mongodb://localhost:27017
```

### 4. Run the FastAPI backend

From the project root run:

```bash
venv\Scripts\python.exe -m uvicorn backend.main:app
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API docs:

```text
http://127.0.0.1:8000/docs
```

## Step 2: Frontend Setup

Open a second terminal inside the `frontend` folder and run a simple static server:

```bash
python -m http.server 5500
```

Then open this page in your browser:

```text
http://127.0.0.1:5500/login.html
```

## Step 3: Sample Data Flow

The easiest beginner flow is:

1. Register one `care_manager` user.
2. Register one `parent` user.
3. Register one `child` user.
4. Note the generated user codes like `CM001`, `P001`, and `C001`.
5. Login as the Care Manager.
6. Create a patient from the dashboard using the Parent and Child codes.
7. Note the generated patient code like `PT001`.
8. Add health data using the patient code.
9. Login as Parent or Child and view patient data.

A sample data file is included here:

- [backend/sample_data.json](/d:/health_project/backend/sample_data.json)

## Small Code Format Used

These small codes are used in forms and API payloads:

- Care Manager: `CM001`
- Parent: `P001`
- Child: `C001`
- Patient: `PT001`

MongoDB still keeps its own internal `_id`, but the frontend uses the small codes so the app is easier for beginners.

## Main API Endpoints

### Authentication

- `POST /auth/register`
- `POST /auth/login`

### Patient and Health

- `GET /api/patients`
- `POST /api/patients`
- `POST /api/health`
- `GET /api/patient/{patient_code}`
- `POST /api/emergency`

### Alerts

- `GET /api/alerts`

## Security Used in This Project

- Passwords are hashed using `bcrypt`
- JWT tokens are used for login sessions
- JWT tokens expire after a set time
- Protected routes require a token
- Role checking is used for access control
- Input validation is handled with Pydantic
- CORS is enabled for browser requests
- Plain passwords are never stored in MongoDB

## Health Alert Rules

- Heart rate below `50` or above `110` creates a warning alert
- Oxygen level below `92` creates a critical alert
- Blood pressure above `140/90` creates a warning alert

## Backend File Explanation

### [backend/main.py](/d:/health_project/backend/main.py)

This is the starting file for FastAPI.
It creates the app, enables CORS, and connects the route files.

### [backend/config.py](/d:/health_project/backend/config.py)

This file loads values from `.env`.
It keeps project settings in one simple place.

### [backend/database.py](/d:/health_project/backend/database.py)

This file connects the project to MongoDB.
It keeps the database connection in one simple place.

### [backend/models.py](/d:/health_project/backend/models.py)

This file stores all request models.
It validates login data, registration data, patient data, and health data.

### [backend/auth.py](/d:/health_project/backend/auth.py)

This file handles password hashing, password checking, and current-user authentication.
It works like simple authentication middleware.

### [backend/routes/auth_routes.py](/d:/health_project/backend/routes/auth_routes.py)

This file contains the register and login APIs.
It also creates simple user codes such as `P001` and `CM001`.

### [backend/routes/health_routes.py](/d:/health_project/backend/routes/health_routes.py)

This file handles patients, health records, patient history, and emergency alerts.
It also creates patient codes such as `PT001` and creates alerts when health values are unsafe.

### [backend/routes/alert_routes.py](/d:/health_project/backend/routes/alert_routes.py)

This file returns alerts based on the logged-in user's role.
Each user only sees alerts for linked patients.

### [backend/utils/jwt_handler.py](/d:/health_project/backend/utils/jwt_handler.py)

This file creates and verifies JWT tokens.
It keeps token logic separate and easy to reuse.

### [backend/utils/role_checker.py](/d:/health_project/backend/utils/role_checker.py)

This file checks whether a user has permission to use an API.
It makes role-based access control simple.

## Frontend File Explanation

### [frontend/login.html](/d:/health_project/frontend/login.html)

This page lets users log in.

### [frontend/register.html](/d:/health_project/frontend/register.html)

This page lets users create a new account.
After registration, the page shows the generated small user code.

### [frontend/dashboard.html](/d:/health_project/frontend/dashboard.html)

This is the main page after login.
It shows role-based links and lets Care Managers create patients using small codes like `P001` and `C001`.

### [frontend/add_health.html](/d:/health_project/frontend/add_health.html)

This page lets Care Managers add health data using the patient code.

### [frontend/alerts.html](/d:/health_project/frontend/alerts.html)

This page shows warning, critical, and emergency alerts.

### [frontend/patient_data.html](/d:/health_project/frontend/patient_data.html)

This page shows patient details and health history.

### [frontend/emergency_button.html](/d:/health_project/frontend/emergency_button.html)

This page lets Parent users send an emergency alert.

### [frontend/css/style.css](/d:/health_project/frontend/css/style.css)

This file contains all styles for the frontend.
It keeps the UI neat, readable, and responsive.

### [frontend/js/auth.js](/d:/health_project/frontend/js/auth.js)

This file stores the token, checks login state, and sends secure API requests.

### [frontend/js/app.js](/d:/health_project/frontend/js/app.js)

This file controls page actions like login, registration, patient loading, alerts, and emergency requests.
It keeps each function small and simple.

## Example API Requests

### Register User

```json
{
  "name": "Anita Care",
  "email": "care@example.com",
  "password": "care1234",
  "role": "care_manager"
}
```

Example register response:

```json
{
  "message": "User registered successfully.",
  "user_id": "mongodb_internal_id",
  "user_code": "CM001",
  "role": "care_manager"
}
```

### Login User

```json
{
  "email": "care@example.com",
  "password": "care1234"
}
```

### Create Patient

```json
{
  "name": "Savitri Devi",
  "age": 72,
  "parent_user_code": "P001",
  "child_user_code": "C001"
}
```

### Add Health Record

```json
{
  "patient_id": "PT001",
  "heart_rate": 115,
  "oxygen_level": 90,
  "systolic_bp": 150,
  "diastolic_bp": 95,
  "notes": "Patient felt weak in the morning"
}
```

### Send Emergency Alert

```json
{
  "patient_id": "PT001",
  "message": "Patient needs immediate assistance"
}
```

## Notes for Beginners

- Start with `register.html` to create users.
- Save the generated user codes after registration.
- Login from `login.html`.
- Use those small codes in the Care Manager dashboard.
- Use Swagger docs to test backend APIs.
- Change the `SECRET_KEY` in `.env` before production use.
- This project is intentionally simple so it is easy to explain in demos and interviews.
