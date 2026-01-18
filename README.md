#  Safety Haven

##  Project Overview

**Safety Haven** is a RESTful API-based platform that assesses safety compliance and estimates improvement costs for Tunisian guesthouses.  
It integrates **real-time weather data** (Open-Meteo) and **emergency facility proximity** (OpenStreetMap Overpass API) to provide property owners with actionable safety scores and detailed cost projections.

This project was developed for the **Web Services course at Tunis Business School** and demonstrates secure authentication, API-driven architecture, database modeling, and data-driven decision support.

---

##  Objectives

- Develop a RESTful API for guesthouse management
- Implement JWT-based authentication
- Design a relational database to store property and equipment data
- Integrate external APIs for weather and emergency facilities
- Implement safety assessment algorithms with environmental adjustments
- Estimate costs for equipment, installation, compliance, and maintenance
- Provide a responsive, user-friendly web interface
- Ensure security, validation, and proper error handling

---

##  System Architecture

The system follows a **three-tier client-server architecture**:

- **Frontend:** HTML5, CSS3, JavaScript (responsive)
- **Backend/API:** Flask 3.0
- **Database:** SQLite 3 (with SQLAlchemy ORM)
- **External Services:** Open-Meteo (weather), Overpass API (emergency facilities)
- **Authentication:** JWT tokens

Clients interact with the API using HTTP + JSON. Authentication and authorization are enforced for all protected endpoints.

---

##  Key Features

###  Owner Management
- Signup, login, and view profile
- JWT-secured endpoints
- One-to-many relationship: Owner → Guesthouses

###  Guesthouse Management
- Create, read, update, delete guesthouses
- Track location, building structure, floors, rooms, and safety equipment
- API gracefully handles optional fields

###  Safety Assessment
- Baseline score based on equipment and building conditions
- Dynamic adjustments for weather and proximity to emergency facilities
- Final score categorized from “Excellent” to “Critical”

###  Cost Estimation
- Calculates required equipment, labor, compliance, and maintenance
- Uses realistic Tunisian market prices for demonstration
- Provides detailed, itemized reports

---

##  API Endpoints

###  Authentication
| Method | Endpoint | Description |
|--------|---------|------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Authenticate |
| GET  | `/api/auth/me` | Get current user |

###  Guesthouses
| Method | Endpoint | Description |
|--------|---------|------------|
| POST   | `/api/guesthouses` | Create guesthouse |
| GET    | `/api/guesthouses` | List owned guesthouses |
| GET    | `/api/guesthouses/{id}` | Retrieve guesthouse details |
| PUT/PATCH | `/api/guesthouses/{id}` | Update guesthouse |
| DELETE | `/api/guesthouses/{id}` | Remove guesthouse |

###  Assessments
| Method | Endpoint | Description |
|--------|---------|------------|
| GET | `/api/guesthouses/{id}/safety-assessment` | Generate safety score |
| GET | `/api/guesthouses/{id}/cost-estimation` | Generate cost estimation |

---

##  Database Design

**Core Tables:**
- `owners`: id, name, email, password_hash, created_at
- `guesthouses`: id, owner_id, name, address, latitude, longitude, construction_year, number_of_floors, number_of_rooms, fire_extinguishers, smoke_detectors, emergency_exits, first_aid_kit, stair_features, building_type, created_at, updated_at

Relationships:
- One Owner → Many Guesthouses
- One Guesthouse → Safety assessments and cost reports

Referential integrity and constraints ensure data consistency.

---

##  Technology Stack

- **Backend:** Flask 3.0
- **Database:** SQLite 3 (SQLAlchemy ORM)
- **Authentication:** Flask-JWT-Extended 4.6
- **HTTP Requests:** Requests 2.31
- **External APIs:** Open-Meteo, OpenStreetMap Overpass API
- **Frontend:** HTML, CSS, JavaScript (responsive)
- **Containerization (optional):** Docker

---

##  How to Run the Project

```bash
git clone https://github.com/your-username/safety-haven.git
cd safety-haven

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload
