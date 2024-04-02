import time, os, socket, re, sys
from selenium import webdriver
from bs4 import BeautifulSoup
from readHTML import is_first_word_in_all_variants
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
actionOptions = True

User_OS=str(sys.platform).lower()

def get_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            username = file.readline().strip()
            password = file.readline().strip()
            if username and password:
                return username, password
    except FileNotFoundError:
        pass
    
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    # Save the credentials for next time
    with open(file_path, 'w') as file:
        file.write(username + '\n' + password + '\n')
    
    return username, password

def fetch_link_descriptions(pass_links):
    link_descriptions = []
    all_clear = False  # Flag to check if any 'nn' found in link texts
    apologize = 0
    
    while not all_clear:
        link_descriptions.clear()  # Clear previous attempt
        all_clear = True

        for i, link in enumerate(pass_links, start=1):
            try:
                descriptive_element = link.find_element(By.XPATH, "./preceding-sibling::span | ./ancestor::li")
                link_text = descriptive_element.text.strip() if descriptive_element else "Review"
            except StaleElementReferenceException:
                print(f"Stale element reference at index {i}, retrying...")
                all_clear = False
                break 
            
            # Check if 'nn' is in the link_text, if so, mark to retry
            if 'nn' in link_text.lower():
                all_clear = False
                if apologize == 0:
                    print(f"Please wait, this might take a moment...")
                elif apologize == 10:
                    print(f"Still waiting for the details to load...")
                break

            link_descriptions.append((link_text, link.get_attribute('href')))
            print(f"Option {i}: {link_text}")

        if not all_clear:
            time.sleep(apologize/3)
            if apologize < 12:
                apologize += 1

    return link_descriptions

# Function to check if a given port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Check if port 9222 is already in use
if is_port_in_use(9222):
    print("Attempting to proceed on port 9222.")
else:
    print("Establishing connection on port 9222.")

# Set up Chrome driver options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
chrome_options.add_argument('--disable-save-password-bubble')

# Function to save HTML content to a file
def save_html(html, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

# Start Chrome with remote debugging
if 'darwin' in User_OS:
    os.system("/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &")
else:
    os.system('start chrome.exe --remote-debugging-port=9222')
time.sleep(1)

try:
    # Set up Chrome driver and connect
    driver = webdriver.Chrome(options=chrome_options)
    print()
    print("Successfully connected to Chrome!")
    print()

    original_window = driver.current_window_handle
    WHG_window_found = False

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "WHG" in driver.title or "WHG" in driver.current_url:
            WHG_window_found = True
            break

    if not WHG_window_found:
        driver.switch_to.window(original_window)
        driver.get("https://whgazetteer.org/")

    credentials_path= 'PRIVATE.txt'
    username, password = get_credentials(credentials_path)
    time.sleep(2)
except Exception as e:
    print(f"Error during script execution: {e}")
    
try:
    login_link = driver.find_element(By.XPATH, "//a[@href='/accounts/login/']")
    login_link.click()
    username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_login")))
    username_input.send_keys(username)
    password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_password")))
    password_input.send_keys(password)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "primaryAction")))
    login_button.click()
    login_successful = True
except Exception:
    print("Skipping login...")

dataset_summary_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/datasets/') and contains(@href, '/summary')]")

# Check if there are multiple dataset options
if len(dataset_summary_links) >= 1:
    print("Datasets found. Please select one of the following options:")
    dataset_options = []  # This will store tuples of (title, href) for each dataset
    for i, link in enumerate(dataset_summary_links, start=1):
        # Pulling text directly from the link, which is expected to be more descriptive
        link_text = link.text.strip() or "No title available"
        dataset_options.append((link_text, link.get_attribute('href')))
        print(f"Option {i}: {link_text}")

    # Wait for user to select an option
    try:
        selected_option = int(input("Enter the number of the dataset you want to work with: ")) - 1  # Adjusting for zero indexing
        # Validate user input
        if selected_option < 0 or selected_option >= len(dataset_options):
            print("Invalid option selected. Exiting.")
            exit(1)
    except ValueError:
        print("Invalid input. Please enter a number.")
        exit(1)

    # Navigate to the selected dataset summary
    selected_dataset_href = dataset_options[selected_option][1]
    driver.get(selected_dataset_href)

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "reconciliation-tab")))
rec_tab = driver.find_element(By.ID, "reconciliation-tab")
rec_tab.click()

pass_links = driver.find_elements(By.XPATH, "//li[contains(text(), 'Pass') and not(contains(text(), 'Deferred'))]//a[contains(@href, '/review/')]")

# Fetch descriptions once correctly, ensuring no 'nn' is present
link_descriptions = fetch_link_descriptions(pass_links)

try:
    selected_option = int(input("Enter the number of the review option you want to select: ")) - 1
    if selected_option < 0 or selected_option >= len(link_descriptions):
        print("Invalid option selected. Exiting.")
        exit(1)
except ValueError:
    print("Invalid input. Please enter a number.")
    exit(1)

# Navigate to the selected "Passes" review option using href from link_descriptions
selected_review_link = link_descriptions[selected_option][1]
driver.get(selected_review_link)

while (actionOptions == True):
    try:
        time.sleep(1)
        html_source = driver.page_source
        save_html(html_source, 'html.html')
        with open('html.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        scale_element = soup.find('div', class_='leaflet-control-scale-line')
        if scale_element:
            scale_text = scale_element.get_text()

            if ' km' in scale_text:
                number = float(re.search(r'\d+', scale_text).group()) * 1000
            elif 'meters' in scale_text:
                number = float(re.search(r'\d+', scale_text).group())
            print(scale_text)
            print(number)
        result = is_first_word_in_all_variants("first_words.txt", "variants.txt")
        result = number < 50000
        print(result)
        if result:
            close_match_buttons = driver.find_elements(By.XPATH, '//input[@type="radio" and @value="closeMatch"]')
            for button in close_match_buttons:
                button.click()  # Click the button
                time.sleep(0.25)

            save_button = driver.find_element(By.ID, "btn_save")
            save_button.click()
            print("\n\n\n\n\n")
            time.sleep(0.25)
        else:
            match = re.search(r'Record (\d+) of', html_source)
            if match:
                record_number = int(match.group(1))
                next_page_number = record_number + 1
                print("\033[91mHuman input required, skipping record #" + str(record_number) + "\033[0m")
                try:
                    next_button = driver.find_element(By.XPATH, f"//a[@href='?page={next_page_number}']")
                    next_button.click()
                except Exception as e:
                    print(f"Failed to click the next button. Error: {e}")
            time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")