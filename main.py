import re
from wiki import get_first_sentence_and_link

references = {}

def replace_words_with_links(text):
    words_regex = r'(?<!\\)\b\w+\b'

    def replacer(match):
        word = match.group(0)
        w = get_first_sentence_and_link(word)
        if w:
            sentence, link = w
            ref_key = word.replace(" ", "_")
            references[ref_key] = sentence
            references[word] = sentence
            return f"\\href{{{link}}}{{{word}}} (\\cite{{{ref_key}}})"

    updated_text = re.sub(words_regex, replacer, text)
    return updated_text

def process_sexy_abstract_block(latex_content):
    pattern = re.compile(r'(?s)(% SEXY_ABSTRACT_BEGIN.*?% SEXY_ABSTRACT_END)')

    def process_block(match):
        block_text = match.group(1)
        abstract_content = re.search(r'(?<=% SEXY_ABSTRACT_BEGIN)(.*?)(?=% SEXY_ABSTRACT_END)', block_text, re.DOTALL)
        if abstract_content:
            original_text = abstract_content.group(1)
            updated_text = replace_words_with_links(original_text)
            return block_text.replace(original_text, updated_text)
        return block_text

    updated_content = re.sub(pattern, process_block, latex_content)
    return updated_content

def add_references(latex_content):
    pattern = re.compile(r'(?s)(% SEXY_REFERENCES_BEGIN.*?% SEXY_REFERENCES_END)')

    def process_block(match):
        block_text = match.group(1)
        updated_text = ''
        for reference in references:
            updated_text += f'\\bibitem{{{reference}}} {references[reference]}\n'
        return block_text.replace(block_text, f'% SEXY_REFERENCES_BEGIN\n{updated_text}% SEXY_REFERENCES_END')

    updated_content = re.sub(pattern, process_block, latex_content)
    return updated_content

def process_latex_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    updated_content = process_sexy_abstract_block(content)
    updated_content = add_references(updated_content)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)

process_latex_file('doc.tex', 'article_with_links.tex')
