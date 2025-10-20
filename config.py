import os

# 获取config.py文件所在的目录作为基准路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ChromeDriver路径
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver-win64", "chromedriver.exe")

# Chrome浏览器路径
CHROME_BINARY_PATH = os.path.join(BASE_DIR, "chrome-win64", "chrome.exe")

# Chrome用户数据目录
CHROME_USER_DATA_DIR = os.path.join(BASE_DIR, "chrome-win64", "User Data")

# 输出文件夹路径
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data")

# CSV文件路径
CSV_FILE_PATH = os.path.join(OUTPUT_FOLDER, "amazon_products.csv")

# CSV列名
CSV_COLUMNS = ["Product Name", "Product URL", "Price", "Rating", "Review Count", "Sales", "Prime", "Delivery"]
