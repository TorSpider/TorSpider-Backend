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

    # Extract the values from scan_result.
    url = scan_result['url']  # Default: None
    hash = scan_result['hash']  # Default: None
    title = scan_result['title']  # Default: None
    fault = scan_result['fault']  # Default: None
    online = scan_result['online']  # Default: False
    new_urls = scan_result['new_urls']  # Default: []
    scan_date = scan_result['scan_date']  # Default: None
    last_node = scan_result['last_node']  # Default: None
    form_dicts = scan_result['form_dicts']  # Default: []

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
    # Add the url's information to the database.
    url = fix_url(url)
    domain = get_domain(url)
    query = get_query(url)
    try:
        # Insert the url into its various tables.

        # Add the url's page to the database.
        add_page(domain, url)

        # Process and add any discovered form data.
        for item in query:
            if item == ['']:
                # Ignore empty form data.
                continue
            try:
                [field, value] = item
            except Exception as e:
                # Sometimes they have a field without a query.
                # e.g. /index.php?do=
                [field] = item
                value = 'none'
            # We don't need to process it if the field is empty.
            if field == '':
                continue

            # Add the field to the forms table.
            add_form(url, field)

            # Next, determine what examples already exist in the database.
            # Only do this if we have a value to add.
            if value == '' or value == 'none':
                continue

            # Query the forms table to see what data already exists.
            result = get_form(url, field)
            if(len(result)):
                result_examples = result[0].get(examples)
            else:
                result_examples = None

            # If there are no examples, save the current example. Otherwise,
            # merge the new examples with the old.
            if not result_examples:
                examples = value
            else:
                # Merge with the returned examples.
                example_list = result_examples.split(',')
                example_list.append(value)
                examples = ','.join(unique(example_list))

            # Finally, update the tables in the database.
            update_form(url, field, examples)

    except Exception as e:
        # Couldn't process the url.
        raise


def add_form(link_url, field):
    # TODO: Complete this function.
    # Only add a form field if it isn't already in the database.
    pass


def add_onion(link_domain):
    # TODO: Complete this function.
    # Only add a domain if the domain isn't already in the database.
    pass


def add_page(link_domain, link_url):
    # TODO: Complete this function.
    # Only add a page if it isn't already in the database.
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


def get_form(link_url, field):
    # TODO: Complete this function.
    # Retrieve the current example data for the specified form field.
    pass


def get_query(url):
    # Get the query information from the url.
    # Queries look like: /page.php?field=value&field2=value2
    # Splitting along the & we get field=value, field2=value2
    query = urlsplit(url).query.split('&')
    result = []
    for item in query:
        # Splitting each query along the '=' we get
        # [[field1, value], [field2, value2]]
        item_parts = item.split('=')
        field = item_parts[0]
        value = '='.join(item_parts[1:])
        result.append([field, value])
    return result


def update_form(url, field, examples):
    # Update the forms table, filling in examples for the specified field.
    # TODO: Complete this function.
    pass
