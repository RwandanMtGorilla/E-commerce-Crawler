import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from bs4 import BeautifulSoup

# 导入配置
from config import (
    CHROME_DRIVER_PATH,
    CHROME_BINARY_PATH,
    CHROME_USER_DATA_DIR,
    OUTPUT_FOLDER,
    CSV_FILE_PATH,
    CSV_COLUMNS
)


def amazon_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://www.amazon.com/s?k={keyword}"

    # 创建ChromeOptions对象
    options = Options()
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = CHROME_BINARY_PATH

    # 确保用户数据目录存在
    os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)
    options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")

    # 设置ChromeDriver路径
    service = Service(CHROME_DRIVER_PATH)

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=options)

    # 使用selenium-stealth隐藏特征
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    # 创建保存文件夹
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 创建CSV文件
    with open(CSV_FILE_PATH, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
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

            current_html_path = os.path.join(OUTPUT_FOLDER, f"amazon_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8-sig") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.find_all("div", class_="sg-col-inner")

            for product_card in product_cards:
                product_name_element = product_card.find("h2",
                                                         class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
                product_name = product_name_element.text.strip() if product_name_element else "N/A"

                product_url_element = product_card.find("a", class_="a-link-normal s-no-outline")
                product_url = "https://www.amazon.com" + product_url_element["href"] if product_url_element else "N/A"

                price_whole_element = product_card.find("span", class_="a-price-whole")
                price_fraction_element = product_card.find("span", class_="a-price-fraction")
                price = price_whole_element.text.strip() + price_fraction_element.text.strip() if price_whole_element and price_fraction_element else "N/A"

                rating_element = product_card.find("a", class_="mvt-review-star-mini-popover")
                rating = rating_element.get("aria-label") if rating_element else "N/A"

                review_count_element = product_card.find("span", {"aria-hidden": True}, class_="s-underline-text")
                review_count = review_count_element.text.strip() if review_count_element else "N/A"

                sales_element = product_card.find("span", class_="a-size-base a-color-secondary")
                sales = sales_element.text.strip() if sales_element else "N/A"

                prime_element = product_card.find("i", class_="a-icon-prime")
                prime = "Yes" if prime_element else "No"

                delivery_element = product_card.find("span", {"aria-label": True})
                delivery = delivery_element["aria-label"] if delivery_element else "N/A"

                with open(CSV_FILE_PATH, "a", newline="", encoding="utf-8-sig") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
                    writer.writerow({
                        "Product Name": product_name,
                        "Product URL": product_url,
                        "Price": price,
                        "Rating": rating,
                        "Review Count": review_count,
                        "Sales": sales,
                        "Prime": prime,
                        "Delivery": delivery
                    })

            try:
                # 等待并定位"下一页"按钮
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".s-pagination-next"))
                )
                driver.execute_script("arguments[0].click();", next_page_button)
                current_page += 1
                time.sleep(1)
                page_height = driver.execute_script("return document.body.scrollHeight")
            except Exception as e:
                print("无法找到下一页按钮或下一页按钮不可点击。Exception: " + str(e))
                break

        print(f"数据已经存储至'{CSV_FILE_PATH}'.")
    finally:
        driver.quit()
