# EduSense-AI

## Mock Seed Data

The backend now includes a full mock data seed command that populates users, classes, timetable, students, attendance, engagement, marks, leave, safety, and notifications.

Run from `server/`:

```bash
python manage.py seed_mock_school_data
```

Useful options:

```bash
python manage.py seed_mock_school_data --students-per-class 20 --history-days 5
python manage.py seed_mock_school_data --dry-run
```

Default seeded login credentials:

- Principal: `principal@edusense.ai` / `Password@123`
- Staff (timetable-assigned): `mentor.staff@edusense.ai` / `Password@123`
- Teachers: `*.teacher@edusense.ai` / `Password@123`

The command is idempotent. Re-running it updates existing seeded records and does not create duplicates for natural-keyed entities.