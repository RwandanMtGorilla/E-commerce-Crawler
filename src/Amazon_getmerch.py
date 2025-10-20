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
from tqdm import tqdm

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


def get_crawled_urls(output_csv):
    """获取已爬取的URL集合"""
    crawled_urls = set()
    if os.path.exists(output_csv):
        try:
            with open(output_csv, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("Product URL", "").strip()
                    if url and url != "N/A":
                        crawled_urls.add(url)
            print(f"已从结果文件中读取 {len(crawled_urls)} 个已爬取的URL")
        except Exception as e:
            print(f"读取已爬取URL时出错: {e}")
    return crawled_urls


def deduplicate_products(rows):
    """对产品列表进行去重，保留第一次出现的记录"""
    seen_urls = set()
    unique_rows = []
    duplicate_count = 0

    for row in rows:
        url = row.get("Product URL", "").strip()
        # 跳过无效的URL
        if not url or url == "N/A":
            continue

        # 如果URL未见过，添加到结果列表
        if url not in seen_urls:
            seen_urls.add(url)
            unique_rows.append(row)
        else:
            duplicate_count += 1

    print(f"URL去重完成：原始数据 {len(rows)} 条，去重后 {len(unique_rows)} 条，去除重复 {duplicate_count} 条")
    return unique_rows


def scrape_product_details(input_csv, output_csv, reviews_csv):
    """主函数：爬取商品详情"""
    # 创建输出文件夹
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 读取输入CSV
    print("正在读取输入文件...")
    with open(input_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"共读取 {len(rows)} 条数据")

    # 1. URL去重
    print("\n开始URL去重...")
    rows = deduplicate_products(rows)

    # 2. 获取已爬取的URL（断点续爬）
    print("\n检查已爬取的数据...")
    crawled_urls = get_crawled_urls(output_csv)

    # 过滤掉已爬取的URL
    rows_to_crawl = [row for row in rows if row.get("Product URL", "").strip() not in crawled_urls]

    print(f"需要爬取 {len(rows_to_crawl)} 条新数据")

    if len(rows_to_crawl) == 0:
        print("没有新数据需要爬取！")
        return

    # 如果输出文件不存在，创建并写入表头
    if not os.path.exists(output_csv):
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=PRODUCT_DETAILS_COLUMNS)
            writer.writeheader()

    if not os.path.exists(reviews_csv):
        with open(reviews_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
            writer.writeheader()

    # 启动浏览器
    print("\n正在启动浏览器...")
    driver = setup_driver()

    try:
        # 3. 使用tqdm显示进度
        print("\n开始爬取数据...\n")
        for row in tqdm(rows_to_crawl, desc="爬取进度", unit="个商品"):
            product_name = row.get("Product Name", "N/A")
            product_url = row.get("Product URL", "N/A")

            # 跳过N/A行（虽然在去重时已过滤，但保险起见再检查）
            if product_name == "N/A" or product_url == "N/A":
                tqdm.write(f"跳过：Product Name 或 URL 为 N/A")
                continue

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

                tqdm.write(f"✓ {product_name[:50]}... | 提取了 {len(reviews)} 条评论")

                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                tqdm.write(f"✗ 处理失败: {product_name[:50]}... | 错误: {str(e)}")
                continue

        print(f"\n所有数据已保存至 '{output_csv}' 和 '{reviews_csv}'")

    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    INPUT_CSV = os.path.join(OUTPUT_FOLDER, "amazon_products.csv")
    OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "amazon_product_details.csv")
    REVIEWS_CSV = os.path.join(OUTPUT_FOLDER, "amazon_product_reviews.csv")

    scrape_product_details(INPUT_CSV, OUTPUT_CSV, REVIEWS_CSV)
