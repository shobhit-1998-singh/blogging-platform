# Blogging Platform — Backend API

A production-grade blogging platform REST API built with **Flask** and **MongoDB Atlas**, inspired by Medium. Designed with clean architecture, separation of concerns, and team development in mind.

---

##  Project Status

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Authentication (Signup, Login, Forgot Password) | ✅ Complete |
| 2 | User Profile + Cloudinary Image Upload | 🔄 In Progress |
| 3 | Blog CRUD + Interest-based Feed | ⬜ Planned |
| 4 | Engagement (Likes, Comments, Share) | ⬜ Planned |
| 5 | Social (Follow System, Social Feed) | ⬜ Planned |
| 6 | Search | ⬜ Planned |
| 7 | Google OAuth | ⬜ Planned |
| 8 | Real-time Chat (WebSockets) | ⬜ Planned |
| 9 | Docker + Deployment | ⬜ Planned |

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Framework | Flask + Flask-Classful |
| Database | MongoDB Atlas (M0 Free Tier) |
| Authentication | JWT (flask-jwt-extended) |
| Password Hashing | Werkzeug (pbkdf2:sha256) |
| Email | Flask-Mail (Gmail SMTP) |
| Media Storage | Cloudinary |
| Environment | python-dotenv |

---

##  Architecture

```
BLOGGING-BACKEND/
├── src/
│   ├── actions/          # Business logic — one action per feature
│   ├── models/           # Database operations — one model per collection
│   ├── routes/           # URL routing — maps endpoints to actions
│   └── utils/            # Shared utilities (mail, response, helpers)
├── docs/                 # Phase-by-phase technical documentation
├── config.py             # Centralized configuration
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

**Design Principles:**
- `actions/` — WHAT to do (business logic, validation, flow control)
- `models/` — HOW to store (all DB queries live here only)
- `routes/` — WHERE to expose (URL mapping, no logic)
- `utils/`  — Shared helpers (mail, responses, constants)

---



### Prerequisites
- Python 3.10+
- MongoDB Atlas account (free tier works)
- Gmail account with App Password enabled
- Cloudinary account (free tier works)

### 1. Clone the repository
```bash
git clone https://github.com/shobhit-1998-singh/blogging-platform.git
cd blogging-platform
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Fill in your credentials in `.env` (see Environment Variables section below).

### 5. Run the server
```bash
python3 main.py
```

Server starts at `http://localhost:5001`

---

## Environment Variables

Create a `.env` file in the project root. **Never commit this file.**

```env
# Flask
SECRET_KEY=your_flask_secret_key

# JWT
JWT_SECRET_KEY=your_jwt_secret_key

# MongoDB Atlas
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/blogging_db

# Gmail SMTP
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App Passwords → Generate one for "Mail".

> **MongoDB Atlas:** Whitelist your IP in Network Access → Add IP Address → Allow from Anywhere (0.0.0.0/0) for development.

---

##  API Reference

**Base URL:** `http://localhost:5001`  
**Content-Type:** `application/json`  
**Auth Header:** `Authorization: Bearer <jwt_token>`

---

###  Authentication

#### Signup Flow (3 Steps)

**Step 1 — Submit Email**
```
POST /user/signup
Body: { "email": "ram@gmail.com" }
```

**Step 2 — Verify OTP**
```
POST /user/verify-otp
Body: { "email": "ram@gmail.com", "otp": "847291" }
```

**Step 3 — Set Password**
```
POST /user/complete-signup
Body: { "email": "ram@gmail.com", "password": "Secure@123" }
```

Password requirements: 8+ chars, uppercase, lowercase, number, special character.

---

#### Login
```
POST /api/user/login
Body: { "email": "ram@gmail.com", "password": "Secure@123" }

Response:
{
  "status": "success",
  "message": "Login successful.",
  "data": {
    "token": "eyJhbGci...",
    "user": {
      "id": "64abc123",
      "email": "ram@gmail.com",
      "profile_completed": false
    }
  }
}
```

> Token expires in **24 hours**. Use `profile_completed` to redirect user to profile setup if `false`.

---

#### Forgot Password Flow (3 Steps)

**Step 1 — Request Reset OTP**
```
POST /user/forgot-password
Body: { "email": "ram@gmail.com" }
```

**Step 2 — Verify Reset OTP**
```
POST /user/verify-reset-otp
Body: { "email": "ram@gmail.com", "otp": "391047" }
```

**Step 3 — Set New Password**
```
POST /user/reset-password
Body: { "email": "ram@gmail.com", "password": "NewSecure@456" }
```

---

###  User Profile *(Phase 2 — In Progress)*

```
POST /user/profile         → Save/update profile    🔒 JWT required
GET  /user/profile         → Get own profile        🔒 JWT required
POST /user/profile/avatar  → Upload profile picture 🔒 JWT required
GET  /user/:id/profile     → Get public profile     Public
```

---

###  Blog *(Phase 3 — Planned)*

```
POST   /blog/create        → Create blog            🔒 JWT required
PUT    /blog/:id           → Update blog            🔒 JWT required
DELETE /blog/:id           → Delete blog            🔒 JWT required
GET    /blog/:id           → Get single blog        Public
GET    /blog/feed          → Interest-based feed    🔒 JWT required
```

---

###  Engagement *(Phase 4 — Planned)*

```
POST   /blog/:id/like        → Like/Unlike toggle   🔒 JWT required
POST   /blog/:id/comment     → Add comment          🔒 JWT required
DELETE /blog/:id/comment/:id → Delete comment       🔒 JWT required
GET    /blog/:id/comments    → Get comments         Public
```

---

###  Social *(Phase 5 — Planned)*

```
POST /user/:id/follow      → Follow/Unfollow toggle 🔒 JWT required
GET  /user/:id/followers   → Followers list         Public
GET  /user/:id/following   → Following list         Public
GET  /feed/following       → Followed users feed    🔒 JWT required
```

---

## Database Collections

| Collection | Purpose | Status |
|-----------|---------|--------|
| `users` | Registered verified users | ✅ Active |
| `pending_signups` | Temporary OTP records during signup | ✅ Active |
| `blogs` | Blog posts | ⬜ Phase 3 |
| `comments` | Blog comments | ⬜ Phase 4 |
| `likes` | Blog likes | ⬜ Phase 4 |
| `follows` | User follow relationships | ⬜ Phase 5 |
| `messages` | Chat messages | ⬜ Phase 8 |

---

## Documentation

Detailed technical documentation for each phase is in the `/docs` folder:

| File | Coverage |
|------|---------|
| `docs/phase-1-auth.md` | Auth system — all APIs, DB schema, business logic, testing checklist |
| `docs/phase-2-user-profile.md` | Profile, Cloudinary, interests, social links *(coming soon)* |

---

##  Security Features

- Passwords hashed with `pbkdf2:sha256` + salt
- JWT tokens signed with `HS256`
- OTPs generated with `secrets` module (cryptographically secure)
- OTPs expire after 10 minutes
- Generic error messages on sensitive routes (prevents email enumeration)
- Sensitive fields (`password`, `otp`) never returned in API responses
- `.env` excluded from version control

---

##  Git Workflow

```bash
# Feature branch workflow
git checkout -b feat/blog-crud
git add .
git commit -m "feat: add blog create and update endpoints"
git push origin feat/blog-crud
```

**Commit message convention:**
```
feat:     new feature
fix:      bug fix
docs:     documentation
refactor: code restructure
chore:    maintenance
```

---

## Contributing

1. Clone the repo
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Follow the existing architecture pattern (actions → models → routes)
4. Add documentation to the relevant `docs/phase-X.md` file
5. Test all endpoints in Postman before pushing
6. Submit a pull request with clear description

---

##  License

MIT License — see [LICENSE](LICENSE) file for details.

---

## Author

**Shobhit Singh**  
[GitHub](https://github.com/shobhit-1998-singh)

---

> Built with focus on production-grade architecture, clean code, and team collaboration.