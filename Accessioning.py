import time
import os
import socket
#import unicodedata
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from readHTML import is_first_word_in_all_variants
#from texts import does_first_word_match
from texts import main as does_first_word_match
from variants import main as check_title1_in_title2

def extract_types_from_html(file_path):
    # Define the pattern you're looking for
    pattern = re.compile(r"type\(s\)</i>: <b>(.*?)</b>", re.IGNORECASE)

    extracted_texts = []

    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Check if the pattern is in the line
            match = pattern.search(line)
            if match:
                # Extract the text between <b> and </b>
                extracted_text = match.group(1)
                extracted_texts.append(extracted_text)

    return extracted_texts

#if ("river" in types1) or ("country" in types1) or ("state" in types1):

# Function to check if a given port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Check if port 9222 is already in use
if is_port_in_use(9222):
    print("Port 9222 is in use. Please terminate other processes using this port or use a different port.")
    exit(1)

# Set up Chrome driver options
chrome_options = webdriver.ChromeOptions()

# Function to save HTML content to a file
def save_html(html, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

# Start Chrome with remote debugging
os.system("/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &")
time.sleep(0.25)

# Attempt to connect to Chrome
for attempt in range(5):
    try:
        print(f"Attempting to connect to Chrome... (Attempt {attempt + 1}/5)")
        driver = webdriver.Chrome(options=chrome_options)
        print("Successfully connected to Chrome!")
        break
    except Exception as e:
        print(f"Failed to connect to Chrome. Error: {e}")
        print("Retrying in 2 seconds...")
        time.sleep(2)
else:
    print("Failed to connect to Chrome after 5 attempts. Exiting...")
    exit(1)

# Navigate to a dummy URL to ensure control over the window
driver.get("about:blank")
time.sleep(0.25)

# Check for a window with "WHG" in the title or URL
tophat_window = None
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    if "WHG" in driver.title.lower() or "WHG" in driver.current_url.lower():
        tophat_window = handle
        break

if tophat_window is None:
    driver.get("https://whgazetteer.org/")
    time.sleep(0.25)

    # Navigate to the login page
    login_link = driver.find_element(By.XPATH, "//a[@href='/accounts/login/']")
    login_link.click()

    # Wait for the login page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_login")))

    # Enter username
    username_input = driver.find_element(By.ID, "id_login")
    username_input.send_keys("mab981")  # Replace with your username

    # Enter password
    password_input = driver.find_element(By.ID, "id_password")
    password_input.send_keys("nuwaef9pobpP*!yhu!7u-09!")  # Replace with your password

    # Click the login button
    login_button = driver.find_element(By.CLASS_NAME, "primaryAction")
    login_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/datasets/1438/summary']")))

    # Navigate to the dataset summary page
    dataset_link = driver.find_element(By.XPATH, "//a[@href='/datasets/1438/summary']")
    dataset_link.click()

    # Wait for the reconciliation tab to become clickable
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "reconciliation-tab")))

    # Click the reconciliation tab
    rec_tab = driver.find_element(By.ID, "reconciliation-tab")
    rec_tab.click()

    # Wait for the review link to become clickable
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/datasets/1438/review/8945a144-563d-4436-938a-71ed62091ff5/pass2']")))

    # Click the review link
    review_link = driver.find_element(By.XPATH, "//a[@href='/datasets/1438/review/8945a144-563d-4436-938a-71ed62091ff5/pass2']")
    review_link.click()
dir=1

# Main loop to process each record
while True:
    try:
        time.sleep(2)
        html_source = driver.page_source
        save_html(html_source, 'html.html')

        with open('html.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract scale text
        scale_element = soup.find('div', class_='leaflet-control-scale-line')
        if scale_element:
            scale_text = scale_element.get_text(strip=True)
            print(f"Extracted scale text: {scale_text}")

            # Extract the number from the scale text
            number_match = re.search(r'\d+', scale_text)
            if number_match:
                number = float(number_match.group())
                if 'km' in scale_text:
                    number *= 1000
                elif 'meters' in scale_text:
                    pass
                #print(f"Scale: {number} meters")

                # Check conditions
                countries = does_first_word_match()
                variants_match = check_title1_in_title2()
                #print(str(number) + " meters")
                print("Country Match: " + str(countries))
                print("Variant Match: " + str(variants_match))
                result = (number <= 300000 and countries and variants_match)
                if (number <= 10000) and (result == False) and variants_match:
                    print("Match justified...")
                    result = True
                elif (result == False) and (number <= 5000):
                    print("Proximity forces match...")
                    result = True
                if (number > 100000) and (number < 1000000) and (result == False) and (countries or variants_match):
                    types1 = extract_types_from_html("html.html")
                    if ("river" in types1) or ("Country" in types1) or ("state" in types1):
                        print("Type justified, Forcing match...")
                        result = True
                    else:
                        print("Type not justified...")
                if result:
                    close_match_buttons = driver.find_elements(By.XPATH, '//input[@type="radio" and @value="closeMatch"]')
                    for button in close_match_buttons:
                        button.click()
                        time.sleep(0.25)
                    save_button = driver.find_element(By.ID, "btn_save")
                    save_button.click()
                    print("Record processed and saved.")
                    time.sleep(0.25)
                else:
                    match = re.search(r'Record (\d+) of', html_source)
                    max = re.search(r' of (\d+)', html_source)
                    if match:
                        record_number = int(match.group(1))
                        print("\033[91mHuman input required, skipping record " + str(record_number) + "\033[0m")
                        max_number = int(max.group(1))
                        if (max_number == record_number) and (record_number >= 2):
                            dir *= -1 #next_page_number = record_number - 1
                        #else:
                        next_page_number = record_number + dir
                        time.sleep(2)
                        try:
                            next_button = driver.find_element(By.XPATH, f"//a[@href='?page={next_page_number}']")
                            next_button.click()
                            print("Moved to the next record.")
                        except Exception as e:
                            print(f"Failed to click the next button. Error: {e}")
                        time.sleep(2)
            else:
                print(f"Number not found in scale text: {scale_text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        break  # or handle the error as you see fit

# Close the browser
driver.quit()
