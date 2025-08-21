import os

import requests


class OutscraperClient:
    def __init__(self):
        self.environment = os.environ.get("ENV", "Staging")
        self.base_url = "https://api.app.outscraper.com"

    @property
    def headers(self):
        common_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        auth_token = {
            "Staging": "MjZjYWUyMzg4MzUxNDk2Zjk0OGRlOTFlMzkyMDhhYWF8ZDhlNzM5OGVmOQ",
            "Prod": "MjZjYWUyMzg4MzUxNDk2Zjk0OGRlOTFlMzkyMDhhYWF8ZDhlNzM5OGVmOQ",
        }.get(self.environment)

        return {**common_headers, "X-API-KEY": auth_token}

    @property
    def webhook_url(self):
        return {
            "Staging": "https://api-staging.getreach.ai/webhooks/data-bridge/outscraper/scraper-completed?token=tRm4k75N9hK1vF0dSwIi0HcMyV",
            "Prod": "https://api.getreach.ai/webhooks/data-bridge/outscraper/scraper-completed?token=tRm4k75N9hK1vF0dSwIi0HcMyV",
        }.get(self.environment)

    def search_google_maps_reviews(
        self, google_place_id: str, start_from: int = None, cutoff=None
    ):
        params = {
            "query": google_place_id,
            "webhook": self.webhook_url,
            "reviewsLimit": 0,
        }
        if start_from:
            params["start"] = start_from
        if cutoff:
            params["cutoff"] = cutoff
        resp = requests.get(
            f"{self.base_url}/maps/reviews-v3",
            headers=self.headers,
            params=params,
        )
        return resp

    def get_job_details(self, job_id: str):
        """Perform a GET request to retrieve details for a specific job using its job_id."""
        url = f"{self.base_url}/requests/{job_id}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_balance(self):
        url = f"{self.base_url}/profile/balance"
        response = requests.get(url, headers=self.headers)
        return response
