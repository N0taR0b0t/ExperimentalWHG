import re
import unicodedata
from bs4 import BeautifulSoup

def normalize_string(s):
    normalized = unicodedata.normalize('NFD', s)
    filtered = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    filtered = filtered.replace("-", " ")
    return filtered.lower()

def extract_text_danger(soup):
    elements = soup.find_all(class_="text-danger")
    return [elem.get_text(strip=True) for elem in elements]

def extract_variants_lines(html_content):
    # Regex pattern to capture text after 'variants</i>:' up to '</b>'
    pattern = re.compile(r'<i>variants</i>:\s*<b>(.*?)</b>', re.IGNORECASE)
    return pattern.findall(html_content)

def write_titles_to_files(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    with open('title1.txt', 'w', encoding='utf-8') as file1, open('title2.txt', 'w', encoding='utf-8') as file2:
        for text in extract_text_danger(soup):
            file1.write(normalize_string(text) + '\n')
        for line in extract_variants_lines(html_content):
            file2.write(normalize_string(line.strip()) + '\n')

def check_title1_in_title2():
    with open('title1.txt', 'r', encoding='utf-8') as file:
        first_line_title1 = file.readline().strip()

    with open('title2.txt', 'r', encoding='utf-8') as file:
        title2_content = file.read()

        words = title2_content.split()
        first_word = words[0] if words else ""
        #print(first_word)
        #print(first_line_title1)

    return (first_line_title1 in title2_content) or (first_word in first_line_title1)
    #return (first_line_title1 in title2_content) or (title2_content in first_line_title1)

def main():
    # Read the content of the html.html file
    with open('html.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Write to files
    write_titles_to_files(html_content)

    # Now check if title1 is in title2
    result = check_title1_in_title2()
    #print(f"Does title1 exist in title2: {result}")
    return result

if __name__ == "__main__":
    main()
