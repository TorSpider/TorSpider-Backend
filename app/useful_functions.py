from urllib.parse import urlsplit, urlunsplit


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
