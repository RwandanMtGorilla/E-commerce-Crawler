
目前只维护amazon 

前往 https://googlechromelabs.github.io/chrome-for-testing/ 分别下载 相同版本的 chrome 和 chrome_driver
并解压到本项目目录中 并确保存在目录:
chromedriver-win64/chromedriver.exe
chrome-win64/chrome.exe

```shell
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

```

由于亚马逊限制 空白指纹用户将无法正常访问
请先运行test.py 在页面中进行一次访问(有条件可以考虑登录)

随后可正常运行爬虫

结果保存在data文件夹中 包含一个utf-8-sig编码的csv文件 以及用于调试的 单页html信息