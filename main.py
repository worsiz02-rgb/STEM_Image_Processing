import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

# створюємо головне вікно програми
window = tk.Tk()
window.title("STEM Image Processing")
window.geometry("1100x750")
window.configure(bg="#f5f5f5")

# змінні для зберігання зображень
original_image = None
processed_image = None
original_photo = None
processed_photo = None

# створюємо заголовок програми
title = tk.Label(
    window,
    text="Обробка зображень текстових документів",
    font=("Arial", 20, "bold"),
    bg="#f5f5f5"
)
title.pack(pady=20)

# функція завантаження зображення
def load_image():
    global original_image, original_photo, processed_image, processed_photo

    # відкриваємо вікно вибору файлу
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Зображення", "*.png *.jpg *.jpeg *.bmp")
        ]
    )

    # якщо користувач не вибрав файл, завершуємо функцію
    if not file_path:
        return

    try:
        # відкриваємо зображення
        with Image.open(file_path) as image:
            original_image = image.convert("RGB")

        # зменшуємо копію для відображення у вікні
        preview = original_image.copy()
        preview.thumbnail((450, 400))

        # перетворюємо зображення для tkinter
        original_photo = ImageTk.PhotoImage(preview)

        # показуємо оригінальне зображення
        original_label.config(image=original_photo, text="")

        # очищаємо попередній результат
        processed_image = None
        processed_photo = None
        processed_label.config(image="", text="Результат обробки")

    except (OSError, ValueError) as error:
        messagebox.showerror(
            "Помилка",
            f"Не вдалося відкрити зображення:\n{error}"
        )

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

    # поки що створюємо копію оригіналу
    processed_image = original_image.copy()

    # створюємо зменшену копію для перегляду
    preview = processed_image.copy()
    preview.thumbnail((450, 400))

    # перетворюємо зображення для tkinter
    processed_photo = ImageTk.PhotoImage(preview)

    # показуємо результат
    processed_label.config(image=processed_photo, text="")

    messagebox.showinfo(
        "Інформація",
        "Інтерфейс працює! Алгоритми додамо наступним кроком."
    )

# функція збереження результату
def save_image():
    if processed_image is None:
        messagebox.showwarning(
            "Увага",
            "Спочатку обробіть зображення!"
        )
        return

    # вибираємо місце збереження
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("BMP", "*.bmp")]
    )

    if file_path:
        try:
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

# створюємо панель керування
control_frame = tk.Frame(window, bg="#f5f5f5")
control_frame.pack(pady=15)

# кнопка завантаження
load_button = tk.Button(
    control_frame,
    text="Завантажити зображення",
    command=load_image,
    width=22
)
load_button.grid(row=0, column=0, padx=10)

# список методів обробки
methods = [
    "Відтінки сірого",
    "Корекція яскравості",
    "Гістограмне вирівнювання",
    "Порогова сегментація",
    "Морфологічна обробка"
]

selected_method = tk.StringVar(value=methods[0])

method_menu = ttk.Combobox(
    control_frame,
    textvariable=selected_method,
    values=methods,
    state="readonly",
    width=27
)
method_menu.grid(row=0, column=1, padx=10)

# кнопка обробки
process_button = tk.Button(
    control_frame,
    text="Обробити",
    command=process_image,
    width=15
)
process_button.grid(row=0, column=2, padx=10)

# кнопка збереження
save_button = tk.Button(
    control_frame,
    text="Зберегти",
    command=save_image,
    width=15
)
save_button.grid(row=0, column=3, padx=10)

# створюємо область для двох зображень
images_frame = tk.Frame(window, bg="#f5f5f5")
images_frame.pack(pady=25)

# створюємо область оригіналу
original_frame = tk.LabelFrame(
    images_frame,
    text="Оригінальне зображення",
    font=("Arial", 13, "bold"),
    bg="white",
    width=480,
    height=450
)
original_frame.grid(row=0, column=0, padx=15)
original_frame.pack_propagate(False)

# створюємо область результату
processed_frame = tk.LabelFrame(
    images_frame,
    text="Результат обробки",
    font=("Arial", 13, "bold"),
    bg="white",
    width=480,
    height=450
)
processed_frame.grid(row=0, column=1, padx=15)
processed_frame.pack_propagate(False)

# підпис для оригінального зображення
original_label = tk.Label(
    original_frame,
    text="Завантажте зображення",
    bg="white",
    font=("Arial", 12)
)
original_label.pack(expand=True)

# підпис для обробленого зображення
processed_label = tk.Label(
    processed_frame,
    text="Результат обробки",
    bg="white",
    font=("Arial", 12)
)
processed_label.pack(expand=True)

# запускаємо програму
window.mainloop()