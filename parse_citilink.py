import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_and_enrich_product_list(driver, page_url):
    """This function scrapes products from one page and immediately fetches detailed information for each."""
    
    # Navigate to the page
    driver.get(page_url)
    time.sleep(5)
    
    # Initialize BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_containers = soup.find_all("div", class_="e1ex4k9s0 app-catalog-1bogmvw e1loosed0")
    
    enriched_data = []
    
    # Loop through each product and fetch details
    for product in product_containers:
        try:
            name = product.find("a", class_="app-catalog-9gnskf").text.strip()
            link = "https://www.citilink.ru" + product.find("a", class_="app-catalog-9gnskf")["href"]
            price = product.find("span", class_="e1j9birj0 e106ikdt0 app-catalog-56qww8 e1gjr6xo0").text.strip()
            
            product_details = fetch_product_details(link + "/properties", driver)
            enriched_data.append({"Name": name, "Link": link, "Price": price, **product_details})
        
        except Exception as e:
            print(f"Failed to extract or enrich some product details: {e}")
    
    return enriched_data

def fetch_product_details(url, driver):
    """Fetches details of a specific product from its individual page."""
    
    # Navigate to the product's detail page
    driver.get(url)
    time.sleep(10)
    
    # Initialize BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_details = {}
    
    # Scrap details of each product
    sections = soup.find_all("li", class_="app-catalog-10ib5jr e14ta1090")
    for section in sections:
        category_header = section.find("h4", class_="e1jylmxb0 eml1k9j0 app-catalog-vgrnu3 e1gjr6xo0")
        if category_header:
            category = category_header.text.strip()
            detail_items = section.find_all("div", class_="app-catalog-xc0ceg e1ckvoeh5")
            for item in detail_items:
                label = item.find("span", class_="e1ckvoeh1 e106ikdt0 app-catalog-fclnc2 e1gjr6xo0").text.strip()
                value = item.find("span", class_="e1ckvoeh0 e106ikdt0 app-catalog-ajic6a e1gjr6xo0").text.strip()
                key = f"{category} - {label}"
                product_details[key] = value
    
    return product_details

if __name__ == "__main__":
    url = "https://www.citilink.ru/catalog/smart-chasy"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    for page_number in range(1, 7): # pages number to be fetched
        page_url = f"{url}?p={page_number}"
        page_data = scrape_and_enrich_product_list(driver, page_url)
        pd.DataFrame(page_data).to_csv(f"../data/products_data_page_{page_number}.csv", index=False)
    
    print("Enriched product data for each page saved to separate CSV files.")
    
    driver.quit()
