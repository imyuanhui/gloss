import requests
import os
from dotenv import load_dotenv

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03"
}


def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


def create_page(data: dict):
    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"data_source_id": DATA_SOURCE_ID},
        "properties": data
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()

