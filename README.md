
目前只维护amazon 

前往 https://googlechromelabs.github.io/chrome-for-testing/ 分别下载 相同版本的 chrome 和 chrome_driver
并解压到本项目目录中 并确保存在目录:
chromedriver-win64/chromedriver.exe
chrome-win64/chrome.exe

由于亚马逊限制 空白指纹用户将无法正常访问
请先运行test.py 在页面中进行一次访问(有条件可以考虑登录)

随后可正常运行爬虫