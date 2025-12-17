# from celery import Celery

# celery_app = Celery(
#     "document_worker",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/1",
#     include=["app.tasks.document_tasks"]
# )

# celery_app.conf.timezone = "UTC"

# celery_app.conf.beat_schedule = {
#     "classify-documents-every-5-minutes": {
#         "task": "app.tasks.document_tasks.process_documents",
#         "schedule": 300.0,  # 5 minutes
#     }
# }
