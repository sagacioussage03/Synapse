module.exports = {
  apps: [
    {
      name: "backend (Port 8000)",
      script: "../venv-Synapse/bin/uvicorn",
      args: "main:app --host 0.0.0.0 --port 8000",
      cwd: "./backend",
      interpreter: "none" 
    },
    {
      name: "frontend (Port 5173)",
      script: "npm",
      args: "run dev -- --host 0.0.0.0",
      cwd: "./frontend"
    }
  ]
};