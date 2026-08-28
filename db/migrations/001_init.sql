-- Postgres + PostGIS initial schema for St-James-st parking app
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- roles
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL -- e.g. resident_unverified, resident_verified, admin, enforcement
);

-- users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  phone TEXT,
  role_id INTEGER REFERENCES roles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- resident verification records
CREATE TABLE resident_verifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  method TEXT NOT NULL, -- document | postcard | invite | third_party
  status TEXT NOT NULL DEFAULT 'pending', -- pending | approved | rejected
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  reviewer_id UUID REFERENCES users(id),
  review_notes TEXT
);

-- uploaded verification documents
CREATE TABLE verification_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  verification_id UUID REFERENCES resident_verifications(id) ON DELETE CASCADE,
  filename TEXT,
  s3_key TEXT, -- or storage location
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- invite codes
CREATE TABLE invite_codes (
  code TEXT PRIMARY KEY,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE,
  used_by UUID REFERENCES users(id),
  used_at TIMESTAMP WITH TIME ZONE
);

-- vehicles
CREATE TABLE vehicles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plate TEXT NOT NULL,
  make TEXT,
  model TEXT,
  color TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- spots (GeoJSON via PostGIS)
CREATE TABLE spots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code TEXT UNIQUE, -- optional human identifier
  geom GEOMETRY(Point, 4326) NOT NULL,
  street_segment TEXT,
  type TEXT, -- curb, driveway, permit, visitor
  permit_required BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_spots_geom ON spots USING GIST (geom);

-- spot status
CREATE TABLE spot_status (
  spot_id UUID PRIMARY KEY REFERENCES spots(id) ON DELETE CASCADE,
  status TEXT NOT NULL, -- free | occupied | reserved | unknown
  source TEXT, -- sensor | manual | reservation
  last_seen TIMESTAMP WITH TIME ZONE DEFAULT now(),
  details JSONB
);

-- reservations
CREATE TABLE reservations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  spot_id UUID REFERENCES spots(id),
  vehicle_id UUID REFERENCES vehicles(id),
  start_at TIMESTAMP WITH TIME ZONE NOT NULL,
  end_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT NOT NULL DEFAULT 'active', -- active | completed | cancelled | no-show
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  payment_ref TEXT
);

-- sensors
CREATE TABLE sensors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  spot_id UUID REFERENCES spots(id),
  protocol TEXT, -- mqtt | lorawan | webhook
  identifier TEXT, -- e.g. MAC or device id or topic
  last_heartbeat TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}'
);

-- telemetry events (for history)
CREATE TABLE telemetry_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sensor_id UUID REFERENCES sensors(id),
  received_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  payload JSONB
);

-- enforcement reports
CREATE TABLE enforcement_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  officer_id UUID REFERENCES users(id),
  spot_id UUID REFERENCES spots(id),
  plate TEXT,
  photo_s3_key TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  notes TEXT
);

-- audit logs
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  actor_id UUID REFERENCES users(id),
  action TEXT,
  entity_type TEXT,
  entity_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  meta JSONB
);
