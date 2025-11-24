import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib.pyplot as plt
import sys
import os
from patient import Patient, PatientForm, StatisticsWindow
from faker import Faker
import random

# Получаем путь к директории проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Определяем путь к data папке (на уровень выше src)
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PATIENTS_FILE = os.path.join(DATA_DIR, 'patients.json')

# Создаем папку data, если она не существует
os.makedirs(DATA_DIR, exist_ok=True)

# Подавление всех сообщений в терминале
os.environ['TK_SILENCE_DEPRECATION'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Перенаправляем stdout и stderr для подавления вывода
original_stdout = sys.stdout
original_stderr = sys.stderr
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

fake = Faker()

class App:
    def __init__(self):
        # Подавление вывода Tkinter
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем окно на время инициализации
        self.root.title("Медицинская система учёта")
        self.root.geometry("800x600")
        
        # Подавление предупреждений Tkinter
        self.root.report_callback_exception = self.handle_exception
        
        self.patients = []
        self.load_data()
        
        self.create_widgets()
        self.update_table()
        
        # Показываем окно после инициализации
        self.root.deiconify()
        
        # Обработчик закрытия главного окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def handle_exception(self, exc, val, tb):
        # Обработчик исключений Tkinter - выводим только реальные ошибки
        import traceback
        error_msg = ''.join(traceback.format_exception(exc, val, tb))
        if "error" in error_msg.lower() or "exception" in error_msg.lower():
            # Восстанавливаем stderr для вывода ошибки
            sys.stderr = original_stderr
            print(f"Ошибка: {error_msg}")
            sys.stderr = open(os.devnull, 'w')
    
    def create_widgets(self):
        # Создаем фрейм для таблицы с прокруткой
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Добавляем прокрутку для таблицы
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(table_frame, columns=("Name", "Age", "Gender", "Height", "Weight", "BMI"), 
                                show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("Name", text="ФИО")
        self.tree.heading("Age", text="Возраст")
        self.tree.heading("Gender", text="Пол")
        self.tree.heading("Height", text="Рост")
        self.tree.heading("Weight", text="Вес")
        self.tree.heading("BMI", text="ИМТ")
        
        # Настраиваем столбцы
        self.tree.column("Name", width=200)
        self.tree.column("Age", width=80)
        self.tree.column("Gender", width=100)
        self.tree.column("Height", width=80)
        self.tree.column("Weight", width=80)
        self.tree.column("BMI", width=80)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Добавить", command=self.add_patient).pack(side='left', padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_patient).pack(side='left', padx=5)
        # tk.Button(button_frame, text="Удалить", command=self.delete_patient).pack(side='left', padx=5)
        tk.Button(button_frame, text="Статистика", command=self.show_stats).pack(side='left', padx=5)
        tk.Button(button_frame, text="Созд. данные", command=self.generate_data).pack(side='left', padx=5)
    
    def add_patient(self):
        form = PatientForm(self.root)
        self.root.wait_window(form)
        if form.patient:
            self.patients.append(form.patient)
            self.update_table()
    
    def edit_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пациента для редактирования")
            return
        
        index = self.tree.index(selected[0])
        form = PatientForm(self.root, self.patients[index])
        self.root.wait_window(form)
        if form.patient:
            self.patients[index] = form.patient
            self.update_table()
    
    # def delete_patient(self):
        # selected = self.tree.selection()
        # if not selected:
            # messagebox.showwarning("Ошибка", "Выберите пациента для удаления")
            # return
        
        # index = self.tree.index(selected[0])
        # patient_name = self.patients[index].name
        
        # if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пациента {patient_name}?"):
            # del self.patients[index]
            # self.update_table()
    
    def show_stats(self):
        if not self.patients:
            messagebox.showwarning("Ошибка", "Нет данных для статистики")
            return
        StatisticsWindow(self.root, self.patients)
    
    def generate_data(self):
        for _ in range(10):
            gender = random.choice(['Мужской', 'Женский'])
            self.patients.append(Patient(
                name=fake.name(),
                age=random.randint(18, 80),
                gender=gender,
                height=random.randint(150, 200),
                weight=random.randint(50, 100)
            ))
        self.update_table()
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for patient in self.patients:
            self.tree.insert("", "end", values=(
                patient.name,
                patient.age,
                patient.gender,
                patient.height,
                patient.weight,
                patient.bmi
            ))
    
    def load_data(self):
        try:
            with open("../data/patients.json", "r") as f:
                data = json.load(f)
                # Обрабатываем старые данные с полем 'full_name'
                for item in data:
                    if 'full_name' in item:
                        item['name'] = item['full_name']
                        del item['full_name']
                self.patients = [Patient(**item) for item in data]
        except FileNotFoundError:
            pass
        except Exception as e:
            # Выводим только реальные ошибки
            messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке данных: {e}")
    
    def save_data(self):
        # Убедимся, что сохраняем данные с правильными именами полей
        data_to_save = []
        for patient in self.patients:
            patient_dict = {
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
                'height': patient.height,
                'weight': patient.weight
            }
            data_to_save.append(patient_dict)
        
        with open("../data/patients.json", "w") as f:
            json.dump(data_to_save, f, indent=2)
    
    def on_closing(self):
        self.save_data()
        # Закрываем все окна matplotlib
        plt.close('all')
        # Завершаем приложение
        self.root.quit()
        self.root.destroy()
        # Принудительно завершаем процесс, если нужно
        sys.exit(0)

if __name__ == "__main__":
    try:
        App()
    except Exception as e:
        # Восстанавливаем stderr для вывода реальных ошибок
        sys.stderr = original_stderr
        print(f"Критическая ошибка: {e}")
    finally:
        # Восстанавливаем stdout и stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr