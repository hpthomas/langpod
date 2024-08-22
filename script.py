from chat import chat
from threading import Thread

TEXT_SYSTEM_PROMPT = "Respond with the exact content requested, line-by-line. Include no additional characters or explanations unless requested."

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

Clean the following text:
{section_text}
"""
    print('Cleaning section', index)
    result = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    lines = result.split('\n')
    result = '\n'.join([line for line in lines if line.strip()])
    cleaned_sections[index] = result

def spanish_english_section(text, translations, index):
    prompt = f"""Create a spanish-english-spanish-english sentence-by-sentence translation of the text below.
You must respond with a Spanish sentence first, followed by the original English sentence, and repeat this pattern for the entire text.
Numbers must be written out in full.
Begin each line with "es:" or "en" to indicate the language of the sentence.

{text}
"""
    results = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    sentences = results.split('\n')
    print(results)
    english = [sentence[3:] for sentence in sentences if sentence.startswith('en:')]
    spanish = [sentence[3:] for sentence in sentences if sentence.startswith('es:')]
    if (len(english) != len(spanish)):
        raise ValueError("Number of Spanish and English sentences do not match.")
    result = {
        'es': spanish,
        'en': english
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

def translate_article(article_contents):
    chunks = chunk_raw_article(article_contents)
    
    translations = [None] * len(chunks)

    for batch_start in range(0, len(chunks), 5):
        batch_end = min(batch_start + 5, len(chunks))
        threads = []
        for index in range(batch_start, batch_end):
            thread = Thread(target=spanish_english_section, args=(chunks[index], translations, index))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    
    joined = {
        'es': [],
        'en': []
    }
    for translation in translations:
        joined['es'] += translation['es']
        joined['en'] += translation['en']
    return joined

def regrade_section(section_text, level, cleaned_sections, index):
    prompt = f"""This article is going to be read out-loud to an English langugage learner at the "{level}" level. 
The article must be written specifically for "{level}" level learners. 
This is not a copy of the original text, but a new, simplified version of the text. 
(Note: If the original text is already simpler than the "{level}" level, make no changes.)
Rewrite the text below to a level they are likely to understand most of the content.
If the level is laughably far below the text, you can shorten the text to a few sentences that are at the correct level. 
For example, "absolute beginner" level text should have sentences of a few words at most.
NOTE: Do not add any introductory text or explanations, and do not add any titles, headers, or notes.
Respond with a simplified version of the text that is suitable for an English language learner at the "{level}" level, and nothing else.

{section_text}
"""
    print('Cleaning section', index)
    print(prompt)
    result = chat(prompt, system_prompt=TEXT_SYSTEM_PROMPT)
    lines = result.split('\n')
    result = '\n'.join([line for line in lines if line.strip()])
    cleaned_sections[index] = result

def regrade_article(article_contents, level):
    chunks = chunk_raw_article(article_contents)
    cleaned_sections = [None] * len(chunks)
    for batch_start in range(0, len(chunks), 5):
        batch_end = min(batch_start + 5, len(chunks))
        threads = []
        for index in range(batch_start, batch_end):
            thread = Thread(target=regrade_section, args=(chunks[index], level, cleaned_sections, index))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return "\n".join(cleaned_sections)