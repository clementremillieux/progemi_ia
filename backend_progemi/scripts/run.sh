sudo lsof -i :8000 | awk '{print $2}' | grep -v PID | xargs kill -9

poetry run uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload --workers 4