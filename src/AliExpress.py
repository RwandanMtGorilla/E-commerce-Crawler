import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def aliexpress_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://www.aliexpress.us/w/wholesale-{keyword}.html?spm=a2g0o.home.search.0&sortType=total_tranpro_desc"

    # ChromeDriver 的路径
    driver_path = "chromedriver_windows.exe"  

    # 创建ChromeOptions对象
    options = Options()
    options.add_argument("--force-device-scale-factor=0.5")  # 设置页面缩放比例为50%

    # # Chrome浏览器的路径
    chrome_path = "chrome-win64/chrome.exe" 
    options.binary_location = chrome_path

    # 设置ChromeDriver路径
    service = Service(driver_path)

    # 创建一个Selenium WebDriver实例
    driver = webdriver.Chrome(service=service, options=options)

    # 创建保存文件夹
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)

    # 创建CSV文件
    csv_file_path = os.path.join(output_folder, "速卖通_products.csv")
    csv_columns = ["Product Name", "Product URL", "Image URL", "Store Name", "Store URL", "Price", "Sales"]
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()

    try:
        # 最大化浏览器窗口
        driver.maximize_window()

        # 打开URL
        driver.get(url)

        # 等待页面加载完成
        time.sleep(5)

        # 定义下滑步长
        scroll_step = 500

        # 获取页面高度
        page_height = driver.execute_script("return document.body.scrollHeight")

        # 模拟逐步下拉滚动到页面底部并点击下一页按钮
        current_scroll = 0
        current_page = 1
        while current_page <= num_pages_to_crawl:
            current_scroll = 0
            while current_scroll < page_height:
                next_scroll = min(current_scroll + scroll_step, page_height)
                driver.execute_script(f"window.scrollTo(0, {next_scroll});")
                time.sleep(random.uniform(0.5, 1.5))
                current_scroll = next_scroll
                page_height = driver.execute_script("return document.body.scrollHeight")

            current_html_path = os.path.join(output_folder, f"速卖通_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.find_all("div", class_="list--gallery--C2f2tvm search-item-card-wrapper-gallery")

            for product_card in product_cards:
                product_name_element = product_card.find("h3", class_="multi--titleText--nXeOvyr")
                product_name = product_name_element.text.strip() if product_name_element else "N/A"
                product_url_element = product_card.find("a", class_="multi--container--1UZxxHY cards--card--3PJxwBm search-card-item")
                product_url = product_url_element["href"] if product_url_element else "N/A"
                image_url_element = product_card.find("img", class_="images--item--3XZa6xf")
                image_url = image_url_element["src"] if image_url_element else "N/A"
                store_name_element = product_card.find("a", class_="cards--storeLink--XkKUQFS")
                store_name = store_name_element.text.strip() if store_name_element else "N/A"
                store_url = store_name_element["href"] if store_name_element else "N/A"
                price_element = product_card.find("div", class_="multi--price-sale--U-S0jtj")
                price = price_element.text.strip() if price_element else "N/A"
                sales_element = product_card.find("span", class_="multi--trade--Ktbl2jB")
                sales = sales_element.text.strip() if sales_element else "N/A"

                with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                    writer.writerow({
                        "Product Name": product_name,
                        "Product URL": product_url,
                        "Image URL": image_url,
                        "Store Name": store_name,
                        "Store URL": store_url,
                        "Price": price,
                        "Sales": sales
                    })

            next_page_button = driver.find_element(By.CLASS_NAME, "comet-pagination-next")
            if next_page_button.is_enabled():
                next_page_button.click()
                current_page += 1
                time.sleep(5)
                page_height = driver.execute_script("return document.body.scrollHeight")
            else:
                break

        print("数据已经存储至'data\速卖通_products.csv'.")
    finally:
        driver.quit()

