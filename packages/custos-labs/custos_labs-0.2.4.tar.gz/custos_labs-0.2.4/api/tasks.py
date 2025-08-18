# alignment/api/tasks.py
from celery import shared_task

@shared_task
def log_token_usage(token_key, endpoint):
    print(f"Used token {token_key} at {endpoint}")