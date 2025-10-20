U-shaped neck pillow


####

当前有一段代码:
```shell
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

def amazon_scrape(keyword, num_pages_to_crawl):
    # 构造URL
    url = f"https://www.amazon.com/s?k={keyword}"
    # url = f"https://www.amazon.com/s?k={keyword}&s=exact-aware-popularity-rank&ds=v1%3AJrxMCJNWth3dfHwbNN9hTYbXakEU%2BZvIoDEmaIymF2w&qid=1721664511&ref=sr_st_exact-aware-popularity-rank"
    # ChromeDriver 的路径
    driver_path = "chromedriver-win64/chromedriver.exe"

    # 创建ChromeOptions对象
    options = Options()
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏Selenium特征
    # Chrome浏览器的路径
    chrome_path = "chrome-win64/chrome.exe"
    options.binary_location = chrome_path

    user_data_dir = os.path.abspath("chrome-win64/User Data")
    os.makedirs(user_data_dir, exist_ok=True)

    options.add_argument(f"--user-data-dir={user_data_dir}")
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
    csv_file_path = os.path.join(output_folder, "amazon_products.csv")
    csv_columns = ["Product Name", "Product URL", "Price", "Rating", "Review Count", "Sales", "Prime", "Delivery"]
    with open(csv_file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
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

            current_html_path = os.path.join(output_folder, f"amazon_page_{current_page}.html")
            with open(current_html_path, "w", encoding="utf-8-sig") as f:
                f.write(driver.page_source)

            print(f"HTML 页 {current_page} 已存储至 '{current_html_path}'.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.find_all("div", class_="sg-col-inner")

            for product_card in product_cards:
                product_name_element = product_card.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
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

                with open(csv_file_path, "a", newline="", encoding="utf-8-sig") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
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
                # 等待并定位“下一页”按钮
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

        print("数据已经存储至'data/amazon_products.csv'.")
    finally:
        driver.quit()



```
可以注意到 其中有很多路径 但是使用的是相对路径 使其受到运行开始位置的影响 我希望你写一个config.py 运行时读取config位置作为基准 随后拼接这些参数为绝对路径 随后此代码中从config里import

####

当前有 data/amazon_products.csv 存储着一系列商品信息 示例如下:
```
Product Name,Product URL,Price,Rating,Review Count,Sales,Prime,Delivery
N/A,N/A,N/A,N/A,N/A,N/A,No,N/A
"Travel Pillow,100% Pure Memory Foam U Shaped Neck Pillow,Super Lightweight Portable Headrest Great for Airplane Chair, Car,Home,Office,Sleeping Rest Cushion (Grey)",https://www.amazon.com/Far-win-Lightweight-Portable-Headrest/dp/B0CNT89Z22/ref=sr_1_1?dib=eyJ2IjoiMSJ9.FeckvjUVbxki-DqC-TaqNYWd8U2WexA_B-I540AJ7Zrc6LkG0yx9QVwI9fYBwi9KksXDKB6tfLz9Nhi9nqpB-QOHo1YPhcktKXAm6Re9_70iCehITH7EX3etj5NqYdi0TUjKKgD5dT0HGyA7dBblkyRZegXjVKYOOCFXed6BCa0aRjLOxrcGUkgYmrIk_U-ZPuBs-bHbV8Ne5ZI7yOpPQcIt45zeufEhxW09m1hPa6z5z96MShYJ-o68_Zc54xjeS6Ag1eBEAC-7xDPAtBhFZB2Hkp2zD37q_SrCGEQIBBY.l0cz22JESusxzL6auoUuv5jRv1eIfT9M7Z6ic4NJKmc&dib_tag=se&keywords=U-shaped+neck+pillow&qid=1760680530&sr=8-1,9.99,"4.5 out of 5 stars, rating details",(762),700+ bought in past month,No,Leave feedback on Sponsored ad
...

```
我希望你书写一个爬虫脚本 遍历该csv文件 取 Product Name 非 N/A 行的 Product URL进行访问 并获取以下信息
信息  元素  获取
About   div id="feature-bullets"    其中所有文本
店铺名/链接  a id="bylineInfo"且class="a-link-normal" 文本/herf
similar Product(记录前四件 分别记录为sim-name-1   sim-link-1 ...)     ol class="a-carousel" 中有多个 li  每个中的 a class="a-link-normal aok-block" 其href 为链接 其子元素中包含的文本为商品名
information div id="prodDetails"    其中所有文本

Top reviews(每个评论一条 单独记录一张表) ul data-hook="top-customer-reviews-widget" 中有多个 li 每个中的 span class="cr-original-review-content" 的文本 为评论内容   每个中的data-hook="helpful-vote-statement" 的文本 为认为评论有帮助的数量

我需要你定位到这些元素 并以新的文件名保存 原csv文件中的其他列也应当保留
评论及其子信息 单独保存到另一个文件中 需要保留url 商品名列 以定位到是哪个商品

作为风格参考 以下是获取商品链接部分的代码:
```py
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

```

现在，请按照要求 仔细思考 完成代码

关于 similar Product 链接和品名的定位元素 除了a class="a-link-normal aok-block"外 加一个条件为 且 role="link"
你只需输出需要修改部分的代码

####
当前代码:
```python
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
    OUTPUT_FOLDER
)

# 定义新的CSV列
PRODUCT_DETAILS_COLUMNS = [
    "Product Name",
    "Product URL",
    "Price",
    "Rating",
    "Review Count",
    "Sales",
    "Prime",
    "Delivery",
    "About",
    "Store Name",
    "Store Link",
    "Sim-Name-1",
    "Sim-Link-1",
    "Sim-Name-2",
    "Sim-Link-2",
    "Sim-Name-3",
    "Sim-Link-3",
    "Sim-Name-4",
    "Sim-Link-4",
    "Information"
]

REVIEW_COLUMNS = [
    "Product Name",
    "Product URL",
    "Review Content",
    "Helpful Count"
]


def setup_driver():
    """设置并返回WebDriver实例"""
    options = Options()
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = CHROME_BINARY_PATH

    os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)
    options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    return driver


def extract_about(soup):
    """提取About信息"""
    try:
        about_div = soup.find("div", id="feature-bullets")
        if about_div:
            return about_div.get_text(strip=True, separator=" ")
        return "N/A"
    except Exception as e:
        print(f"提取About信息时出错: {e}")
        return "N/A"


def extract_store_info(soup):
    """提取店铺名称和链接"""
    try:
        store_element = soup.find("a", id="bylineInfo", class_="a-link-normal")
        if store_element:
            store_name = store_element.get_text(strip=True)
            store_link = "https://www.amazon.com" + store_element.get("href", "")
            return store_name, store_link
        return "N/A", "N/A"
    except Exception as e:
        print(f"提取店铺信息时出错: {e}")
        return "N/A", "N/A"


def extract_similar_products(soup):
    """提取相似商品信息（前4个）"""
    similar_products = {}
    for i in range(1, 5):
        similar_products[f"Sim-Name-{i}"] = "N/A"
        similar_products[f"Sim-Link-{i}"] = "N/A"

    try:
        carousel = soup.find("ol", class_="a-carousel")
        if carousel:
            items = carousel.find_all("li", limit=4)
            for idx, item in enumerate(items, 1):
                link_element = item.find("a", class_="a-link-normal aok-block", attrs={"role": "link"})
                if link_element:
                    sim_link = "https://www.amazon.com" + link_element.get("href", "")
                    sim_name = link_element.get_text(strip=True)
                    similar_products[f"Sim-Name-{idx}"] = sim_name
                    similar_products[f"Sim-Link-{idx}"] = sim_link
    except Exception as e:
        print(f"提取相似商品信息时出错: {e}")

    return similar_products


def extract_information(soup):
    """提取产品详细信息"""
    try:
        info_div = soup.find("div", id="prodDetails")
        if info_div:
            return info_div.get_text(strip=True, separator=" ")
        return "N/A"
    except Exception as e:
        print(f"提取Information信息时出错: {e}")
        return "N/A"


def extract_reviews(soup):
    """提取评论信息"""
    reviews = []
    try:
        review_list = soup.find("ul", attrs={"data-hook": "top-customer-reviews-widget"})
        if review_list:
            review_items = review_list.find_all("li")
            for review_item in review_items:
                # 提取评论内容
                content_element = review_item.find("span", class_="cr-original-review-content")
                content = content_element.get_text(strip=True) if content_element else "N/A"

                # 提取有帮助数
                helpful_element = review_item.find(attrs={"data-hook": "helpful-vote-statement"})
                helpful_count = helpful_element.get_text(strip=True) if helpful_element else "N/A"

                reviews.append({
                    "Review Content": content,
                    "Helpful Count": helpful_count
                })
    except Exception as e:
        print(f"提取评论信息时出错: {e}")

    return reviews


def scrape_product_details(input_csv, output_csv, reviews_csv):
    """主函数：爬取商品详情"""
    driver = setup_driver()

    # 创建输出文件
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 写入表头
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=PRODUCT_DETAILS_COLUMNS)
        writer.writeheader()

    with open(reviews_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()

    try:
        # 读取输入CSV
        with open(input_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for idx, row in enumerate(rows, 1):
            product_name = row.get("Product Name", "N/A")
            product_url = row.get("Product URL", "N/A")

            # 跳过N/A行
            if product_name == "N/A" or product_url == "N/A":
                print(f"跳过第 {idx} 行（Product Name 或 URL 为 N/A）")
                continue

            print(f"正在处理第 {idx} 行: {product_name}")

            try:
                # 访问商品页面
                driver.get(product_url)
                time.sleep(random.uniform(3, 5))

                # 解析页面
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # 提取信息
                about = extract_about(soup)
                store_name, store_link = extract_store_info(soup)
                similar_products = extract_similar_products(soup)
                information = extract_information(soup)
                reviews = extract_reviews(soup)

                # 保存商品详情
                product_data = {
                    "Product Name": product_name,
                    "Product URL": product_url,
                    "Price": row.get("Price", "N/A"),
                    "Rating": row.get("Rating", "N/A"),
                    "Review Count": row.get("Review Count", "N/A"),
                    "Sales": row.get("Sales", "N/A"),
                    "Prime": row.get("Prime", "N/A"),
                    "Delivery": row.get("Delivery", "N/A"),
                    "About": about,
                    "Store Name": store_name,
                    "Store Link": store_link,
                    "Information": information
                }
                product_data.update(similar_products)

                with open(output_csv, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=PRODUCT_DETAILS_COLUMNS)
                    writer.writerow(product_data)

                # 保存评论
                for review in reviews:
                    review_data = {
                        "Product Name": product_name,
                        "Product URL": product_url,
                        "Review Content": review["Review Content"],
                        "Helpful Count": review["Helpful Count"]
                    }
                    with open(reviews_csv, "a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
                        writer.writerow(review_data)

                print(f"第 {idx} 行处理完成，提取了 {len(reviews)} 条评论")

                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"处理第 {idx} 行时出错: {e}")
                continue

        print(f"所有数据已保存至 '{output_csv}' 和 '{reviews_csv}'")

    finally:
        driver.quit()


if __name__ == "__main__":
    INPUT_CSV = os.path.join(OUTPUT_FOLDER, "amazon_products.csv")
    OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "amazon_product_details.csv")
    REVIEWS_CSV = os.path.join(OUTPUT_FOLDER, "amazon_product_reviews.csv")

    scrape_product_details(INPUT_CSV, OUTPUT_CSV, REVIEWS_CSV)

```

现在需要做一些修改:
1. 在爬虫任务创建前 对要爬取的url进行去重
2. 断点功能 每次爬虫访问一个url前 先看看结果文件中是否已经有该行数据
3. 用tqdm显示进度 

现在，请按照要求 仔细思考 完成代码