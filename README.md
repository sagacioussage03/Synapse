# 🧠 Project Synapse

**Synapse** transforms an Android device into a headless, self-hosted smart hub. It acts as a **central controller** — a single dashboard that can manage, launch, and interact with other applications running on your phone-server.

Think of it as your personal command center: control hardware, monitor system health, and manage companion apps (like a cloud storage uploader) — all from any browser on your network.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Browser                         │
│              (any device on the LAN)                    │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐            ┌──────────────────┐
│  React Frontend │            │  FastAPI Backend  │
│  (Vite :5173)   │───────────▶│  (Uvicorn :8000)  │
└─────────────────┘   API      └────────┬─────────┘
                                        │
                               ┌────────┴─────────┐
                               │   Termux-API      │
                               │  (torch, tts,     │
                               │   battery, etc.)  │
                               └──────────────────┘
```

| Layer          | Tech                    |
|----------------|-------------------------|
| **Frontend**   | React 19 + Vite 7       |
| **Backend**    | Python · FastAPI + Uvicorn |
| **Hardware**   | Termux-API              |
| **App Mgmt**   | Companion apps (planned)|

---

## 📋 Prerequisites

| Requirement      | Notes                                     |
|------------------|-------------------------------------------|
| **Android phone** | Running [Termux](https://termux.dev)     |
| **Python 3.10+** | `pkg install python` in Termux            |
| **Node.js 18+**  | `pkg install nodejs` in Termux            |
| **termux-api**    | `pkg install termux-api` + install the Termux:API app from F-Droid |

---

## 🚀 Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/Synapse.git
cd Synapse
```

### 2. Create & activate a Python virtual environment

```bash
python -m venv ../venv-Synapse
source ../venv-Synapse/bin/activate
```

> The venv lives **one level above** the project root (sibling directory). This keeps the project directory clean.

### 3. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## ▶️ Running Synapse

### Using the start script (recommended)

```bash
chmod +x start.sh    # first time only
./start.sh
```

This will:
- Activate the virtual environment (or detect it's already active)
- Start the **FastAPI backend** on port `8000`
- Start the **Vite dev server** on port `5173`
- Cleanly shut down both with `Ctrl+C`

### Running manually

**Terminal 1 — Backend:**
```bash
source ../venv-Synapse/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

### Accessing the dashboard

Open a browser on any device on the same network and navigate to:

```
http://<phone-ip>:5173
```

Find your phone's IP with `ifconfig` or `termux-wifi-connectioninfo`.

---

## 📁 Project Structure

```
Synapse/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       ├── hardware.py      # Torch, TTS, vibrate endpoints
│       └── system.py        # CPU, memory, battery, network
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Router & page layout
│   │   ├── components/      # NavBar, Button, PageSection
│   │   ├── features/        # Page-level feature modules
│   │   │   ├── dashboard/
│   │   │   ├── camera/
│   │   │   ├── health/
│   │   │   └── bots/        # Apps launcher (future)
│   │   └── services/
│   │       └── api.js       # Axios API client
│   └── package.json
├── start.sh                  # One-command launcher
└── README.md
```

---

## 🔌 Adding New Apps

Synapse is designed as a **central controller**. To add a new companion app:

1. **Create a backend router** in `backend/routers/your_app.py`
2. **Register it** in `backend/main.py`: `app.include_router(your_app.router)`
3. **Add a frontend page** under `frontend/src/features/`
4. **Add a route** in `App.jsx` and a link in `NavBar.jsx`

Example idea: a **Cloud Storage** app that lets you upload images from any device to your phone-server.

---

## 📝 License

This project is for personal use. Add a license file if you plan to open-source it.