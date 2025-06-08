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
