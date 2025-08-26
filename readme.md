# Poll Application

A Django-based polling application that allows administrators to create polls with multiple options and set expiry dates. Users can vote on polls, and expired polls are automatically marked as inactive.

---

## 🚀 Features
- Admins can create polls with multiple options.
- Expiry date for each poll.
- Poll automatically becomes inactive after expiry.
- User login & authentication.
- Vote tracking and results display.


## ⚙️ Setup Instructions

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows


## Install Dependencies

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver


Admin - Superuser

User - Normal User(Access via registration)
