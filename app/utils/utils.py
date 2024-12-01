import whois
import tldextract
import requests
import re
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import validators

def extract_url_features(url):
    # Helper function to extract domain and TLD
    def extract_domain_info(url):
        ext = tldextract.extract(url)
        return ext.domain or "", ext.suffix or ""

    # Helper function to extract domain age
    def extract_domain_age(domain):
        try:
            domain_info = whois.whois(domain)
            creation_date = domain_info.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if creation_date:
                return (datetime.now() - creation_date).days // 365
        except Exception:
            pass
        return 0

    # Helper function to extract number of hyperlinks
    def extract_nb_hyperlinks(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            return len(soup.find_all('a'))
        except:
            return 0

    # Helper function to extract favicon
    def extract_favicon(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            favicon = soup.find("link", rel="icon")
            return 1 if favicon else 0
        except:
            return 0

    # Helper function to extract redirects
    def extract_redirects(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return len(response.history)
        except:
            return 0

    # Parsing the URL and domain extraction
    parsed_url = urlparse(url)
    domain, tld = extract_domain_info(url)

    # Extracting features
    features = {
        "url": url,
        "length_url": len(url),
        "length_hostname": len(parsed_url.hostname) if parsed_url.hostname else 0,
        "ip": 1 if validators.ipv4(url) or validators.ipv6(url) else 0,
        "nb_dots": url.count('.'),
        "nb_dots_host": parsed_url.hostname.count('.') if parsed_url.hostname else 0,
        "nb_hyphens": url.count('-'),
        "nb_at": url.count('@'),
        "nb_qm": url.count('?'),
        "nb_and": url.count('&'),
        "nb_or": url.count('|'),
        "nb_eq": url.count('='),
        "nb_underscore": url.count('_'),
        "nb_tilde": url.count('~'),
        "nb_percent": url.count('%'),
        "nb_slash": url.count('/'),
        "nb_star": url.count('*'),
        "nb_colon": url.count(':'),
        "nb_comma": url.count(','),
        "nb_semicolumn": url.count(';'),
        "nb_dollar": url.count('$'),
        "nb_space": url.count(' '),
        "nb_www": 1 if 'www' in parsed_url.hostname else 0,
        "nb_com": 1 if parsed_url.hostname.endswith('.com') else 0,
        "nb_dslash": 1 if url.startswith('http://') or url.startswith('https://') else 0,
        "http_in_path": 1 if 'http' in parsed_url.path else 0,
        "https_token": 1 if 'https' in parsed_url.path else 0,
        "nb_external_redirection": extract_redirects(url),
        "nb_redirection": extract_redirects(url),
        "ratio_digits_host": (len(re.findall(r'\d', parsed_url.hostname)) / len(parsed_url.hostname)) if parsed_url.hostname else 0.0,
        "phish_hints": 1 if "login" in url or "secure" in url else 0,
        "suspecious_tld": 1 if tld in ['xyz', 'top', 'club'] else 0,
        "external_favicon": extract_favicon(url),
        "abnormal_subdomain": 1 if len(parsed_url.hostname.split('.')) > 3 else 0,
        "shortening_service": 1 if "bit.ly" in url or "goo.gl" in url else 0,
        "domain_age": extract_domain_age(domain),
        "tld_in_subdomain": 1 if tld in parsed_url.hostname else 0,
        "nb_subdomains": len(parsed_url.hostname.split('.')) - 1 if parsed_url.hostname else 0,
    }

    # Fallback for missing features
    for key, value in features.items():
        if value is None:
            features[key] = 0  # Replace None with 0

    return features
