from celery.schedules import crontab

CELERY_IMPORTS = ('app.tasks.top20')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'app.tasks.top20.update_lists',
        # Top of every hour
        'schedule': crontab(minute="0"),
    }
}
