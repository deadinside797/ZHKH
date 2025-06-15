import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

class HousingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учета для ЖКХ")
        self.root.geometry("1200x700")

        self.db_connection = sqlite3.connect('housing.db')
        self.create_tables()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_accounts_tab()
        self.create_requests_tab()
        self.create_meters_tab()
        self.create_reports_tab()
        
    def create_tables(self):
        cursor = self.db_connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            address TEXT NOT NULL,
            owner TEXT NOT NULL,
            balance REAL DEFAULT 0,
            subsidy BOOLEAN DEFAULT FALSE,
            last_payment TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            date TEXT NOT NULL,
            address TEXT NOT NULL,
            problem TEXT NOT NULL,
            contact TEXT,
            status TEXT NOT NULL,
            contractor TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meters (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            address TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meter_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meter_id TEXT NOT NULL,
            date TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY (meter_id) REFERENCES meters(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contractors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            contact TEXT
        )
        ''')
        
        self.db_connection.commit()

    def execute_query(self, query, params=(), fetch=False):
        cursor = self.db_connection.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        self.db_connection.commit()
        
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
            
        accounts = self.execute_query("SELECT * FROM accounts", fetch=True)
        for account in accounts:
            self.accounts_tree.insert("", tk.END, values=(
                account[0], 
                account[1], 
                account[2], 
                f"{account[3]:.2f} руб.", 
                "Да" if account[4] else "Нет", 
                account[5] if account[5] else "-" 
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
            self.execute_query(
                "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)",
                (
                    id_entry.get(),
                    address_entry.get(),
                    owner_entry.get(),
                    float(balance_entry.get()),
                    subsidy_var.get(),
                    "-"
                )
            )
            self.refresh_accounts()
            dialog.destroy()
            messagebox.showinfo("Успех", "Лицевой счет успешно добавлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=5, column=1, padx=5, pady=10, sticky=tk.E)
        
    def delete_account(self):
        selected = self.accounts_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счет для удаления")
            return
            
        account_id = self.accounts_tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить счет №{account_id}?"):
            self.execute_query("DELETE FROM accounts WHERE id = ?", (account_id,))
            self.refresh_accounts()
    
    def generate_receipt(self):
        selected = self.accounts_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счет для генерации квитанции")
            return

        account_data = self.accounts_tree.item(selected[0])["values"]
        account_id = account_data[0]

        account = self.execute_query(
            "SELECT * FROM accounts WHERE id = ?", 
            (account_id,), 
            fetch=True
        )[0]

        pdf = FPDF()
        pdf.add_page()

        try:
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
            pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
            pdf.add_font('DejaVu', 'I', 'DejaVuSansCondensed-Oblique.ttf', uni=True)
            pdf.set_font('DejaVu', '', 14)
            self._generate_russian_receipt(pdf, account)
            filename = f"Квитанция_{account_id}.pdf"
            success_msg = "Квитанция успешно сохранена"
        except Exception as e:
            print(f"Ошибка при использовании DejaVu: {e}")
            try:
                pdf.add_font('Arial', '', 'arial.ttf', uni=True)
                pdf.add_font('Arial', 'B', 'arialbd.ttf', uni=True)
                pdf.add_font('Arial', 'I', 'ariali.ttf', uni=True)
                pdf.set_font('Arial', '', 14)
                self._generate_russian_receipt(pdf, account)
                filename = f"Квитанция_{account_id}.pdf"
                success_msg = "Квитанция успешно сохранена"
            except Exception as e:
                print(f"Ошибка при использовании Arial: {e}")
                pdf.set_font('helvetica', '', 14)
                self._generate_english_receipt(pdf, account)
                filename = f"Receipt_{account_id}.pdf"
                success_msg = "Receipt saved successfully"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename
        )

        if save_path:
            pdf.output(save_path)
            messagebox.showinfo("Успех", success_msg)

    def _generate_russian_receipt(self, pdf, account):
        from fpdf.enums import XPos, YPos

        pdf.cell(0, 10, "Квитанция ЖКХ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)

        pdf.set_font('DejaVu', '', 12)
        self._add_pdf_row(pdf, "№ счета:", str(account[0]))
        self._add_pdf_row(pdf, "Адрес:", str(account[1]))
        self._add_pdf_row(pdf, "Владелец:", str(account[2]))
        pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, "Начисления:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        pdf.set_font('DejaVu', '', 10)
        col_widths = [80, 40, 40, 40]

        headers = ["Услуга", "Тариф", "Объем", "Сумма"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align='C')
        pdf.ln()

        services = [
            ("Холодная вода", 35.78, 5.2),
            ("Горячая вода", 150.25, 3.8),
            ("Электричество", 4.25, 120),
            ("Отопление", 25.60, 45.3)
        ]

        total = 0
        for service in services:
            amount = service[1] * service[2]
            total += amount

            pdf.cell(col_widths[0], 10, service[0], border=1)
            pdf.cell(col_widths[1], 10, f"{service[1]:.2f} руб.", border=1, align='R')
            pdf.cell(col_widths[2], 10, f"{service[2]:.1f}", border=1, align='R')
            pdf.cell(col_widths[3], 10, f"{amount:.2f} руб.", border=1, align='R')
            pdf.ln()

        pdf.ln(5)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f"Итого к оплате: {total:.2f} руб.", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if account[4]:
            pdf.cell(0, 10, "С учетом субсидии 30%:", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 10, f"К оплате: {total * 0.7:.2f} руб.", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(10)
        pdf.set_font('DejaVu', 'I', 10)
        pdf.cell(0, 10, f"Дата формирования: {datetime.now().strftime('%d.%m.%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _generate_english_receipt(self, pdf, account):
        from fpdf.enums import XPos, YPos

        pdf.cell(0, 10, "Housing Services Receipt", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)

        pdf.set_font('helvetica', '', 12)
        self._add_pdf_row(pdf, "Account No:", str(account[0]))
        self._add_pdf_row(pdf, "Address:", str(account[1]))
        self._add_pdf_row(pdf, "Owner:", str(account[2]))
        pdf.ln(10)

        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, "Charges:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        pdf.set_font('helvetica', '', 10)
        col_widths = [80, 40, 40, 40]

        headers = ["Service", "Rate", "Amount", "Total"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align='C')
        pdf.ln()

        services = [
            ("Cold water", 35.78, 5.2),
            ("Hot water", 150.25, 3.8),
            ("Electricity", 4.25, 120),
            ("Heating", 25.60, 45.3)
        ]

        total = 0
        for service in services:
            amount = service[1] * service[2]
            total += amount

            pdf.cell(col_widths[0], 10, service[0], border=1)
            pdf.cell(col_widths[1], 10, f"{service[1]:.2f} RUB", border=1, align='R')
            pdf.cell(col_widths[2], 10, f"{service[2]:.1f}", border=1, align='R')
            pdf.cell(col_widths[3], 10, f"{amount:.2f} RUB", border=1, align='R')
            pdf.ln()

        pdf.ln(5)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, f"Total amount: {total:.2f} RUB", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if account[4]:
            pdf.cell(0, 10, "With 30% subsidy:", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 10, f"Amount due: {total * 0.7:.2f} RUB", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(10)
        pdf.set_font('helvetica', 'I', 10)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d.%m.%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _add_pdf_row(self, pdf, label, value):
        from fpdf.enums import XPos, YPos
        pdf.cell(40, 10, label)
        pdf.cell(0, 10, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def create_requests_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Диспетчеризация")

        control_frame = ttk.LabelFrame(tab, text="Управление")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Добавить заявку", command=self.add_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Закрыть заявку", command=self.close_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Назначить подрядчика", command=self.assign_contractor).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.refresh_requests).pack(side=tk.LEFT, padx=5)

        columns = ("id", "date", "address", "problem", "status", "contractor")
        self.requests_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
        
        self.requests_tree.heading("id", text="№ заявки")
        self.requests_tree.heading("date", text="Дата")
        self.requests_tree.heading("address", text="Адрес")
        self.requests_tree.heading("problem", text="Проблема")
        self.requests_tree.heading("status", text="Статус")
        self.requests_tree.heading("contractor", text="Подрядчик")
        
        self.requests_tree.column("id", width=80)
        self.requests_tree.column("date", width=100)
        self.requests_tree.column("address", width=150)
        self.requests_tree.column("problem", width=250)
        self.requests_tree.column("status", width=100)
        self.requests_tree.column("contractor", width=150)
        
        self.requests_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.refresh_requests()
    
    def refresh_requests(self):
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
            
        requests = self.execute_query("SELECT * FROM requests", fetch=True)
        for request in requests:
            self.requests_tree.insert("", tk.END, values=(
                request[0], 
                request[2], 
                request[3], 
                request[4], 
                request[6], 
                request[7] if request[7] else "-"
            ))

    def add_request(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить заявку")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Адрес:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        address_entry = ttk.Entry(dialog)
        address_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Проблема:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        problem_entry = tk.Text(dialog, height=5, width=40)
        problem_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Контактное лицо:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        contact_entry = ttk.Entry(dialog)
        contact_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            request_id = f"REQ-{len(self.execute_query('SELECT * FROM requests', fetch=True)) + 1:04d}"
            
            self.execute_query(
                "INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    request_id,
                    None,
                    datetime.now().strftime("%d.%m.%Y"),
                    address_entry.get(),
                    problem_entry.get("1.0", tk.END).strip(),
                    contact_entry.get(),
                    "Открыта",
                    None
                )
            )
            self.refresh_requests()
            dialog.destroy()
            messagebox.showinfo("Успех", "Заявка успешно добавлена")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
    
    def close_request(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заявку для закрытия")
            return
            
        request_id = self.requests_tree.item(selected[0])["values"][0]
        
        status = self.execute_query(
            "SELECT status FROM requests WHERE id = ?", 
            (request_id,), 
            fetch=True
        )[0][0]
        
        if status == "Закрыта":
            messagebox.showinfo("Информация", "Эта заявка уже закрыта")
            return
        
        self.execute_query(
            "UPDATE requests SET status = ? WHERE id = ?",
            ("Закрыта", request_id)
        )
        self.refresh_requests()
        messagebox.showinfo("Успех", "Заявка закрыта")

    def assign_contractor(self):
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заявку")
            return
            
        request_id = self.requests_tree.item(selected[0])["values"][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Назначить подрядчика")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Выберите подрядчика:").pack(pady=10)
        
        contractor_var = tk.StringVar()
        contractors = [c[1] for c in self.execute_query("SELECT * FROM contractors", fetch=True)]
        contractor_combobox = ttk.Combobox(dialog, textvariable=contractor_var, values=contractors)
        contractor_combobox.pack(pady=5)
        
        def save():
            contractor = contractor_var.get()
            if not contractor:
                messagebox.showwarning("Ошибка", "Выберите подрядчика")
                return
                
            self.execute_query(
                "UPDATE requests SET contractor = ?, status = ? WHERE id = ?",
                (contractor, "В работе", request_id)
            )
            self.refresh_requests()
            dialog.destroy()
            messagebox.showinfo("Успех", f"Подрядчик {contractor} назначен")
        
        ttk.Button(dialog, text="Назначить", command=save).pack(pady=10)
    
    def create_meters_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Учет ресурсов")

        control_frame = ttk.LabelFrame(tab, text="Управление")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Добавить счетчик", command=self.add_meter).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Внести показания", command=self.add_meter_reading).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Анализ расхода", command=self.analyze_consumption).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.refresh_meters).pack(side=tk.LEFT, padx=5)

        columns = ("id", "type", "address", "last_reading", "last_date")
        self.meters_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
        
        self.meters_tree.heading("id", text="№ счетчика")
        self.meters_tree.heading("type", text="Тип")
        self.meters_tree.heading("address", text="Адрес")
        self.meters_tree.heading("last_reading", text="Последние показания")
        self.meters_tree.heading("last_date", text="Дата")
        
        self.meters_tree.column("id", width=100)
        self.meters_tree.column("type", width=120)
        self.meters_tree.column("address", width=150)
        self.meters_tree.column("last_reading", width=120)
        self.meters_tree.column("last_date", width=100)
        
        self.meters_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.refresh_meters()

    def refresh_meters(self):
        for item in self.meters_tree.get_children():
            self.meters_tree.delete(item)
            
        meters = self.execute_query("SELECT * FROM meters", fetch=True)
        for meter in meters:
            last_reading = self.execute_query(
                "SELECT date, value FROM meter_readings WHERE meter_id = ? ORDER BY date DESC LIMIT 1",
                (meter[0],),
                fetch=True
            )
            
            last_reading_value = "-"
            last_reading_date = "-"
            
            if last_reading:
                last_reading_date = last_reading[0][0]
                last_reading_value = last_reading[0][1]
            
            self.meters_tree.insert("", tk.END, values=(
                meter[0],
                meter[1],
                meter[2], 
                last_reading_value,
                last_reading_date
            ))

    def add_meter(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить счетчик")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="№ счетчика:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        type_combobox = ttk.Combobox(dialog, values=["Холодная вода", "Горячая вода", "Электричество", "Газ", "Отопление"])
        type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Адрес:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        address_entry = ttk.Entry(dialog)
        address_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Начальные показания:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        reading_entry = ttk.Entry(dialog)
        reading_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        reading_entry.insert(0, "0")

        def save():
            meter_id = id_entry.get()

            self.execute_query(
                "INSERT INTO meters VALUES (?, ?, ?)",
                (meter_id, type_combobox.get(), address_entry.get())
            )

            self.execute_query(
                "INSERT INTO meter_readings (meter_id, date, value) VALUES (?, ?, ?)",
                (meter_id, datetime.now().strftime("%d.%m.%Y"), float(reading_entry.get()))
            )
            
            self.refresh_meters()
            dialog.destroy()
            messagebox.showinfo("Успех", "Счетчик успешно добавлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)
    
    def add_meter_reading(self):
        selected = self.meters_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счетчик")
            return
            
        meter_id = self.meters_tree.item(selected[0])["values"][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Внести показания")
        dialog.geometry("300x200")
        
        meter = self.execute_query(
            "SELECT * FROM meters WHERE id = ?", 
            (meter_id,), 
            fetch=True
        )[0]
        
        ttk.Label(dialog, text=f"Счетчик: {meter[0]}").pack(pady=5)
        ttk.Label(dialog, text=f"Тип: {meter[1]}").pack(pady=5)
        ttk.Label(dialog, text=f"Адрес: {meter[2]}").pack(pady=5)
        
        ttk.Label(dialog, text="Показания:").pack(pady=5)
        reading_entry = ttk.Entry(dialog)
        reading_entry.pack(pady=5)
        
        def save():
            try:
                reading = float(reading_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
                return
                
            self.execute_query(
                "INSERT INTO meter_readings (meter_id, date, value) VALUES (?, ?, ?)",
                (meter_id, datetime.now().strftime("%d.%m.%Y"), reading)
            )
            
            self.refresh_meters()
            dialog.destroy()
            messagebox.showinfo("Успех", "Показания сохранены")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
    
    def analyze_consumption(self):
        selected = self.meters_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счетчик")
            return
            
        meter_id = self.meters_tree.item(selected[0])["values"][0]
        
        readings = self.execute_query(
            "SELECT date, value FROM meter_readings WHERE meter_id = ? ORDER BY date",
            (meter_id,),
            fetch=True
        )
        
        if len(readings) < 2:
            messagebox.showinfo("Информация", "Недостаточно данных для анализа")
            return

        dates = [r[0] for r in readings]
        values = [r[1] for r in readings]

        consumption = []
        for i in range(1, len(values)):
            consumption.append(values[i] - values[i-1])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

        ax1.plot(dates, values, 'o-')
        ax1.set_title(f"Показания счетчика {meter_id}")
        ax1.set_ylabel("Показания")
        ax1.grid(True)

        ax2.bar(dates[1:], consumption)
        ax2.set_title("Потребление между показаниями")
        ax2.set_ylabel("Потребление")
        ax2.grid(True)
        
        plt.tight_layout()

        graph_window = tk.Toplevel(self.root)
        graph_window.title(f"Анализ потребления - {meter_id}")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Отчетность")

        control_frame = ttk.LabelFrame(tab, text="Отчеты")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Отчет по платежам", command=self.generate_payments_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отчет по заявкам", command=self.generate_requests_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отчет по счетчикам", command=self.generate_meters_report).pack(side=tk.LEFT, padx=5)

        self.report_text = tk.Text(tab, wrap=tk.WORD, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tab, command=self.report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.config(yscrollcommand=scrollbar.set)
    
    def generate_payments_report(self):
        accounts = self.execute_query("SELECT * FROM accounts", fetch=True)
        total_balance = sum(acc[3] for acc in accounts)
        subsidy_count = sum(1 for acc in accounts if acc[4])
        
        report = f"Отчет по платежам\nДата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        report += f"Всего лицевых счетов: {len(accounts)}\n"
        report += f"Субсидии предоставлены: {subsidy_count} счетам\n"
        report += f"Общая сумма задолженности: {total_balance:.2f} руб.\n\n"
        
        report += "Топ-5 должников:\n"
        debtors = sorted(accounts, key=lambda x: x[3], reverse=True)[:5]
        for i, debtor in enumerate(debtors, 1):
            report += f"{i}. {debtor[1]} ({debtor[2]}): {debtor[3]:.2f} руб.\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
    
    def generate_requests_report(self):
        requests = self.execute_query("SELECT * FROM requests", fetch=True)
        open_count = sum(1 for req in requests if req[6] == "Открыта")
        in_progress_count = sum(1 for req in requests if req[6] == "В работе")
        closed_count = sum(1 for req in requests if req[6] == "Закрыта")
        
        report = f"Отчет по заявкам\nДата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        report += f"Всего заявок: {len(requests)}\n"
        report += f"Открытые: {open_count}\n"
        report += f"В работе: {in_progress_count}\n"
        report += f"Закрытые: {closed_count}\n\n"
        
        contractors = self.execute_query("SELECT * FROM contractors", fetch=True)
        if contractors:
            report += "Заявки по подрядчикам:\n"
            for contractor in contractors:
                count = sum(1 for req in requests if req[7] == contractor[1])
                report += f"{contractor[1]}: {count} заявок\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
    
    def generate_meters_report(self):
        meters = self.execute_query("SELECT type, COUNT(*) FROM meters GROUP BY type", fetch=True)
        
        report = f"Отчет по счетчикам\nДата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        report += f"Всего счетчиков: {sum(m[1] for m in meters)}\n\n"
        
        report += "Количество по типам:\n"
        for meter_type, count in meters:
            report += f"{meter_type}: {count}\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)

    def __del__(self):
        if hasattr(self, 'db_connection'):
            self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = HousingApp(root)
    root.mainloop()