import urllib
import requests
import time
import sys

TERMS_DESKTOP = [
    "income inequality", "Campaign Fundraising", "Broadcasting", "republicans",
    "Spokane", "gang", "fast food", "Foreign Intelligence Surveillance Act",
    "georgia"]

TERMS_SERVER = ["campaign finance", "student privacy",
    "Early learning", "FISA", "baltimore", "domestic violence", "NFL", "highway",
    "Tepfer", "diabetes", "Actuary", "energy storage", "RUC"]


def print_time(s):
    print "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), s)

try:
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    DOMAIN = sys.argv[3].strip('/')
    if sys.argv[4] == 'server':
        TERMS = TERMS_SERVER
    elif sys.argv[4] == 'desktop':
        TERMS = TERMS_DESKTOP
except IndexError:
    print_time("Usage: api_race_tester.py USER PASS PROTOCOL://DOMAIN[:PORT]")
    print_time("For example: mlissner password https://www.courtlistener.com")
    exit(1)

print_time("Using user %s with password %s on domain %s" % (USERNAME, PASSWORD, DOMAIN))


def fetch_to_json(url):
    """get the contents of a URL and return it as JSON
    """
    r = requests.get(
        url,
        headers={'User-Agent': 'api-race-tester-mlr'},
        auth=(USERNAME, PASSWORD),
    )
    return r.json  # Requests is a great library.


def url_for(term, DOMAIN):
    """ Make a good URL for the term
    """
    escaped = urllib.quote(term)
    return "%s/api/rest/v1/search/?&format=json&q=%%22%s%%22" % (DOMAIN, escaped)


def response_is_effed_up(query, snippet):
    """ Check if the highlighted (marked) text from the result is contained in the query
    """
    # Find the text after the first 'mark', before the closing mark and lowercase it.
    try:
        marked_text = snippet.split('<mark>')[1].split('</mark>')[0].lower()
    except IndexError:
        print_time("snippet was: %s" % snippet)
        exit(1)

    # Normalize the query
    query = query.lower()

    print_time("    marked_text is: \t%s" % marked_text)
    print_time("    query is: \t\t\t%s" % query)

    return marked_text[0:2] not in query


# Until the program is nuked, query like a mother fucker.
while True:
    for term in TERMS:
        url = url_for(term, DOMAIN)
        print_time("Trying: '%s'" % term)
        print_time("    URL is: %s" % url)

        json = fetch_to_json(url)()
        try:
            first_snippet = json['objects'][0]['snippet']
        except KeyError:
            print_time("    KeyError. Json was: %s" % json)
            if json['error_message'] == u'Sorry, this request could not be processed. Please try again later.':
                print_time("    Continuing onwards...\n")
                continue
            else:
                print_time("    Unknown json content. Exiting.")
                exit(1)

        if response_is_effed_up(term, first_snippet):
            print_time("mismatched thing.\n")
            exit(1)
        else:
            print_time(" --- OK! ---\n")
