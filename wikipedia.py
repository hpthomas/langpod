import wikipediaapi
import requests
from chat import chat, TEXT_SYSTEM_PROMPT

def get_full_article_text(article_name, language):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='github.com/hpthomas/langpod',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        language=language
    )
    page_py = wiki_wiki.page(article_name)
    if not page_py.exists():
        print(f"Article '{article_name}' does not exist.")
        return None
    return page_py.text

def search_wikipedia(query, language, limit=10):
    url = f"https://{language}.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit={limit}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        search_results = data['query']['search']
        return [result['title'] for result in search_results]
    else:
        return f"Error: Unable to perform search. Status code: {response.status_code}"

def translate_query(query, source_language, target_language):
    prompt = f"""Translate this from {source_language} to {target_language}. Return only the translated text and no explanation or note.
{query}
"""
    result = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    return result.strip()

def find_article(query: str, home_language: str, away_language: str, translate_search: bool):
    if translate_search:
        query = translate_query(query, home_language, away_language)
    candidates = search_wikipedia(query, away_language)
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