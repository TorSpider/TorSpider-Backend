from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

import datetime

Base = declarative_base()

from app import db


class SerializerMixin:
    """Provide dict-like interface to db.Model subclasses."""

    def __getitem__(self, key):
        """Expose object attributes like dict values."""
        return getattr(self, key)

    def keys(self):
        """Identify what db columns we have."""
        return inspect(self).attrs.keys()


class CreatedUpdatedMixin(object):
    created = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), index=True)


class Onions(db.Model, CreatedUpdatedMixin, SerializerMixin):
    '''
    Onions: Information about each individual onion domain.
         - id:            The numerical ID of that domain.
         - domain:        The domain itself (i.e. 'google.com').
         - online:        Whether the domain was online in the last scan.
         - last_online:   The last date the page was seen online.
         - scan_date:          The date of the last scan.
         - last_node:     The last node to scan this domain.
         - tries:         How many attempts have been made to connect?
         - offline_scans: How many times the onion has scanned offline.
    '''
    __tablename__ = "onions"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, index=True)
    domain = db.Column(db.String, unique=True, nullable=False, index=True)
    online = db.Column(db.Boolean, default=True)
    last_online = db.Column(db.Date, default=datetime.date(1900, 1, 1))
    scan_date = db.Column(db.Date, default=datetime.date(1900, 1, 1))
    last_node = db.Column(db.String)
    tries = db.Column(db.Integer, default=0)
    offline_scans = db.Column(db.Integer, default=0)


class Urls(db.Model, CreatedUpdatedMixin, SerializerMixin):
    ''' Urls: Information about each url discovered.  This is each unique url endpoint, each ?Page=1 param would
        be a different url.
         - id:            The numerical ID of that url.
         - title:         The url's title.
         - domain:        The numerical ID of the url's parent domain.
         - url:           The url itself.
         - hash:          The page's sha1 hash, for detecting changes.
         - date:          The date of the last scan.
         - fault:         If there's a fault preventing scanning, log it.
     '''
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, index=True)
    title = db.Column(db.String, default="none")
    domain = db.Column(db.String, db.ForeignKey('onions.domain', ondelete='cascade'))
    domain_info = db.relationship('Onions', backref=db.backref('urls', lazy='dynamic'))
    url = db.Column(db.String, unique=True)
    hash = db.Column(db.String(40))
    date = db.Column(db.Date, default=datetime.date(1900, 1, 1))
    fault = db.Column(db.String)
    __table_args__ = (UniqueConstraint('domain', 'url', name='unique_url'),)


class Pages(db.Model, CreatedUpdatedMixin, SerializerMixin):
    ''' Pages: Information about the various pages in each domain.  This means base pages, in the case of a url with 
        multiple parameters such as Joomla or Wordpress would use.
        - id:            The numerical ID of the page.
        - url:           The url of the page.
        - title:         The title of the page.
        - domain:        The numerical ID of the page's parent domain.
        - fault:         If there's a fault preventing scanning, log it.
    '''
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, index=True)
    url = db.Column(db.String, db.ForeignKey('urls.url', ondelete='cascade'), unique=True)
    title = db.Column(db.String, default="none")
    domain = db.Column(db.String, db.ForeignKey('onions.domain', ondelete='cascade'))
    fault = db.Column(db.String, default="none")
    __table_args__ = (UniqueConstraint('domain', 'url', name='unique_page'),)


class Forms(db.Model, CreatedUpdatedMixin, SerializerMixin):
    ''' Forms: Information about the various form fields for each page.
        - id:            The numerical ID of the form field.
        - page:          The numerical ID of the page it links to.
        - field:         The name of the form field.
        - examples:      Some examples of found values.
    '''
    __tablename__ = "forms"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, index=True)
    page = db.Column(db.String, db.ForeignKey('pages.url', ondelete='cascade'), unique=True)
    field = db.Column(db.String)
    examples = db.Column(db.String)
    __table_args__ = (UniqueConstraint('page', 'field', name='unique_field'),)


class Links(db.Model, CreatedUpdatedMixin, SerializerMixin):
    ''' Links: Information about which domains connect to each other.
        - domain_from:        The numerical ID of the origin domain.
        - domain_to:          The numerical ID of the target domain.
    '''
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, index=True)
    domain_from = db.Column(db.String, db.ForeignKey('onions.domain', ondelete='cascade'))
    domain_to = db.Column(db.String, db.ForeignKey('onions.domain', ondelete='cascade'))
    __table_args__ = (UniqueConstraint('domain_from', 'domain_to', name='unique_link'),)


class Nodes(db.Model, CreatedUpdatedMixin, SerializerMixin):
    __tablename__ = "nodes"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    unique_id = db.Column(db.String(32), nullable=False, unique=True)
    api_key = db.Column(db.String(40), nullable=True, unique=True)
    owner = db.Column(db.String(32), nullable=False)
    active = db.Column(db.Boolean, default=True)

class TopLists(db.Model, SerializerMixin):
    __tablename__ = "top_lists"

    list_name = db.Column(db.String(32), primary_key=True, nullable=False, unique=True)
    list_data = db.Column(db.String, nullable=True)
    
class UrlQueue(db.Model, SerializerMixin):
    __tablename__ = "url_queue"

    url = db.Column(db.String, unique=True)