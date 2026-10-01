# MediExtract AI - Clinical Note Classification & Medical Information Extraction System

MediExtract AI is an AI-powered healthcare application designed to process unstructured clinical notes, discharge summaries, and medical records. It automatically extracts key medical entities, classifies notes into hospital departments, predicts ICD-10 diagnostic codes, and indexes records in **MongoDB Atlas** for search, filtering, and analytics.

---

## 🌟 Key Features

1. **User Authentication & Authorization**:
   - Secure registration and login using JWT (JSON Web Tokens) with hashed password storage.
   - Protected endpoints and isolated user patient histories.

2. **Multi-Modal Note Intake**:
   - Direct text pasting with sample clinical note loader.
   - Document upload for `.txt` and `.pdf` files.
   - Voice Dictation using the Web Speech API.

3. **AI & Medical NLP Entity Extraction (spaCy)**:
   - **Patient Details**: Name, Age, Gender.
   - **Diagnoses & Conditions**: Type 2 Diabetes, Unstable Angina, Essential Hypertension, Asthma, GERD, Stroke, etc.
   - **Symptoms**: Chest pain, Shortness of breath, Cough, Fever, Dizziness, Fatigue, etc.
   - **Medications & Dosages**: Metformin 500mg, Aspirin 325mg, Omeprazole, Lisinopril, Metoprolol, etc.
   - **Treatments & Lab Tests**: ECG/EKG, Cardiac enzymes, X-ray, MRI, Blood tests, CT scan, Biopsy, etc.
   - **Allergies**: Penicillin, Sulfa, NSAIDs, etc.

4. **Dynamic Department Classification & ICD-10 Prediction**:
   - Automatically maps clinical notes into departments: **Cardiology**, **Endocrinology**, **Pulmonology**, **Gastroenterology**, **Neurology**, **Orthopedics**, **Oncology**, or **General Medicine**.
   - Predicts standard **ICD-10 diagnostic codes** (e.g., `I20.9` for Unstable Angina, `E11.9` for Diabetes, `J45.909` for Asthma, `I10` for Hypertension, `K21.9` for GERD).
   - Computes dynamic confidence scores based on entity completeness.

5. **MongoDB Atlas Integration (Dual Database Support)**:
   - Asynchronous database operations powered by Motor (`AsyncIOMotorClient`).
   - Connects directly to **MongoDB Atlas** when `MONGODB_URL` is configured in `.env`.
   - Automatically falls back to a local SQLite database (`data/mediextract.db`) for offline testing or local development.
   - Real-time MongoDB status indicator badge in the frontend UI.

6. **Search & Filter Patient Records**:
   - Search patient records by keyword, patient name, diagnosis, medication, or department.
   - Filter records by department and diagnosis.
   - Detailed modal view displaying complete note text and extracted entities.
   - Delete report capability.

7. **Reports & Analytics Dashboard**:
   - Visual summary metrics: Total Notes, Unique Patients, Active Departments, Average Confidence Score.
   - Department distribution progress bars.
   - Ranked lists for Top Diagnoses, Common Symptoms, and Top Prescribed Medications.

---

## 🛠️ Tech Stack

- **Frontend**: React 19, Vite, Modern Responsive CSS.
- **Backend**: Python 3.13, FastAPI, Uvicorn, PyJWT.
- **AI & NLP**: spaCy (`en_core_web_sm`), Regex Clinical NER, PyPDF parser.
- **Database**: MongoDB Atlas (Async Motor client), SQLite fallback.
- **Testing**: pytest, FastAPI TestClient.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```env
APP_NAME=MediExtract AI
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key-here
MONGODB_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DATABASE_NAME=mediextract
```

### 3. Backend Setup
```bash
# Install backend dependencies
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm

# Run FastAPI backend server
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
# Install frontend dependencies and start development server
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

Run the automated backend pytest test suite covering authentication, extraction, department classification, ICD-10 prediction, report search/filter, analytics calculation, and deletion:
```bash
python -m pytest
```

## 🤖 Training the Diagnosis Model

The supplied `dataset/medical_data.csv` is a de-identified MIMIC-style discharge-summary dataset. It contains 744 complete notes, but 434 diagnosis labels; most labels are too rare for reliable supervised learning. The training script therefore keeps the 23 diagnosis classes with at least 5 examples.

Run:
```bash
python ml/train_diagnosis_model.py
```

The script trains a TF-IDF word n-gram model with balanced logistic regression and writes `models/diagnosis_classifier.joblib` plus evaluation metrics. The current held-out result is 44.4% accuracy, 0.365 macro-F1, and 0.415 weighted-F1. The model is an experimental fallback only: the existing clinical rules remain primary, and no model artifact or clinical CSV is committed by default.

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check & MongoDB Atlas status |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate user & issue JWT token |
| `GET` | `/auth/me` | Get current user profile |
| `POST` | `/extraction/` | Extract medical entities from text payload |
| `POST` | `/extraction/file` | Extract medical entities from uploaded `.txt` or `.pdf` |
| `POST` | `/reports/` | Save extracted report to MongoDB Atlas / SQLite |
| `GET` | `/reports/` | Query/search/filter reports (`?search=`, `?department=`, `?diagnosis=`) |
| `GET` | `/reports/analytics` | Get analytics metrics for dashboard |
| `GET` | `/reports/{id}` | Get single report details |
| `DELETE` | `/reports/{id}` | Delete report |

---

## 📄 License

MIT License
