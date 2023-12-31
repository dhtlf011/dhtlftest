from tkinter import ttk, filedialog, messagebox, BooleanVar
from ttkwidgets import CheckboxTreeview
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from random import choice, randint
import random
import threading
import time
import tkinter as tk
import glob
import json
import os

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.field_style = ttk.Style()
        self.field_style.configure('Placeholder.TEntry', foreground='#808080')

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self._on_focus_out(None)

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(style='TEntry')

    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(style='Placeholder.TEntry')

class PlaceholderText(tk.Text):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self.insert('1.0', self.placeholder)
        self.tag_configure("placeholder", foreground="#808080")
        self.tag_add("placeholder", "1.0", "end")

    def _on_focus_in(self, event):
        if self.get("1.0", 'end-1c') == self.placeholder:
            self.delete('1.0', tk.END)
            self.tag_remove("placeholder", "1.0", "end")

    def _on_focus_out(self, event):
        if not self.get("1.0", 'end-1c'):
            self.insert('1.0', self.placeholder)
            self.tag_add("placeholder", "1.0", "end")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.check_states = {}  # 각 항목의 체크 상태를 저장할 딕셔너리입니다.
        self.title("New GUI Window")
        self.geometry("650x400")

        self.create_widgets()

    def create_widgets(self):
        self.new_button = tk.Button(text="New", command=self.new_project)
        self.new_button.place(x=0, y=5, width=60, height=25) 

        self.open_button = tk.Button(text="Open", command=self.open_project)
        self.open_button.place(x=70, y=5, width=60, height=25) 

        self.save_button = tk.Button(text="Save", command=self.save_project)
        self.save_button.place(x=140, y=5, width=60, height=25) 

        self.start_button = tk.Button(text="Start", command=self.start_project)
        self.start_button.place(x=210, y=5, width=60, height=25) 

        self.stop_button = tk.Button(text="Stop", command=self.stop_project)
        self.stop_button.place(x=280, y=5, width=60, height=25)                                 

        self.notebook = ttk.Notebook(self)
        self.tab_scripts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scripts, text='Scripts')
        self.notebook.place(x=0, y=30, width=650, height=360) 

        self.script_tree = CheckboxTreeview(self.tab_scripts)
        self.script_tree.column("#0", width=150, minwidth=150, stretch=False)
        self.script_tree.heading("#0", text="Script Name")
        self.script_tree.place(x=0, y=0, width=200, height=250) 

        self.input_notebook = ttk.Notebook(self.tab_scripts)
        self.input_notebook.place(x=200, y=0, width=450, height=250) 

        self.tab_keywords = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_keywords, text='Keywords')
        self.keywords_text = tk.Text(self.tab_keywords, height=1)
        self.keywords_text.place(x=0, y=0, width=450, height=225) 

        self.tab_titles = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_titles, text='Titles')
        self.titles_text = tk.Text(self.tab_titles, height=1)
        self.titles_text.place(x=0, y=0, width=450, height=225) 

        self.tab_links = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_links, text='Links')
        self.links_text = tk.Text(self.tab_links, height=1)
        self.links_text.place(x=0, y=0, width=450, height=225) 

        self.tab_refer_urls = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_refer_urls, text='Refer URLs')
        self.refer_urls_text = tk.Text(self.tab_refer_urls, height=1)
        self.refer_urls_text.place(x=0, y=0, width=450, height=225) 

        self.log_list = tk.Listbox(self)
        self.log_list.place(x=0, y=300, width=650, height=100) 

        # Options 탭을 생성합니다.
        self.tab_options = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_options, text='Options')

        # 각각의 입력 필드와 레이블을 생성합니다.
        self.thread_entry = PlaceholderEntry(self.tab_options, placeholder="5")
        self.thread_entry.place(x=0, y=10, width=200, height=20) 

        self.min_time_entry = PlaceholderEntry(self.tab_options, placeholder="50")
        self.min_time_entry.place(x=0, y=40, width=200, height=20) 

        self.max_time_entry = PlaceholderEntry(self.tab_options, placeholder="100")
        self.max_time_entry.place(x=0, y=70, width=200, height=20) 

        self.num_obj_entry = PlaceholderEntry(self.tab_options, placeholder="9999999")
        self.num_obj_entry.place(x=0, y=100, width=200, height=20) 

        # 드롭다운 리스트를 생성합니다.
        self.proxy_mode = ttk.Combobox(self.tab_options, values=["Private Proxies", "No Proxy"])
        self.proxy_mode.place(x=0, y=130, width=200) 

        self.proxy_type = ttk.Combobox(self.tab_options, values=["HTTP", "SOCK4", "SOCK5"])
        self.proxy_type.place(x=0, y=160, width=200) 

        # 체크박스를 생성합니다.
        self.headless_var = tk.IntVar()
        self.headless_check = tk.Checkbutton(self.tab_options, text="HeadLess Mode", variable=self.headless_var)
        self.headless_check.place(x=0, y=190, width=200) 

        # User Agents 탭을 생성합니다.
        self.tab_user_agents = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_user_agents, text='User Agents')

        self.agent_text = PlaceholderText(self.tab_user_agents, placeholder="유저 에이전트를 한줄에 하나씩 입력하세요.")
        self.agent_text.place(x=0, y=0, width=646, height=247) 

        # Private Proxies 탭을 생성합니다.
        self.tab_private_proxies = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_private_proxies, text='Private Proxies')

        self.proxies_text = PlaceholderText(self.tab_private_proxies, placeholder="프록시를 한줄에 하나씩 입력하세요.")
        self.proxies_text.place(x=0, y=0, width=646, height=247) 
        
        # Browser Extensions 탭을 생성합니다.
        self.tab_extensions = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_extensions, text='Browser Extensions')

        self.extensions_tree = CheckboxTreeview(self.tab_extensions)
        self.extensions_tree.column("#0", width=646, minwidth=150, stretch=False)
        self.extensions_tree.heading("#0", text="Extensions Name")
        self.extensions_tree.place(x=0, y=0, width=646, height=247) 

        self.load_scripts()

        # Results 탭을 생성합니다.
        self.tab_result = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_result, text='Results')

        self.result_tree = CheckboxTreeview(self.tab_result)
        self.result_tree['columns'] = ("#1", "#2", "#3", "#4", "#5")
        self.result_tree.column("#0", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#0", text="Started")

        self.result_tree.column("#1", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#1", text="Script")

        self.result_tree.column("#2", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#2", text="Proxy")

        self.result_tree.column("#3", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#3", text="User Agent")

        self.result_tree.column("#4", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#4", text="Browsing Time")

        self.result_tree.column("#5", width=107, minwidth=107, stretch=False)
        self.result_tree.heading("#5", text="Output")

        self.result_tree.place(x=0, y=0, width=646, height=247) 

    def start_project(self):
        pass

    def stop_project(self):
        pass

    def load_scripts(self):
        script_files = glob.glob(os.path.join('scripts', '*.py'))

        for script in script_files:
            self.script_tree.insert('', 'end', text=os.path.basename(script), values=[script])

        self.script_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        extensions_files = glob.glob(os.path.join('extensions', '*.crx'))

        for extensions in extensions_files:
            self.extensions_tree.insert('', 'end', text=os.path.basename(extensions), values=[extensions])

        self.extensions_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def on_tree_select(self, event=None):
        selected_items = self.script_tree.selection()
        if not selected_items:  # 선택된 항목이 없을 때
            return  # 아무런 동작도 하지 않고 함수를 종료합니다.
        selected_item = selected_items[0]

    def new_project(self):
        # 새 프로젝트를 생성하면서 모든 위젯의 값을 초기화합니다.
        self.keywords_text.delete('1.0', tk.END)
        self.titles_text.delete('1.0', tk.END)
        self.links_text.delete('1.0', tk.END)
        self.refer_urls_text.delete('1.0', tk.END)
        self.thread_entry.delete(0, tk.END)
        self.min_time_entry.delete(0, tk.END)
        self.max_time_entry.delete(0, tk.END)
        self.num_obj_entry.delete(0, tk.END)
        self.agent_text.delete('1.0', tk.END)
        self.proxies_text.delete('1.0', tk.END)
        self.proxy_mode.set(0)
        self.proxy_type.set(0)
        self.headless_var.set(0)  # 체크박스 초기화
        self.extensions_tree.delete(*self.extensions_tree.get_children())  # 트리뷰 초기화
        
        # 특정 디렉토리를 탐색하여 '*.crx' 파일들을 불러옵니다.
        directory = 'extensions'  # 실제 디렉토리 경로로 변경해주세요.
        for filename in os.listdir(directory):
            if filename.endswith('.crx'):
                self.extensions_tree.insert('', 'end', text=filename)


    def open_project(self):
        filename = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
        if not filename:
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        # 위젯 값 복원
        self.keywords_text.delete(1.0, 'end')
        self.keywords_text.insert(1.0, data['keywords'])
        self.titles_text.delete(1.0, 'end')
        self.titles_text.insert(1.0, data['titles'])
        self.links_text.delete(1.0, 'end')
        self.links_text.insert(1.0, data['links'])
        self.refer_urls_text.delete(1.0, 'end')
        self.refer_urls_text.insert(1.0, data['refer_urls'])
        self.thread_entry.delete(0, 'end')
        self.thread_entry.insert(0, data['thread'])
        self.min_time_entry.delete(0, 'end')
        self.min_time_entry.insert(0, data['min_time'])
        self.max_time_entry.delete(0, 'end')
        self.max_time_entry.insert(0, data['max_time'])
        self.num_obj_entry.delete(0, 'end')
        self.num_obj_entry.insert(0, data['num_obj'])
        self.proxy_mode.set(data['proxy_mode'])
        self.proxy_type.set(data['proxy_type'])
        self.headless_var.set(data['headless_check'])
        self.agent_text.delete(1.0, 'end')
        self.agent_text.insert(1.0, data['agent'])
        self.proxies_text.delete(1.0, 'end')
        self.proxies_text.insert(1.0, data['proxies'])

    def save_project(self):
        # 프로젝트를 저장하는 코드를 작성합니다.
        data = {
            'keywords': self.keywords_text.get(1.0, 'end-1c'),
            'titles': self.titles_text.get(1.0, 'end-1c'),
            'links': self.links_text.get(1.0, 'end-1c'),
            'refer_urls': self.refer_urls_text.get(1.0, 'end-1c'),
            'thread': self.thread_entry.get(),
            'min_time': self.min_time_entry.get(),
            'max_time': self.max_time_entry.get(),
            'num_obj': self.num_obj_entry.get(),
            'proxy_mode': self.proxy_mode.get(),
            'proxy_type': self.proxy_type.get(),
            'headless_check': self.headless_var.get(),
            'agent': self.agent_text.get(1.0, 'end-1c'),
            'proxies': self.proxies_text.get(1.0, 'end-1c'),
        }
        filename = filedialog.asksaveasfilename(filetypes=[('JSON Files', '*.json')], defaultextension='.json')
        if not filename:
            return

        with open(filename, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
