import json

class BaseResult:
    """
    A result class for scraping operations, supporting specific result types such as website pages, robots.txt,
    sitemaps, and files.

    This class stores the source of the data (either URL for HTTP or file path for file-based operations),
    a success flag, logs, and the actual scraped data.

    Attributes:
        source (str): The source of the scraped data. For HTTP, it's the URL; for file scraping, it's the file path.
        success (bool): Indicates whether the scrape was successful.
        logs (list): A list of log messages or errors encountered during the scraping operation.
        data (dict): A dictionary containing the scraped data, such as emails, URLs, or other relevant information.
        result_type (str): The type of the result, which can be one of the following:
            - 'website': Classic website scrape (e.g., HTML page response).
            - 'robots_txt': Scraped robots.txt file (contains crawl instructions for web crawlers).
            - 'sitemap': Scraped sitemap file (typically XML containing URLs of a website).
            - 'file': File-based scraping (e.g., local file scraping, such as text or CSV).
    """

    def __init__(self, source: str, success: bool = False, logs: list = None, data: dict = None, result_type: str = 'website'):
        """
        Initializes the BaseResult instance.

        Args:
            source (str): The source of the scraped data. Can be a URL for HTTP scraping or a file path for file scraping.
            success (bool): Whether the scrape was successful or not.
            logs (list): List of logs or error messages encountered during scraping.
            data (dict): A dictionary containing the actual scraped data (e.g., emails, URLs).
            result_type (str): The type of the result, which can be one of the following:
                - 'website': Classic website scrape (e.g., HTML page response).
                - 'robots_txt': Scraped robots.txt file.
                - 'sitemap': Scraped sitemap file.
                - 'file': File-based scraping (e.g., local file scraping).
        """
        self.source = source
        self.success = success
        self.logs = logs if logs else []
        self.data = data if data else {}

    def __repr__(self):
        return str(json.dumps(self.to_dict(), indent=4))

    def to_dict(self):
        """
        Converts the BaseResult object to a dictionary format.

        Returns:
            dict: A dictionary representation of the scrape result.
        """
        return {
            "source": self.source,
            "success": self.success,
            "logs": self.logs,
            "data": self.data
        }