from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from config import (
    CHROME_DRIVER_PATH,
    CHROME_BINARY_PATH,
    CHROME_USER_DATA_DIR,
)

driver_path = CHROME_DRIVER_PATH
options = Options()
chrome_path = CHROME_BINARY_PATH
options.binary_location = chrome_path

user_data_dir = CHROME_USER_DATA_DIR
os.makedirs(user_data_dir, exist_ok=True)

options.add_argument(f"--user-data-dir={user_data_dir}")

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 获取用户数据目录
user_data_dir = driver.execute_script("return navigator.userAgent")
print("User Data Dir:", driver.capabilities.get('chrome', {}).get('userDataDir'))

driver.get("https://www.amazon.com")

input("请在浏览器中登录Amazon,完成后按回车继续...")
# driver.quit()
