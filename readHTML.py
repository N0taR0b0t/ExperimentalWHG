import re
from bs4 import BeautifulSoup

html_file_path = 'html.html'
keyword = 'Variants'

def extract_first_word_and_save(file_path, output_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(class_='text-danger')

    with open(output_file, 'w', encoding='utf-8') as file:
        for element in elements:
            text = element.get_text().strip()
            words = re.findall(r'\b[a-zA-Z]+\b', text)  # Find all words with letters only
            first_word = words[0] if words else ""  # Take the first word if available
            file.write(first_word + '\n')

def extract_text_after_variants_and_save(file_path, keyword, output_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(class_='scroll65')

    with open(output_file, 'w', encoding='utf-8') as file:
        for element in elements:
            text = element.get_text().strip()
            keyword_index = text.find(keyword)
            if keyword_index != -1:
                text_after_keyword = text[keyword_index + len(keyword):].strip()
                file.write(text_after_keyword + '\n###\n')

def is_first_word_in_all_variants(first_words_file, variants_file):
    extract_first_word_and_save(html_file_path, 'first_words.txt')
    extract_text_after_variants_and_save(html_file_path, keyword, 'variants.txt')
    # Read the first entry from first_words.txt and strip whitespace
    with open(first_words_file, 'r', encoding='utf-8') as file:
        first_word = file.readline().strip()

    # Read and split variants.txt by "###", trimming whitespace
    with open(variants_file, 'r', encoding='utf-8') as file:
        variants_content = file.read().strip()
        instances = [instance.strip() for instance in variants_content.split('###') if instance.strip()]

    # Check if the first word is present in each non-empty instance
    for instance in instances:
        if first_word not in instance:
            return False

    return True if instances else False

#result = is_first_word_in_all_variants("first_words.txt", "variants.txt")
