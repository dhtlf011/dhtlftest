from tkinter import ttk, filedialog, messagebox
from ttkwidgets import CheckboxTreeview
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

        self.saveas_button = tk.Button(text="Save as", command=self.save_as_project)
        self.saveas_button.place(x=210, y=5, width=60, height=25) 

        self.start_button = tk.Button(text="Start", command=self.start_project)
        self.start_button.place(x=280, y=5, width=60, height=25) 

        self.stop_button = tk.Button(text="Stop", command=self.stop_project)
        self.stop_button.place(x=350, y=5, width=60, height=25)                                 

        self.notebook = ttk.Notebook(self)
        self.tab_scripts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scripts, text='Scripts')
        self.notebook.place(x=0, y=30, width=650, height=360) 

        self.script_tree = CheckboxTreeview(self.tab_scripts)
        self.script_tree.column("#0", width=150, minwidth=150, stretch=False)
        self.script_tree.heading("#0", text="Script Name")
        self.script_tree.place(x=0, y=0, width=200, height=250) 

        self.load_scripts()

        self.input_notebook = ttk.Notebook(self.tab_scripts)
        self.input_notebook.place(x=200, y=0, width=450, height=250) 

        self.tab_keywords = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_keywords, text='Keywords')
        self.keywords_entry = tk.Text(self.tab_keywords, height=1)
        self.keywords_entry.place(x=0, y=0, width=450, height=225) 

        self.tab_titles = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_titles, text='Titles')
        self.titles_entry = tk.Text(self.tab_titles, height=1)
        self.titles_entry.place(x=0, y=0, width=450, height=225) 

        self.tab_links = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_links, text='Links')
        self.links_entry = tk.Text(self.tab_links, height=1)
        self.links_entry.place(x=0, y=0, width=450, height=225) 

        self.tab_refer_urls = ttk.Frame(self.input_notebook)
        self.input_notebook.add(self.tab_refer_urls, text='Refer URLs')
        self.refer_urls_entry = tk.Text(self.tab_refer_urls, height=1)
        self.refer_urls_entry.place(x=0, y=0, width=450, height=225) 

        self.log_list = tk.Listbox(self)
        self.log_list.place(x=0, y=300, width=650, height=100) 

        # Options 탭을 생성합니다.
        self.tab_options = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_options, text='Options')

        # 각각의 입력 필드와 레이블을 생성합니다.
        self.thread_entry = PlaceholderEntry(self.tab_options, placeholder="쓰레드 수 입력.")
        self.thread_entry.place(x=0, y=10, width=200, height=20) 

        self.min_time_entry = PlaceholderEntry(self.tab_options, placeholder="객체의 최소 시간 입력.")
        self.min_time_entry.place(x=0, y=40, width=200, height=20) 

        self.max_time_entry = PlaceholderEntry(self.tab_options, placeholder="객체의 최대 시간 입력.")
        self.max_time_entry.place(x=0, y=70, width=200, height=20) 

        self.num_obj_entry = PlaceholderEntry(self.tab_options, placeholder="쓰레드 총 반복 수")
        self.num_obj_entry.place(x=0, y=100, width=200, height=20) 

        # 드롭다운 리스트를 생성합니다.
        self.proxy_mode = ttk.Combobox(self.tab_options, values=["Private Proxies", "No Proxy"])
        self.proxy_mode.place(x=0, y=130, width=200) 

        self.proxy_type = ttk.Combobox(self.tab_options, values=["HTTP", "SOCK4", "SOCK5"])
        self.proxy_type.place(x=0, y=160, width=200) 

        # 체크박스를 생성합니다.
        self.headless_check = ttk.Checkbutton(self.tab_options, text="HeadLess Mode")
        self.headless_check.place(x=0, y=190, width=200) 

        # User Agents 탭을 생성합니다.
        self.tab_user_agents = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_user_agents, text='User Agents')

        self.agent_entry = PlaceholderText(self.tab_user_agents, placeholder="유저 에이전트를 한줄에 한개씩 입력하세요.")
        self.agent_entry.place(x=0, y=0, width=646, height=247) 

        # Private Proxies 탭을 생성합니다.
        self.tab_private_proxies = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_private_proxies, text='Private Proxies')

        self.proxies_entry = PlaceholderText(self.tab_private_proxies, placeholder="프록시를 한줄에 한개씩 입력하세요.")
        self.proxies_entry.place(x=0, y=0, width=646, height=247) 
        
        # Browser Extensions 탭을 생성합니다.
        self.tab_extensions = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_extensions, text='Browser Extensions')

        self.extensions_tree = CheckboxTreeview(self.tab_extensions)
        self.extensions_tree.column("#0", width=646, minwidth=150, stretch=False)
        self.extensions_tree.heading("#0", text="Extensions Name")
        self.extensions_tree.place(x=0, y=0, width=646, height=247) 

        # Results 탭을 생성합니다.
        self.tab_result = ttk.Frame(self.notebook) # 'self.notebook'을 사용합니다.
        self.notebook.add(self.tab_result, text='Browser Extensions')

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

    def load_scripts(self):
        script_files = glob.glob(os.path.join('scripts', '*.py'))

        for script in script_files:
            self.script_tree.insert('', 'end', text=os.path.basename(script))

        self.script_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def on_tree_select(self, event):
        selected_item = self.script_tree.selection()[0]

        for item in self.script_tree.get_children():
            if item != selected_item:
                self.script_tree.change_state(item, "unchecked")

        self.script_tree.change_state(selected_item, "checked")

    def new_project(self):
        # 새 프로젝트를 생성하면서 모든 위젯의 값을 초기화합니다.
        self.keywords_entry.delete(0, tk.END)
        self.titles_entry.delete(0, tk.END)
        self.links_entry.delete(0, tk.END)
        self.refer_urls_entry.delete(0, tk.END)
        self.thread_entry.delete(0, tk.END)
        self.min_time_entry.delete(0, tk.END)
        self.max_time_entry.delete(0, tk.END)
        self.num_obj_entry.delete(0, tk.END)
        self.agent_entry.delete(0, tk.END)
        self.proxies_entry.delete(0, tk.END)
        self.proxy_mode.set(0)  # 체크박스 초기화
        self.proxy_type.set(0)  # 체크박스 초기화
        self.headless_check.set(False)  # 체크박스 초기화
        self.extensions_tree.delete(*self.extensions_tree.get_children())  # 트리뷰 초기화
        
        # 특정 디렉토리를 탐색하여 '*.crx' 파일들을 불러옵니다.
        directory = '/path/to/your/directory'  # 실제 디렉토리 경로로 변경해주세요.
        for filename in os.listdir(directory):
            if filename.endswith('.crx'):
                # 파일을 트리뷰에 추가하는 코드...
                # self.extensions_tree.insert('', 'end', text=filename)
                pass



    def open_project(self):
        # 프로젝트를 불러오는 코드를 작성합니다.
        filepath = filedialog.askopenfilename(filetypes=[("Json files", "*.json")])
        if not filepath:
            return
        with open(filepath, 'r') as file:
            data = json.load(file)
            # 데이터를 각 위젯에 적용
            self.keywords_entry.insert(0, data['keywords'])
            self.titles_entry.insert(0, data['titles'])
            # 나머지 위젯들도 같은 방식으로 적용
    
    def save_project(self):
        # 프로젝트를 저장하는 코드를 작성합니다.
        data = {
            'keywords': self.keywords_entry.get(),
            'titles': self.titles_entry.get(),
            # 나머지 위젯들의 값을 가져와서 저장합니다.
        }
        filepath = filedialog.asksaveasfilename(defaultextension="json", filetypes=[("Json files", "*.json")])
        if not filepath:
            return
        with open(filepath, 'w') as file:
            json.dump(data, file)

    def save_as_project(self):
        # 프로젝트를 다른 이름으로 저장하는 코드를 작성합니다.
        # save_project와 동일하게 작동합니다.
        self.save_project()

    def start_project(self):
        # 프로젝트를 실행하는 코드를 작성합니다.
        pass

    def stop_project(self):
        # 프로젝트를 중지하는 코드를 작성합니다.
        pass

if __name__ == "__main__":
    app = Application()
    app.mainloop()
