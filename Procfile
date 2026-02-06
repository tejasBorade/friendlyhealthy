web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.services.celery_tasks.celery_app worker --loglevel=info
