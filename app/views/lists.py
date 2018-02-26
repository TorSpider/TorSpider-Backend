from app.models import Onions, Links, Pages
from flask.login import login_required
from sqlalchemy import desc
from flask import jsonify
from flask import request
from app import db

"""
Page Count:
SELECT DISTINCT onions.domain, count(pages.url)
FROM pages INNER JOIN onions ON onions.domain = pages.domain
WHERE pages.fault IS NOT NULL AND pages.domain IN (
    SELECT domain FROM onions
    WHERE online IS TRUE
    AND last_online IS NOT NULL)
GROUP BY onions.domain
ORDER BY COUNT(pages.url) DESC LIMIT 20;
"""

@app.route("/api/top20/pages", methods=["GET"])
# @login_required
def top_twenty_page_count():
    # Retrieve the top twenty onions in order of page count.
    query = db.session.query(
        Onions.domain,
        db.func.count(Pages.url)
    ).join(Pages).filter(
        Pages.fault == 'none',
        Pages.domain.in_(
            db.session.query(Onions.domain).filter(
                Onions.online == True,
                Onions.last_online != None
            ).all()
        )
    ).order_by(
        desc(db.func.count(Pages.url))
    ).group_by(Onions).limit(20)
    results = query.all()
    if len(results) is 0:
        return jsonify({'object': {}})
    return jsonify({'objects': results})


"""
Outgoing Links:
SELECT DISTINCT onions.domain, count(links.domain_to)
FROM links INNER JOIN onions ON onions.domain = links.domain_from
WHERE links.domain_to IN (
    SELECT domain FROM onions
    WHERE online IS TRUE
    AND last_online IS NOT NULL)
AND links.domain_from IN (
    SELECT domain FROM onions
    WHERE online IS TRUE
    AND last_online IS NOT NULL)
GROUP BY onions.domain ORDER BY COUNT(links.domain_to) DESC
LIMIT 20;
"""

@app.route("/api/top20/outlinks", methods=["GET"])
# @login_required
def top_twenty_outlinks():
    # Retrieve the top twenty onions in order of outgoing links.
    query = db.session.query(
        Onions.domain,
        db.func.count(Links.domain_to)
    ).join(Links, Onions.domain == Links.domain_from).filter(
        Links.domain_to.in_(
            db.session.query(Onions.domain).filter(
                Onions.online == True,
                Onions.last_online != None
            )
        ),
        Links.domain_from.in_(
            db.session.query(Onions.domain).filter(
                Onions.online == True,
                Onions.last_online != None
            )
        )
    ).order_by(
        desc(db.func.count(Links.domain_to))
    ).group_by(Onions).limit(20)
    results = query.all()
    if len(results) is 0:
        return jsonify({'object': {}})
    return jsonify({'objects': results})

"""
Incoming Links:
SELECT DISTINCT onions.domain, count(links.domain_from)
FROM links INNER JOIN onions ON onions.domain = links.domain_to
WHERE links.domain_to IN (
    SELECT domain FROM onions
    WHERE online IS TRUE
    AND last_online IS NOT NULL)
AND links.domain_from IN (
    SELECT domain FROM onions
    WHERE online IS TRUE
    AND last_online IS NOT NULL)
GROUP BY onions.domain ORDER BY COUNT(links.domain_from) DESC
LIMIT 20;
"""

@app.route("/api/top20/inlinks", methods=["GET"])
# @login_required
def top_twenty_inlinks():
    # Retrieve the top twenty onions in order of incoming links.
    query = db.session.query(
        Onions.domain,
        db.func.count(Links.domain_from)
    ).join(Links, Onions.domain == Links.domain_to).filter(
        Links.domain_to.in_(
            db.session.query(Onions.domain).filter(
                Onions.online == True,
                Onions.last_online != None
            )
        ),
        Links.domain_from.in_(
            db.session.query(Onions.domain).filter(
                Onions.online == True,
                Onions.last_online != None
            )
        )
    ).order_by(
        desc(db.func.count(Links.domain_from))
    ).group_by(Onions).limit(20)
    results = query.all()
    if len(results) is 0:
        return jsonify({'object': {}})
    return jsonify({'objects': results})
