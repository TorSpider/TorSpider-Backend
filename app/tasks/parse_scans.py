import celery
from sqlalchemy.dialects.postgresql import insert
from app.models import Urls, Onions, Pages, Links, Forms, ParseQueue
from app import db, app
from urllib.parse import urlsplit, urlunsplit
import datetime
from datetime import date, timedelta
import json


@celery.task()
def parse_scan(queue_id):
    with app.app_context():
        this_onion = this_page = this_url = None
        # We pass the queue id from the tasker, so this runs immediately on the specific queued item.
        queue_item = ParseQueue.query.filter(ParseQueue.id == queue_id).first()
        if queue_item:
            try:
                scan_result = json.loads(queue_item.parse_data)
            except:
                app.logger.critical('Failed to parse the scan results for id {}.  JSON loading error'.format(queue_id))
        else:
            # We don't have any data for some reason, something isn't right, but we'll move on.
            return False

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

        try:
            scan_date = datetime.datetime.strptime(scan_date, '%Y-%m-%d').date()
        except:
            scan_date = date.today()

        # Get additional values.
        domain = get_domain(url)
        page = get_page(url)

        this_onion = Onions.query.filter(Onions.domain == domain).first()
        this_url = Urls.query.filter(Urls.url == url).first()

        if not this_onion:
            # We couldn't find the onion, which is strange, so we'll skip out
            app.logger.critical('Could not find onion domain for parsing: {}'.format(domain))
            return False
        if not this_url:
            # We couldn't find the url, which is strange, so we'll skip out
            app.logger.critical('Could not find url for parsing: {}'.format(url))
            return False
        # Process the domain depending on whether the domain is online or not.
        if online:
            # If the url is online, update onions and set last_online to scan_date,
            # tries to 0, and offline_scans to 0.
            this_onion.last_online = scan_date
            this_onion.tries = 0
            this_onion.offline_scans = 0
            # If the url is online and there is no fault, process_url.
            if not fault:
                process_url(url)
                process_forms(form_dicts, domain, page, url)
                this_page = Pages.query.filter(Pages.url == page).first()
        else:
            # If the url is offline, increment tries. If tries >= 3, set
            # tries = 0 and onion as offline, then set offline_scans += 1. Then set
            # the onion scan_date to the current date + offline_scans.
            this_onion.tries += 1
            if this_onion.tries >= 3:
                this_onion.offline_scans += 1
                this_onion.tries = 0
        # Set the scan date and last node
        this_onion.scan_date = (scan_date + timedelta(days=this_onion.offline_scans)).strftime('%Y-%m-%d')
        this_onion.last_node = last_node
        # Set the date of the url to scan_date.
        this_url.date = this_onion.scan_date
        if fault:
            this_url.fault = fault

        # For every new_url in the new_urls list, add_to_queue the url.
        for new_url in new_urls:
            add_to_queue(new_url, domain)

        # Update the page's hash if the hash is set.
        if hash:
            this_url.hash = hash

        # If we found a title, update it
        if title:
            # Update the url's title.
            if this_url.title != 'Unknown':
                this_url.title = merge_titles(this_url.title, title)
            if this_page:
                # Update the page's title.
                if this_page.title != 'Unknown':
                    this_page.title = merge_titles(this_page.title, title)

        # Update all of the records
        try:
            db.session.merge(this_onion)
            db.session.merge(this_url)
            if this_page:
                db.session.merge(this_page)
            db.session.delete(queue_item)
            db.session.commit()
        except:
            app.logger.critical('Failed to update the scan results for url: {}'.format(url))
            db.session.rollback()
        return True


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
    page = get_page(url)
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
            add_form(page, field)

            # Next, determine what examples already exist in the database.
            # Only do this if we have a value to add.
            if value == '' or value == 'none':
                continue

            # Query the forms table to see what data already exists.
            this_form = get_form(page, field)
            if this_form:
                result_examples = this_form.examples
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
            update_form(page, field, examples)

    except Exception as e:
        # Couldn't process the url.
        raise


def add_form(page, field):
    # Only add a form field if it isn't already in the database.
    insert_stmt = insert(Forms).values(
        page=page,
        field=field)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['page', 'field'])
    db.engine.execute(do_nothing_stmt.execution_options(autocommit=True))
    return True


def add_onion(link_domain):
    # Only add a domain if the domain isn't already in the database.
    insert_stmt = insert(Onions).values(
        domain=link_domain)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['domain'])
    db.engine.execute(do_nothing_stmt.execution_options(autocommit=True))
    return True


def add_page(link_domain, page):
    # Only add a page if it isn't already in the database.
    insert_stmt = insert(Pages).values(
        domain=link_domain,
        url=page)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['url'])
    db.engine.execute(do_nothing_stmt.execution_options(autocommit=True))
    return True


def add_url(link_domain, link_url):
    # Only add a url if the url isn't already in the database.
    insert_stmt = insert(Urls).values(
        domain=link_domain,
        url=link_url)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['domain', 'url'])
    db.engine.execute(do_nothing_stmt.execution_options(autocommit=True))
    return True


def add_link(origin_domain, link_domain):
    # Only add a link if the origin_domain and link_domain are not the same
    # and only if the link isn't already in the database.
    if origin_domain == link_domain:
        return True
    insert_stmt = insert(Links).values(
        domain_from=origin_domain,
        domain_to=link_domain)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['domain_from', 'domain_to'])
    db.engine.execute(do_nothing_stmt.execution_options(autocommit=True))


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


def get_page(url):
    # Get the page of the url, using urlsplit.
    s = urlsplit(url)
    page_url = urlunsplit((s.scheme, s.netloc, s.path, '', ''))
    return page_url


def get_form(page, field):
    # Retrieve the current example data for the specified form field.
    data = Forms.query.filter(Forms.page == page, Forms.field == field).first()
    return data


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


def update_form(page, field, examples):
    # Update the forms table, filling in examples for the specified field.
    try:
        update = Forms.query.filter(Forms.page == page, Forms.field == field).first()
        update.examples = examples
        db.session.merge(update)
        db.session.commit()
    except:
        db.session.rollback()
    return True


def process_forms(form_dicts, domain, page, url):
    # Add the forms to the database.
    for form_dict in form_dicts:
        # Process the form's information.

        # Make sure the necessary fields exist.
        if 'action' not in form_dict.keys():
            form_dict['action'] = ''
        if 'method' not in form_dict.keys():
            form_dict['method'] = ''
        if 'target' not in form_dict.keys():
            form_dict['target'] = ''

        # Get the form's action, and add it to the database.
        action_url = merge_urls(form_dict['action'], url)
        if '.onion' not in action_url or '.onion.' in action_url:
            # Ignore any non-onion domain.
            continue
        add_page(get_domain(action_url), get_page(action_url))
        add_to_queue(action_url, domain)

        # Now we'll need to add each input field and its
        # possible default values.
        fields = {}

        # Process text fields.
        text_fields = form_dict['text_fields']
        for key in text_fields.keys():
            fields[key] = text_fields[key]

        # Process radio buttons.
        radio_buttons = form_dict['radio_buttons']
        for key in radio_buttons.keys():
            rb_values = radio_buttons[key]
            rb_values = prune_exact(rb_values, ['', None])
            fields[key] = ','.join(rb_values)

        # Process checkboxes.
        checkboxes = form_dict['checkboxes']
        for key in checkboxes.keys():
            cb_values = checkboxes[key]
            cb_values = prune_exact(cb_values, ['', None])
            fields[key] = ','.join(cb_values)

        # Process dropdowns.
        dropdowns = form_dict['dropdowns']
        for key in dropdowns.keys():
            dd_values = dropdowns[key]
            dd_values = prune_exact(dd_values, ['', None])
            fields[key] = ','.join(dd_values)

        # Process text areas.
        text_areas = form_dict['text_areas']
        for key in text_areas.keys():
            fields[key] = text_areas[key]

        # Process dates.
        for d in form_dict['dates']:
            fields[d] = ''

        # Process datetimes.
        for dt in form_dict['datetimes']:
            fields[dt] = ''

        # Process months.
        for month in form_dict['months']:
            fields[month] = ''

        # Process numbers.
        for number in form_dict['numbers']:
            fields[number] = ''

        # Process ranges.
        for r in form_dict['ranges']:
            fields[r] = ''

        # Process times.
        for t in form_dict['times']:
            fields[t] = ''

        # Process weeks.
        for week in form_dict['weeks']:
            fields[week] = ''

        # Process the retrieved fields and add them to the
        # database.
        for key in fields.keys():
            value = fields[key]
            if key is None or key == '':
                key = 'None'
            if value is None or value == '':
                value = 'None'
            # Add the key to the database if it isn't there.
            add_form(action_url, key)
            if value == 'None':
                continue

            # Retrieve the current list of examples for this
            # particular form field.
            this_form = get_form(page, key)
            if this_form:
                result_examples = this_form.examples
            else:
                result_examples = None

            examples_have_changed = False
            if not result_examples:
                # We have no current values.
                examples = value
            else:
                # Merge with the returned examples.
                example_list = result_examples.split(',')
                old_list = list(example_list)
                example_list.append(value)
                example_list = unique(example_list)
                example_list.sort()
                if old_list != example_list:
                    examples_have_changed = True
                examples = ','.join(example_list)

            # Update the examples in the database, but only if
            # the values have changed.
            if examples_have_changed:
                update_form(page, key, examples)


def merge_titles(title1, title2):
    title1_parts = title1.split()
    title2_parts = title2.split()
    new_title_parts = extract_exact(title1_parts, title2_parts)
    new_title = ' '.join(new_title_parts)
    return new_title


def extract_exact(list1, list2):
    # Return the common items from both lists.
    return [item for item in list1 if any(scan == item for scan in list2)]


def prune_exact(items, scan_list):
    # Return all items from items list that match no items in scan_list.
    return [item for item in items
            if not any(scan == item for scan in scan_list)]


def unique(items):
    # Return the same list without duplicates)
    return list(set(items))


def merge_urls(url1, url2):
    url1 = '' if url1 is None else url1
    # Split up url1 and url into their component parts.
    (ascheme, anetloc, apath, aquery, afragment) = urlsplit(url1)
    (uscheme, unetloc, upath, uquery, ufragment) = urlsplit(url2)
    scheme = ascheme if ascheme is not '' else uscheme
    netloc = anetloc if anetloc is not '' else unetloc
    try:
        if apath[0] == '/':
            # The path starts at root.
            newpath = apath
        elif apath[0] == '.':
            # The path starts in either the current directory or a
            # higher directory.
            short = upath[:upath.rindex('/') + 1]
            split_apath = apath.split('/')
            apath = '/'.join(split_apath[1:])
            if split_apath[0] == '.':
                # Targeting the current directory.
                short = '/'.join(short.split('/')[:-1])
            elif split_apath[0] == '..':
                # Targeting the previous directory.
                traverse = -2
                while apath[0:3] == '../':
                    split_apath = apath.split('/')
                    apath = '/'.join(split_apath[1:])
                    traverse -= 1
                try:
                    short = '/'.join(short.split('/')[:traverse])
                except Exception as e:
                    short = '/'
            newpath = '/'.join([short, apath])
        else:
            # The path is just a page name.
            short = upath[:upath.rindex('/')]
            newpath = '/'.join([short, apath])
    except Exception as e:
        newpath = upath
    query = aquery
    fragment = ''
    link = urlunsplit((scheme, netloc, newpath, query, fragment))
    return link
