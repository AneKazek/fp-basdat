# Crypto Monitoring Dashboard

Project monitoring website berbasis file/database dengan tampilan modern dan fitur real-time.

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS v4, Redux Toolkit, Chart.js.
- **Backend:** FastAPI, SQLAlchemy, PyMySQL.
- **Database:** MySQL (InnoDB Engine).

## Project Structure

- `/frontend`: React application source code.
  - `/src/components/layout`: Sidebar, Header, MainLayout.
  - `/src/pages`: Dashboard and other pages.
  - `/src/types`: TypeScript interfaces matching the Database schema.
- `/app`: FastAPI backend.
  - `/models/sql_models.py`: SQLAlchemy ORM models mapping `contohDatabase.sql`.
  - `/database.py`: Database connection setup.

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.10+
- MySQL Database

### 1. Database Setup
Import `contohDatabase.sql` into your MySQL server:
```bash
mysql -u root -p fp_basdat < contohDatabase.sql
```

### 2. Backend Setup
Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

Configure `.env` file with your database credentials:
```env
DATABASE_URL="mysql+pymysql://user:password@localhost:3306/fp_basdat"
```

Run the server:
```bash
uvicorn app.main:app --reload --port 8001
```

### 3. Frontend Setup
Navigate to frontend directory and install dependencies:
```bash
cd frontend
npm install
```

Run the development server:
```bash
npm run dev
```

Access the application at `http://localhost:5173`.

## Features Implemented
- **Dashboard UI:** Replicated "Akademi Crypto" design with Blue/Green theme.
- **Real-time Charts:** Mocked WebSocket behavior for live transaction updates.
- **Responsive Layout:** Sidebar and Header adapt to mobile/desktop.
- **Database Integration:** SQLAlchemy models ready for connection.
