

# MathForStudent

MathForStudent is an educational application designed to help students from Grade 9 to University solve academic questions.

## Subjects
- Mathematics
- Physics
- Chemistry
- Computer Science

## Features
- Type academic questions.
- Upload question photos.
- Receive step-by-step explanations.
- Use specialist calculation engines.
- Use AI assistance when configured.
- Register and log in.
- Save question history and learning progress.
- Installable Progressive Web App (PWA).

## Technology
- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Database: SQLite for local development, PostgreSQL for deployment
- Calculations: SymPy and specialist subject engines
- AI: OpenAI API (optional configuration)

## Installation

1. Install Python 3.11 or newer.
2. Create a virtual environment:

   `python -m venv .venv`

3. Activate it:

   Linux/Termux:
   `source .venv/bin/activate`

   Windows:
   `.venv\Scripts\activate`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Copy `.env.example` to `.env`.
6. Configure your secret key and optional AI API key.
7. Start the application:

   `python -m backend.app`

8. Open:

   `http://127.0.0.1:5000`

## Testing

Run:

`pytest -q`

## Photo Questions

Photo text extraction requires Tesseract OCR to be installed on the operating system, in addition to the Python package.

## Deployment

Before public deployment:
- Configure PostgreSQL.
- Set a strong SECRET_KEY.
- Configure HTTPS.
- Configure secure session cookies and CSRF protection.
- Restrict CORS to trusted origins.
- Configure production logging and database migrations.
- Add real PWA icons.
- Test all API routes and subject engines.

## Important

AI answers and specialist engines must be checked. The application should request missing information rather than inventing an answer.
