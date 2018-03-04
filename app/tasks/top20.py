import celery
from app.models import TopLists
from app.helpers import top_twenty_page_count, top_twenty_outlinks, top_twenty_inlinks
from app import db, app

@celery.task()
def update_lists():
    with app.app_context():
        # within this block, current_app points to app.
        thelists = [
            ('pages', top_twenty_page_count()),
            ('outlinks', top_twenty_outlinks()),
            ('inlinks', top_twenty_inlinks())
        ]

        for item in thelists:
            try:
                newlist = TopLists()
                newlist.list_name = item[0]
                newlist.list_data = item[1]
                db.session.merge(newlist)
                db.session.commit()
            except Exception as e:
                app.logger.error("Failed to update list: {}".format(item[0]))
                app.logger.error(e)
                continue
