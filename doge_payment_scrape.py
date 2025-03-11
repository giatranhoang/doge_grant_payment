from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time
import re

# Date pattern (e.g., "March 6, 2025")
date_pattern = r"([A-Za-z]+ \d{1,2}, \d{4})"

# Initialize WebDriver
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for performance
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=options)
    return driver

# Extract all available dates from the page
def get_dates(driver):
    wait = WebDriverWait(driver, 10)
    date_elements = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[contains(@class, 'cursor-pointer')]")
    ))
    
    dates = []
    for element in date_elements:
        match = re.search(date_pattern, element.text)
        if match:
            dates.append((match.group(1), element))  # Store (date, element) pairs
    
    print(f"Found {len(dates)} dates.")
    return dates

# Scrape data for a specific date
def scrape_date(date, driver):
    wait = WebDriverWait(driver, 10)
    all_data = []

    # Click on the "View All" button if available
    try:
        view_all_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(text(), 'View All')]")
        ))
        view_all_button.click()
        print(f"Clicked 'View All' for {date}.")
        time.sleep(2)
    except Exception:
        print(f"'View All' button not found for {date}.")

    # Find and click the date filter
    try:
        date_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(text(), '{date}')]")
        ))
        date_element.click()
        print(f"Clicked date: {date}")
        time.sleep(2)
    except Exception as e:
        print(f"Error clicking date {date}: {e}")
        return []

    # Pagination loop
    while True:
        print(f"Scraping data for {date}...")
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr")))
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                row_data = [col.text.strip() for col in cols]
                row_data.append(date)  # Add "REQUEST DATE"
                all_data.append(row_data)

            print(f"Extracted {len(rows)} rows for {date}")

            # Click "Next" button if enabled
            try:
                next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                    print(f"Reached last page for {date}.")
                    break

                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(1.5)  # Allow time for data to load
            except Exception:
                print(f"No 'Next' button found for {date}, stopping pagination.")
                break

        except Exception as e:
            print(f"Error scraping table data for {date}: {e}")
            break  # Stop loop if no table rows

    return all_data

# Multi-threaded execution for scraping each date
def process_date(date):
    driver = get_driver()
    driver.get("https://doge.gov/payments")
    data = scrape_date(date, driver)
    driver.quit()
    return data

# Main execution
if __name__ == "__main__":
    main_driver = get_driver()
    main_driver.get("https://doge.gov/payments")

    try:
        date_list = get_dates(main_driver)  # Extract dates
    except Exception as e:
        print(f"Error extracting dates: {e}")
        date_list = []

    main_driver.quit()  # ✅ Quit only after extracting dates

    all_results = []

    # Multi-threading for faster scraping
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda d: process_date(d[0]), date_list)

    # Collect results
    for result in results:
        all_results.extend(result)

    # Save to CSV
    columns = ["AGENCY", "RECIPIENT", "AWARD DESCRIPTION", "PAYMENT DATE", "PAYMENT", "REQUEST DATE"]
    df = pd.DataFrame(all_results, columns=columns)
    df.to_csv("doge_payments.csv", index=False)

    print("Scraping complete. Data saved to 'doge_payments.csv'.")
