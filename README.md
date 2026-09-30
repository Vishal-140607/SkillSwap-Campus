# SkillSwap (DjangoLab)

A peer-to-peer skill exchange platform for students. Users list skills they
can teach or want to learn, browse other students, send learning requests,
accept/reject them, receive real-time notifications, and leave reviews after
a completed exchange.

## Features

- User registration & authentication
- Student profiles (department, year, bio)
- Add/remove skills you can teach or want to learn
- Explore page to search and find other students by skill
- Learning requests (send / accept / reject)
- Real-time notifications via Django Channels (WebSockets)
- Reviews & ratings after an accepted exchange

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```
   python manage.py migrate
   ```

4. Create an admin account (used to add Skills via /admin):
   ```
   python manage.py createsuperuser
   ```

5. Run the server:
   ```
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/`, then log into `http://127.0.0.1:8000/admin/`
   to add a few Skills (e.g. Python, Guitar, Photography) before testing the
   Explore and Manage Skills pages.

## Tech stack

- Django 6.1.1
- Django Channels (WebSocket notifications)
- SQLite (default dev database)
