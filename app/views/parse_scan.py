from app import app, db
from app.helpers import check_api_auth
from app.models import *
from flask import jsonify
from flask import request
from flask import abort
import json
from sqlalchemy import and_, or_
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import urlsplit, urlunsplit


@app.route("/api/parse_scan", methods=["PUT", "POST"])
def parse_scan():
    # Parse the scan data returned by the spider.
    if not check_api_auth():
        abort(401)  # Unauthorized.

    # Get the scan_result from the query.
    try:
        scan_result = json.loads(request.values.get('q'))
    except:
        # Could not load the scan_result from the query.
        abort(400)  # Bad request.

    # TODO: Process the data in scan_result.

    # TODO: Set the scan_date and last_node of the onion.

    # TODO: Set the date of the url to scan_date.

    # TODO: If the url is online, update onions and set last_online to
    # scan_date, tries to 0, and offline_scans to 0.

    # TODO: If the url is offline, increment tries. If tries >= 3, set
    # tries = 0 and onion as offline, then set offline_scans += 1. Then set
    # the onion scan_date to the current date + offline_scans.

    # TODO: If there's a fault in the url, log that fault in the database.

    # TODO: If the url is online and there is no fault, process_url.

    # TODO: For every new_url in the new_urls list, add_to_queue the url.

    # TODO: Update the page's hash if scan_result['hash'] is set.

    # TODO: Update the url's title if it has changed.

    # TODO: Update the page's title if it has changed.

    # TODO: Update the page's form data based on form_dicts.

    return "Success!"


def add_to_queue(link_url, origin_domain):
    # Add a new url to the database.
    link_url = fix_url(link_url)
    link_domain = get_domain(link_url)
    if '.onion' not in link_domain or '.onion.' in link_domain:
        # This domain isn't a .onion domain.
        return
    add_onion(link_domain)
    add_url(link_domain, link_url)
    add_link(origin_domain, link_domain)


def process_url(url):
    # TODO: Complete this function.
    pass


def add_onion(link_domain):
    # TODO: Complete this function.
    # Only add a domain if the domain isn't already in the database.
    pass


def add_url(link_domain, link_url):
    # TODO: Complete this function.
    # Only add a url if the url isn't already in the database.
    pass


def add_link(origin_domain, link_domain):
    # TODO: Complete this function.
    # Only add a link if the origin_domain and link_domain are not the same
    # and only if the link isn't already in the database.
    pass


def defrag_domain(domain):
    # Defragment the given domain.
    domain_parts = domain.split('.')
    # Onion domains don't have strange symbols or numbers in them, so be
    # sure to remove any of those just in case someone's obfuscating
    # domains for whatever reason.
    domain_parts[-2] = ''.join(
        ch for ch in domain_parts[-2] if ch.isalnum())
    domain = '.'.join(domain_parts)
    return domain


def fix_url(url):
    # Fix obfuscated urls.
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    netloc = defrag_domain(netloc)
    url = urlunsplit((scheme, netloc, path, query, fragment))
    return url.replace('\x00', '')


def get_domain(url):
    # Get the defragmented domain of the given url.
    # Omit subdomains. Rather than having separate records for urls
    # like sub1.onionpage.onion and sub2.onionpage.onion, just keep them
    # all under onionpage.onion.
    return '.'.join(defrag_domain(urlsplit(url).netloc).split('.')[-2:])
