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


    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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

    def refresh_accounts(self):
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
            
        for account in self.accounts:
            self.accounts_tree.insert("", tk.END, values=(
                account["id"],
                account["address"],
                account["owner"],
                f"{account['balance']:.2f} руб.",
                "Да" if account["subsidy"] else "Нет",
                account["last_payment"]
            ))

    def add_account(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить лицевой счет")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="№ счета:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Адрес:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        address_entry = ttk.Entry(dialog)
        address_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Владелец:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        owner_entry = ttk.Entry(dialog)
        owner_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Начальный баланс:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        balance_entry = ttk.Entry(dialog)
        balance_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        balance_entry.insert(0, "0.00")
        
        subsidy_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Субсидия", variable=subsidy_var).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            new_account = {
                "id": id_entry.get(),
                "address": address_entry.get(),
                "owner": owner_entry.get(),
                "balance": float(balance_entry.get()),
                "subsidy": subsidy_var.get(),
                "last_payment": "-"
            }
            self.accounts.append(new_account)
            self.save_data("accounts.json", self.accounts)
            self.refresh_accounts()
            dialog.destroy()
            messagebox.showinfo("Успех", "Лицевой счет успешно добавлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=5, column=1, padx=5, pady=10, sticky=tk.E)
