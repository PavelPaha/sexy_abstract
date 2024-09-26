import re
from wiki import *

references = {}

def replace_words_with_links(text, word_data):
    words_regex = r'(?<!\\)\b\w+\b'

    def replacer(match):
        word = match.group(0)
        if word in word_data and word_data[word]:
            sentence, link = word_data[word]
            ref_key = word.replace(" ", "_")
            references[ref_key] = sentence
            references[word] = sentence
            return f"\\href{{{link}}}{{{word}}} (\\cite{{{ref_key}}})"
        return word

    updated_text = re.sub(words_regex, replacer, text)
    return updated_text


async def fetch_references(words):
    async with aiohttp.ClientSession() as session:
        tasks = [get_first_sentence_and_link_async(session, word) for word in words]
        results = await asyncio.gather(*tasks)
        return dict(zip(words, results))


async def process_sexy_abstract_block_async(latex_content):
    pattern = re.compile(r'(?s)(% SEXY_ABSTRACT_BEGIN.*?% SEXY_ABSTRACT_END)')

    def process_block(match):
        block_text = match.group(1)
        abstract_content = re.search(r'(?<=% SEXY_ABSTRACT_BEGIN)(.*?)(?=% SEXY_ABSTRACT_END)', block_text, re.DOTALL)
        if abstract_content:
            original_text = abstract_content.group(1)
            words = re.findall(r'(?<!\\)\b\w+\b', original_text)
            return original_text, block_text, words
        return None, block_text, []

    matches = [process_block(match) for match in pattern.finditer(latex_content)]

    all_words = {word for _, _, words in matches for word in words}
    word_data = await fetch_references(all_words)

    updated_content = latex_content
    for original_text, block_text, words in matches:
        if original_text:
            updated_text = replace_words_with_links(original_text, word_data)
            updated_content = updated_content.replace(original_text, updated_text)

    return updated_content


def add_references(latex_content):
    pattern = re.compile(r'(?s)(% SEXY_REFERENCES_BEGIN.*?% SEXY_REFERENCES_END)')

    def process_block(match):
        block_text = match.group(1)
        updated_text = ''
        for reference in references:
            updated_text += f'\\bibitem{{{reference}}} \\newblock {references[reference]}\n'
        return block_text.replace(block_text, f'% SEXY_REFERENCES_BEGIN\n{updated_text}% SEXY_REFERENCES_END')

    updated_content = re.sub(pattern, process_block, latex_content)
    return updated_content


# Основная функция для обработки файла
async def process_latex_file_async(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    updated_content = await process_sexy_abstract_block_async(content)
    updated_content = add_references(updated_content)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)


# Запуск асинхронной обработки
asyncio.run(process_latex_file_async('doc.tex', 'article_with_links.tex'))
