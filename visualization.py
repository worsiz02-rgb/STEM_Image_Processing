import csv
import math
from pathlib import Path
from statistics import mean

import matplotlib

# використовуємо режим збереження графіків у файли
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# визначаємо папку з результатами експериментів
RESULTS_DIR = (
    Path.home()
    / "Desktop"
    / "STEM_Image_Processing_results"
)

# шлях до таблиці з метриками
CSV_PATH = RESULTS_DIR / "comparison.csv"

# папка для збереження графіків
GRAPHS_DIR = RESULTS_DIR / "graphs"


# назви алгоритмів для підписів
ALGORITHM_NAMES = {
    "grayscale": "Відтінки сірого",
    "brightness": "Корекція яскравості",
    "histogram_equalization": "Гістограмне вирівнювання",
    "threshold_segmentation": "Порогова сегментація",
    "morphology": "Морфологічна обробка"
}


# налаштовуємо відображення українських символів
plt.rcParams["font.family"] = "DejaVu Sans"


# функція завантаження результатів
def load_results():

    # перевіряємо існування таблиці
    if not CSV_PATH.is_file():
        raise FileNotFoundError(
            f"Файл не знайдено: {CSV_PATH}"
        )

    # відкриваємо CSV-файл
    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        # читаємо всі рядки
        reader = csv.DictReader(file)
        results = list(reader)

    # перевіряємо наявність даних
    if not results:
        raise ValueError("Таблиця comparison.csv порожня")

    return results


# функція обчислення середніх значень
def calculate_averages(results, metric):

    # створюємо словник для накопичення значень
    grouped_values = {
        algorithm: []
        for algorithm in ALGORITHM_NAMES
    }

    # перебираємо результати
    for row in results:

        algorithm = row["algorithm"]

        # пропускаємо невідомі алгоритми
        if algorithm not in grouped_values:
            continue

        # перетворюємо значення на число
        value = float(row[metric])

        # нескінченні значення не включаємо
        # до обчислення середнього
        if math.isfinite(value):
            grouped_values[algorithm].append(value)

    # обчислюємо середні значення
    averages = {}

    for algorithm, values in grouped_values.items():

        if values:
            averages[algorithm] = mean(values)
        else:
            averages[algorithm] = None

    return averages


# функція створення графіка
def create_graph(
    results,
    metric,
    title,
    ylabel,
    filename,
    color
):

    # обчислюємо середні значення
    averages = calculate_averages(results, metric)

    # отримуємо назви алгоритмів
    algorithms = list(ALGORITHM_NAMES.keys())

    # створюємо підписи
    labels = [
        ALGORITHM_NAMES[algorithm]
        for algorithm in algorithms
    ]

    # отримуємо числові значення
    values = [
        averages[algorithm]
        for algorithm in algorithms
    ]

    # створюємо графік
    fig, ax = plt.subplots(figsize=(13, 7))

    # будуємо стовпчики
    bars = ax.bar(
        range(len(algorithms)),
        [
            value if value is not None else 0
            for value in values
        ],
        color=color,
        edgecolor="#333333",
        width=0.65
    )

    # додаємо назву графіка
    ax.set_title(
        title,
        fontsize=17,
        fontweight="bold",
        pad=20
    )

    # підписуємо вертикальну вісь
    ax.set_ylabel(
        ylabel,
        fontsize=12
    )

    # встановлюємо підписи алгоритмів
    ax.set_xticks(range(len(algorithms)))

    ax.set_xticklabels(
        labels,
        rotation=15,
        ha="right",
        fontsize=10
    )

    # додаємо горизонтальні лінії
    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    ax.set_axisbelow(True)

    # додаємо числові значення над стовпчиками
    for bar, value in zip(bars, values):

        if value is None:

            # для нескінченного PSNR не обчислюємо середнє
            label = "∞ / немає середнього"

        else:

            label = f"{value:.3f}"

        ax.annotate(
            label,
            xy=(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height()
            ),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9
        )

    # залишаємо місце для підписів
    ax.margins(y=0.2)

    fig.tight_layout()

    # формуємо шлях збереження
    output_path = GRAPHS_DIR / filename

    # зберігаємо графік
    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight"
    )

    # закриваємо графік
    plt.close(fig)

    print(f"Збережено: {output_path}")


# головна функція
def main():

    # створюємо папку для графіків
    GRAPHS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # завантажуємо результати експериментів
    results = load_results()

    print()
    print("STEM IMAGE PROCESSING")
    print("Побудова графіків")
    print()

    print(f"Завантажено рядків: {len(results)}")
    print()

    # графік середнього MSE
    create_graph(
        results,
        metric="mse",
        title="Порівняння алгоритмів за MSE",
        ylabel="Середнє MSE",
        filename="mse_comparison.png",
        color="#E57373"
    )

    # графік середнього PSNR
    create_graph(
        results,
        metric="psnr",
        title="Порівняння алгоритмів за PSNR",
        ylabel="Середнє PSNR, дБ",
        filename="psnr_comparison.png",
        color="#64B5F6"
    )

    # графік середнього Global SSIM
    create_graph(
        results,
        metric="global_ssim",
        title="Порівняння алгоритмів за Global SSIM",
        ylabel="Середнє Global SSIM",
        filename="ssim_comparison.png",
        color="#81C784"
    )

    # графік середнього часу виконання
    create_graph(
        results,
        metric="time_seconds",
        title="Порівняння швидкодії алгоритмів",
        ylabel="Середній час виконання, с",
        filename="time_comparison.png",
        color="#BA68C8"
    )

    print()
    print("Усі 4 графіки успішно створено!")
    print(f"Папка: {GRAPHS_DIR}")


# запускаємо програму
if __name__ == "__main__":
    main()