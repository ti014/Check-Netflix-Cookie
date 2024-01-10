import json
import os
import sys
import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import progressbar
import psutil
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

stop_flag = threading.Event()

def process_file(filepath):
    global exceptions
    with open(filepath, "r", encoding="utf-8") as file:
        try:
            cookies = load_cookies_from_json(filepath)
            open_webpage_with_cookies("https://netflix.com/login", cookies, os.path.basename(filepath))
        except json.decoder.JSONDecodeError:
            print(f"Please use cookie_converter.py to convert your cookies to json format! (File: {os.path.basename(filepath)})\n")
            exceptions += 1
        except Exception as e:
            print(f"Error occurred: {str(e)} - {os.path.basename(filepath)}")
            exceptions += 1

        if stop_flag.is_set():
            sys.exit()


ti_netflix_folder = f"ti_checked_{datetime.now().strftime('%H-%M-%S_%d-%m-%Y')}"
exceptions = 0
working_cookies = 0
expired_cookies = 0

def kill_driver(driver):
    driver.quit()

def get_folder_path():
    if os.name == "posix":
        folder_path = "json_cookies"
        if not os.path.isdir(folder_path):
            print("Error: Default 'json_cookies' folder not found, please run cookie_converter.py first.")
            sys.exit()
    else:
        import tkinter
        from tkinter import filedialog

        folder_path = filedialog.askdirectory() if config.use_folder_selector else "json_cookies"
        print(f"Using path: {folder_path}")

    return folder_path

def maximum():
    count = 0
    for _, _, files in os.walk("json_cookies"):
        count += len(files)
    return count

def load_cookies_from_json(json_cookies_path):
    with open(json_cookies_path, "r", encoding="utf-8") as cookie_file:
        return json.load(cookie_file)

def open_webpage_with_cookies(link, json_cookies, filename):
    global working_cookies, expired_cookies
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)

    for cookie in json_cookies:
        driver.add_cookie(cookie)

    driver.refresh()

    if driver.find_elements(By.CSS_SELECTOR, ".btn") or driver.find_elements(By.CSS_SELECTOR, ".e1ax5wel1"):
        print(f"Cookie Not working - {filename}")
        expired_cookies += 1
    else:
        os.makedirs(ti_netflix_folder, exist_ok=True)
        ti_filename = f"{ti_netflix_folder}/ti_cookie_{working_cookies + 1}"
        with open(f"{ti_filename}.json", "w", encoding="utf-8") as a:
            json.dump(json_cookies, a, indent=4)
        working_cookies += 1
        print(f"Working cookie found! - {filename}. Moved to {ti_filename}")

    kill_driver(driver)

def process_file(filepath):
    global exceptions
    with open(filepath, "r", encoding="utf-8") as file:
        try:
            cookies = load_cookies_from_json(filepath)
            open_webpage_with_cookies("https://netflix.com/login", cookies, os.path.basename(filepath))
        except json.decoder.JSONDecodeError:
            print(f"Please use cookie_converter.py to convert your cookies to json format! (File: {os.path.basename(filepath)})\n")
            exceptions += 1
        except Exception as e:
            print(f"Error occurred: {str(e)} - {os.path.basename(filepath)}")
            exceptions += 1

if __name__ == "__main__":
    try:
        folder_path = get_folder_path()
        progress = 0
        pbar = progressbar.ProgressBar(maxval=maximum())
        pbar.start()

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_filepath = {executor.submit(process_file, os.path.join(folder_path, filename)): filename for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))}
            for future in as_completed(future_to_filepath):
                future.result()

        pbar.finish()

        print(
        f"\nSummary:\nTotal cookies: {maximum()}\nWorking cookies: {working_cookies}\nExpired cookies: {maximum() - working_cookies}\nInvalid cookies: {exceptions}"
    )

    except KeyboardInterrupt:
        print("\n\nProgram Interrupted by user")
        stop_flag.set()