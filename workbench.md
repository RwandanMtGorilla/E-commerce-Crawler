U-shaped neck pillow

当前有 data/amazon_products.csv 存储着一系列商品信息 示例如下:
```
Product Name,Product URL,Price,Rating,Review Count,Sales,Prime,Delivery
N/A,N/A,N/A,N/A,N/A,N/A,No,N/A
"Travel Pillow,100% Pure Memory Foam U Shaped Neck Pillow,Super Lightweight Portable Headrest Great for Airplane Chair, Car,Home,Office,Sleeping Rest Cushion (Grey)",https://www.amazon.com/Far-win-Lightweight-Portable-Headrest/dp/B0CNT89Z22/ref=sr_1_1?dib=eyJ2IjoiMSJ9.FeckvjUVbxki-DqC-TaqNYWd8U2WexA_B-I540AJ7Zrc6LkG0yx9QVwI9fYBwi9KksXDKB6tfLz9Nhi9nqpB-QOHo1YPhcktKXAm6Re9_70iCehITH7EX3etj5NqYdi0TUjKKgD5dT0HGyA7dBblkyRZegXjVKYOOCFXed6BCa0aRjLOxrcGUkgYmrIk_U-ZPuBs-bHbV8Ne5ZI7yOpPQcIt45zeufEhxW09m1hPa6z5z96MShYJ-o68_Zc54xjeS6Ag1eBEAC-7xDPAtBhFZB2Hkp2zD37q_SrCGEQIBBY.l0cz22JESusxzL6auoUuv5jRv1eIfT9M7Z6ic4NJKmc&dib_tag=se&keywords=U-shaped+neck+pillow&qid=1760680530&sr=8-1,9.99,"4.5 out of 5 stars, rating details",(762),700+ bought in past month,No,Leave feedback on Sponsored ad
...

```
我希望你书写一个爬虫脚本 遍历该csv文件 取 Product Name 非 N/A 行的 Product URL进行访问 并获取以下信息
About
Product 
information

Top reviews

评论:

