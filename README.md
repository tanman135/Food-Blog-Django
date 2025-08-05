# 🍽️ Django Food Blog

A simple yet functional web application built using Django, allowing staff users to post recipes with rich content, manage drafts, and browse recipes with pagination and image support.

## ✨ Features

- 📝 Create and publish recipes
- 💾 Auto-save drafts for incomplete posts
- 📸 Upload recipe images with a fallback default image
- 🔍 View paginated list of all published recipes
- 👩‍🍳 About section for the blog creator
- 🔒 Only staff users can create or publish recipes

## 🧱 Tech Stack

- **Backend:** Django 4.x
- **Frontend:** Bootstrap 5 (via templates)
- **Database:** SQLite (default)
- **Image Handling:** Pillow
- **Form Enhancements:** django-widget-tweaks

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/django-food-blog.git
cd django-food-blog
```

### 2. Create and activate a virtual environment
```bash
python -m venv virtenv
source virtenv/bin/activate  # On Windows: virtenv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Start the server
```bash
python manage.py runserver
```

Access the site at: http://127.0.0.1:8000


---


## 👩‍🍳 Author
Tanisha Mangaonkar • K.J. Somaiya College of Engineering
## 🔗 Connect with Me
[LinkedIn](www.linkedin.com/in/tanisha-mangaonkar-484063294) • [GitHub](https://github.com/tanman135)
