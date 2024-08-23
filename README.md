# LangPod
Turns any Wikipedia article into a multilingual "podcast" in your target language. More experimentally, it can rewrite an article to a level more suitable to newer learners before converting to audio. 

Warning - this gets quite expensive. A large article like [España](https://es.wikipedia.org/wiki/Espa%C3%B1a), plus it's English translation, totals over 300k characters, which would cost close to $100 using ElevenLabs' entry-level plans (but only 1/3rd of that on the highest usage tier).

If you'd like to be a beta-tester for a (paid) web generation UI & content vault for this sort of multilingual audio, [join the waiting list](https://docs.google.com/forms/d/1FU_2kR9lYWMMeF-1QcF6NVVd_8nVcL3peXKn7ZHuk24/)!

## Examples
LangPod generates audio sentence-by-sentence and can repeat sentences in various configurations - I (an English speaker learning Spanish) find it helpful to play a Spanish sentence twice, then play the English translation once, which is how these examples are structured. Most of these are short subsets of articles, given the cost, but the Spanish version is a complete article.

___[Aprendizaje Automático (Machine Learning)](https://es.wikipedia.org/wiki/Aprendizaje_autom%C3%A1tico)___: [Spanish/English](https://github.com/hpthomas/langpod/blob/main/samples/ML_es_es_en.mp3?raw=true) or [Spanish Only](https://github.com/hpthomas/langpod/blob/main/samples/ML_es.mp3?raw=true)

__[Apprentissage Automatique (Machine Learning)](https://fr.wikipedia.org/wiki/Apprentissage_automatique)__: [French/English](https://github.com/hpthomas/langpod/blob/main/samples/ML_fr_fr_en.mp3?raw=true) or [French Only](https://github.com/hpthomas/langpod/blob/main/samples/ML_fr.mp3?raw=true)

__[Maschinelles Lernen (Machine Learning)](https://de.wikipedia.org/wiki/Maschinelles_Lernen)__: [German/English](https://github.com/hpthomas/langpod/blob/main/samples/ML_de_de_en.mp3?raw=true) or [German Only](https://github.com/hpthomas/langpod/blob/main/samples/ML_de.mp3?raw=true)

## Usage
An OpenAI API key is required (`OPENAI_API_KEY`) for text translations, and an ElevelLabs API Key (`ELEVENLABS_API_KEY`) is strongly reccomended for dictation - the OpenAI endpoint for this works fine but sounds much worse to me. Voice IDs are hard-coded at the moment. This saves files and translations locally so it won't make the same API calls repeatedly.

```
python langpod.py <search_query> [level] [options]
```

Arguments
```
  search_query           The search query for the Wikipedia article
  level                  The level for regrading the article (optional)
```

Options
```
  -h, --help             Show this help message and exit
  -hl, --home-language   The language you speak (default: en)
  -al, --away-language   The language you are learning (default: es)
  -ts, --translate-search
                         Translate the search query (i.e. query in English for Spanish article)
  -ht, --home-tts {eleven,openai}
                         TTS engine for home language
  -at, --away-tts {eleven,openai}
                         TTS engine for away language
  -t, --tts {eleven,openai}
                         TTS engine for both languages
  -p, --play-order       Order to play audio file. Use language abbreviation separated by "-", e.g. "es-es-en"
  -s, --silent           Do not play audio. By default, langpod will download a batch of five sentences, play them, then continue
  -l, --limit LIMIT      Limit the number of sentences to translate
  -o, --outfile OUTFILE  Output file for combined audio (default: output.mp3)
```
Example:
```
python langpod.py "Machine Learning" -hl en -al fr -t eleven -p fr-fr-en-fr -l 20 -o einstein.mp3
```

This command will:
1. Search for an article about Albert Einstein
2. Regrade it to an intermediate level
3. Translate between English (home language) and French (away language)
4. Use Eleven Labs for text-to-speech in both languages
5. Play the audio in Spanish-English-Spanish order
6. Limit processing to 20 sentences
7. Save the combined audio as einstein.mp3

__Note:__ Both a person and a translation request can be said to have a "target language", so the code & params use "away language" to mean the language you're learning, to avoid (or introduce?) confusion. 

## Pedagogy
- I think this approach can be genuinely useful __for indermediate+ language learners__, especially if you want to work on __vocabulary retention__ for technical subjects
- It's best to learn from text originally written in your target language by a native/fluent speaker, so you should generally use an article __from your target language's wikipedia__ - avoid learning from text machine-translated into your target language if possible
- When you use an LLM to re-grade target-language text, you are listening to machine-generated text which might contian unnatural uses of your target language