from celery.schedules import crontab

CELERY_IMPORTS = ('app.tasks.top20',
                  'app.tasks.populate_url_queue',
                  'app.tasks.parse_scans')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'update_lists': {
        'task': 'app.tasks.top20.update_lists',
        # Top of every hour
        'schedule': crontab(minute="0"),
    },
    'update_queue': {
        'task': 'app.tasks.populate_url_queue.repopulate_queue',
        # Every 5 minutes
        'schedule': crontab(minute="*/5"),
    },
    'parse_scans': {
        'task': 'app.tasks.parse_scans.parse_scan',
        # Every second
        'schedule': crontab(second="*"),
    }
}
