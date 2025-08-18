import re

from bs4 import BeautifulSoup

from ptlibs import ptprinthelper
from modules import metadata, emails, comments, forms, phone_numbers, ip_addresses, urls

from modules.results.base_result import BaseResult

class FileScraper:
    def __init__(self, args, things_to_extract: dict, ptjsonlib: object, lock: object):
        self.use_json: bool = args.json
        self.extract_types: dict = things_to_extract
        self.lock = lock

    def process_file(self, path_to_local_file: str, args, things_to_extract: dict, ptjsonlib: object) -> dict:
        """Returns extracted info from <filepath>"""
        self.result = BaseResult(source=path_to_local_file)
        try:
            import magic
            import mimetypes
            mimetype       = mimetypes.guess_type(path_to_local_file)[0]
            content_type   = magic.from_file(path_to_local_file)
        except Exception as e:
            self.ptjsonlib.end_error("Dependency not found, please install: sudo apt install libmagic1", self.use_json)

        is_readable    = True if re.findall("text", content_type.lower()) else False
        file_extension = path_to_local_file.split("/")[-1].split(".")[-1] if "." in path_to_local_file.split("/")[-1] else None

        self.result.logs.append([f"Provided source: {path_to_local_file.split('/')[-1]}", "INFO"])
        self.result.logs.append([f"Extension: {file_extension}", "INFO"])
        self.result.logs.append([f"Source-Type: {content_type}", "INFO"])
        self.result.logs.append([f"MIME Type: {mimetype}", "INFO"])

        result = self._scrape_file(path_to_local_file, is_readable, mimetype, ptjsonlib, args, things_to_extract)
        return result

    def _scrape_file(self, path_to_local_file: str, is_readable, mimetype, ptjsonlib, args, extract_types: dict) -> dict:
        """Scrapes extract_types from <filepath>"""
        self.result.data: dict = {"url": path_to_local_file.rsplit("/")[-1], "metadata": None, "emails": None, "phone_numbers": None, "ip_addresses": None, "abs_urls": None, "internal_urls": None, "internal_urls_with_parameters": None, "external_urls": None, "insecure_sources": None, "subdomains": None, "forms": None, "comments": None}
        if extract_types["metadata"]:
            extracted_metadata = metadata.MetadataExtractor().get_metadata(path_to_local_file=path_to_local_file)
            self.result.data["metadata"] = extracted_metadata
            if len(extracted_metadata.keys()) == 1 and "ExifTool" in list(extracted_metadata)[0]:
                self.result.data["metadata"] = {list(extracted_metadata)[0].split("ExifTool:")[-1]: list(extracted_metadata.values())[0]}

        if not is_readable:
            return self.result

        with open(path_to_local_file, "rb") as file:
            file_content = str(file.read())

            if extract_types["emails"]:
                self.result.data["emails"] = emails.find_emails(file_content)

            if extract_types["comments"]:
                self.result.data["comments"] = {}

            if extract_types["phone_numbers"]:
                self.result.data["phone_numbers"] = phone_numbers.find_phone_numbers(file_content)

            if extract_types["ip_addresses"]:
                self.result.data["ip_addresses"] = ip_addresses.find_ip_addresses(file_content)

            if any([extract_types["internal_urls"], extract_types["external_urls"], extract_types["internal_urls_with_parameters"], extract_types["subdomains"]]):
                self.result.data["external_urls"] = urls.find_urls_in_file(file_content)

            if extract_types["subdomains"]:
                self.result.data["subdomains"] = urls.get_subdomains_from_list(self.result.data["external_urls"])

            if extract_types["internal_urls_with_parameters"]:
                self.result.data["internal_urls_with_parameters"] = dict()
                """
                if args.grouping_complete:
                    self.result.data["internal_urls_with_parameters"] = dict()
                else:
                    self.result.data["internal_urls_with_parameters"] = "Not a HTML file"
                """

            if extract_types["forms"]:
                if str(mimetype) in ["text/html"]:
                    soup = self._get_soup(file_content)
                    self.result.data["forms"] = forms.get_forms(soup)
                else:
                    self.result.data["forms"] = {}
                    """
                    if args.grouping_complete:
                        self.result.data["forms"] = dict()
                    else:
                        self.result.data["forms"] = "Not a HTML file"
                    """
        return self.result

    def _get_soup(self, string, args):
        if "<!ENTITY".lower() in string.lower():
            ptprinthelper.ptprint(f"Forbidden entities found", "ERROR", not self.use_json, colortext=True)
            return False
        else:
            soup = BeautifulSoup(string, features="lxml")
            bdos = soup.find_all("bdo", {"dir": "rtl"})
            for item in bdos:
                item.string.replace_with(item.text[::-1])
            return soup
