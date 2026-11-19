import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import json
import math
from pathlib import Path

# імпортуємо математичні метрики
from metrics import calculate_mse, calculate_psnr, calculate_ssim

# імпортуємо модулі для збереження результатів
import csv
from datetime import datetime

# визначаємо папку проєкту
BASE_DIR = Path(__file__).resolve().parent

# визначаємо шлях до конфігураційного файлу
CONFIG_PATH = BASE_DIR / "config.json"


# функція завантаження налаштувань
def load_config():

    # стандартні значення параметрів
    default_config = {
        "brightness": 30,
        "threshold": 128,
        "morphology_operation": "Ерозія",
        "morphology_size": 3
    }

    # якщо файл налаштувань відсутній
    if not CONFIG_PATH.exists():
        return default_config

    try:

        # відкриваємо конфігураційний файл
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)

        # отримуємо значення параметрів
        brightness_value = int(config.get("brightness", 30))
        threshold_value = int(config.get("threshold", 128))
        operation = config.get("morphology_operation", "Ерозія")
        size = int(config.get("morphology_size", 3))

        # перевіряємо значення яскравості
        if not -100 <= brightness_value <= 100:
            raise ValueError("Яскравість має бути від -100 до 100")

        # перевіряємо значення порога
        if not 0 <= threshold_value <= 255:
            raise ValueError("Поріг має бути від 0 до 255")

        # перевіряємо морфологічну операцію
        if operation not in ["Ерозія", "Дилатація"]:
            raise ValueError("Невідома морфологічна операція")

        # перевіряємо розмір вікна
        if size not in [3, 5]:
            raise ValueError("Розмір вікна має бути 3 або 5")

        # повертаємо налаштування
        return {
            "brightness": brightness_value,
            "threshold": threshold_value,
            "morphology_operation": operation,
            "morphology_size": size
        }

    except (OSError, ValueError, TypeError) as error:

        # повідомляємо про помилку
        print(f"Помилка конфігурації: {error}")

        # використовуємо стандартні параметри
        return default_config


# завантажуємо налаштування
config = load_config()


# створюємо головне вікно програми
window = tk.Tk()

# задаємо назву вікна
window.title("STEM Image Processing")

# задаємо розмір вікна
window.geometry("1100x850")

# встановлюємо колір фону
window.configure(bg="#f5f5f5")


# змінні для зберігання зображень
original_image = None
processed_image = None
original_photo = None
processed_photo = None


# перший алгоритм: перетворення у відтінки сірого
def grayscale(image):

    # отримуємо ширину та висоту зображення
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо всі пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо складові кольору
            r, g, b = image.getpixel((x, y))

            # обчислюємо яскравість пікселя
            gray = round(
                0.299 * r +
                0.587 * g +
                0.114 * b
            )

            # записуємо сірий піксель
            result.putpixel(
                (x, y),
                (gray, gray, gray)
            )

    # повертаємо оброблене зображення
    return result


# другий алгоритм: корекція яскравості
def brightness(image, value):

    # отримуємо розміри зображення
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо всі пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо кольорові складові
            r, g, b = image.getpixel((x, y))

            # змінюємо червону складову
            new_r = max(0, min(255, r + value))

            # змінюємо зелену складову
            new_g = max(0, min(255, g + value))

            # змінюємо синю складову
            new_b = max(0, min(255, b + value))

            # записуємо новий піксель
            result.putpixel(
                (x, y),
                (new_r, new_g, new_b)
            )

    # повертаємо результат
    return result


# третій алгоритм: гістограмне вирівнювання
def histogram_equalization(image):

    # перетворюємо зображення у відтінки сірого
    gray_image = grayscale(image)

    # отримуємо ширину та висоту
    width, height = gray_image.size

    # створюємо гістограму з 256 значень
    histogram = [0] * 256

    # підраховуємо кількість пікселів кожної яскравості
    for y in range(height):
        for x in range(width):

            # отримуємо яскравість пікселя
            gray = gray_image.getpixel((x, y))[0]

            # збільшуємо відповідне значення гістограми
            histogram[gray] += 1

    # створюємо накопичену гістограму
    cdf = [0] * 256

    # змінна для накопичення кількості пікселів
    total = 0

    # обчислюємо накопичену гістограму
    for i in range(256):

        total += histogram[i]

        cdf[i] = total

    # знаходимо перше ненульове значення
    cdf_min = next(
        (value for value in cdf if value > 0),
        0
    )

    # обчислюємо загальну кількість пікселів
    pixels_count = width * height

    # якщо всі пікселі мають однакову яскравість
    if pixels_count == cdf_min:
        return gray_image

    # створюємо таблицю перетворення
    lookup_table = [0] * 256

    # обчислюємо нову яскравість для кожного рівня
    for i in range(256):

        new_value = round(
            255 * (cdf[i] - cdf_min) /
            (pixels_count - cdf_min)
        )

        # обмежуємо значення від 0 до 255
        lookup_table[i] = max(0, min(255, new_value))

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # змінюємо яскравість усіх пікселів
    for y in range(height):
        for x in range(width):

            # отримуємо початкову яскравість
            gray = gray_image.getpixel((x, y))[0]

            # знаходимо нову яскравість
            new_gray = lookup_table[gray]

            # записуємо результат
            result.putpixel(
                (x, y),
                (new_gray, new_gray, new_gray)
            )

    return result


# четвертий алгоритм: порогова сегментація
def threshold_segmentation(image, threshold):

    # перетворюємо зображення у відтінки сірого
    gray_image = grayscale(image)

    # отримуємо розміри зображення
    width, height = gray_image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо всі пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо яскравість пікселя
            gray = gray_image.getpixel((x, y))[0]

            # порівнюємо яскравість із порогом
            if gray < threshold:

                # робимо піксель чорним
                new_gray = 0

            else:

                # робимо піксель білим
                new_gray = 255

            # записуємо новий піксель
            result.putpixel(
                (x, y),
                (new_gray, new_gray, new_gray)
            )

    return result


# п'ятий алгоритм: морфологічна обробка
def morphology(image, operation, size):

    # перевіряємо правильність параметрів
    if operation not in ["Ерозія", "Дилатація"]:
        raise ValueError("Невідома морфологічна операція")

    if size not in [3, 5]:
        raise ValueError("Розмір вікна має бути 3 або 5")

    # перетворюємо зображення у відтінки сірого
    gray_image = grayscale(image)

    # отримуємо розміри зображення
    width, height = gray_image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # обчислюємо радіус вікна
    radius = size // 2

    # перебираємо всі пікселі зображення
    for y in range(height):
        for x in range(width):

            # створюємо список значень сусідніх пікселів
            neighbors = []

            # перебираємо рядки вікна
            for dy in range(-radius, radius + 1):

                # перебираємо стовпці вікна
                for dx in range(-radius, radius + 1):

                    # обчислюємо координати сусіднього пікселя
                    nx = x + dx
                    ny = y + dy

                    # перевіряємо межі зображення
                    if 0 <= nx < width and 0 <= ny < height:

                        # отримуємо яскравість сусіда
                        gray = gray_image.getpixel((nx, ny))[0]

                        # додаємо значення до списку
                        neighbors.append(gray)

            # виконуємо ерозію
            if operation == "Ерозія":

                # вибираємо мінімальну яскравість
                new_gray = min(neighbors)

            # виконуємо дилатацію
            else:

                # вибираємо максимальну яскравість
                new_gray = max(neighbors)

            # записуємо результат
            result.putpixel(
                (x, y),
                (new_gray, new_gray, new_gray)
            )

    return result


# функція відображення зображення
def show_image(image, label):

    # створюємо копію
    preview = image.copy()

    # зменшуємо копію для вікна
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

    # якщо користувач не вибрав файл
    if not file_path:
        return

    try:

        # відкриваємо зображення
        with Image.open(file_path) as image:
            original_image = image.convert("RGB")

        # відображаємо оригінальне зображення
        original_photo = show_image(
            original_image,
            original_label
        )

        # очищаємо попередній результат
        processed_image = None
        processed_photo = None

        processed_label.config(
            image="",
            text="Результат обробки"
        )

        processed_label.image = None

    except (OSError, ValueError) as error:

        messagebox.showerror(
            "Помилка",
            f"Не вдалося відкрити зображення:\n{error}"
        )
# функція автоматичного збереження результатів
def save_experiment(image, method, mse, psnr, ssim):

    # створюємо папку результатів
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    # створюємо унікальну назву запуску
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # формуємо шлях до зображення
    image_path = output_dir / f"result_{timestamp}.png"

    # зберігаємо оброблене зображення
    image.save(image_path)

    # визначаємо шлях до CSV-файлу
    csv_path = output_dir / "metrics.csv"

    # перевіряємо, чи існує файл
    file_exists = csv_path.exists() and csv_path.stat().st_size > 0

    # відкриваємо файл для додавання результатів
    with open(csv_path, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        # записуємо заголовки під час першого запуску
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

    # перевіряємо наявність зображення
    if original_image is None:

        messagebox.showwarning(
            "Увага",
            "Спочатку завантажте зображення!"
        )
        return

    # отримуємо вибраний метод
    method = selected_method.get()

    try:

        # перший метод
        if method == "Відтінки сірого":

            processed_image = grayscale(
                original_image
            )

        # другий метод
        elif method == "Корекція яскравості":

            # отримуємо значення повзунка
            value = int(brightness_slider.get())

            # застосовуємо алгоритм
            processed_image = brightness(
                original_image,
                value
            )

        # третій метод
        elif method == "Гістограмне вирівнювання":

            processed_image = histogram_equalization(
                original_image
            )

        # четвертий метод
        elif method == "Порогова сегментація":

            # отримуємо значення порога
            threshold_value = int(threshold_slider.get())

            # застосовуємо алгоритм
            processed_image = threshold_segmentation(
                original_image,
                threshold_value
            )

        # п'ятий метод
        elif method == "Морфологічна обробка":

            # отримуємо вибрану операцію
            operation = selected_operation.get()

            # отримуємо розмір вікна
            size = int(selected_size.get())

            # застосовуємо морфологічну обробку
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

        # показуємо оброблене зображення
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

        # обчислюємо глобальний SSIM
        ssim = calculate_ssim(
            original_image,
            processed_image
        )

        # формуємо текст із результатами
        psnr_text = "∞" if math.isinf(psnr) else f"{psnr:.2f}"

        metrics_text = (
            f"MSE: {mse:.2f}   |   "
            f"PSNR: {psnr_text} dB   |   "
            f"Global SSIM: {ssim:.4f}"
        )

        # показуємо метрики у вікні
        metrics_label.config(text=metrics_text)

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


# функція збереження результату
def save_image():

    # перевіряємо, чи є результат
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

# встановлюємо значення з конфігурації
brightness_slider.set(config["brightness"])

brightness_slider.grid(
    row=0,
    column=1,
    padx=10
)


# підпис порогової сегментації
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

# встановлюємо значення з конфігурації
threshold_slider.set(config["threshold"])

threshold_slider.grid(
    row=1,
    column=1,
    padx=10
)


# створюємо панель морфологічної обробки
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


# створюємо область для зображень
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

# створюємо підпис для математичних метрик
metrics_label = tk.Label(
    window,
    text="MSE: —   |   PSNR: —   |   Global SSIM: —",
    font=("Arial", 13, "bold"),
    bg="#f5f5f5",
    fg="#333333"
)

# розміщуємо метрики під зображеннями
metrics_label.pack(pady=10)


# запускаємо головний цикл програми
window.mainloop()