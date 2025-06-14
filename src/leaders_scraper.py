"""
WikipediaScraper module: fetches and enriches leader data from a public API 
and Wikipedia.
"""

# src/leaders_scraper.py

import csv
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

from utils.print_utils import Color, PrintUtils


class WikipediaScraper:
    """
    A scraper class for retrieving and enriching information about country
    leaders from a public API and Wikipedia.

    This class provides methods to fetch country and leader data,
    enrich leader information with Wikipedia summaries,
    and export the results to JSON or CSV files.
    """

    def __init__(self):
        """
        Initialize the WikipediaScraper instance with API endpoints, session,
        and storage for leader data.

        Sets up the base URLs for API access, creates a requests session,
        retrieves the initial cookie, and initializes the data structure
        for storing leaders per country.
        """
        # Base URL for the API that provides information about country leaders
        self.base_url = "https://country-leaders.onrender.com"

        # URL endpoint to fetch a valid session cookie
        self.cookie_url = f"{self.base_url}/cookie"

        # URL endpoint to retrieve the list of countries
        self.country_endpoint = f"{self.base_url}/countries"

        # URL endpoint to retrieve the leaders for a given country
        self.leaders_endpoint = f"{self.base_url}/leaders"

        # Create a reusable requests session for all HTTP calls
        # (more efficient than multiple requests)
        self.session = requests.Session()

        # Retrieve and store cookies needed for API access
        self.cookie = self._get_cookies()

        # Will store leaders per country with summaries
        self.leaders_data = {}

    def refresh_cookie(self):
        """
        Public method to refresh and return a new session cookie.

        This method is an alias for the internal _get_cookies() method.
        Returns:
        - requests.cookies.RequestsCookieJar: refreshed cookie object
        """
        self.cookie = self._get_cookies()
        return self.cookie

    def get_countries(self):
        """
        Retrieve the list of countries supported by the API.

        Returns:
        - list[str]: List of ISO country codes (e.g., ['us', 'fr', 'be'])
        """
        response = self.session.get(self.country_endpoint, cookies=self.cookie)
        return response.json()

    def get_leaders(self, country: str):
        """
        Fetch the list of political leaders for a given country.

        Parameters:
        - country (str): ISO country code (e.g., 'us', 'fr')

        Returns:
        - list[dict]: List of leaders with their metadata
          (excluding Wikipedia summary)
        """
        params = {"country": country}
        response = self.session.get(
            self.leaders_endpoint, cookies=self.cookie, params=params
        )
        return response.json()

    def _get_cookies(self):
        """
        Retrieve a fresh set of cookies from the API.

        This is typically required before making further requests,
        as the API expects valid cookies for authentication or session
        handling.

        Returns:
        - requests.cookies.RequestsCookieJar: cookies object to be reused in
          subsequent API calls
        """
        # Send a GET request to the /cookie endpoint using the session
        response = self.session.get(self.cookie_url)

        # Return the cookies received in the response
        return response.cookies

    def get_first_paragraph(self, wikipedia_url: str):
        """
        Fetch and clean the first paragraph of a Wikipedia article.
        This method:
        - Sends a GET request to the provided Wikipedia URL
        - Parses the HTML content using BeautifulSoup
        - Finds the first meaningful paragraph (<p>) with more than
          80 characters
        - Removes citation markers like [1], [2], etc. using regex
        - Returns the cleaned paragraph as a string

        Parameters:
        - wikipedia_url (str): The URL of the Wikipedia article

        Returns:
        - str: Cleaned first paragraph text, or empty string if none found
        """

        # Cyrillic or Arabic characters may display incorrectly
        # Print the human-readable URL (for debugging purposes)
        print(unquote(wikipedia_url))

        # Send HTTP GET request to the Wikipedia page
        response = self.session.get(wikipedia_url)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Iterate over all paragraph elements
        for p in soup.find_all("p"):
            text = p.get_text(
                strip=True
            )  # Extract text and strip leading/trailing whitespace

            # Skip short or empty paragraphs
            if len(text) > 80:
                # Remove citation references like [1], [2], etc.
                cleaned = re.sub(r"\[[0-9]+\]", "", text)
                return cleaned

        # --- Bug: no paragraph available, but nothing is printed
        # If no suitable paragraph was found, log a warning
        print(f"[WARN] No suitable paragraph found for {wikipedia_url}")

        # Return empty string if no suitable paragraph was found
        return ""

    def enrich_leader(self, leader: dict[str, Any]) -> dict[str, Any]:
        """
        Enrich a single leader dictionary with a cleaned Wikipedia URL and a
        summary paragraph.

        This method:
        - Decodes the Wikipedia URL to ensure proper character display
          (e.g., Cyrillic, accents)
        - Fetches and adds the first meaningful paragraph from the leader's
          Wikipedia page

        Parameters:
        - leader (dict): A dictionary representing a political leader,
          containing at least a 'wikipedia_url' key

        Returns:
        - dict: The updated leader dictionary, now including a 'summary' field
          (if URL was valid)
        """
        if "wikipedia_url" in leader and leader["wikipedia_url"]:
            # Decode percent-encoded characters (e.g., %D0%9F → П)
            if isinstance(leader["wikipedia_url"], str):
                leader["wikipedia_url"] = unquote(leader["wikipedia_url"])

            # Extract and attach the first paragraph of the Wikipedia page
            leader["summary"] = self.get_first_paragraph(leader["wikipedia_url"])

        return leader

    def enrich_all_leaders(
        self, leaders: list[dict[str, Any]], use_multithreading: bool = False
    ):
        """
        Enrich a list of leaders with decoded Wikipedia URLs and summaries.

        Parameters:
        - leaders (list[dict]): list of leader dictionaries to enrich
        - use_multithreading (bool): whether to use threads for parallel
          enrichment

        Returns:
        - list[dict]: enriched leader dictionaries
        """
        # A thread pool is a collection of pre-initialized threads that are
        # kept ready to execute tasks. Instead of creating and destroying a
        # thread for each task (which is costly in terms of time and system
        # resources), a thread pool reuses a limited number of threads to
        # efficiently manage concurrent execution.
        if use_multithreading:
            # Use ThreadPoolExecutor to parallelize the enrichment of leaders
            # Each leader is passed to the enrich_leader() method in a
            # separate thread
            # executor.map returns an iterator over the results,
            # which we convert into a list
            with ThreadPoolExecutor() as executor:
                return list(executor.map(self.enrich_leader, leaders))
        else:
            # If multithreading is disabled, process leaders sequentially
            # Apply enrich_leader() to each leader one by one using a list
            # comprehension
            return [self.enrich_leader(leader) for leader in leaders]

    def _fetch_countries(self) -> List[str]:
        """Fetch the list of countries via the API."""
        return self.session.get(self.country_endpoint, cookies=self.cookie).json()

    def _fetch_leaders_for_country(self, country: str) -> List[Dict[str, Any]]:
        """Fetch the list of leaders for a given country."""
        params = {"country": country}
        res = self.session.get(
            self.leaders_endpoint, cookies=self.cookie, params=params
        )
        return res.json()

    def _enrich_and_log_leaders(
        self,
        country: str,
        leaders_data: List[Dict[str, Any]],
        limit_per_country: Optional[int],
        use_multithreading: bool,
    ) -> List[Dict[str, Any]]:
        """Limits, enriches and logs leaders for a given country."""
        if limit_per_country is not None:
            leaders_data = leaders_data[:limit_per_country]
        leaders_data = self.enrich_all_leaders(
            leaders_data, use_multithreading=use_multithreading
        )
        if not leaders_data:
            PrintUtils.print_color(
                f">>> No leaders returned for country '{country}'",
                Color.YELLOW,
            )
        else:
            PrintUtils.print_color(
                (f">>> Country '{country}' - {len(leaders_data)} " "leaders enriched."),
                Color.CYAN,
            )
        return leaders_data

    def _print_verbose_sample(
        self, leaders_per_country: Dict[str, List[Dict[str, Any]]]
    ):
        """Display a sample of leaders enriched if verbose=True."""
        for country, leaders in leaders_per_country.items():
            PrintUtils.print_color(
                (f">>> Country '{country}' - {len(leaders)} leaders enriched."),
                Color.CYAN,
            )
            for leader in leaders:
                summary = leader.get("summary", "")
                url = leader.get("wikipedia_url", "")
                first = leader.get("first_name", "")
                last = leader.get("last_name", "")
                name = (first + " " + last).strip() or "Unknown"
                print(f"- {name}: {summary[:150]}...")
                print(str(url) if url else "[No Wikipedia URL found]")

    def fetch_leaders(
        self,
        limit_per_country: Optional[int] = None,
        verbose: bool = False,
        use_multithreading: bool = False,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch leaders per country and enrich with Wikipedia summaries.

        Parameters:
        - limit_per_country (int or None): max number of leaders to fetch per
          country
        - verbose (bool): if True, print a sample of the enriched results

        Returns:
        - dict: mapping of country code to list of leader dictionaries
          (with Wikipedia summaries)
        """
        countries = self._fetch_countries()
        leaders_per_country: Dict[str, List[Dict[str, Any]]] = {}
        for country in countries:
            leaders_data = self._fetch_leaders_for_country(country)
            leaders_data = self._enrich_and_log_leaders(
                country, leaders_data, limit_per_country, use_multithreading
            )
            leaders_per_country[country] = leaders_data
        if verbose:
            self._print_verbose_sample(leaders_per_country)
        self.leaders_data = leaders_per_country
        return leaders_per_country  # type: ignore[reportUndefinedVariable]

    def to_json_file(self, filepath: str = "leaders.json"):
        """
        Save the leaders_data attribute to a JSON file.

        Parameters:
        - filepath (str): The file path where the JSON will be written.
          Default is 'leaders.json'.

        This method writes the internal `self.leaders_data` dictionary to a
        file in JSON format. The output is encoded in UTF-8 and prettified for
        readability.
        """
        # Default output in 'outputs/' if no folder is provided
        if not os.path.dirname(filepath):
            filepath = os.path.join("outputs", filepath)

        with open(filepath, "w", encoding="utf-8") as f:
            # Serialize the dictionary to a UTF-8 encoded JSON file
            # ensure_ascii=False: keeps special characters
            # (e.g., é, ñ, Ж, ع) intact
            # indent=2: formats the output for better readability
            json.dump(self.leaders_data, f, ensure_ascii=False, indent=2)

        # Print confirmation message in green
        PrintUtils.print_color(f"\n>>> JSON export completed: {filepath}", Color.GREEN)

    def to_csv_file(self, filepath: str = "leaders_data.csv"):
        """
        Save the leaders_data attribute to a CSV file.

        Parameters:
        - filepath (str): The file path where the CSV will be written.
          Default is 'leaders_data.csv'.
        """
        # Default output in 'outputs/' if no folder is provided
        if not os.path.dirname(filepath):
            filepath = os.path.join("outputs", filepath)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Country",
                    "First Name",
                    "Last Name",
                    "Wikipedia URL",
                    "Summary",
                ]
            )

            for country, leaders in self.leaders_data.items():
                for leader in leaders:
                    writer.writerow(
                        [
                            country,
                            leader.get("first_name", ""),
                            leader.get("last_name", ""),
                            leader.get("wikipedia_url", ""),
                            leader.get("summary", "")
                            .replace("\n", " ")
                            .replace("\r", " "),
                        ]
                    )

        # Print confirmation message in green
        PrintUtils.print_color(f"\n>>> CSV export completed: {filepath}", Color.GREEN)
