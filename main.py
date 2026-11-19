import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import json
from pathlib import Path


# визначаємо папку, в якій знаходиться програма
BASE_DIR = Path(__file__).resolve().parent

# визначаємо шлях до файлу налаштувань
CONFIG_PATH = BASE_DIR / "config.json"


# функція завантаження налаштувань
def load_config():

    # стандартне значення яскравості
    default_config = {"brightness": 30}

    # якщо файл налаштувань відсутній
    if not CONFIG_PATH.exists():
        return default_config

    try:

        # відкриваємо файл налаштувань
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)

        # отримуємо значення яскравості
        brightness = int(config.get("brightness", 30))

        # перевіряємо допустимий діапазон
        if not -100 <= brightness <= 100:
            raise ValueError("Яскравість має бути від -100 до 100")

        return {"brightness": brightness}

    except (OSError, ValueError, TypeError) as error:

        # повідомляємо про помилку налаштувань
        print(f"Помилка конфігурації: {error}")

        # використовуємо стандартні налаштування
        return default_config


# завантажуємо налаштування
config = load_config()


# створюємо головне вікно
window = tk.Tk()

# задаємо назву програми
window.title("STEM Image Processing")

# задаємо розмір вікна
window.geometry("1100x750")

# встановлюємо колір фону
window.configure(bg="#f5f5f5")


# змінні для збереження зображень
original_image = None
processed_image = None
original_photo = None
processed_photo = None


# перший алгоритм: перетворення у відтінки сірого
def grayscale(image):

    # отримуємо ширину та висоту
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо всі пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо складові пікселя
            r, g, b = image.getpixel((x, y))

            # обчислюємо яскравість
            gray = round(
                0.299 * r +
                0.587 * g +
                0.114 * b
            )

            # записуємо значення пікселя
            result.putpixel(
                (x, y),
                (gray, gray, gray)
            )

    # повертаємо результат
    return result


# другий алгоритм: корекція яскравості
def brightness(image, value):

    # отримуємо ширину та висоту
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо всі пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо складові кольору
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

    # повертаємо оброблене зображення
    return result


# функція відображення зображення
def show_image(image, label):

    # створюємо копію
    preview = image.copy()

    # зменшуємо копію для вікна
    preview.thumbnail((450, 400))

    # створюємо об'єкт для tkinter
    photo = ImageTk.PhotoImage(preview)

    # показуємо зображення
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

        processed_label.config(
            image="",
            text="Результат обробки"
        )

        processed_label.image = None

    except (OSError, ValueError) as error:

        messagebox.showerror(
            "Помилка",
            f"Не вдалося відкрити файл:\n{error}"
        )


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

    # перетворення у відтінки сірого
    if method == "Відтінки сірого":

        processed_image = grayscale(
            original_image
        )

    # корекція яскравості
    elif method == "Корекція яскравості":

        # отримуємо значення повзунка
        value = int(brightness_slider.get())

        # застосовуємо алгоритм
        processed_image = brightness(
            original_image,
            value
        )

    # інші алгоритми ще не реалізовані
    else:

        messagebox.showinfo(
            "Інформація",
            "Цей алгоритм реалізуємо пізніше."
        )
        return

    # відображаємо результат
    processed_photo = show_image(
        processed_image,
        processed_label
    )


# функція збереження зображення
def save_image():

    # перевіряємо наявність результату
    if processed_image is None:

        messagebox.showwarning(
            "Увага",
            "Спочатку обробіть зображення!"
        )
        return

    # вибираємо місце збереження
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("BMP", "*.bmp")
        ]
    )

    # якщо шлях вибрано
    if file_path:

        try:

            # зберігаємо результат
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


# створюємо заголовок
title = tk.Label(
    window,
    text="Обробка зображень текстових документів",
    font=("Arial", 20, "bold"),
    bg="#f5f5f5"
)

title.pack(pady=20)


# створюємо панель керування
control_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

control_frame.pack(pady=15)


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

# випадний список
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


# створюємо блок налаштування яскравості
settings_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

settings_frame.pack(pady=10)


# підпис повзунка
brightness_label = tk.Label(
    settings_frame,
    text="Яскравість:",
    font=("Arial", 12),
    bg="#f5f5f5"
)

brightness_label.pack(side="left", padx=10)


# створюємо повзунок
brightness_slider = tk.Scale(
    settings_frame,
    from_=-100,
    to=100,
    orient="horizontal",
    length=350,
    bg="#f5f5f5"
)

# встановлюємо значення з конфігурації
brightness_slider.set(config["brightness"])

brightness_slider.pack(side="left")


# створюємо область зображень
images_frame = tk.Frame(
    window,
    bg="#f5f5f5"
)

images_frame.pack(pady=15)


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


# підпис результату
processed_label = tk.Label(
    processed_frame,
    text="Результат обробки",
    bg="white",
    font=("Arial", 12)
)

processed_label.pack(expand=True)


# запускаємо програму
window.mainloop()