

# EduSense AI

EduSense AI is an AI-powered school intelligence platform that combines:

- Face-based attendance support (including ESP32-CAM integration)
- Classroom engagement monitoring (YOLO pose analysis)
- Safety/ragging alert detection
- Academic, leave, marks, and reporting workflows
- A modern React dashboard for school administrators and staff

This repository contains three major parts:

- `server/`: Django + Django REST Framework backend APIs
- `frontend/`: React + Vite dashboard
- `ESP32-CAM/`: camera firmware for attendance capture workflows

## Core Features

- Authentication with JWT (`login`, `refresh`, `me`, `logout`)
- Student registry, profile, and bulk upload flows
- Attendance APIs including manual, bulk, and camera-assisted marking
- Engagement logging, trend/history, and heatmap endpoints
- Safety alert management and stats
- Leave approval/rejection and unexcused absence notifications
- Marks, exams, subjects, results, and report generation workflows
- Notification templates, resend/test actions, and report endpoints

## Tech Stack

- Backend: Django 4.2, Django REST Framework, SimpleJWT, django-filter
- Database: MySQL
- AI/CV: OpenCV, NumPy, Ultralytics YOLO
- Frontend: React 18, Vite 5, Tailwind CSS, Recharts
- Messaging integrations: Twilio (SMS/WhatsApp), Groq (configured via env)

## Repository Structure

```text
EduSense-AI/
|- server/                    # Django backend (manage.py, settings, API app)
|- frontend/                  # React dashboard
|- models/                    # AI scripts for attendance, engagement, safety
|- ESP32-CAM/                 # ESP32 camera web server firmware
|- yolov8n.pt                 # YOLO model (person detection)
|- yolov8n-pose.pt            # YOLO pose model
|- requirements.txt
`- README.md
```

## Prerequisites

- Python 3.10+ recommended
- Node.js 18+ and npm
- MySQL 8+
- Git

## Quick Start

### 1. Clone and enter project

```bash
git clone https://github.com/zoro1324/EduSense-AI.git
cd EduSense-AI
```

### 2. Configure backend environment

Create a `.env` file in the repository root (`EduSense-AI/.env`).

Minimum recommended values:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=edusense_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

FRONTEND_URL=http://localhost:5173
```

Optional integrations/settings (supported by current backend):

- Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `TWILIO_SMS_FROM`
- Groq: `GROQ_API_KEY`
- ESP32: `ESP32_DEVICE_TOKEN`, `ESP32_FACE_MATCH_THRESHOLD`, `ESP32_DEFAULT_PERIOD`
- Engagement monitor: `ENGAGEMENT_*`
- Ragging/safety monitor: `RAGGING_*`

### 3. Set up backend

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations (from the folder that contains `manage.py`):

```bash
cd server
python manage.py migrate
```

Seed demo data:

```bash
python manage.py seed_mock_school_data
```

Start backend server:

```bash
python manage.py runserver
```

Backend base URL: `http://localhost:8000/api/`

### 4. Set up frontend

Open a new terminal at repository root, then:

```bash
cd frontend
npm install
```

Create `.env` in `frontend/` (or copy from `.env.example`) and set:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Run frontend:

```bash
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Seeded Credentials

Default seeded login credentials:

- Principal: `principal@edusense.ai` / `Password@123`
- Staff (timetable-assigned): `mentor.staff@edusense.ai` / `Password@123`
- Teachers: `*.teacher@edusense.ai` / `Password@123`

The seed command is idempotent. Re-running it updates existing seeded records and avoids duplicates for natural-keyed entities.

Useful seed options:

```bash
python manage.py seed_mock_school_data --students-per-class 30 --history-days 10
python manage.py seed_mock_school_data --dry-run
```

## Key API Areas

All endpoints are prefixed by `/api/`.

- Auth: `/auth/login/`, `/auth/refresh/`, `/auth/me/`, `/auth/logout/`
- Users: `/users/`
- Academic: `/academic/classes/`, `/academic/faculties/`, `/academic/timetable/`
- Students: `/students/`, `/students/bulk-upload/`, `/students/{id}/register-face/`
- Attendance: `/attendance/`, `/attendance/mark/`, `/attendance/camera-mark/`, `/attendance/summary/`
- Engagement: `/engagement/log/`, `/engagement/logs/`, `/engagement/history/`, `/engagement/heatmap/`
- Safety: `/safety/alerts/`, `/safety/stats/`
- Leave: `/leaves/`, `/leaves/unexcused/`, approval/rejection endpoints
- Marks/Results: `/marks/*`
- Notifications: `/notifications/*`
- Reports: `/reports/dashboard/`, `/reports/attendance/`, `/reports/engagement/`, `/reports/safety/`, `/reports/academic/`

## ESP32-CAM Integration

Firmware lives in `ESP32-CAM/CameraWebServer/`.

Typical integration flow:

- ESP32-CAM captures student image/frame
- Backend camera-attendance endpoint processes recognition and marks attendance
- Frontend reflects attendance and alerts in near real time

Set `ESP32_DEVICE_TOKEN` and related ESP32 settings in `.env` before production use.

## AI Models and Scripts

- `models/attendance/`: face registration/recognition scripts
- `models/engagements/`: engagement notebook and snapshots
- `models/raging/ragging_detection.py`: safety/ragging detection logic

Model files expected in repository/root paths include:

- `yolov8n.pt`
- `yolov8n-pose.pt`

## Common Development Commands

Backend:

```bash
cd server
python manage.py migrate
python manage.py seed_mock_school_data
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

## Notes

- Backend default auth requirement is `IsAuthenticated`; authenticate first to call protected APIs.
- CORS is configured from `FRONTEND_URL` and defaults to `http://localhost:5173`.
- Media files are served from `server/media/` via Django during development.