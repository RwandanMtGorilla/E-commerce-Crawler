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

def toutiao_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://so.toutiao.com/search?wid_ct=1716484620155&dvpf=pc&source=input&keyword=%E6%9D%AD%E5%B7%9E%E5%B8%82%E5%85%AC%E5%85%B1%E6%96%87%E5%8C%96%E8%AE%BE%E6%96%BD&pd=synthesis&action_type=search_subtab_switch&from=search_tab&cur_tab_title=search_tab&page_num=0"#"#
        # = f"https://so.toutiao.com/search?wid_ct=1716484620155&dvpf=pc&source=pagination&keyword=%E6%9D%AD%E5%B7%9E%E5%B8%82%E5%85%AC%E5%85%B1%E6%96%87%E5%8C%96%E8%AE%BE%E6%96%BD&pd=synthesis&action_type=pagination&from=search_tab&cur_tab_title=search_tab&page_num=1&search_id=20240524011729A2D5C33573C8265EA3CD"
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
    csv_file_path = os.path.join(output_folder, "头条_products.csv")
    csv_columns = ["Product Name", "Product URL"]
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()

    try:
        # 最大化浏览器窗口
        driver.maximize_window()

        # 打开URL
        driver.get(url)

        # 等待页面加载完成
        time.sleep(10)

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

            current_html_path = os.path.join(output_folder, f"头条_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")

            product_cards = soup.find_all("div", class_="cs-view cs-view-block cs-card-content")

            for product_card in product_cards:
                product_name_element = product_card.find("div", class_="flex-1 text-darker text-xl text-medium d-flex align-items-center overflow-hidden")
                product_name = product_name_element.text.strip() if product_name_element else "N/A"
                div_element = product_card.find("div", class_="flex-1 text-darker text-xl text-medium d-flex align-items-center overflow-hidden")  # 首先找到类名为 "_95X4G" 的div元素
                if div_element:
                    a_element = div_element.find("a")  # 在div元素内找到<a>元素
                    product_url = a_element["href"] if a_element else "N/A"
                else:
                    product_url = "N/A" 


                with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                    writer.writerow({
                        "Product Name": product_name,
                        "Product URL": product_url,
                    })

            
            next_page_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cs-view.cs-view-inline-block.cs-button.cs-button-mb.cs-button-default.text-darker.text-m.radius-m.text-center.text-nowrap:not(.margin-right-6)"))
            )
            print("找到下一页按钮。")
            # 检查按钮是否可用并进行点击
            if next_page_button.is_enabled():
                next_page_button.click()
                current_page += 1
                time.sleep(5)  # 等待页面加载
                # 获取更新后的页面高度
                page_height = driver.execute_script("return document.body.scrollHeight")
            else:
                break



        print("数据已经存储至'data\\头条_products.csv'.")
    finally:
        driver.quit()

