import wikipediaapi
import requests

def get_full_article_text(article_name):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='github.com/hpthomas/langpod',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        language='en'
    )
    page_py = wiki_wiki.page(article_name)
    if not page_py.exists():
        print(f"Article '{article_name}' does not exist.")
        return None
    return page_py.text

def search_wikipedia(query, limit=10):
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        search_results = data['query']['search']
        return [result['title'] for result in search_results]
    else:
        return f"Error: Unable to perform search. Status code: {response.status_code}"

def find_article(query):
    candidates = search_wikipedia(query)
    if not candidates:
        return "No articles found."
    else:
        for candidate in candidates:
            print(candidate)
            if candidate == query:
                return candidate
            valid = input(f"Is this the article you are looking for? (y/n): ")
            if valid.lower() == 'y':
                return candidate
        return "No articles found."