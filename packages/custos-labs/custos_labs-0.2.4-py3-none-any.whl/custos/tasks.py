# custos/tasks.py

from celery import shared_task

@shared_task
def test_celery_task(name):
    return f"Hello, {name}! Celery is working!"
