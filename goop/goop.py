import re
import requests

try:
    from urllib.parse import quote_plus as url_encode
except ImportError:
    from urllib import quote_plus as url_encode

def decode_html(string):
    "decode common html/xml entities"
    new_string = string
    decoded = ['>', '<', '"', '&', '\'']
    encoded = ['&gt;', '&lt;', '&quot;', '&amp;', '&#039;']
    for e, d in zip(encoded, decoded):
        new_string = new_string.replace(e, d)
    for e, d in zip(encoded[::-1], decoded[::-1]):
        new_string = new_string.replace(e, d)
    return new_string

def parse(string):
    "extract and parse resutls"
    parsed = {}
#     pattern = r'''<div><div class="[^"]+">
# <div class="[^"]+"><a href="/url\?q=(.+?)&sa=[^"]+"><div class="[^"]+">(.*?)</div>
# <div class="[^"]+">.*?</div></a></div>
# <div class="[^"]+"></div>
# <div class="[^"]+"><div><div class="[^"]+"><div><div><div class="[^"]+">(?:(.*?)(?: ...)?</div>|\n<span class="[^"]+">.*?</span><span class="[^"]+">.*?</span>(.*?)</div>)'''
    pattern = r'''<div class="[^"]+"><a href="/url\?q=(.+?)&sa=[^"]+">'''
    matches = re.finditer(pattern, string)
    num = 0
    for match in matches:
        # parsed[num] = {'url' : match.group(1), 'text' : match.group(2), 'summary' : match.group(3) or match.group(4)}
        parsed[num] = {'url' : match.group(1), 'text' : '', 'summary' : ''}
        num += 1
    return parsed

def search(query, cookie, page=0, full=False):
    """
    main function, returns parsed results
    Args:
    query - search string
    cookie - facebook cookie
    page - search result page number (optional)
    """
    offset = page * 10
    filter = 1 if not full else 0
    escaped = url_encode('https://google.com/search?q=%s&start=%i&filter=%i' % (url_encode(query), offset, filter))
    headers = {
    'Host': 'developers.facebook.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'deflate',
    'Connection': 'keep-alive',
    'Cookie': cookie,
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
    }
    response = requests.get('https://developers.facebook.com/tools/debug/echo/?q=%s' % escaped, headers=headers)
    cleaned_response = decode_html(response.text)
    parsed = parse(cleaned_response)
    return parsed
