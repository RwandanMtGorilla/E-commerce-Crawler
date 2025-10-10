import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd



def lazada_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://www.lazada.com.ph/catalog/?q={keyword}"

    # ChromeDriver 的路径
    driver_path = "chromedriver_windows.exe"  

    # 创建ChromeOptions对象
    options = Options()
    options.add_argument("--force-device-scale-factor=0.5")  # 设置页面缩放比例为50%

    # # Chrome浏览器的路径
    # chrome_path = "chrome-win64/chrome.exe" 
    # options.binary_location = chrome_path

    # 设置ChromeDriver路径
    service = Service(driver_path)

    # 创建一个Selenium WebDriver实例
    driver = webdriver.Chrome(service=service, options=options)

    # 创建保存文件夹
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)

    # 创建CSV文件
    csv_file_path = os.path.join(output_folder, "拉赞达_products.csv")
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

        # # 等待页面加载完成
        # wait = WebDriverWait(driver, 60)  # 这里的10表示超时时间为10秒，你可以根据实际情况调整
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Bm3ON")))  # 等待页面加载完成

        # # 在这里添加条件，如果没有出现正文元素，就停止执行后续操作
        # if "Bm3ON" not in driver.page_source:  
        #     print("页面未加载成功，停止执行后续操作。")
        #     return  # 或者使用其他合适的方法来停止执行后续操作

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

            current_html_path = os.path.join(output_folder, f"拉赞达_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.find_all("div", class_="Bm3ON")

            for product_card in product_cards:
                product_name_element = product_card.find("div", class_="RfADt")
                product_name = product_name_element.text.strip() if product_name_element else "N/A"

                div_element = product_card.find("div", class_="_95X4G")  # 首先找到类名为 "_95X4G" 的div元素
                if div_element:
                    a_element = div_element.find("a")  # 在div元素内找到<a>元素
                    product_url = a_element["href"] if a_element else "N/A"
                else:
                    product_url = "N/A"              
                price_element = product_card.find("div", class_="aBrP0")
                price = price_element.text.strip() if price_element else "N/A"
                sales_element = product_card.find("span", class_="_1cEkb")
                sales = sales_element.text.strip() if sales_element else "N/A"

                with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                    writer.writerow({
                        "Product Name": product_name,
                        "Product URL": product_url,
                        "Price": price,
                        "Sales": sales
                    })


            # 通过更具体的选择器找到 next_page_button
            next_page_li = driver.find_element(By.CSS_SELECTOR, "li[title='Next Page']")
            next_page_button = next_page_li.find_element(By.CLASS_NAME, "ant-pagination-item-link")

            # 检查按钮是否可用并进行点击
            if next_page_button.is_enabled():
                next_page_button.click()
                current_page += 1
                time.sleep(5)  # 等待页面加载
                # 获取更新后的页面高度
                page_height = driver.execute_script("return document.body.scrollHeight")
            else:
                break

        print("数据已经存储至'data/products.csv'.")
    finally:
        driver.quit()

