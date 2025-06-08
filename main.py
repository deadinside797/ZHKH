import tkinter as tk
from tkinter import ttk

class HousingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учета для ЖКХ")
        self.root.geometry("1200x700")

        self.accounts = self.load_data("accounts.json")
        self.requests = self.load_data("requests.json")
        self.meters = self.load_data("meters.json")
        self.contractors = self.load_data("contractors.json")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_accounts_tab()
        self.create_requests_tab()
        self.create_meters_tab()
        self.create_reports_tab()

def create_accounts_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Лицевые счета")

        control_frame = ttk.LabelFrame(tab, text="Управление")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Добавить счет", command=self.add_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить счет", command=self.delete_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сформировать квитанцию", command=self.generate_receipt).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.refresh_accounts).pack(side=tk.LEFT, padx=5)

        columns = ("id", "address", "owner", "balance", "subsidy", "last_payment")
        self.accounts_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
        
        self.accounts_tree.heading("id", text="№ счета")
        self.accounts_tree.heading("address", text="Адрес")
        self.accounts_tree.heading("owner", text="Владелец")
        self.accounts_tree.heading("balance", text="Баланс")
        self.accounts_tree.heading("subsidy", text="Субсидия")
        self.accounts_tree.heading("last_payment", text="Последний платеж")
        
        self.accounts_tree.column("id", width=80)
        self.accounts_tree.column("address", width=200)
        self.accounts_tree.column("owner", width=150)
        self.accounts_tree.column("balance", width=100)
        self.accounts_tree.column("subsidy", width=100)
        self.accounts_tree.column("last_payment", width=120)
        
        self.accounts_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.refresh_accounts()
