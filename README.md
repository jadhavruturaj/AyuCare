# आयुCare (AyuCare) — Smart Symptom Guidance & Specialist Recommendation Platform

> **Health Today, Better Tomorrow**  
> *An educational, full-stack healthcare guidance and specialist navigation web application.*

---

## 📌 1. Project Overview & Identity

- **Project Name:** आयुCare — AyuCare
- **Tagline:** Health Today, Better Tomorrow
- **Platform Type:** Smart Symptom Guidance & Specialist Recommendation Platform
- **Academic Scope:** Educational Prototype (Second-Year Engineering Project)
- **Primary Clinical Scope:** 50 Predefined Curated Symptoms & 11 Specialist Categories

### Project Purpose & Motivation
When people feel unwell, searching online often leads to catastrophic self-diagnoses (*cyberchondria*), overwhelming jargon, and confusion regarding which medical specialist to consult. 

**AyuCare** solves this by offering:
1. **Rule-Based Preliminary Guidance:** Non-diagnostic, clear health insights.
2. **Responsible Mild Home Care:** Supportive non-pharmacological comfort measures provided **only** when clinically appropriate for mild conditions.
3. **Emergency Red-Flag Screening:** Immediate escalation of critical indicators (such as acute chest pain or slurred speech) to emergency numbers (**112 / 108 / 911**).
4. **Specialist Recommendation:** Direct mapping from symptoms to the appropriate medical field (e.g., Dermatologist, ENT, Neurologist, Cardiologist).
5. **Doctor Consultation Booking:** Patients can request consultations with verified medical practitioners.
6. **AyuBot Health Guide:** A 24/7 floating interactive assistant answering queries and navigating the platform.

> ⚠️ **Important Medical Disclaimer:**  
> AyuCare is strictly an educational prototype. It does **NOT** diagnose medical illnesses and does **NOT** prescribe medications or drug dosages. It serves solely as a navigational and preliminary care guide.

---

## 🛠️ 2. Technology Stack

- **Frontend:** HTML5, CSS3, ES6 JavaScript Modules, Three.js (3D Graphics & Animations), FontAwesome 6, Google Fonts (Poppins & Inter).
- **Backend:** Python 3, Flask REST API, PBKDF2-HMAC-SHA256 password hashing, HMAC bearer token authentication, CORS.
- **Database:** MySQL Relational Database (`ayucare_db`) with relational schema, foreign keys, and indexes. *(Includes an automated zero-config fallback to SQLite for immediate local evaluation without MySQL running).*
- **Design System:** Healthcare Blue (`#1565C0`), Dark Blue (`#0D3158`), Nature Green (`#2E7D32`), Fresh Green (`#66BB6A`), White (`#FFFFFF`), Light Blue (`#EAF5FF`), Light Green (`#EAF7EC`).

---

## 📂 3. Project Structure

```text
ayucare/
│
├── frontend/
│   ├── index.html                 # Hero page with 3D canvas, how it works, features & stats
│   ├── about.html                 # Problem definition, aim, objectives, architecture & limits
│   ├── login.html                 # Patient login with password reset modal
│   ├── register.html              # Patient registration form with validation
│   ├── doctor-login.html          # Doctor portal authentication
│   ├── doctor-register.html       # Doctor credential registration (Pending status)
│   ├── dashboard.html             # Patient dashboard: history, stats & consultations
│   ├── doctor-dashboard.html      # Doctor dashboard: request management & status updates
│   ├── symptom-checker.html       # 50-symptom triage form & detailed guidance report
│   ├── specialists.html           # 11 specialist categories & verified doctor directory
│   ├── contact.html               # Contact & feedback form with MySQL persistence
│   ├── css/
│   │   ├── style.css              # Master styling, typography, colors, animations & responsive grids
│   │   ├── dashboard.css          # Patient & doctor dashboard layout, metrics & tables
│   │   └── chatbot.css            # Floating AyuBot launcher, popup window, bubbles & chips
│   ├── js/
│   │   ├── api.js                 # Central API client, token management & toast notifications
│   │   ├── main.js                # Navbar state, mobile drawer & animated counters
│   │   ├── three-hero.js          # Three.js 3D animated heart, cross, leaves & particles
│   │   ├── symptom-checker.js     # Form handler, emergency triage & report renderer
│   │   ├── dashboard.js           # Patient dashboard controller
│   │   ├── doctor-dashboard.js    # Doctor consultation management controller
│   │   └── chatbot.js             # AyuBot interactive conversational assistant
│   └── assets/
│       └── ayucare-logo.png       # Official AyuCare project logo
│
├── backend/
│   ├── app.py                     # Flask application factory, CORS, static serving & error handling
│   ├── config.py                  # Environment configuration & DB settings
│   ├── database.py                # Dual MySQL / SQLite database connector & seeder
│   ├── requirements.txt           # Python dependencies
│   ├── routes/
│   │   ├── auth_routes.py         # Patient & doctor login/register/logout endpoints
│   │   ├── symptom_routes.py      # Symptom retrieval, triage processing & history
│   │   ├── specialist_routes.py   # Specialist categories & verified doctors list
│   │   ├── consultation_routes.py # Consultation creation, doctor status updates & notes
│   │   ├── chatbot_routes.py      # AyuBot FAQ matcher & emergency response
│   │   ├── contact_routes.py      # Contact message submission endpoint
│   │   └── profile_routes.py      # Patient & doctor dashboard statistics & profile updates
│   └── services/
│       ├── auth_service.py        # PBKDF2 hashing, HMAC tokens & role guards
│       ├── symptom_service.py     # 50-symptom dataset matcher & emergency red-flag logic
│       └── chatbot_service.py     # FAQ scoring & conversational fallback
│
├── database/
│   ├── schema.sql                 # MySQL relational schema (9 tables, FKs, indexes)
│   └── seed.sql                   # Initial seed data: 11 specialists, 50 symptoms, FAQs & sample doctors
│
├── .env.example                   # Environment configuration template
├── .env                           # Local environment configuration
├── .gitignore                     # Git exclusions
└── README.md                      # Comprehensive project guide & documentation
```

---

## 🚀 4. Step-by-Step Installation & Local Setup

Follow these exact steps to run AyuCare locally in **Visual Studio Code**:

### Prerequisites
- Python 3.10+ (tested on Python 3.12 / 3.14)
- MySQL 5.7+ / 8.0+ or MySQL Workbench *(optional: automatic fallback runs if MySQL is not yet configured)*
- Google Chrome or any modern web browser
- Visual Studio Code

---

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File** → **Open Folder...**
3. Select the `ayucare` directory.

---

### Step 2: Set Up Python Virtual Environment
Open the VS Code integrated terminal (`Ctrl + ~` or `Cmd + ~`) and run:

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate
# On Windows (PowerShell):
# venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure MySQL Database (Using MySQL Workbench)

1. Open **MySQL Workbench** and connect to your local MySQL instance (`localhost:3306`).
2. Go to **File** → **Open SQL Script...** and select `database/schema.sql`.
3. Click the **Execute (Lightning Bolt ⚡)** icon to create `ayucare_db` and all 9 tables.
4. Next, open `database/seed.sql` in MySQL Workbench.
5. Click **Execute ⚡** to populate:
   - 11 Specialist Categories
   - 50 Clinical Symptoms & Guidance
   - 10 Chatbot FAQs
   - Sample Verified Doctors
6. Refresh the MySQL Workbench schema panel to confirm the tables are populated.

---

### Step 4: Configure Environment Variables
In the project root, a `.env` file is ready. If needed, create or update `.env`:

```ini
# Flask Secret Key
SECRET_KEY=ayucare-super-secret-key-change-in-prod-2026

# Database Type: 'mysql' or 'sqlite'
DB_TYPE=mysql

# MySQL Connection Details
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ayucare_db

# Server Settings
PORT=5000
FLASK_DEBUG=True
CORS_ORIGINS=*
TOKEN_EXPIRATION_HOURS=24
```

> 💡 **Zero-Config Evaluator Feature:**  
> If MySQL is not running or your credentials are not yet configured, AyuCare's `database.py` will **automatically connect to an internal SQLite fallback** and auto-seed all 50 symptoms, specialists, and doctors. The application runs immediately without crashing!

---

### Step 5: Start the Flask Backend Server
With your virtual environment activated in `backend/`:

```bash
python app.py
```

You should see:
```text
=======================================================
  आयुCare (AyuCare) Health Platform Server
  Running at: http://localhost:5001
  Frontend:   http://localhost:5001/index.html
  API Health: http://localhost:5001/api/health
=======================================================
```

*(Note: Port 5001 is used by default because on macOS Monterey/Ventura/Sonoma/Sequoia, port 5000 is occupied by Apple's AirPlay Receiver system service).*

---

### Step 6: Access the Web Application
Open your web browser (Google Chrome) and visit:
👉 **[http://localhost:5001](http://localhost:5001)**

*(Alternatively, you can open `frontend/index.html` via VS Code Live Server on `http://127.0.0.1:5500`, and `api.js` will automatically communicate with the Flask API on port 5000).*

---

## 🔑 5. Demo / Evaluation Accounts

| Role | Email / Identifier | Password | Specialization / Features |
| :--- | :--- | :--- | :--- |
| **Verified Doctor** | `dr.rajesh@ayucare.in` | `Doctor@123` | General Physician (15 yrs exp, can accept/manage requests) |
| **Verified Doctor** | `dr.sunita@ayucare.in` | `Doctor@123` | Dermatologist (10 yrs exp) |
| **Verified Doctor** | `dr.amitav@ayucare.in` | `Doctor@123` | Orthopedic Specialist (12 yrs exp) |
| **Patient Registration** | New Patient via `/register.html` | User chosen | Full patient dashboard, history & booking |

---

## 🩺 6. The 50-Symptom Relational Dataset

AyuCare maintains 50 curated clinical symptoms mapped to 11 specialist categories:

| # | Symptom Name | Category | Urgency Level | Recommended Specialist | Mild Home-Care Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Fever** | General | Moderate | General Physician | Hydration, lukewarm sponge, rest |
| 2 | **Headache** | Neurological | Mild | Neurologist | Dim light rest, water, neck stretch |
| 3 | **Migraine** | Neurological | Moderate | Neurologist | Dark room, ice pack on temples |
| 4 | **Cough** | Respiratory | Mild | General Physician | Warm water, honey, steam inhalation |
| 5 | **Sore throat** | ENT & Eyes | Mild | ENT Specialist | Warm salt water gargles, warm teas |
| 6 | **Runny nose** | ENT & Eyes | Mild | ENT Specialist | Saline nasal spray, elevated head |
| 7 | **Sneezing** | ENT & Eyes | Mild | ENT Specialist | Avoid allergens, wash linens |
| 8 | **Nasal congestion** | ENT & Eyes | Mild | ENT Specialist | Steam inhalation, saline mist |
| 9 | **Skin rash** | Skin | Moderate | Dermatologist | Mild moisturizer, avoid scratching |
| 10 | **Itching** | Skin | Mild | Dermatologist | Lukewarm bath, fragrance-free emollient |
| 11 | **Acne** | Skin | Mild | Dermatologist | Gentle cleansing, avoid picking |
| 12 | **Dry skin** | Skin | Mild | Dermatologist | Ceramide cream, short warm showers |
| 13 | **Ear pain** | ENT & Eyes | Moderate | ENT Specialist | *Safe clinical evaluation advised* |
| 14 | **Eye redness** | ENT & Eyes | Mild | Ophthalmologist | 20-20-20 rule, cool eyelid compress |
| 15 | **Watery eyes** | ENT & Eyes | Mild | Ophthalmologist | Sunglasses, gentle eyelid washing |
| 16 | **Stomach pain** | Digestive | Moderate | Gastroenterologist | Ginger tea, light bland meals |
| 17 | **Nausea** | Digestive | Mild | Gastroenterologist | Chilled clear fluids, upright rest |
| 18 | **Vomiting** | Digestive | Moderate | Gastroenterologist | Small frequent sips of ORS |
| 19 | **Diarrhea** | Digestive | Moderate | Gastroenterologist | Continuous ORS rehydration |
| 20 | **Constipation** | Digestive | Mild | Gastroenterologist | Increase dietary fiber, water, walking |
| 21 | **Indigestion** | Digestive | Mild | Gastroenterologist | Smaller meals, chew slowly |
| 22 | **Bloating** | Digestive | Mild | Gastroenterologist | Peppermint/fennel tea, 15m walk |
| 23 | **Joint pain** | Musculoskeletal | Moderate | Orthopedic Specialist | Rest, ice/heat compress, gentle motion |
| 24 | **Back pain** | Musculoskeletal | Mild | Orthopedic Specialist | Ergonomic support, gentle activity |
| 25 | **Neck pain** | Musculoskeletal | Mild | Orthopedic Specialist | Slow neck rolls, screen at eye level |
| 26 | **Shoulder pain** | Musculoskeletal | Mild | Orthopedic Specialist | Cold pack first 48h, pendular swing |
| 27 | **Knee pain** | Musculoskeletal | Mild | Orthopedic Specialist | R.I.C.E protocol (Rest, Ice, Elevate) |
| 28 | **Muscle cramps** | Musculoskeletal | Mild | Orthopedic Specialist | Calf stretch, electrolytes, hydration |
| 29 | **Fatigue** | General | Mild | General Physician | 7-8 hours sleep, natural daylight |
| 30 | **Dizziness** | Neurological | Moderate | Neurologist | Rise slowly, drink water, sit down |
| 31 | **Loss of appetite** | Digestive | Mild | General Physician | Small nutrient-dense soups/fruit |
| 32 | **Mild dehydration** | General | Mild | General Physician | Water, ORS, watermelon, cucumber |
| 33 | **Allergy symptoms** | ENT & Eyes | Mild | General Physician | Avoid allergen, HEPA air filtration |
| 34 | **Sunburn** | Skin | Mild | Dermatologist | Cool compress, aloe vera, extra fluids |
| 35 | **Minor burn** | Skin | Mild | Dermatologist | Cool running water 10-15m, aloe vera |
| 36 | **Insect bite** | Skin | Mild | Dermatologist | Soap and water, cold pack, calamine |
| 37 | **Motion sickness** | General | Mild | General Physician | Horizon focus, fresh air, ginger tea |
| 38 | **Hiccups** | Digestive | Mild | General Physician | Ice cold water, hold breath 15s |
| 39 | **Bad breath** | Dentistry | Mild | Dentist | Brush 2m twice daily, floss, scrape tongue |
| 40 | **Tooth sensitivity** | Dentistry | Mild | Dentist | Soft toothbrush, desensitizing paste |
| 41 | **Bleeding gums** | Dentistry | Moderate | Dentist | Gentle brushing, warm salt rinse |
| 42 | **Mouth ulcer** | Dentistry | Mild | Dentist | Salt water rinse, raw honey dab |
| 43 | **Chapped lips** | Skin | Mild | Dermatologist | Petroleum jelly or beeswax balm |
| 44 | **Dry eyes** | ENT & Eyes | Mild | Ophthalmologist | Frequent blinking, artificial tears |
| 45 | **Hoarseness** | ENT & Eyes | Mild | ENT Specialist | Voice rest (no whispering), steam |
| 46 | **Mild anxiety** | Mental Health | Mild | Psychiatrist | 4-7-8 breathing, brisk walk, limit caffeine |
| 47 | **Sleep difficulty** | Mental Health | Mild | Psychiatrist | Fixed sleep schedule, no screens 1h |
| 48 | **Mild leg swelling**| General | Moderate | General Physician | Elevate legs on pillows, reduce salt |
| 49 | **Menstrual cramps** | Women Health | Mild | Gynecologist | Warm heating pad, gentle yoga, ginger tea |
| 50 | **Cold hands** | General | Mild | General Physician | Warm gloves, lukewarm water, avoid smoking |

---

## 🔒 7. Security & Privacy Features

- **Password Hashing:** Passwords hashed using PBKDF2 with HMAC-SHA256 and unique 16-byte random salts.
- **Role-Based Authorization:** Strict boundary separation between Patient and Doctor routes.
- **Doctor Privacy Isolation:** Doctors can **only** inspect consultation records requested with their own practice. No public or unrelated patient records are exposed.
- **SQL Injection Defense:** All queries utilize parameterized `%s` statements.
- **CORS Configuration:** Configurable origins to avoid unauthorized cross-site requests.

---

## 🤖 8. AyuBot – Your Health Guide Capabilities

AyuBot provides 24/7 intelligent platform navigation and guidance:
- Explains how AyuCare works.
- Guides users on entering duration and severity.
- Recommends specialist categories based on user queries.
- Directs users to the appropriate registration or symptom checker pages.
- Detects emergency triggers (e.g., chest pain, stroke signs) and immediately escalates to **112 / 108 / 911**.
- Highlights that AyuCare is an educational tool and not a diagnosis platform.

---

## 🧪 9. Automated Testing Suite

To run the automated test suite verifying all 10 project phases:

```bash
# In the backend directory with venv activated
python -c "
import sys
from app import create_app
app = create_app()
client = app.test_client()

# 1. Health check
res = client.get('/api/health')
assert res.status_code == 200, 'Health check failed'

# 2. Symptoms dataset verification
res = client.get('/api/symptoms')
assert res.get_json()['count'] == 50, 'Symptoms count mismatch'

# 3. Specialist count verification
res = client.get('/api/specialists')
assert len(res.get_json()['specialists']) == 11, 'Specialists count mismatch'

# 4. Chatbot response verification
res = client.post('/api/chatbot/message', json={'message': 'How does AyuCare work?'})
assert res.get_json()['data']['sender'] == 'AyuBot', 'Chatbot failed'

# 5. Symptom check triage verification
res = client.post('/api/symptoms/check', json={
    'symptom_name': 'Headache',
    'duration': '2 days',
    'severity': 'Mild',
    'description': 'Tension headache'
})
assert res.status_code == 200, 'Triage check failed'

print('All automated tests passed successfully!')
"
```

---

## 🎓 10. Student Project Defense Highlights

When presenting this project to an examiner or professor:
1. **Explain the Architecture:** Point out the clean 3-tier separation (`frontend/`, `backend/`, `database/`).
2. **Demonstrate 3D WebGL Hero:** Showcase the interactive Three.js floating heart with heartbeat scaling, rotating cross, drifting leaves, and mouse parallax.
3. **Demonstrate the Symptom Checker:** Show how selecting "Severe" or typing "chest pain" immediately triggers the **EMERGENCY WARNING** before routine home-care advice.
4. **Demonstrate Doctor Workflow:** Log in as `dr.rajesh@ayucare.in` (`Doctor@123`), review a patient's consultation request, accept it, write clinical notes, and switch back to the patient dashboard to show the live status update.
5. **Demonstrate AyuBot:** Click the floating circular AyuBot launcher, click a suggested question chip, and demonstrate its safety disclaimer.

---

## 📄 License & Attribution
Developed for educational software engineering demonstration.  
Official AyuCare Logo & Brand Identity &copy; 2026 AyuCare. All rights reserved.
