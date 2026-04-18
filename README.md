# Flask AI Chatbot Backend

A Flask + MongoDB backend for role-based AI chat.

## Features

- JWT-based authentication
- User profile management
- Role-based chat organization
- Chat creation, renaming, listing, and deletion
- AI chat endpoint with memory handling
- Role memory update endpoint
- Pagination for chat lists and chat messages
- Structured JSON error responses

## Tech Stack

- Flask
- MongoDB (PyMongo)
- JWT (PyJWT)
- Google Gemini API
- Gunicorn (for deployment)

## Project Structure

```text
chatbot/
├─ app.py
├─ config.py
├─ Procfile
├─ requirements.txt
├─ db/
│  └─ mongo.py
├─ models/
│  ├─ chat_model.py
│  ├─ role_model.py
│  └─ user_model.py
├─ routes/
│  ├─ ai_routes.py
│  ├─ auth_routes.py
│  ├─ chat_routes.py
│  ├─ other_routes.py
│  ├─ role_routes.py
│  └─ user_routes.py
├─ services/
│  ├─ ai_service.py
│  ├─ chat_service.py
│  ├─ memory_service.py
│  └─ role_service.py
└─ utils/
   ├─ api_errors.py
   ├─ hash.py
   ├─ id_utils.py
   ├─ jwt_handler.py
   └─ prompt_builder.py
```

## Environment Variables

Create a `.env` file in the project root and set:

- `SECRET_KEY` = Flask/JWT secret
- `DATABASE_URI` = MongoDB connection URI
- `MONGO_DB_NAME` = MongoDB Database Name
- `GEMINI_API_KEY` = primary Gemini API key
- `GEMINI_API_KEY_2` = secondary Gemini API key fallback
- `GEMINI_MODEL` = Gemini model name (default: `gemini-3-flash-preview`)
- `SHORT_TERM_MEMORY_LIMIT` = number of recent messages used as memory context

## Local Setup

1. Activate virtual environment (already created in this project):
   - Windows CMD:
     - `venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run app:
   - `python app.py`

App runs by default on:

- `http://127.0.0.1:5000`

## Render Deployment

This project includes a `Procfile`:

```text
web: gunicorn app:app
```

Typical Render setup:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

## Authentication

Protected routes require:

- Header: `Authorization: Bearer <token>`

Get token from:

- `POST /api/auth/login`

## API Routes

### Auth

- `POST /api/auth/register`
  - Body: `name`, `email`, `password`, `confirm_password`
- `POST /api/auth/login`
  - Body: `email`, `password`

### User

- `GET /api/user/profile` (auth required)
- `PUT /api/user/profile` (auth required)
  - Body:
    - `profile.name`
    - `profile.username`
    - `profile.age`
    - `profile.tags` (array)

### Health

- `GET /api/health`

### Roles

- `GET /api/roles` (auth required)
- `POST /api/roles` (auth required)
  - Body: `role_type`, `config`
- `PUT /api/roles/<role_id>` (auth required)
  - Body: `config`
- `DELETE /api/roles/delete/<role_id>` (auth required)
- `PUT /api/roles/<role_id>/memory` (auth required)
  - Body: `memory` (string or string array), optional `replace` (boolean)

### Chats

- `GET /api/roles/<role_id>/chats` (auth required)
  - Query params:
    - `page` (default 1)
    - `limit` (default 10, max 100)
  - Response includes:
    - `chat_list`
    - `pagination` object with `page`, `limit`, `total`

- `POST /api/roles/<role_id>/chats` (auth required)
  - Body: `title`

- `PUT /api/roles/<role_id>/chats/<chat_id>` (auth required)
  - Body: `title`

- `GET /api/chats/<chat_id>` (auth required)
  - Query params:
    - `page` (default 1)
    - `limit` (default 10, max 100)
  - Response includes:
    - `messages`
    - `pagination` object with `page`, `limit`, `total`

- `DELETE /api/chats/<chat_id>` (auth required)

### AI

- `POST /api/ai/chat` (auth required)
  - Body: `chat_id`, `message`

## Notes

- Assistant/default role is ensured for users when roles are listed.
- Gemini key fallback is supported using `GEMINI_API_KEY_2`.
- Keep `SECRET_KEY` and API keys private.
