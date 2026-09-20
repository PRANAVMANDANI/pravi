# 🛡️ Pravi ID — Gujarat Family Identity & Beneficiary Management Platform

> **A Unified State-Level Household Identity, Scheme Eligibility Engine & Inter-Department Governance Platform.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS%20v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

---

## 📌 Executive Summary

**Pravi ID** is a Next-Generation State-Level Household Identity and Social Welfare Governance Infrastructure designed for Gujarat State. It solves the critical challenges of **duplicate beneficiary leakage**, **fragmented department siloes**, and **manual scheme enrollment overhead** by establishing a single source of truth for family units while enforcing strict data privacy and access governance.

### Key Value Pillars
1. **Unified Family 360 Record**: Single state-wide family ID (`GJ-FAM-YYYY-XXXXXXXX`) establishing relationships, demographics, and household status.
2. **Automated Scheme Eligibility Engine**: Real-time evaluation of rules (income bands, age, category, district) matching eligible families to government welfare programs.
3. **De-duplication & Identity Matching**: Fuzzy logic matching engine (Jellyfish + RapidFuzz) detecting potential duplicate citizen profiles before benefit disbursement.
4. **Data Minimization & Inter-Department Privacy**: Attribute-level scope restriction so departments (Education, Food, Health) only access fields permitted by state policy.
5. **Tamper-Evident Immutable Audit Ledger**: Every view, update, login, and scheme approval is logged for auditability and compliance.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Client Layer
        CitizenUI["👤 Citizen Portal (React / Vite)"]
        AdminUI["🏛️ Government Admin Portal (React / Vite)"]
        KioskUI["🎧 Jan Seva Kendra Operator Kiosk"]
    end

    subgraph API Gateway & Service Layer
        API["⚡ FastAPI Application (/api/v1)"]
        AuthModule["🔒 JWT Auth & RBAC Middleware"]
        RulesEngine["⚙️ Eligibility Rule Evaluation Engine"]
        MatchingEngine["🔍 Deduplication & Matching Engine (Fuzzy Matching)"]
        AuditService["📜 Immutable Audit Ledger Logger"]
    end

    subgraph Data & Storage Layer
        DB[(🐘 PostgreSQL / SQLite Database)]
        Alembic["🔄 Alembic Migration Manager"]
    end

    CitizenUI -->|HTTPS / REST| API
    AdminUI -->|HTTPS / REST| API
    KioskUI -->|HTTPS / REST| API

    API --> AuthModule
    API --> RulesEngine
    API --> MatchingEngine
    API --> AuditService

    AuthModule --> DB
    RulesEngine --> DB
    MatchingEngine --> DB
    AuditService --> DB
    Alembic --> DB
```

---

## 🔄 Core Data Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen / Kiosk Operator
    participant FE as Frontend App
    participant API as FastAPI Backend
    participant Auth as RBAC / Security
    participant Engine as Rules & Matching Engine
    participant DB as PostgreSQL Database
    participant Audit as Audit Ledger

    Citizen->>FE: Fill & Submit Family Update / Event
    FE->>API: POST /api/v1/change-requests (Bearer Token)
    API->>Auth: Validate JWT & User Role
    Auth-->>API: Authorized
    API->>DB: Save Change Request (Status: Pending)
    API->>Audit: Record Change Request Created Event
    API-->>FE: Return Request Receipt ID

    actor Officer as Verification Officer
    Officer->>FE: Open Verification Queue
    FE->>API: GET /api/v1/change-requests
    API->>DB: Fetch Pending Requests
    API-->>FE: Display Requests
    Officer->>FE: Approve Request
    FE->>API: POST /api/v1/change-requests/{id}/approve
    API->>DB: Update Family / Member Snapshot
    API->>Engine: Trigger Scheme Eligibility Re-evaluation
    Engine->>DB: Store New Eligibility Results
    API->>Audit: Log Immutable Approval Entry
    API-->>FE: Success Notification
```

---

## 🗄️ Database Schema ERD

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : "triggers"
    USERS }|--|| DEPARTMENTS : "belongs_to"
    FAMILIES ||--|{ MEMBERS : "contains"
    FAMILIES ||--o{ CHANGE_REQUESTS : "initiates"
    FAMILIES ||--o{ LIFE_EVENTS : "reports"
    FAMILIES ||--o{ ELIGIBILITY_RESULTS : "evaluated_for"
    FAMILIES ||--o{ BENEFIT_LEDGER : "receives"
    SCHEMES ||--|{ SCHEME_RULES : "defines"
    SCHEMES ||--o{ ELIGIBILITY_RESULTS : "produces"
    SCHEMES ||--o{ BENEFIT_LEDGER : "disburses"

    FAMILIES {
        string family_id PK
        string head_member_id
        string status
        string district
        string taluka
        string village_city
        string income_band
        string category
        string verification_status
        datetime created_at
    }

    MEMBERS {
        string member_id PK
        string family_id FK
        string full_name
        string gender
        date dob
        string relationship
        string aadhaar_hash
        string mobile
        boolean is_active
    }

    SCHEMES {
        int id PK
        string code UK
        string name
        string department
        string benefit_type
        decimal budget_allocated
        boolean is_active
    }

    BENEFIT_LEDGER {
        string benefit_id PK
        string family_id FK
        int scheme_id FK
        decimal amount
        string status
        datetime disbursed_at
    }

    AUDIT_LOGS {
        int id PK
        string audit_id UK
        int actor_id
        string action
        string entity_type
        string entity_id
        string description
        datetime created_at
    }
```

---

## 👥 Role-Based Access Control (RBAC) Matrix

| User Role | Credentials (Demo Password: `demo123`) | Primary Function | Access Permissions |
| :--- | :--- | :--- | :--- |
| **Citizen** | `citizen` | Household self-service | View own family, check eligible schemes, submit change requests, report life events. |
| **Verification Officer** | `verifier` | Field verification officer | Review pending change requests, resolve duplicate identity matches, approve family updates. |
| **Scheme Officer** | `scheme_officer` | Welfare program manager | Configure scheme rules, trigger state eligibility engine, track scheme disbursements. |
| **Department Officer** | `dept_officer` | Department data consumer | View scope-restricted family data filtered according to department privacy policy. |
| **State Administrator** | `admin` | Executive supervisor | Full platform oversight, state analytics, access control logs, immutable audit ledger. |
| **Assisted Operator** | `operator` | Service kiosk assistant | Help non-tech-savvy citizens submit filings and requests at local Jan Seva Kendras. |

---

## 🛡️ Security & Privacy Architecture

- **Attribute-Level Data Minimization**: Departments (Food, Health, Education) only receive fields authorized for their legal mandate. Unapproved fields (e.g. bank accounts, raw Aadhaar numbers) are redacted at the backend layer.
- **Password Security**: Passwords are hashed using `bcrypt` with `passlib`.
- **Stateless Authentication**: Signed JSON Web Tokens (JWT) with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES=480`).
- **Cryptographic Hashing**: Aadhaar numbers are hashed using SHA-256 (`aadhaar_hash`) to avoid storing plain-text identity numbers.
- **Audit Compliance**: High-level actions trigger an entry in `audit_logs` capturing actor, action, timestamp, IP address, and entity context.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **ORM & DB**: [SQLAlchemy v2](https://www.sqlalchemy.org/) with PostgreSQL / SQLite support
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Fuzzy Matching**: `jellyfish` & `rapidfuzz` for identity de-duplication
- **Security**: `python-jose` (JWT) & `passlib[bcrypt]`

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **State & Data Fetching**: [@tanstack/react-query v5](https://tanstack.com/query)
- **Icons & UI**: [Lucide React](https://lucide.dev/) & [Recharts](https://recharts.org/)

---

## ⚡ Quickstart Guide

### Prerequisites
- **Node.js** (v18+) & **npm**
- **Python** (3.10+)
- **Docker & Docker Compose** *(Optional for containerized run)*

---

### Option A: Running with Docker Compose (Recommended)

One-command setup starting PostgreSQL database, FastAPI backend, and Vite frontend:

```bash
# Clone the repository
git clone https://github.com/PRANAVMANDANI/pravi.git
cd pravi

# Start all services
docker compose up --build
```

Access the applications:
- 🌐 **Frontend Application**: `http://localhost:3000`
- 📚 **Interactive Swagger API Docs**: `http://localhost:8000/api/docs`
- 🩺 **Backend Healthcheck**: `http://localhost:8000/health`

---

### Option B: Running Locally (Manual Development)

#### 1. Backend Setup (FastAPI)

```bash
# Navigate to backend folder
cd backend

# Create & activate virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install python dependencies
pip install -r requirements.txt

# Run migrations & seed synthetic demo database
alembic upgrade head
python -m app.seed

# Start FastAPI Uvicorn development server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (React + Vite)

```bash
# Open a new terminal and navigate to frontend folder
cd frontend

# Install Node modules
npm install

# Start Vite development server
npm run dev
```

Open **`http://localhost:3000`** in your web browser.

---

## 📡 Key REST API Routes Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT token | No |
| `GET` | `/api/v1/auth/me` | Fetch active logged-in user profile | Yes |
| `GET` | `/api/v1/families` | List families with district/status filtering | Yes (Govt Roles) |
| `GET` | `/api/v1/families/{id}/360` | Comprehensive Family 360-degree profile | Yes (Govt Roles) |
| `POST` | `/api/v1/change-requests` | Submit household data change request | Yes |
| `POST` | `/api/v1/change-requests/{id}/approve` | Approve change request & update records | Yes (Verifier) |
| `GET` | `/api/v1/schemes` | List government welfare schemes & rules | Yes |
| `GET` | `/api/v1/eligibility/{family_id}` | Retrieve scheme eligibility for a family | Yes |
| `POST` | `/api/v1/identity/match` | Run deduplication fuzzy match check | Yes (Govt Roles) |
| `GET` | `/api/v1/audit` | Query immutable system audit log ledger | Yes (Admin) |
| `GET` | `/api/v1/analytics` | State-level household statistics & metrics | Yes (Admin) |

---

## 📜 License & Demo Disclaimer

This project is created as a **Prototype / Hackathon Demo**. All household data, Aadhaar hashes, and member names are completely **SYNTHETIC** and generated for demonstration purposes. This application is not connected to live government production networks.

---
*Built with ❤️ for Gujarat Social Infrastructure & Digital Governance.*
