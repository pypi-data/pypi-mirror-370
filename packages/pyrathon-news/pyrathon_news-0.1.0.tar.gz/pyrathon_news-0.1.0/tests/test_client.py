from pyrathon_news import PyrathonClient

def test_get_news():
    client = PyrathonClient("http://localhost/pyrathon/pagina%20portafolio/news/")
    try:
        data = client.get_news()
        print("✅ Noticias recibidas:", data)
    except Exception as e:
        print("❌ Error al obtener noticias:", e)

if __name__ == "__main__":
    test_get_news()