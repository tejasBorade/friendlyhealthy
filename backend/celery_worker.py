"""
Celery worker configuration.
Run with: celery -A celery_worker.celery_app worker --loglevel=info
"""
from app.services.celery_tasks import celery_app

if __name__ == '__main__':
    celery_app.start()
