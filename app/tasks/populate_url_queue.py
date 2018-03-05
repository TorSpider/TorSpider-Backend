import celery
from sqlalchemy import and_, or_
from app.models import Urls, Onions, UrlQueue
from datetime import date, timedelta
from app import db


@celery.task()
def repopulate_queue():
    week_ago = (date.today() - timedelta(days=7))
    day_ago = (date.today() - timedelta(days=1))
    candidates = db.session.query(Urls.url).join(Onions).filter(
        or_(
            and_(
                Urls.fault == None,
                Urls.date < week_ago
            ), and_(
                Onions.online == True,
                Onions.tries != 0
            ), and_(
                Onions.online == False,
                Onions.scan_date < day_ago
            )
        )
    ).all()
    # Empty the current table and re-build the queue.
    # We are emptying because some of the items in there may no longer be 'good'
    # Empty the queue
    db.session.query(UrlQueue).delete()
    for candidate in candidates:
        # Let's not queue non-http urls for now.
        if not candidate.url.startswith('http'):
            continue
        try:
            # Rebuild the queue
            q = UrlQueue()
            q.url = candidate.url
            db.session.merge(q)
        except:
            db.session.rollback()
    # Commit the change, this means that we won't have committed the delete and rebuild until after it's all done
    db.session.commit()
