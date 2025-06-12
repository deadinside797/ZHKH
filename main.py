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
        
 def delete_account(self):
        selected = self.accounts_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счет для удаления")
            return
            
        account_id = self.accounts_tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить счет №{account_id}?"):
            self.accounts = [acc for acc in self.accounts if acc["id"] != account_id]
            self.save_data("accounts.json", self.accounts)
            self.refresh_accounts()
    
    def generate_receipt(self):
        selected = self.accounts_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите счет для генерации квитанции")
            return
            
        account_data = self.accounts_tree.item(selected[0])["values"]
        account_id = account_data[0]

        account = next(acc for acc in self.accounts if acc["id"] == account_id)

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 14)
        
        pdf.cell(0, 10, "Квитанция на оплату жилищно-коммунальных услуг", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(40, 10, "№ счета:", 0, 0)
        pdf.cell(0, 10, account["id"], 0, 1)
        
        pdf.cell(40, 10, "Адрес:", 0, 0)
        pdf.cell(0, 10, account["address"], 0, 1)
        
        pdf.cell(40, 10, "Владелец:", 0, 0)
        pdf.cell(0, 10, account["owner"], 0, 1)
        pdf.ln(10)
        
        pdf.cell(0, 10, "Начисления:", 0, 1)
        pdf.ln(5)

        pdf.set_font('DejaVu', '', 10)
        col_widths = [80, 40, 40, 40]

        pdf.cell(col_widths[0], 10, "Услуга", 1, 0, 'C')
        pdf.cell(col_widths[1], 10, "Тариф", 1, 0, 'C')
        pdf.cell(col_widths[2], 10, "Объем", 1, 0, 'C')
        pdf.cell(col_widths[3], 10, "Сумма", 1, 1, 'C')

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
            
            pdf.cell(col_widths[0], 10, service[0], 1)
            pdf.cell(col_widths[1], 10, f"{service[1]:.2f} руб.", 1, 0, 'R')
            pdf.cell(col_widths[2], 10, f"{service[2]:.1f}", 1, 0, 'R')
            pdf.cell(col_widths[3], 10, f"{amount:.2f} руб.", 1, 1, 'R')
        
        pdf.ln(5)
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f"Итого к оплате: {total:.2f} руб.", 0, 1, 'R')
        
        if account["subsidy"]:
            pdf.cell(0, 10, "С учетом субсидии: 30%", 0, 1, 'R')
            pdf.cell(0, 10, f"К оплате: {total * 0.7:.2f} руб.", 0, 1, 'R')
        
        pdf.ln(10)
        pdf.cell(0, 10, f"Дата формирования: {datetime.now().strftime('%d.%m.%Y')}", 0, 1)

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Квитанция_{account_id}.pdf"
        )
        
        if filename:
            pdf.output(filename)
            messagebox.showinfo("Успех", f"Квитанция сохранена как {filename}")
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
            
        for request in self.requests:
            self.requests_tree.insert("", tk.END, values=(
                request["id"],
                request["date"],
                request["address"],
                request["problem"],
                request["status"],
                request.get("contractor", "-")
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
            new_request = {
                "id": f"REQ-{len(self.requests) + 1:04d}",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "address": address_entry.get(),
                "problem": problem_entry.get("1.0", tk.END).strip(),
                "contact": contact_entry.get(),
                "status": "Открыта",
                "contractor": ""
            }
            self.requests.append(new_request)
            self.save_data("requests.json", self.requests)
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
        
        for request in self.requests:
            if request["id"] == request_id:
                if request["status"] == "Закрыта":
                    messagebox.showinfo("Информация", "Эта заявка уже закрыта")
                    return
                
                request["status"] = "Закрыта"
                self.save_data("requests.json", self.requests)
                self.refresh_requests()
                messagebox.showinfo("Успех", "Заявка закрыта")
                return


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
        contractors = [c["name"] for c in self.contractors]
        contractor_combobox = ttk.Combobox(dialog, textvariable=contractor_var, values=contractors)
        contractor_combobox.pack(pady=5)
        
        def save():
            contractor = contractor_var.get()
            if not contractor:
                messagebox.showwarning("Ошибка", "Выберите подрядчика")
                return
                
            for request in self.requests:
                if request["id"] == request_id:
                    request["contractor"] = contractor
                    request["status"] = "В работе"
                    self.save_data("requests.json", self.requests)
                    self.refresh_requests()
                    dialog.destroy()
                    messagebox.showinfo("Успех", f"Подрядчик {contractor} назначен")
                    return
        
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
            
        for meter in self.meters:
            readings = meter.get("readings", [])
            last_reading = "-"
            last_date = "-"
            
            if readings:
                last_reading = readings[-1]["value"]
                last_date = readings[-1]["date"]
            
            self.meters_tree.insert("", tk.END, values=(
                meter["id"],
                meter["type"],
                meter["address"],
                last_reading,
                last_date
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
            new_meter = {
                "id": id_entry.get(),
                "type": type_combobox.get(),
                "address": address_entry.get(),
                "readings": [{
                    "date": datetime.now().strftime("%d.%m.%Y"),
                    "value": float(reading_entry.get())
                }]
            }
            self.meters.append(new_meter)
            self.save_data("meters.json", self.meters)
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
        
        meter = next(m for m in self.meters if m["id"] == meter_id)
        
        ttk.Label(dialog, text=f"Счетчик: {meter['id']}").pack(pady=5)
        ttk.Label(dialog, text=f"Тип: {meter['type']}").pack(pady=5)
        ttk.Label(dialog, text=f"Адрес: {meter['address']}").pack(pady=5)
        
        ttk.Label(dialog, text="Показания:").pack(pady=5)
        reading_entry = ttk.Entry(dialog)
        reading_entry.pack(pady=5)
        
        def save():
            try:
                reading = float(reading_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
                return
                
            meter["readings"].append({
                "date": datetime.now().strftime("%d.%m.%Y"),
                "value": reading
            })
            
            self.save_data("meters.json", self.meters)
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
        meter = next(m for m in self.meters if m["id"] == meter_id)
        
        if len(meter.get("readings", [])) < 2:
            messagebox.showinfo("Информация", "Недостаточно данных для анализа")
            return

        dates = [r["date"] for r in meter["readings"]]
        values = [r["value"] for r in meter["readings"]]

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
    
