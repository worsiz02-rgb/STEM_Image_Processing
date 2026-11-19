import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
from datetime import datetime

import json
import csv
import math

# імпортуємо п'ять алгоритмів обробки зображень
from algorithms import (
    grayscale,
    brightness,
    histogram_equalization,
    threshold_segmentation,
    morphology
)

# імпортуємо математичні метрики
from metrics import (
    calculate_mse,
    calculate_psnr,
    calculate_ssim
)


# визначаємо папку проєкту
BASE_DIR = Path(__file__).resolve().parent

# визначаємо шлях до конфігураційного файлу
CONFIG_PATH = BASE_DIR / "config.json"

# визначаємо папку для збереження результатів
OUTPUT_DIR = BASE_DIR / "output"


# функція завантаження налаштувань
def load_config():

    # стандартні параметри програми
    default_config = {
        "brightness": 30,
        "threshold": 128,
        "morphology_operation": "Ерозія",
        "morphology_size": 3
    }

    # якщо файл конфігурації відсутній
    if not CONFIG_PATH.exists():
        return default_config

    try:

        # відкриваємо конфігураційний файл
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)

        # отримуємо параметри
        brightness_value = int(config.get("brightness", 30))
        threshold_value = int(config.get("threshold", 128))
        operation = config.get("morphology_operation", "Ерозія")
        size = int(config.get("morphology_size", 3))

        # перевіряємо діапазон яскравості
        if not -100 <= brightness_value <= 100:
            raise ValueError("Яскравість має бути від -100 до 100")

        # перевіряємо діапазон порога
        if not 0 <= threshold_value <= 255:
            raise ValueError("Поріг має бути від 0 до 255")

        # перевіряємо морфологічну операцію
        if operation not in ["Ерозія", "Дилатація"]:
            raise ValueError("Невідома морфологічна операція")

        # перевіряємо розмір вікна
        if size not in [3, 5]:
            raise ValueError("Розмір вікна має бути 3 або 5")

        # повертаємо параметри
        return {
            "brightness": brightness_value,
            "threshold": threshold_value,
            "morphology_operation": operation,
            "morphology_size": size
        }

    except (OSError, ValueError, TypeError) as error:

        # повідомляємо про помилку
        print(f"Помилка конфігурації: {error}")

        # використовуємо стандартні значення
        return default_config


# завантажуємо налаштування
config = load_config()


# створюємо головне вікно програми
window = tk.Tk()

# встановлюємо назву вікна
window.title("STEM Image Processing")

# встановлюємо розмір вікна
window.geometry("1100x850")

# встановлюємо колір фону
window.configure(bg="#f5f5f5")


# змінні для зберігання зображень
original_image = None
processed_image = None

# змінні для відображення зображень
original_photo = None
processed_photo = None


# функція відображення зображення
def show_image(image, label):

    # створюємо копію зображення
    preview = image.copy()

    # зменшуємо копію для перегляду
    preview.thumbnail((450, 400))

    # перетворюємо зображення для tkinter
    photo = ImageTk.PhotoImage(preview)

    # відображаємо зображення
    label.config(
        image=photo,
        text=""
    )

    # зберігаємо посилання на зображення
    label.image = photo

    return photo


# функція завантаження зображення
def load_image():

    global original_image, processed_image
    global original_photo, processed_photo

    # відкриваємо вікно вибору файлу
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Зображення", "*.png *.jpg *.jpeg *.bmp")
        ]
    )

    # якщо файл не вибрано
    if not file_path:
        return

    try:

        # відкриваємо зображення
        with Image.open(file_path) as image:
            original_image = image.convert("RGB")

        # показуємо оригінал
        original_photo = show_image(
            original_image,
            original_label
        )

        # очищаємо попередній результат
        processed_image = None
        processed_photo = None

        # очищаємо область результату
        processed_label.config(
            image="",
            text="Результат обробки"
        )

        processed_label.image = None

        # очищаємо попередні метрики
        metrics_label.config(
            text="MSE: —   |   PSNR: —   |   Global SSIM: —"
        )

    except (OSError, ValueError) as error:

        messagebox.showerror(
            "Помилка",
            f"Не вдалося відкрити зображення:\n{error}"
        )


# функція автоматичного збереження результатів
def save_experiment(image, method, mse, psnr, ssim):

    # створюємо папку результатів
    OUTPUT_DIR.mkdir(exist_ok=True)

    # формуємо унікальну назву запуску
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # визначаємо шлях до зображення
    image_path = OUTPUT_DIR / f"result_{timestamp}.png"

    # зберігаємо оброблене зображення
    image.save(image_path)

    # визначаємо шлях до CSV-файлу
    csv_path = OUTPUT_DIR / "metrics.csv"

    # перевіряємо, чи існує таблиця результатів
    file_exists = (
        csv_path.exists() and
        csv_path.stat().st_size > 0
    )

    # відкриваємо CSV-файл
    with open(
        csv_path,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # записуємо заголовки, якщо файл новий
        if not file_exists:

            writer.writerow([
                "datetime",
                "method",
                "image_path",
                "mse",
                "psnr",
                "global_ssim"
            ])

        # записуємо результати експерименту
        writer.writerow([
            timestamp,
            method,
            image_path.name,
            mse,
            psnr,
            ssim
        ])

    return image_path


# функція обробки зображення
def process_image():

    global processed_image, processed_photo

    # перевіряємо, чи завантажено зображення
    if original_image is None:

        messagebox.showwarning(
            "Увага",
            "Спочатку завантажте зображення!"
        )
        return

    # отримуємо вибраний метод
    method = selected_method.get()

    try:

        # перший алгоритм: відтінки сірого
        if method == "Відтінки сірого":

            processed_image = grayscale(
                original_image
            )

        # другий алгоритм: корекція яскравості
        elif method == "Корекція яскравості":

            # отримуємо значення повзунка
            value = int(brightness_slider.get())

            # застосовуємо алгоритм
            processed_image = brightness(
                original_image,
                value
            )

        # третій алгоритм: гістограмне вирівнювання
        elif method == "Гістограмне вирівнювання":

            processed_image = histogram_equalization(
                original_image
            )

        # четвертий алгоритм: порогова сегментація
        elif method == "Порогова сегментація":

            # отримуємо значення порога
            threshold_value = int(threshold_slider.get())

            # застосовуємо алгоритм
            processed_image = threshold_segmentation(
                original_image,
                threshold_value
            )

        # п'ятий алгоритм: морфологічна обробка
        elif method == "Морфологічна обробка":

            # отримуємо вибрану операцію
            operation = selected_operation.get()

            # отримуємо розмір вікна
            size = int(selected_size.get())

            # застосовуємо алгоритм
            processed_image = morphology(
                original_image,
                operation,
                size
            )

        # якщо метод не знайдено
        else:

            messagebox.showerror(
                "Помилка",
                "Невідомий метод обробки."
            )
            return

        # відображаємо результат
        processed_photo = show_image(
            processed_image,
            processed_label
        )

        # обчислюємо MSE
        mse = calculate_mse(
            original_image,
            processed_image
        )

        # обчислюємо PSNR
        psnr = calculate_psnr(
            original_image,
            processed_image
        )

        # обчислюємо Global SSIM
        ssim = calculate_ssim(
            original_image,
            processed_image
        )

        # формуємо текст PSNR
        if math.isinf(psnr):
            psnr_text = "∞"
        else:
            psnr_text = f"{psnr:.2f}"

        # формуємо рядок з метриками
        metrics_text = (
            f"MSE: {mse:.2f}   |   "
            f"PSNR: {psnr_text} dB   |   "
            f"Global SSIM: {ssim:.4f}"
        )

        # відображаємо метрики у вікні
        metrics_label.config(
            text=metrics_text
        )

        # автоматично зберігаємо результати
        save_experiment(
            processed_image,
            method,
            mse,
            psnr,
            ssim
        )

    except (ValueError, OSError) as error:

        # повідомляємо про помилку обробки
        messagebox.showerror(
            "Помилка",
            f"Не вдалося обробити зображення:\n{error}"
        )


# функція ручного збереження зображення
def save_image():

    # перевіряємо наявність результату
    if processed_image is None:

        messagebox.showwarning(
            "Увага",
            "Спочатку обробіть зображення!"
        )
        return

    # відкриваємо вікно збереження
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("BMP", "*.bmp")
        ]
    )

    # якщо користувач вибрав шлях
    if file_path:

        try:

            # зберігаємо зображення
            processed_image.save(file_path)

            messagebox.showinfo(
                "Успіх",
                "Зображення успішно збережено!"
            )

        except OSError as error:

            messagebox.showerror(
                "Помилка",
                f"Не вдалося зберегти файл:\n{error}"
            )


# створюємо заголовок програми
title = tk.Label(
    window,
    text="Обробка зображень текстових документів",
    font=("Arial", 20, "bold"),
    bg="#f5f5f5"
)

title.pack(pady=15)


# створюємо панель керування
control_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

control_frame.pack(pady=10)


# кнопка завантаження
load_button = tk.Button(
    control_frame,
    text="Завантажити зображення",
    command=load_image,
    width=22
)

load_button.grid(
    row=0,
    column=0,
    padx=10
)


# список методів обробки
methods = [
    "Відтінки сірого",
    "Корекція яскравості",
    "Гістограмне вирівнювання",
    "Порогова сегментація",
    "Морфологічна обробка"
]


# змінна вибраного методу
selected_method = tk.StringVar(
    value=methods[0]
)


# створюємо випадний список
method_menu = ttk.Combobox(
    control_frame,
    textvariable=selected_method,
    values=methods,
    state="readonly",
    width=27
)

method_menu.grid(
    row=0,
    column=1,
    padx=10
)


# кнопка обробки
process_button = tk.Button(
    control_frame,
    text="Обробити",
    command=process_image,
    width=15
)

process_button.grid(
    row=0,
    column=2,
    padx=10
)


# кнопка збереження
save_button = tk.Button(
    control_frame,
    text="Зберегти",
    command=save_image,
    width=15
)

save_button.grid(
    row=0,
    column=3,
    padx=10
)


# створюємо панель налаштувань
settings_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

settings_frame.pack(pady=10)


# підпис яскравості
brightness_label = tk.Label(
    settings_frame,
    text="Яскравість:",
    font=("Arial", 12),
    bg="#f5f5f5"
)

brightness_label.grid(
    row=0,
    column=0,
    padx=10
)


# повзунок яскравості
brightness_slider = tk.Scale(
    settings_frame,
    from_=-100,
    to=100,
    orient="horizontal",
    length=300,
    bg="#f5f5f5"
)

brightness_slider.set(
    config["brightness"]
)

brightness_slider.grid(
    row=0,
    column=1,
    padx=10
)


# підпис порога
threshold_label = tk.Label(
    settings_frame,
    text="Поріг:",
    font=("Arial", 12),
    bg="#f5f5f5"
)

threshold_label.grid(
    row=1,
    column=0,
    padx=10
)


# повзунок порога
threshold_slider = tk.Scale(
    settings_frame,
    from_=0,
    to=255,
    orient="horizontal",
    length=300,
    bg="#f5f5f5"
)

threshold_slider.set(
    config["threshold"]
)

threshold_slider.grid(
    row=1,
    column=1,
    padx=10
)


# панель морфологічної обробки
morphology_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

morphology_frame.pack(pady=5)


# підпис морфологічної операції
operation_label = tk.Label(
    morphology_frame,
    text="Морфологічна операція:",
    bg="#f5f5f5",
    font=("Arial", 12)
)

operation_label.grid(
    row=0,
    column=0,
    padx=10
)


# змінна вибраної операції
selected_operation = tk.StringVar(
    value=config["morphology_operation"]
)


# список морфологічних операцій
operation_menu = ttk.Combobox(
    morphology_frame,
    textvariable=selected_operation,
    values=["Ерозія", "Дилатація"],
    state="readonly",
    width=15
)

operation_menu.grid(
    row=0,
    column=1,
    padx=10
)


# підпис розміру вікна
size_label = tk.Label(
    morphology_frame,
    text="Розмір вікна:",
    bg="#f5f5f5",
    font=("Arial", 12)
)

size_label.grid(
    row=0,
    column=2,
    padx=10
)


# змінна розміру вікна
selected_size = tk.StringVar(
    value=str(config["morphology_size"])
)


# список розмірів вікна
size_menu = ttk.Combobox(
    morphology_frame,
    textvariable=selected_size,
    values=["3", "5"],
    state="readonly",
    width=5
)

size_menu.grid(
    row=0,
    column=3,
    padx=10
)


# створюємо область зображень
images_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

images_frame.pack(pady=10)


# область оригінального зображення
original_frame = tk.LabelFrame(
    images_frame,
    text="Оригінальне зображення",
    font=("Arial", 13, "bold"),
    bg="white",
    width=480,
    height=450
)

original_frame.grid(
    row=0,
    column=0,
    padx=15
)

original_frame.pack_propagate(False)


# область результату обробки
processed_frame = tk.LabelFrame(
    images_frame,
    text="Результат обробки",
    font=("Arial", 13, "bold"),
    bg="white",
    width=480,
    height=450
)

processed_frame.grid(
    row=0,
    column=1,
    padx=15
)

processed_frame.pack_propagate(False)


# підпис оригінального зображення
original_label = tk.Label(
    original_frame,
    text="Завантажте зображення",
    bg="white",
    font=("Arial", 12)
)

original_label.pack(expand=True)


# підпис обробленого зображення
processed_label = tk.Label(
    processed_frame,
    text="Результат обробки",
    bg="white",
    font=("Arial", 12)
)

processed_label.pack(expand=True)


# створюємо підпис математичних метрик
metrics_label = tk.Label(
    window,
    text="MSE: —   |   PSNR: —   |   Global SSIM: —",
    font=("Arial", 13, "bold"),
    bg="#f5f5f5",
    fg="#333333"
)

metrics_label.pack(pady=10)


# запускаємо головний цикл програми
window.mainloop()