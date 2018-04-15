import celery
from sqlalchemy import and_, or_
from app.models import Urls, Onions, UrlQueue
from datetime import date, timedelta
from app import db


@celery.task()
def repopulate_queue():
    # This process is expensive and slows other queries down.  Let's no do it without a reason.  If we still have 100
    # urls left in the queue, we do nothing...if it's close to empty, we can do something
    url_count = db.session.query(UrlQueue.url).count()
    if url_count > 100:
        # Do nothing
        return True
    # Empty the current table and re-build the queue.
    # We are emptying because some of the items in there may no longer be 'good'
    # Empty the queue
    db.session.query(UrlQueue).delete()
    week_ago = (date.today() - timedelta(days=7))
    day_ago = (date.today() - timedelta(days=1))
    # Force unscanned onions first, so we can get better statistics about which onions are online if we find new ones
    unscanned_onions = db.session.query(Onions).filter(
        Onions.scan_date == date(1900, 1, 1)
    ).limit(1000).all()
    unscanned_list = []
    for onion in unscanned_onions:
        # Grab the first matching url to the onion and add it to the scan list
        url = db.session.query(Urls.url).filter(Urls.domain == onion.domain).first()
        if not url.url.startswith('http'):
            continue
        unscanned_list.append(url.url)
    # It seems we don't need to populate the queue with millions of Urls if we repopulate it every 5 min or so.
    # 1k should be ok.  Can be adjusted later.
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
    ).order_by(db.func.random()).limit(1000).all()
    for candidate in unscanned_list:
        try:
            # Rebuild the queue
            q = UrlQueue()
            q.url = candidate.url
            db.session.merge(q)
        except:
            db.session.rollback()
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
