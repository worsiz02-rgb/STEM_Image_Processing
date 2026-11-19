import csv
import json
import time
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from algorithms import (
    grayscale,
    brightness,
    histogram_equalization,
    threshold_segmentation,
    morphology
)

from metrics import (
    calculate_mse,
    calculate_psnr,
    calculate_ssim
)


# визначаємо головну папку проєкту
PROJECT_DIR = Path(__file__).resolve().parent

# задаємо папку з тестовими зображеннями
DATASET_DIR = PROJECT_DIR / "dataset"

# задаємо папку для результатів експериментів
RESULTS_DIR = Path.home()/"Desktop"/"STEM_Image_Processing_results"

# задаємо шлях до таблиці з метриками
CSV_PATH = RESULTS_DIR / "comparison.csv"

# задаємо шлях до конфігурації
CONFIG_PATH = PROJECT_DIR / "config.json"

# встановлюємо максимальну сторону зображення
MAX_IMAGE_SIDE = 700

# дозволені формати зображень
SUPPORTED_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
}


# функція завантаження параметрів
def load_config():

    # встановлюємо стандартні параметри
    config = {
        "brightness": 30,
        "threshold": 128,
        "morphology_operation": "Ерозія",
        "morphology_size": 3
    }

    # перевіряємо існування файлу
    if CONFIG_PATH.exists():

        # відкриваємо файл конфігурації
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:

            # читаємо збережені параметри
            saved_config = json.load(file)

        # оновлюємо стандартні параметри
        config.update(saved_config)

    return config


# функція завантаження зображення
def load_image(image_path):

    # відкриваємо зображення
    with Image.open(image_path) as image:

        # перетворюємо у формат RGB
        result = image.convert("RGB")

    # зменшуємо надто великі зображення
    # оригінальні файли залишаються незмінними
    result.thumbnail(
        (MAX_IMAGE_SIDE, MAX_IMAGE_SIDE),
        Image.Resampling.LANCZOS
    )

    return result


# функція застосування алгоритму
def apply_algorithm(image, algorithm_name, config):

    # перетворення у відтінки сірого
    if algorithm_name == "grayscale":

        return grayscale(image)

    # корекція яскравості
    elif algorithm_name == "brightness":

        return brightness(
            image,
            int(config["brightness"])
        )

    # гістограмне вирівнювання
    elif algorithm_name == "histogram_equalization":

        return histogram_equalization(image)

    # порогова сегментація
    elif algorithm_name == "threshold_segmentation":

        return threshold_segmentation(
            image,
            int(config["threshold"])
        )

    # морфологічна обробка
    elif algorithm_name == "morphology":

        return morphology(
            image,
            config["morphology_operation"],
            int(config["morphology_size"])
        )

    # повідомляємо про невідомий алгоритм
    else:

        raise ValueError(
            f"Невідомий алгоритм: {algorithm_name}"
        )


# функція обчислення метрик
def calculate_metrics(original, processed):

    # середньоквадратична похибка
    mse = calculate_mse(original, processed)

    # пікове відношення сигналу до шуму
    psnr = calculate_psnr(original, processed)

    # глобальний індекс структурної подібності
    ssim = calculate_ssim(original, processed)

    return mse, psnr, ssim


# функція проведення експериментів
def run_experiments():

    # перевіряємо наявність папки dataset
    if not DATASET_DIR.is_dir():

        print("Помилка: папку dataset не знайдено.")
        print(f"Очікуваний шлях: {DATASET_DIR}")

        return

    # створюємо папку для результатів
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # завантажуємо параметри
    config = load_config()

    # визначаємо п'ять алгоритмів
    algorithms = [
        "grayscale",
        "brightness",
        "histogram_equalization",
        "threshold_segmentation",
        "morphology"
    ]

    # отримуємо список зображень
    image_files = sorted(
        file
        for file in DATASET_DIR.iterdir()
        if (
            file.is_file()
            and file.suffix.lower() in SUPPORTED_FORMATS
        )
    )

    # перевіряємо наявність зображень
    if not image_files:

        print("У папці dataset немає зображень.")

        return

    # створюємо список результатів
    results = []

    # лічильник успішних обробок
    successful = 0

    # лічильник помилок
    failed = 0

    # виводимо початкову інформацію
    print()
    print("STEM IMAGE PROCESSING")
    print("Автоматичне тестування алгоритмів")
    print()

    print(f"Кількість зображень: {len(image_files)}")
    print(f"Кількість алгоритмів: {len(algorithms)}")

    print(
        f"Заплановано обробок: "
        f"{len(image_files) * len(algorithms)}"
    )

    print()

    # обходимо всі зображення
    for image_number, image_path in enumerate(
        image_files,
        start=1
    ):

        print(
            f"[{image_number}/{len(image_files)}] "
            f"{image_path.name}"
        )

        # намагаємося відкрити зображення
        try:

            original = load_image(image_path)

        except (
            UnidentifiedImageError,
            OSError,
            ValueError
        ) as error:

            print(f"  Помилка відкриття: {error}")

            failed += len(algorithms)

            continue

        # створюємо папку для поточного зображення
        image_results_dir = (
            RESULTS_DIR / image_path.stem
        )

        image_results_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # застосовуємо кожен алгоритм
        for algorithm_name in algorithms:

            try:

                # запам'ятовуємо початковий час
                start_time = time.perf_counter()

                # обробляємо зображення
                processed = apply_algorithm(
                    original,
                    algorithm_name,
                    config
                )

                # обчислюємо час обробки
                elapsed_time = (
                    time.perf_counter() - start_time
                )

                # обчислюємо метрики
                mse, psnr, ssim = calculate_metrics(
                    original,
                    processed
                )

                # формуємо назву результату
                output_path = (
                    image_results_dir
                    / f"{algorithm_name}.png"
                )

                # зберігаємо оброблене зображення
                processed.save(
                    output_path,
                    format="PNG"
                )

                # додаємо результат до таблиці
                results.append({
                    "image": image_path.name,
                    "algorithm": algorithm_name,
                    "width": original.width,
                    "height": original.height,
                    "mse": round(mse, 4),
                    "psnr": round(psnr, 4),
                    "global_ssim": round(ssim, 6),
                    "time_seconds": round(
                        elapsed_time,
                        4
                    ),
                    "output_file": str(output_path)
                })

                successful += 1

                # виводимо результат у термінал
                print(
                    f"  {algorithm_name}: OK "
                    f"({elapsed_time:.3f} с)"
                )

            except Exception as error:

                failed += 1

                print(
                    f"  {algorithm_name}: "
                    f"ПОМИЛКА — {error}"
                )

        print()

    # перевіряємо наявність результатів
    if results:

        # визначаємо назви стовпців
        fieldnames = [
            "image",
            "algorithm",
            "width",
            "height",
            "mse",
            "psnr",
            "global_ssim",
            "time_seconds",
            "output_file"
        ]

        # відкриваємо CSV-файл
        with open(
            CSV_PATH,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as csv_file:

            # створюємо об'єкт запису
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            # записуємо заголовки
            writer.writeheader()

            # записуємо результати
            writer.writerows(results)

    # виводимо підсумки
    print("Експерименти завершено!")
    print()

    print(f"Успішних обробок: {successful}")
    print(f"Помилок: {failed}")

    if results:
        print(f"Таблиця результатів: {CSV_PATH}")

    print(f"Папка результатів: {RESULTS_DIR}")


# запускаємо експерименти
if __name__ == "__main__":

    run_experiments()