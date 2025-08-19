import requests

class PyrathonClient:
    def __init__(self, base_url="http://localhost/pyrathon/pagina%20portafolio/news/news.php"):
        self.base_url = base_url.rstrip("/")

    def get_news(self):
        """
        Obtiene noticias desde la API (endpoint: news_api.php)
        """
        url = f"{self.base_url}/news_api.php"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()