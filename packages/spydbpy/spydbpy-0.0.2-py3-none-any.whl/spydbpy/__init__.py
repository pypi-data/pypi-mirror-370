import requests

class Spyrgedb:
    def __init__(self, api_key, api_url="http://fi8.bot-hosting.net:21253"):
        self.api_key = api_key
        self.api_url = api_url

    def save(self, collection, data):
        """Saves a new document to a collection."""
        payload = {
            "apiKey": self.api_key,
            "collection": collection,
            "data": data
        }
        try:
            response = requests.post(f"{self.api_url}/api/save", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error saving data: {e}")
            return {"success": False, "message": "Failed to save data."}

    def get(self, collection):
        """Retrieves all documents from a collection."""
        params = {
            "apiKey": self.api_key,
            "collection": collection
        }
        try:
            response = requests.get(f"{self.api_url}/api/get", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting data: {e}")
            return {"success": False, "message": "Failed to retrieve data."}

    def delete(self, collection, query):
        """Deletes documents from a collection based on a query."""
        payload = {
            "apiKey": self.api_key,
            "collection": collection,
            "query": query
        }
        try:
            response = requests.post(f"{self.api_url}/api/delete", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error deleting data: {e}")
            return {"success": False, "message": "Failed to delete data."}