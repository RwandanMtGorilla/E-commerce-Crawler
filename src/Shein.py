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

def shein_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://us.shein.com/pdsearch/{keyword}/?sort=7"#"#

    # ChromeDriver 的路径
    driver_path = "chromedriver_windows.exe"  

    # 创建ChromeOptions对象
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏Selenium特征

    # 设置ChromeDriver路径
    service = Service(driver_path)

    # 创建一个Selenium WebDriver实例
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
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)

    # 创建CSV文件
    csv_file_path = os.path.join(output_folder, "希音_products.csv")
    csv_columns = ["Product Name", "Product URL", "Price", "Sales"]
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

            current_html_path = os.path.join(output_folder, f"希音_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.find_all("section", class_="product-card multiple-row-card j-expose__product-item hover-effect product-list__item product-list__item-new")

            for product_card in product_cards:
                product_name_element = product_card.find("div", class_="product-card__goods-title-container")
                product_name = product_name_element.text.strip() if product_name_element else "N/A"
                div_element = product_card.find("div", class_="product-card__goods-title-container")  # 首先找到类名为 "_95X4G" 的div元素
                if div_element:
                    a_element = div_element.find("a")  # 在div元素内找到<a>元素
                    product_url = a_element["href"] if a_element else "N/A"
                else:
                    product_url = "N/A" 
                price_element = product_card.find("span", class_="normal-price-ctn__sale-price normal-price-ctn__sale-price_promo")
                price = price_element.text.strip() if price_element else "N/A"
                sales_element = product_card.find("div", class_="product-card__sales-label")
                sales = sales_element.text.strip() if sales_element else "N/A"

                with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                    writer.writerow({
                        "Product Name": product_name,
                        "Product URL": "https://us.shein.com/"+product_url,
                        "Price": price,
                        "Sales": sales
                    })

            try:
                # 检查并关闭弹窗
                try:
                    close_button = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sui-icon-common__wrap.she-close.homepage-she-close"))
                    )
                    print("找到弹窗关闭按钮。")
                    driver.execute_script("arguments[0].click();", close_button)
                    time.sleep(1)
                except Exception as e:
                    print("没有找到弹窗或弹窗不可点击。Exception: " + str(e))


                # 等待并定位“下一页”按钮
                try:
                    next_page_button = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sui-pagination__next.sui-pagination__btn.sui-pagination__hover"))
                    )
                    print("找到下一页按钮。")
                    driver.execute_script("arguments[0].click();", next_page_button)
                    current_page += 1
                    time.sleep(1)
                    page_height = driver.execute_script("return document.body.scrollHeight")
                except Exception as e:
                    print("无法找到下一页按钮或下一页按钮不可点击。Exception: " + str(e))
                    break
            except Exception as e:
                print("发生其他异常。Exception: " + str(e))



        print("数据已经存储至'data\\希音_products.csv'.")
    finally:
        driver.quit()

