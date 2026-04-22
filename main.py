"""
Expense Tracker - Трекер личных расходов
Автор: Максим Купин
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from decimal import Decimal

class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = []
        self.categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Одежда", "Другое"]
        self.load()
    
    def load(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.expenses = json.load(f)
        except:
            self.expenses = []
    
    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def add(self, amount_str, category, date_str, desc=""):
        try:
            amount = float(Decimal(amount_str))
            if amount <= 0:
                raise ValueError("Сумма должна быть положительным числом")
        except:
            raise ValueError("Сумма должна быть положительным числом (например: 150.50)")
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД (например: 2024-01-15)")
        
        new_id = max([e.get('id', 0) for e in self.expenses], default=0) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str,
            "desc": desc.strip()
        })
        self.save()
        return new_id
    
    def delete(self, expense_id):
        self.expenses = [e for e in self.expenses if e.get('id') != expense_id]
        self.save()
    
    def filter(self, category="Все", start="", end=""):
        result = self.expenses.copy()
        if category != "Все":
            result = [e for e in result if e['category'] == category]
        if start:
            result = [e for e in result if e['date'] >= start]
        if end:
            result = [e for e in result if e['date'] <= end]
        return sorted(result, key=lambda x: x['date'], reverse=True)
    
    def total(self, filtered):
        return sum(e['amount'] for e in filtered)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Максим Купин")
        self.root.geometry("800x550")
        self.tracker = ExpenseTracker()
        
        self.cat_var = tk.StringVar(value="Все")
        self.start_var = tk.StringVar(value=datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        self.end_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        self._build_ui()
        self._refresh()
    
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Добавление
        add_frame = ttk.LabelFrame(main, text="Добавить расход", padding=5)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = ttk.Entry(add_frame, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.cat_combo = ttk.Combobox(add_frame, values=self.tracker.categories, state="readonly", width=12)
        self.cat_combo.current(0)
        self.cat_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Дата:").grid(row=1, column=0, padx=5)
        self.date_entry = ttk.Entry(add_frame, width=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(add_frame, text="Описание:").grid(row=1, column=2, padx=5)
        self.desc_entry = ttk.Entry(add_frame, width=20)
        self.desc_entry.grid(row=1, column=3, padx=5)
        
        ttk.Button(add_frame, text="➕ Добавить расход", command=self._add).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(main, text="Фильтрация", padding=5)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Категория:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(filter_frame, textvariable=self.cat_var, values=["Все"]+self.tracker.categories, 
                    state="readonly", width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="С даты:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(filter_frame, textvariable=self.start_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="По дату:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(filter_frame, textvariable=self.end_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self._refresh).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="🗑 Удалить выбранное", command=self._delete).pack(side=tk.RIGHT, padx=5)
        
        # Таблица
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        cols = ("ID", "Дата", "Категория", "Сумма", "Описание")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=40)
        self.tree.column("Дата", width=80)
        self.tree.column("Категория", width=100)
        self.tree.column("Сумма", width=80)
        self.tree.column("Описание", width=200)
        
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Статистика
        self.stats_label = ttk.Label(main, text="", font=('Arial', 10, 'bold'))
        self.stats_label.pack(pady=5)
    
    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        filtered = self.tracker.filter(self.cat_var.get(), self.start_var.get(), self.end_var.get())
        
        for e in filtered:
            self.tree.insert("", tk.END, values=(e['id'], e['date'], e['category'], f"{e['amount']:.2f}", e.get('desc', '')))
        
        total = self.tracker.total(filtered)
        self.stats_label.config(text=f"Записей: {len(filtered)} | Сумма за период: {total:.2f} руб")
    
    def _add(self):
        try:
            self.tracker.add(
                self.amount_entry.get(),
                self.cat_combo.get(),
                self.date_entry.get(),
                self.desc_entry.get()
            )
            self.amount_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self._refresh()
            messagebox.showinfo("Успех", "Расход добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка валидации", str(e))
    
    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите записи для удаления")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить {len(sel)} записей?"):
            for item in sel:
                self.tracker.delete(self.tree.item(item)['values'][0])
            self._refresh()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
