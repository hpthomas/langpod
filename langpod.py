from sys import argv
from wikipedia import pull_article
from chat import chat

def main():
    if len(argv) < 2:
        print("Usage: python langpod.py <search_query>")
        return
    search_query = argv[1]
    article_contents = pull_article(search_query)
    print(article_contents)
    print(chat("say hi in json"))
    

if __name__ == '__main__':
    main()