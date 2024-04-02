from bs4 import BeautifulSoup
import re

def clean_text(text):
    return re.sub(r'[^A-Za-z]+', ' ', text).strip()

def does_first_word_match():
    with open('1country.txt', 'r', encoding='utf-8') as file:
        first_word_1country = file.readline().split()[0]

    with open('2country.txt', 'r', encoding='utf-8') as file:
        words_2country = file.read().split()

    return (first_word_1country in words_2country) or ("unspecified" in words_2country)

def main():
    html_content = ""

    with open('html.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    paragraphs = soup.find_all('p')

    text_for_1country = ""
    texts_for_2country = []

    found_first_modern_country = False

    for p in paragraphs:
        if 'Modern countries' in p.get_text():
            if not found_first_modern_country:  # Only for the first occurrence
                text_for_1country = clean_text(p.get_text().split(':', 1)[-1])
                found_first_modern_country = True
        if 'Countries:' in p.get_text():
            texts_for_2country.append(clean_text(p.get_text().split(':', 1)[-1]))

    if text_for_1country:
        with open('1country.txt', 'w', encoding='utf-8') as file:
            file.write(text_for_1country + '\n')

    with open('2country.txt', 'w', encoding='utf-8') as file:
        for text in texts_for_2country:
            file.write(text + '\n')

    # Example usage of does_first_word_match function
    match_result = does_first_word_match()
    return(match_result)
    #print(f"Does the first word match: {match_result}")

if __name__ == "__main__":
    main()
