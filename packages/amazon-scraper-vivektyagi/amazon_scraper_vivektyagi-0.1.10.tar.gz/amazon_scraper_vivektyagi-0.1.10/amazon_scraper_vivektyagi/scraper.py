import os
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _setup_driver():
    USER_DATA_DIR = os.path.join(os.getcwd(), "chrome-user-data")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)

def extract_bsr(soup):
    """Extract Parent & Child Best Sellers Rank from page."""
    parent_rank = "NA"
    child_rank = "NA"

    # Method 1: structured product details tables
    possible_tables = soup.select("#productDetails_detailBullets_sections1, #productDetails_db_sections")
    for table in possible_tables:
        text = table.get_text(" ", strip=True)
        match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", text)
        if match:
            if len(match) >= 1:
                parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
            if len(match) >= 2:
                child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
            return parent_rank, child_rank

    # Method 2: detail bullets wrapper
    detail_bullets = soup.select("#detailBulletsWrapper_feature_div")
    for section in detail_bullets:
        text = section.get_text(" ", strip=True)
        match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", text)
        if match:
            if len(match) >= 1:
                parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
            if len(match) >= 2:
                child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
            return parent_rank, child_rank

    # Method 3: fallback - search entire page
    full_text = soup.get_text(" ", strip=True)
    match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", full_text)
    if match:
        if len(match) >= 1:
            parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
        if len(match) >= 2:
            child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
    return parent_rank, child_rank


def _scrape_product_details(driver, asin, country_code):
    url = f"https://www.amazon.{country_code}/dp/{asin}"
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def safe_find(selector, attr=None):
        tag = soup.select_one(selector)
        if tag:
            return tag.get(attr) if attr else tag.get_text(strip=True)
        return 'N/A'

    # Basic product info
    title = safe_find('#productTitle')
    price_tag = soup.select_one('.a-price .a-offscreen')
    price = price_tag.get_text(strip=True) if price_tag else 'N/A'
    rating_tag = soup.select_one('#acrPopover')
    rating = rating_tag['title'] if rating_tag and 'title' in rating_tag.attrs else 'N/A'
    reviews = safe_find('#acrCustomerReviewText')
    image = safe_find('#landingImage', 'src')
    if reviews != 'N/A':
        reviews = ''.join(filter(str.isdigit, reviews))

    # Brand
    brand_tag = soup.find("a", id="bylineInfo")
    if not brand_tag:
        brand_tag = soup.find("tr", string=lambda t: t and "Brand" in t)
        if brand_tag:
            brand_tag = brand_tag.find_next("td")
    brand = brand_tag.get_text(strip=True) if brand_tag else "Not Found"

    # BSR
    parent_rank, child_rank = extract_bsr(soup)

    # Product Description
    product_desc_section = soup.find(id="productDescription")
    product_desc_available = "Yes" if product_desc_section else "NA"

    # From the Manufacturer
    from_manufacturer_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "From the manufacturer" in tag.get_text())
    from_manufacturer_available = "Yes" if from_manufacturer_section else "NA"
    
    # Bought in past month (robust extraction)
    bought = "N/A"
    try:
        suffix_elems = driver.find_elements(By.XPATH, "//span[contains(text(), 'in past month')]")
        if suffix_elems:
            # Look for preceding bold number
            bold_elem = suffix_elems[0].find_element(By.XPATH, "./preceding-sibling::span[@class='a-text-bold']")
            if bold_elem:
                bought_text = bold_elem.text.strip()  # e.g., "6K+", "500+"
                bought_raw = bought_text.replace("+", "").upper()

                if "K" in bought_raw:
                    bought = str(int(float(bought_raw.replace("K", "")) * 1000))
                elif "M" in bought_raw:
                    bought = str(int(float(bought_raw.replace("M", "")) * 1000000))
                else:
                    bought = str(int(bought_raw))
    except Exception as e:
        print(f"[DEBUG] Bought extraction failed for {asin}: {e}")
        bought = "N/A"




    return {
        'ASIN': asin,
        'Title': title,
        'Price': price,
        'Bought': bought,
        'Rating': rating,
        'Reviews': reviews,
        'Image': image,
        'Brand': brand,
        'Parent_Category_Rank': parent_rank,
        'Child_Category_Rank': child_rank,
        'Product_Description': product_desc_available,
        'From_Manufacturer': from_manufacturer_available
    }


def get_amazon_product_details(asin, country_code="in"):
    driver = _setup_driver()
    try:
        return _scrape_product_details(driver, asin, country_code)
    finally:
        driver.quit()


def get_multiple_product_details(asin_list, country_code="in", delay=5):
    driver = _setup_driver()
    results = []
    try:
        for asin in asin_list:
            try:
                data = _scrape_product_details(driver, asin, country_code)
                results.append(data)
                print(f"Scraped: {asin}")
            except Exception as e:
                print(f"Failed {asin}: {e}")
                results.append({'ASIN': asin, 'Error': str(e)})
            time.sleep(delay)
    finally:
        driver.quit()
    return results
