# St-James-st Parking App Setup Guide

## Quick Start

### 1. Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS extension
- pip/virtualenv

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb stjames

# Enable PostGIS extension
psql -d stjames -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -d stjames -c "CREATE EXTENSION IF NOT EXISTS uuid-ossp;"

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stjames"

# Initialize schema (FastAPI app will do this on startup)
```

### 4. Seed Initial Data

```bash
# Add roles and invite codes to database
python3 scripts/seed_db.py
```

Output:
```
Seeded roles and invite codes:
 - J7K9L2X4QZ
 - M3V8R1T6SB
```

### 5. Start the Server

```bash
uvicorn main:app --reload
```

Server will be available at: **http://localhost:8000**

API docs (interactive): **http://localhost:8000/docs**

### 6. Test the API

In another terminal:

```bash
python3 scripts/test_api.py
```

This will:
- ✓ Check health endpoint
- ✓ Sign up a test user
- ✓ Login and get JWT token
- ✓ List parking spots
- ✓ Test verification flow
- ✓ Create a reservation

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create user account
- `POST /api/auth/login` - Login and get JWT token

### Verification
- `POST /api/verification/request` - Request verification (method: document/postcard/invite/third_party)
- `POST /api/verification/redeem-invite` - Redeem invite code to become verified resident

### Spots
- `GET /api/spots` - List all parking spots (GeoJSON format)
- `GET /api/spots?bbox=minLon,minLat,maxLon,maxLat` - List spots in bounding box

### Reservations
- `POST /api/reservations` - Create new reservation (verified residents only)

### Health
- `GET /health` - Health check

---

## Project Structure

```
St-James-st/
├── main.py                 # FastAPI app entry point
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic request/response schemas
├── auth_utils.py           # JWT & password utilities
├── database.py             # Database configuration
├── dependencies.py         # FastAPI dependency injection
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── openapi.yaml            # API specification
├── db/
│   └── migrations/
│       └── 001_init.sql    # PostgreSQL schema
└── scripts/
    ├── seed_db.py          # Seed initial roles & invites
    └── test_api.py         # Integration test suite
```

---

## Key Features

✅ **Authentication**: JWT-based with bcrypt password hashing
✅ **Resident Verification**: Multiple methods (invite codes, documents, postcards)
✅ **Geospatial**: PostGIS support for parking spot locations
✅ **Reservations**: Time-based parking spot booking with conflict detection
✅ **Role-based Access**: Different permissions for residents, admin, enforcement

---

## Environment Variables

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration

---

## Troubleshooting

### "psycopg2 is required"
```bash
pip install psycopg2-binary
```

### "Connection refused" (database)
Ensure PostgreSQL is running:
```bash
psql -U postgres -d stjames
```

### "PostGIS extension not found"
Enable it manually:
```bash
psql -d stjames -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### "Module not found" errors
Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

1. **Add email verification** - Send verification emails for signup
2. **Implement admin dashboard** - Streamlit or React frontend
3. **Add sensor integration** - MQTT/LoRaWAN for real-time spot status
4. **Payment processing** - Stripe or similar for premium features
5. **Deploy** - Docker, Heroku, AWS, etc.
