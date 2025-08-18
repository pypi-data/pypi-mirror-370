import re
import requests
import urllib
import html
import sys

from bs4 import BeautifulSoup

from ptlibs import ptprinthelper, ptmisclib, ptnethelper

from modules import metadata, emails, comments, forms, phone_numbers, ip_addresses, urls
from modules.scraping import google, re_search


from modules.results.base_result import BaseResult

class WebsiteScraper:
    def __init__(self, args, things_to_extract: dict, url_list_len: int, ptjsonlib: object, lock: object):
        self.use_json: bool = args.json
        self.extract_types: dict = things_to_extract
        self.ptjsonlib: object = ptjsonlib
        self.url_list_len = url_list_len
        self.args = args
        self.lock = lock

    def scrape_url(self, url: str) -> dict:
        """Scrape <things_to_extract> from <url>'s response"""
        self.result = BaseResult(source=url)
        self.result.data: dict = {"url": '', "metadata": None, "emails": None, "phone_numbers": None, "ip_addresses": None, "abs_urls": None, "internal_urls": None, "internal_urls_with_parameters": None, "external_urls": None, "insecure_sources": None, "subdomains": None, "forms": None, "comments": None}
        try:
            response = self.get_response(url)
            self.result.data["url"] = response.url
            if response is None:
                return self.result

            if self.stop_on_redirect(response=response):
                return self.result

            if response.text:
                return self._scrape_response(response)

            #if response.url.endswith("robots.txt"):
            #    return self.parse_robots_txt(response)
            else:
                self.result.logs.append(["Response returned no content", "ERROR"])
                return self.result

        except requests.exceptions.RequestException:
            self.result.logs.append(["Server not responding", "ERROR"])
            return self.result


    def target_is_url(self, source: str) -> bool:
        """Check whether the provided source is a valid URL"""
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?' # optional ports
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return regex.match(source)
 
    def get_response(self, url: str):
        """Retrieves response from <url>"""
        self.result.logs.append([f"Request URL: {url}", "TITLE"])
        response = ptmisclib.load_url_from_web_or_temp(url=url, method="GET" if not self.args.post_data else "POST", headers=ptnethelper.get_request_headers(self.args), proxies={"http": self.args.proxy, "https": self.args.proxy}, data=self.args.post_data, timeout=self.args.timeout, redirects=self.args.redirects, verify=False, cache=self.args.cache_requests)
        response.encoding = response.apparent_encoding

        self.result.logs.append([f"Content-Type: {response.headers.get('content-type', 'None').split(';')[0]}", "TITLE"])
        return response

        """
        except requests.exceptions.RequestException:
            ptprinthelper.ptprint(f"[error]", condition=not self.use_json)
            if self.url_list_len > 1:
                ptprinthelper.ptprint(f"Server not responding", "ERROR")
                return
            else:
                self.ptjsonlib.end_error("Server not responding", self.use_json)
        """

    def stop_on_redirect(self, response):
        """Stop on redirect if not --redirects"""
        history = [*response.history, response] if response.history else [response]
        if response.is_redirect and not self.args.redirects:
            if response.headers.get("location"):
                self.result.logs.append([f"Location: {response.headers.get('location')}", "TITLE"])

            self.result.logs.append([f"Redirects disabled, use -r/--redirect to follow", "ERROR"])
            return self.result

        if self.args.redirects and len(history) > 1:
            self.result.logs.append([f"Redirect URL: {history[-1].url} [{history[-1].status_code}]", "TITLE"])

    def _get_soup(self, response):
        if "<!ENTITY".lower() in response.text.lower():
            ptprinthelper.ptprint(f"Forbidden entities found", "ERROR", not self.use_json, colortext=True)
            return False
        else:
            soup = BeautifulSoup(response.text, features="lxml")
            bdos = soup.find_all("bdo", {"dir": "rtl"})
            for item in bdos:
                item.string.replace_with(item.text[::-1])
            return soup

    def _scrape_response(self, response) -> dict:
            """Extracts <extract_types> from <response>"""
            content_type = response.headers.get("content-type")

            # Find Metadata
            if self.extract_types["metadata"]:
                self.result.data["metadata"] = metadata.MetadataExtractor().get_metadata(response=response)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("metadata", None, None, properties={"metadata": self.result.data["metadata"]}))


            if "text" not in content_type:
                return self.result

            PAGE_CONTENT = urllib.parse.unquote(urllib.parse.unquote(html.unescape(response.text)))

            # Find Emails
            if self.extract_types["emails"]:
                self.result.data["emails"] = emails.find_emails(PAGE_CONTENT)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("emails", None, None, properties={"emails": self.result.data["emails"]}))

            # Find Page Comments
            if self.extract_types["comments"]:
                self.result.data["comments"] = comments.find_comments(PAGE_CONTENT)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("comments", None, None, properties={"comments": self.result.data["comments"]}))

            # Find Phone numbers
            if self.extract_types["phone_numbers"]:
                self.result.data["phone_numbers"] = phone_numbers.find_phone_numbers(PAGE_CONTENT)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("phone_numbers", None, None, properties={"phone_numbers": self.result.data["phone_numbers"]}))

            # Find IP Addresses
            if self.extract_types["ip_addresses"]:
                self.result.data["ip_addresses"] = ip_addresses.find_ip_addresses(PAGE_CONTENT)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("ip_addresses", None, None, properties={"ip_addresses": self.result.data["ip_addresses"]}))

            # Find Forms
            if self.extract_types["forms"]:
                soup = self._get_soup(response)
                if soup:
                    self.result.data["forms"] = forms.get_forms(soup)
                    self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("form", None, None, properties={"forms": self.result.data["forms"]}))

            # Find Absolute URLs
            if any([self.extract_types["external_urls"], self.extract_types["subdomains"], self.extract_types["internal_urls"], self.extract_types["internal_urls_with_parameters"], self.extract_types["insecure_sources"]]):
                self.result.data["abs_urls"] = urls.find_abs_urls(PAGE_CONTENT)
                #self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("abs_urls", None, None, properties={"abs_urls": result_data["abs_urls"]}))

                # Find External URLs | Filters through absolute_urls
                if self.extract_types["external_urls"] or self.extract_types["insecure_sources"]:
                    self.result.data['external_urls'] = urls.find_urls_in_response(PAGE_CONTENT, r'(href=|src=)[\'"](.+?)[\'"]', response.url, "external", without_parameters=self.args.without_parameters, abs_urls=self.result.data["abs_urls"])
                    if self.extract_types["external_urls"]:
                        self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("external_urls", None, None, properties={"external_urls": self.result.data["external_urls"]}))

                # Find Subdomains | Filters through absolute_urls
                if self.extract_types["subdomains"]:
                    self.result.data['subdomains'] = urls.find_urls_in_response(PAGE_CONTENT, r'(href=|src=)[\'"](.+?)[\'"]', response.url, "subdomain", without_parameters=self.args.without_parameters, abs_urls=self.result.data["abs_urls"])
                    self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("subdomains", None, None, properties={"subdomains": self.result.data["subdomains"]}))

                # Find Internal URLs | Filters through absolute_urls
                if self.extract_types["internal_urls"] or self.extract_types["internal_urls_with_parameters"] or self.extract_types["insecure_sources"]:
                    self.result.data["internal_urls"] = urls.find_urls_in_response(PAGE_CONTENT, r'(href=|src=)[\'"](.+?)[\'"]', response.url, "internal", without_parameters=self.args.without_parameters, abs_urls = self.result.data["abs_urls"])

                    # Add to self.ptjsonlib
                    if self.extract_types["internal_urls"]:
                        self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("internal_urls", None, None, properties={"internal_urls": self.result.data["internal_urls"]}))

                    # Find Internal URLs containing parameters | Filters through internal_urls
                    if self.extract_types["internal_urls_with_parameters"]:
                        self.result.data["internal_urls_with_parameters"] = sorted(urls._find_internal_parameters(self.result.data["internal_urls"], group_parameters=self.args.group_parameters), key=lambda k: k['url'])
                        self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("internal_urls_with_parameters", None, None, properties={"internal_urls_with_parameters": self.result.data["internal_urls_with_parameters"]}))
                        if not self.extract_types["internal_urls"]:
                            self.result.data["internal_urls"] = None

                if self.extract_types["insecure_sources"]:
                    self.result.data["insecure_sources"] = []
                    self.result.data["insecure_sources"].extend(self._find_insecure_sources(all_urls=self.result.data["abs_urls"] + self.result.data["external_urls"] + self.result.data["internal_urls"]))
                    self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("insecure_sources", None, None, properties={"insecure_sources": self.result.data["insecure_sources"]}))
                    if not self.extract_types["internal_urls"]:
                        self.result.data["internal_urls"] = None
                    if not self.extract_types["external_urls"]:
                        self.result.data["external_urls"] = None

            # Extract Google Keys
            if self.extract_types["google_keys"]:
                self.result.data["google_keys"] = google.parse_google_identifiers(response)
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("google_keys", None, None, properties={"google_keys": self.result.data["google_keys"]}))

            if self.extract_types["regex_search"]:
                self.result.data["regex_search"] = re_search.parse_search_regex(response, self.args.search)

            return self.result

    def _find_insecure_sources(self, all_urls) -> list:
        """Finds URLs loaded via not secure HTTP protocol."""
        insecure_sources = sorted(list(set([u for u in all_urls if re.match(r"http://", u)])))
        return insecure_sources

    def parse_robots_txt(self, response):
        ptprinthelper.ptprint(f"Robots.txt:\n", "TITLE", not self.use_json)
        ptprinthelper.ptprint(response.text.rstrip(), condition=not self.use_json)
        ptprinthelper.ptprint(" ", condition=not self.use_json)
        allow = list({pattern.lstrip() for pattern in re.findall(r"^Allow: ([\S ]*)", response.text, re.MULTILINE)})
        disallow = list({pattern.lstrip() for pattern in re.findall(r"^Disallow: ([\S ]*)", response.text, re.MULTILINE)})
        sitemaps = re.findall(r"[Ss]itemap: ([\S ]*)", response.text, re.MULTILINE)
        test_data = {"allow": allow, "disallow": disallow, "sitemaps": sitemaps}

        parsed_url = urllib.parse.urlparse(response.url)
        internal_urls = []
        for section_header in test_data.values():
            for finding in section_header:
                parsed_finding = urllib.parse.urlparse(finding)
                if not parsed_finding.netloc:
                    full_path = urllib.parse.urlunparse((parsed_url[0], parsed_url[1], parsed_finding[2], "", "", ""))
                else:
                    full_path = finding
                internal_urls.append(full_path)
        return {"url": response.url, "internal_urls": internal_urls}