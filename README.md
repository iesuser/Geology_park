# Geological Museum — Flask App

A bilingual (English / Georgian) museum web app for displaying geological specimens with QR codes.

## Features

- **Public home page** — grid of specimen cards from the database
- **Detail pages** — `/1`, `/2`, etc. (stable IDs for QR codes)
- **Admin panel** — `/admin` (login required) to create and edit specimens
- **No delete** — specimens can be hidden instead, preserving QR codes
- **Optional fields** — photos, titles, and descriptions are all optional
- **QR codes** — auto-generated on creation, pointing to `BASE_URL/{id}`
- **File cleanup** — removing a photo during edit deletes it from disk

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set FLASK_SECRET_KEY, ADMIN_PASSWORD, BASE_URL

# 4. Run
python run.py
```

Open http://localhost:5000 for the collection.  
Admin login: http://localhost:5000/auth/login (then `/admin`).

## Project Structure

```
app/
├── __init__.py          # App factory (create_app)
├── config.py            # Settings from .env
├── extensions.py        # db, login_manager, csrf
├── models.py            # Artifact model
├── auth/routes.py       # Login / logout
├── main/routes.py       # Home + specimen detail
├── admin/
│   ├── routes.py        # Create / edit specimens
│   └── forms.py         # WTForms validation
├── services/
│   ├── file_service.py  # Upload & delete images
│   └── qr_service.py    # QR code generation
├── templates/           # Jinja2 HTML
└── static/
    ├── css/style.css
    └── uploads/         # Photos & QR codes
instance/museum.db       # SQLite database (auto-created)
run.py                   # Entry point
```

## Configuration (.env)

| Variable | Description |
|----------|-------------|
| `FLASK_SECRET_KEY` | Session signing key (use a long random string) |
| `ADMIN_USERNAME` | Admin login username |
| `ADMIN_PASSWORD` | Admin login password |
| `BASE_URL` | Public URL used in QR codes (e.g. `https://museum.example.com`) |
| `DATABASE_URL` | SQLAlchemy URI (default: SQLite in `instance/`) |

## How to Modify

### Change styling
Edit `app/static/css/style.css`. CSS variables at the top control colors.

### Change page layout
- Home: `app/templates/main/index.html`
- Specimen detail: `app/templates/main/artifact.html`
- Admin: `app/templates/admin/`

### Add a new field to specimens
1. Add column in `app/models.py` (`Artifact` class)
2. Add form field in `app/admin/forms.py`
3. Handle in `app/admin/routes.py` (create + edit)
4. Display in `app/templates/main/artifact.html` and admin templates

After model changes, delete `instance/museum.db` and restart (or use Flask-Migrate for production).

### Change QR code target URL
QR URLs are built in `app/services/qr_service.py` using `BASE_URL` from config.  
Set `BASE_URL` in `.env` to your production domain before creating specimens.

### Change authentication
Credentials are in `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`).  
Logic is in `app/auth/routes.py` and `app/extensions.py`.

### Switch to PostgreSQL (production)
Set in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost/museum
```

### Hide instead of delete
Set `is_active = False` on edit. Hidden specimens are excluded from the home page but remain at `/id` if someone has the QR link.

## Security

- CSRF protection on all forms (Flask-WTF)
- Admin routes require login (`@login_required`)
- File uploads restricted by extension and size (10 MB)
- Secrets in `.env` (never commit `.env`)

## Production Notes

- Set `FLASK_DEBUG=0`
- Use a strong `FLASK_SECRET_KEY` and `ADMIN_PASSWORD`
- Serve with Gunicorn + Nginx
- Set `BASE_URL` to your real domain before generating QR codes
- Back up `instance/museum.db` and `app/static/uploads/`
