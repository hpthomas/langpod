from sys import argv
from wikipedia import find_article, get_full_article_text
from script import get_clean_article, translate_article, regrade_article
from audio import speak_batch, play_mp3
import os
import json


def main():
    search_query = argv[1]
    if len(argv) > 2:
        level = argv[2]
    else:
        level = None
    article_name = find_article(search_query)
    article_contents = None
    article_dir = f"data/{article_name.replace(' ', '_')}"

    if not os.path.exists(article_dir):
        os.makedirs(article_dir)
    if not os.path.exists(f"{article_dir}/en/"):
        os.makedirs(f"{article_dir}/en/")
    if not os.path.exists(f"{article_dir}/es/"):
        os.makedirs(f"{article_dir}/es/")

    if level is not None and not os.path.exists(f"{article_dir}/{level.replace(' ','_')}/"):
        os.makedirs(f'{article_dir}/{level.replace(" ","_")}/')
    if level is not None and not os.path.exists(f'{article_dir}/{level.replace(" ","_")}/en/'):
        os.makedirs(f'{article_dir}/{level.replace(" ","_")}/en/')
    if level is not None and not os.path.exists(f'{article_dir}/{level.replace(" ","_")}/es/'):
        os.makedirs(f'{article_dir}/{level.replace(" ","_")}/es/')

    base_path = f"{article_dir}/base.json"
    translation = None
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            translation = json.load(f)
    else:
        article_contents = get_full_article_text(article_name)
        cleaned = get_clean_article(article_contents, max_sections=1)
        translation = translate_article(cleaned)
        with open(base_path, 'w') as f:
            json.dump(translation, f)

    if level is not None:
        article_dir = f"{article_dir}/{level.replace(' ','_')}"
        level_article_path = f"{article_dir}/base.json"
        if os.path.exists(level_article_path):
            with open(level_article_path, 'r') as f:
                translation = json.load(f)
        else:
            clean_article_contents = '\n'.join(translation['en'])
            regraded = regrade_article(clean_article_contents, level)
            translation = translate_article(regraded)
            with open(level_article_path, 'w') as f:
                json.dump(translation, f)

    if translation is None:
        raise ValueError("No translatio found.")  

    # go through translation['en'] in batches of 5
    num_texts = len(translation['en'])
    if num_texts != len(translation['es']):
        raise ValueError("Number of English and Spanish translations do not match.")
    
    for i in range(0, num_texts, 5):
        english_batch = translation['en'][i:i+5]
        spanish_batch = translation['es'][i:i+5]

        english_filenames = []
        spanish_filenames = []

        for x in range(i, i+5):
            english_filenames.append(f"{article_dir}/en/{x}.mp3")
            spanish_filenames.append(f"{article_dir}/es/{x}.mp3")

        speak_batch(english_batch, english_filenames, 'eleven')
        speak_batch(spanish_batch, spanish_filenames, 'eleven')
        spanish_only = False
        for i in range(len(english_filenames)):
            if spanish_only:
                play_mp3(spanish_filenames[i])
                continue
            play_mp3(spanish_filenames[i])
            play_mp3(spanish_filenames[i])
            play_mp3(english_filenames[i])

if __name__ == "__main__":
    main()