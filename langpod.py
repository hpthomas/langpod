import argparse
from sys import argv
from wikipedia import find_article, get_full_article_text
from script import get_clean_article, translate_article, regrade_article
from audio import speak_batch, play_mp3
from languages import LANGUAGES
import os
import json
from pydub import AudioSegment


def main():
    parser = argparse.ArgumentParser(description='Process Wikipedia articles with TTS options.')
    parser.add_argument('search_query', help='The search query for the Wikipedia article')
    parser.add_argument('level', nargs='?', default=None, help='The level for regrading the article')
    parser.add_argument('-hl', '--home-language', help='The language you speak', default='en')
    parser.add_argument('-al', '--away-language', help='The language you are learning', default='es')
    parser.add_argument('-ts', '--translate-search', action='store_true', help='Translate the search query (i.e. query in English for Spanish article)')
    parser.add_argument('-ht', '--home-tts', choices=['eleven', 'openai'], help='TTS engine for home language')
    parser.add_argument('-at', '--away-tts', choices=['eleven', 'openai'], help='TTS engine for away language')
    parser.add_argument('-t', '--tts', choices=['eleven', 'openai'], help='TTS engine for both languages')
    parser.add_argument('-p', '--play-order', help='Order to play audio file. Use language abbreviation separated by "-", e.g. "es-es-en"')
    parser.add_argument('-s', '--silent', help='do not play audio', action='store_true')
    parser.add_argument('-l', '--limit', type=int, help='Limit the number of sentences to translate')
    parser.add_argument('-o', '--outfile', help='Output file for combined audio', default='output.mp3')

    args = parser.parse_args()

    if args.tts and (args.home_tts or args.away_tts):
        parser.error("The -t/--tts option is incompatible with -ht/--home-tts and -at/--away-tts")

    home_tts = args.home_tts or args.tts or 'openai'
    away_tts = args.away_tts or args.tts or 'eleven'

    article_name = find_article(args.search_query, args.home_language, args.away_language, args.translate_search)
    article_contents = None
    language_dir = f"data/{args.away_language}"
    if not os.path.exists(language_dir):
        os.makedirs(language_dir)
    article_dir = f"{language_dir}/{article_name.replace(' ', '_')}"

    if not os.path.exists(article_dir):
        os.makedirs(article_dir)
    if not os.path.exists(f"{article_dir}/{args.home_language}/"):
        os.makedirs(f"{article_dir}/{args.home_language}/")
    if not os.path.exists(f"{article_dir}/{args.away_language}/"):
        os.makedirs(f"{article_dir}/{args.away_language}/")
    if not os.path.exists(f"{article_dir}/{args.home_language}/{home_tts}/"):
        os.makedirs(f"{article_dir}/{args.home_language}/{home_tts}/")
    if not os.path.exists(f"{article_dir}/{args.away_language}/{away_tts}/"):
        os.makedirs(f"{article_dir}/{args.away_language}/{away_tts}/")

    if args.level is not None:
        level_dir = f"{article_dir}/{args.level.replace(' ','_')}"
        if not os.path.exists(level_dir):
            os.makedirs(level_dir)
        if not os.path.exists(f'{level_dir}/{args.home_language}/{home_tts}/'):
            os.makedirs(f'{level_dir}/{args.home_language}/{home_tts}/')
        if not os.path.exists(f'{level_dir}/{args.away_language}/{away_tts}/'):
            os.makedirs(f'{level_dir}/{args.away_language}/{away_tts}/')

    base_path = f"{article_dir}/contents.json"
    translation = None
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            translation = json.load(f)
    else:
        article_contents = get_full_article_text(article_name, args.away_language)
        cleaned = get_clean_article(article_contents)
        translation = translate_article(cleaned, args.home_language, args.away_language)
        with open(base_path, 'w') as f:
            json.dump(translation, f)

    if args.level is not None:
        level_article_path = f"{level_dir}/contents.json"
        if os.path.exists(level_article_path):
            with open(level_article_path, 'r') as f:
                translation = json.load(f)
        else:
            clean_article_contents = '\n'.join(translation[args.home_language])
            regraded = regrade_article(clean_article_contents, args.level, args.away_language)
            translation = translate_article(regraded, args.home_language, args.away_language)
            with open(level_article_path, 'w') as f:
                json.dump(translation, f)

    if translation is None:
        raise ValueError("No translation found.")  

    num_texts = len(translation[args.home_language])
    if num_texts != len(translation[args.away_language]):
        raise ValueError("Number of home and Spanish translations do not match.")
    
    combined_audio = AudioSegment.empty()

    print(f'Will generate audio for {num_texts} sentences in {args.home_language} and {args.away_language}. ok?') 
    input("Press Enter to continue...")

    for i in range(0, num_texts, 5):
        # enforce limit 
        if args.limit and i >= args.limit:
            break
        elif args.limit and i + 5 > args.limit:
            batch_size = args.limit - i
        else:
            batch_size = 5
        home_batch = translation[args.home_language][i:i+batch_size]
        away_batch = translation[args.away_language][i:i+batch_size]

        num_to_speak = len(home_batch)

        home_filenames = []
        away_filenames = []

        for x in range(i, i+num_to_speak):
            home_filenames.append(f"{level_dir if args.level else article_dir}/{args.home_language}/{home_tts}/{x}.mp3")
            away_filenames.append(f"{level_dir if args.level else article_dir}/{args.away_language}/{away_tts}/{x}.mp3")

        speak_batch(home_batch, home_filenames, home_tts)
        speak_batch(away_batch, away_filenames, away_tts)

        for j in range(len(home_filenames)):
            if args.play_order:
                order = args.play_order.split('-')
                for lang in order:
                    if lang == args.home_language:
                        combined_audio += AudioSegment.from_mp3(home_filenames[j])
                        if not args.silent:
                            play_mp3(home_filenames[j])
                    elif lang == args.away_language:
                        combined_audio += AudioSegment.from_mp3(away_filenames[j])
                        if not args.silent:
                            play_mp3(away_filenames[j])
            else:
                combined_audio += AudioSegment.from_mp3(away_filenames[j])
                combined_audio += AudioSegment.from_mp3(away_filenames[j])
                combined_audio += AudioSegment.from_mp3(home_filenames[j])
                if not args.silent:
                    play_mp3(away_filenames[j])
                    play_mp3(away_filenames[j])
                    play_mp3(home_filenames[j])

    combined_audio.export(args.outfile, format="mp3")

if __name__ == "__main__":
    main()