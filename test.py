from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

driver_path = "chromedriver-win64//chromedriver.exe"
options = Options()
chrome_path = "chrome-win64//chrome.exe"
options.binary_location = chrome_path

user_data_dir = os.path.abspath("chrome-win64/User Data")
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
