import requests

def fetch_markdown(url: str) -> str:
    
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url, timeout=10)
    response.raise_for_status()  # Raise error if request fails
    return response.text

if __name__ == "__main__":
    url = "https://github.com/alexeygrigorev/minsearch"
    characters_content = fetch_markdown(url)
    print(f'Characters in the markdown content: {len(characters_content)}')
    
