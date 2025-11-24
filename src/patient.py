import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings("ignore")
plt.rcParams.update({'figure.max_open_warning': 0})
from faker import Faker
import random
import sys
import os

# Подавление всех предупреждений и информационных сообщений
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

fake = Faker()

class Patient:
    def __init__(self, name, age, gender, height, weight):
        self.name = name
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
    
    @property
    def bmi(self):
        return round(self.weight / ((self.height / 100) ** 2), 2)

class PatientForm(tk.Toplevel):
    def __init__(self, parent, patient=None):
        super().__init__(parent)
        self.patient = patient
        
        self.title("Данные пациента")
        self.geometry("400x210")
        
        tk.Label(self, text="ФИО:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(self, text="Возраст:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.age_spinbox = tk.Spinbox(self, from_=0, to=150, width=27)
        self.age_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(self, text="Пол:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.gender_var = tk.StringVar(value="Мужской")
        gender_frame = tk.Frame(self)
        gender_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(gender_frame, text="Мужской", variable=self.gender_var, value="Мужской").pack(side="left")
        tk.Radiobutton(gender_frame, text="Женский", variable=self.gender_var, value="Женский").pack(side="left")
        
        tk.Label(self, text="Рост (см):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.height_spinbox = tk.Spinbox(self, from_=50, to=250, width=27)
        self.height_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(self, text="Вес (кг):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.weight_spinbox = tk.Spinbox(self, from_=5, to=300, width=27)
        self.weight_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        button_frame = tk.Frame(self)
        button_frame.grid(row=5, columnspan=2, pady=20)
        tk.Button(button_frame, text="Сохранить", command=self.save).pack(side="left", padx=10)
        
        self.columnconfigure(1, weight=1)
        
        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        if patient:
            self.fill_form()
    
    def on_close(self):
        # Устанавливаем patient в None, если форма закрыта без сохранения
        self.patient = None
        self.destroy()
    
    def fill_form(self):
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, self.patient.name)
        self.age_spinbox.delete(0, 'end')
        self.age_spinbox.insert(0, self.patient.age)
        self.gender_var.set(self.patient.gender)
        self.height_spinbox.delete(0, 'end')
        self.height_spinbox.insert(0, self.patient.height)
        self.weight_spinbox.delete(0, 'end')
        self.weight_spinbox.insert(0, self.patient.weight)
    
    def save(self):
        try:
            name = self.name_entry.get()
            age = int(self.age_spinbox.get())
            gender = self.gender_var.get()
            height = int(self.height_spinbox.get())
            weight = int(self.weight_spinbox.get())
            
            if not name:
                raise ValueError("ФИО не может быть пустым")
            
            self.patient = Patient(name, age, gender, height, weight)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

class StatisticsWindow(tk.Toplevel):
    def __init__(self, parent, patients):
        super().__init__(parent)
        self.patients = patients
        self.title("Сводная статистика")
        self.geometry("700x600")
        
        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Создаем фигуру с 4 подграфиками в сетке 2x2
        self.fig, self.axes = plt.subplots(2, 2, figsize=(8, 6))
        self.fig.suptitle("Сводная статистика пациентов", fontsize=14)
        
        self.create_gender_plot()
        self.create_age_plot()
        self.create_bmi_gender_plot()
        self.create_bmi_age_plot()
        
        # Убираем лишние подграфики, если они есть
        for ax in self.axes.flat:
            if not ax.has_data():
                ax.remove()
                
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.canvas.draw()
    
    def on_close(self):
        # Закрываем фигуру matplotlib при закрытии окна
        plt.close(self.fig)
        self.destroy()
    
    def create_gender_plot(self):
        ax = self.axes[0, 0]
        genders = [p.gender for p in self.patients]
        gender_counts = {g: genders.count(g) for g in set(genders)}
        
        ax.pie(gender_counts.values(), labels=gender_counts.keys(), autopct='%1.1f%%')
        ax.set_title("Распределение по полу")
    
    def create_age_plot(self):
        ax = self.axes[0, 1]
        ages = [p.age for p in self.patients]
        age_groups = {'0-18':0, '19-35':0, '36-60':0, '60+':0}
        for age in ages:
            if age <= 18: age_groups['0-18'] += 1
            elif age <= 35: age_groups['19-35'] += 1
            elif age <= 60: age_groups['36-60'] += 1
            else: age_groups['60+'] += 1
        
        ax.bar(age_groups.keys(), age_groups.values())
        ax.set_title("Распределение по возрасту")
        ax.set_ylabel("Количество пациентов")
    
    def create_bmi_gender_plot(self):
        ax = self.axes[1, 0]
        male_bmi = [p.bmi for p in self.patients if p.gender == 'Мужской']
        female_bmi = [p.bmi for p in self.patients if p.gender == 'Женский']
        
        # Используем boxplot только если есть данные
        data_to_plot = []
        labels = []
        if male_bmi:
            data_to_plot.append(male_bmi)
            labels.append('Мужчины')
        if female_bmi:
            data_to_plot.append(female_bmi)
            labels.append('Женщины')
            
        if data_to_plot:
            ax.boxplot(data_to_plot, labels=labels)
            ax.set_title("Распределение ИМТ по полу")
            ax.set_ylabel("ИМТ")
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Распределение ИМТ по полу")
    
    def create_bmi_age_plot(self):
        ax = self.axes[1, 1]
        ages = [p.age for p in self.patients]
        bmis = [p.bmi for p in self.patients]
        
        if ages and bmis:
            ax.scatter(ages, bmis, alpha=0.5)
            ax.set_title("Зависимость ИМТ от возраста")
            ax.set_xlabel("Возраст")
            ax.set_ylabel("ИМТ")
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Зависимость ИМТ от возраста")