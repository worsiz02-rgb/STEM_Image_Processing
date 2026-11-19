import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import json
from pathlib import Path


# визначаємо папку проєкту
BASE_DIR = Path(__file__).resolve().parent

# визначаємо шлях до конфігураційного файлу
CONFIG_PATH = BASE_DIR / "config.json"


# функція завантаження налаштувань
def load_config():

    # стандартні значення параметрів
    default_config = {
        "brightness": 30,
        "threshold": 128
    }

    # якщо файл відсутній
    if not CONFIG_PATH.exists():
        return default_config

    try:

        # відкриваємо файл налаштувань
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)

        # зчитуємо параметри
        brightness_value = int(config.get("brightness", 30))
        threshold_value = int(config.get("threshold", 128))

        # перевіряємо значення яскравості
        if not -100 <= brightness_value <= 100:
            raise ValueError("Яскравість має бути від -100 до 100")

        # перевіряємо значення порога
        if not 0 <= threshold_value <= 255:
            raise ValueError("Поріг має бути від 0 до 255")

        return {
            "brightness": brightness_value,
            "threshold": threshold_value
        }

    except (OSError, ValueError, TypeError) as error:

        # повідомляємо про помилку
        print(f"Помилка конфігурації: {error}")

        # повертаємо стандартні параметри
        return default_config


# завантажуємо параметри
config = load_config()


# створюємо головне вікно
window = tk.Tk()

# задаємо назву програми
window.title("STEM Image Processing")

# задаємо розмір вікна
window.geometry("1100x800")

# встановлюємо колір фону
window.configure(bg="#f5f5f5")


# змінні для зберігання зображень
original_image = None
processed_image = None
original_photo = None
processed_photo = None


# перший алгоритм: відтінки сірого
def grayscale(image):

    # отримуємо розміри зображення
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо складові кольору
            r, g, b = image.getpixel((x, y))

            # обчислюємо яскравість
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

    return result


# другий алгоритм: корекція яскравості
def brightness(image, value):

    # отримуємо ширину та висоту
    width, height = image.size

    # створюємо нове зображення
    result = Image.new("RGB", (width, height))

    # перебираємо пікселі
    for y in range(height):
        for x in range(width):

            # отримуємо складові кольору
            r, g, b = image.getpixel((x, y))

            # змінюємо значення каналів
            new_r = max(0, min(255, r + value))
            new_g = max(0, min(255, g + value))
            new_b = max(0, min(255, b + value))

            # записуємо новий піксель
            result.putpixel(
                (x, y),
                (new_r, new_g, new_b)
            )

    return result


# третій алгоритм: гістограмне вирівнювання
def histogram_equalization(image):

    # перетворюємо зображення у відтінки сірого
    gray_image = grayscale(image)

    # отримуємо розміри
    width, height = gray_image.size

    # створюємо гістограму
    histogram = [0] * 256

    # підраховуємо кількість пікселів кожної яскравості
    for y in range(height):
        for x in range(width):

            gray = gray_image.getpixel((x, y))[0]

            histogram[gray] += 1

    # створюємо накопичену гістограму
    cdf = [0] * 256

    total = 0

    # обчислюємо накопичену кількість пікселів
    for i in range(256):

        total += histogram[i]

        cdf[i] = total

    # знаходимо перше ненульове значення
    cdf_min = next(
        (value for value in cdf if value > 0),
        0
    )

    # обчислюємо кількість пікселів
    pixels_count = width * height

    # якщо всі пікселі мають однакову яскравість
    if pixels_count == cdf_min:
        return gray_image

    # створюємо таблицю нових значень
    lookup_table = [0] * 256

    # обчислюємо нову яскравість
    for i in range(256):

        new_value = round(
            255 * (cdf[i] - cdf_min) /
            (pixels_count - cdf_min)
        )

        lookup_table[i] = max(0, min(255, new_value))

    # створюємо результат
    result = Image.new("RGB", (width, height))

    # змінюємо яскравість кожного пікселя
    for y in range(height):
        for x in range(width):

            gray = gray_image.getpixel((x, y))[0]

            new_gray = lookup_table[gray]

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

    # повертаємо результат
    return result


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

    # перевіряємо, чи вибрано файл
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

    # перший метод
    if method == "Відтінки сірого":

        processed_image = grayscale(
            original_image
        )

    # другий метод
    elif method == "Корекція яскравості":

        value = int(brightness_slider.get())

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

        # застосовуємо порогову сегментацію
        processed_image = threshold_segmentation(
            original_image,
            threshold_value
        )

    # п'ятий метод поки не реалізовано
    else:

        messagebox.showinfo(
            "Інформація",
            "Цей алгоритм реалізуємо пізніше."
        )
        return

    # показуємо результат
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

    # відкриваємо вікно збереження
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("BMP", "*.bmp")
        ]
    )

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


# список методів
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


# панель налаштувань
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


# повзунок порогової сегментації
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


# область результату
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


# запускаємо програму
window.mainloop()