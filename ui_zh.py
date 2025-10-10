import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread, Lock
from src.AliExpress import aliexpress_scrape
from src.Lazada import lazada_scrape
from src.Shein import shein_scrape
from src.Amazon import amazon_scrape

import sys
import io


class RedirectText(io.StringIO):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget

    def write(self, text):
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.insert(tk.END, text)
        self.log_widget.see(tk.END)
        self.log_widget.config(state=tk.DISABLED)


def start_scraping():
    website = website_combobox.get()
    keyword = keyword_entry.get()
    try:
        num_pages = int(pages_entry.get())
    except ValueError:
        messagebox.showerror("无效输入", "页数必须是整数。")
        return

    if website and keyword and num_pages > 0 and not scrape_thread_lock.locked():
        scrape_button.config(state=tk.DISABLED)
        log_widget.config(state=tk.NORMAL)
        log_widget.delete("1.0", tk.END)
        log_widget.config(state=tk.DISABLED)
        scrape_thread = Thread(target=scrape, args=(website, keyword, num_pages))
        scrape_thread.start()
    else:
        messagebox.showerror("无效输入", "请输入有效的输入。")


def scrape(website, keyword, num_pages):
    with scrape_thread_lock:
        try:
            if website == "AliExpress":
                aliexpress_scrape(keyword, num_pages)
                messagebox.showinfo("成功", f"关键字'{keyword}'的爬取已完成，共 {num_pages} 页。")
            elif website == "Lazada":
                lazada_scrape(keyword, num_pages)
                messagebox.showinfo("成功", f"关键字'{keyword}'的爬取已完成，共 {num_pages} 页。")
            elif website == "Shein":
                shein_scrape(keyword, num_pages)
                messagebox.showinfo("成功", f"关键字'{keyword}'的爬取已完成，共 {num_pages} 页。")
            elif website == "Amazon":
                amazon_scrape(keyword, num_pages)
                messagebox.showinfo("成功", f"关键字'{keyword}'的爬取已完成，共 {num_pages} 页。")

            else:
                messagebox.showerror("错误", f"不支持的网站: {website}")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
        finally:
            scrape_button.config(state=tk.NORMAL)


# Initialize the lock
scrape_thread_lock = Lock()

# Create the main window
root = tk.Tk()
root.title("网络爬虫")

# Create a frame for input widgets
input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(input_frame, text="网站:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
website_combobox = ttk.Combobox(input_frame, values=["AliExpress","Lazada","Shein","Amazon"])
website_combobox.current(0)
website_combobox.grid(row=0, column=1, padx=10, pady=5)

tk.Label(input_frame, text="关键字:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
keyword_entry = tk.Entry(input_frame)
keyword_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(input_frame, text="页数:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
pages_entry = tk.Entry(input_frame)
pages_entry.grid(row=2, column=1, padx=10, pady=5)

scrape_button = tk.Button(input_frame, text="开始爬取", command=start_scraping)
scrape_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Create a frame for the log widget
log_frame = tk.Frame(root)
log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

log_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=10, width=40)
log_widget.pack(fill=tk.BOTH, expand=True)

# Redirect console output to the log widget
sys.stdout = RedirectText(log_widget)
sys.stderr = RedirectText(log_widget)

# Run the main loop
root.mainloop()
