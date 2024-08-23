from chat import chat, TEXT_SYSTEM_PROMPT
from threading import Thread
from languages import LANGUAGES


CHUNK_LIMIT_CHARS = 5000
def chunk_raw_article(article_contents, max_sections = None):
    chunks = article_contents.split('\n')
    max_section_length = 5000
    sections = []
    current_section = ""
    for chunk in chunks:
        if len(current_section) + len(chunk) > max_section_length:
            sections.append(current_section + '\n')
            current_section = ""
        current_section += chunk + '\n'
    if current_section:
        sections.append(current_section)

    if max_sections:
        sections = sections[:max_sections]
    
    return sections

def clean_section(section_text, cleaned_sections, index):
    prompt = f"""This article is going to be read out-loud to a User.
Remove any content that is not suitable for reading out-loud to a User.
Remove lists, tables, and any other content that is not a part of the main text.
Include titles and section headers.
Every sentence should be on its own line, with no empty lines.
Write out numbers and symbols fully - do not include any digits!
Write out dates in a natural way, e.g. "January first, nineteen eighty two"
The text must remain in it's source language, but be cleaned up for reading out-loud.

Clean the following text:
{section_text}
"""
    print('Cleaning section', index)
    result = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    lines = result.split('\n')
    result = '\n'.join([line for line in lines if line.strip()])
    cleaned_sections[index] = result

def translate_section(text, home, away, translations, index):
    prompt = f"""Create a line by line {away}-{home} sentence-by-sentence translation of the text below.
You must respond with an original {LANGUAGES[away]} sentence first, followed by it's ${LANGUAGES[home]} translation, and repeat this pattern for the entire text.
Numbers must be written out in full.
Begin each line with "{away}:" or "{home}" to indicate the language of the sentence.

{text}
"""
    results = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    sentences = results.split('\n')
    print(results)
    home_sentences = [sentence[3:] for sentence in sentences if sentence.startswith(home) or sentence.startswith(LANGUAGES[home])]
    away_sentences = [sentence[3:] for sentence in sentences if sentence.startswith(away) or sentence.startswith(LANGUAGES[away])]
    if (len(home) != len(away)):
        raise ValueError("Number of Spanish and home sentences do not match.")
    result = {
        away: away_sentences,
        home: home_sentences
    }
    translations[index] = result

def get_clean_article(article_contents, max_sections = None):
    sections = chunk_raw_article(article_contents, max_sections)
    if len(sections) == 0:
        raise ValueError("No sections found in article, or could not add first without exceeding limit.")

    cleaned_sections = [None] * len(sections)

    for batch_start in range(0, len(sections), 5):
        batch_end = min(batch_start + 5, len(sections))
        threads = []
        for index in range(batch_start, batch_end):
            thread = Thread(target=clean_section, args=(sections[index], cleaned_sections, index))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return "\n".join(cleaned_sections)

def translate_article(article_contents, home, away):
    chunks = chunk_raw_article(article_contents)
    
    translations = [None] * len(chunks)

    for batch_start in range(0, len(chunks), 5):
        batch_end = min(batch_start + 5, len(chunks))
        threads = []
        for index in range(batch_start, batch_end):
            thread = Thread(target=translate_section, args=(chunks[index], home, away, translations, index))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    
    joined = {
        away: [],
        home: []
    }
    for translation in translations:
        joined[home] += translation[home]
        joined[away] += translation[away]
    return joined

def regrade_section(section_text, level, language, cleaned_sections, index):
    prompt = f"""This article is going to be read out-loud to a {LANGUAGES[language]} learner at a {level} level. 
The article must be written specifically for {level}-level {LANGUAGES[language]} learners. 
If the text is substantially above this level, it is expected that you greatly simplify the text - for a sentence like "The quick brown fox jumps over the lazy dog" into "The fox jobs over the dog.".
Do not write a copy of the original text, but a new, simplified version of the text. 
NOTE: Do not add any introductory text or explanations, and do not add any titles, headers, or notes.
Respond with a simplified version of the text that is suitable for an home language learner at the a {level} {LANGUAGES[language]} level, and nothing else.

{section_text}
"""
    print('Cleaning section', index)
    print(prompt)
    result = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    lines = result.split('\n')
    result = '\n'.join([line for line in lines if line.strip()])
    cleaned_sections[index] = result

def regrade_article(article_contents, level, away_language):
    chunks = chunk_raw_article(article_contents)
    cleaned_sections = [None] * len(chunks)
    for batch_start in range(0, len(chunks), 5):
        batch_end = min(batch_start + 5, len(chunks))
        threads = []
        for index in range(batch_start, batch_end):
            thread = Thread(target=regrade_section, args=(chunks[index], level, away_language, cleaned_sections, index))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return "\n".join(cleaned_sections)