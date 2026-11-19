import unittest
import sys
from pathlib import Path
from PIL import Image


# визначаємо головну папку проєкту
PROJECT_DIR = Path(__file__).resolve().parent.parent

# додаємо папку проєкту до шляхів імпорту
sys.path.insert(0, str(PROJECT_DIR))


# імпортуємо п'ять алгоритмів
from algorithms import (
    grayscale,
    brightness,
    histogram_equalization,
    threshold_segmentation,
    morphology
)


# створюємо клас тестування алгоритмів
class TestAlgorithms(unittest.TestCase):

    # тест 1: перетворення у відтінки сірого
    def test_grayscale(self):

        # створюємо зображення 3x3
        image = Image.new("RGB", (3, 3), (100, 150, 200))

        # застосовуємо алгоритм
        result = grayscale(image)

        # вручну обчислюємо очікувану яскравість
        expected = round(
            0.299 * 100 +
            0.587 * 150 +
            0.114 * 200
        )

        # перевіряємо центральний піксель
        self.assertEqual(
            result.getpixel((1, 1)),
            (expected, expected, expected)
        )


    # тест 2: збільшення яскравості
    def test_brightness_increase(self):

        # створюємо зображення 3x3
        image = Image.new("RGB", (3, 3), (100, 100, 100))

        # збільшуємо яскравість на 30
        result = brightness(image, 30)

        # очікуємо значення 130
        self.assertEqual(
            result.getpixel((1, 1)),
            (130, 130, 130)
        )


    # тест 3: обмеження максимальної яскравості
    def test_brightness_limit(self):

        # створюємо світле зображення
        image = Image.new("RGB", (3, 3), (250, 250, 250))

        # збільшуємо яскравість на 30
        result = brightness(image, 30)

        # значення не повинно перевищувати 255
        self.assertEqual(
            result.getpixel((1, 1)),
            (255, 255, 255)
        )


    # тест 4: гістограмне вирівнювання
    def test_histogram_equalization(self):

        # створюємо зображення 3x3
        image = Image.new("RGB", (3, 3))

        # задаємо початкові яскравості
        values = [
            50, 50, 50,
            100, 100, 100,
            150, 150, 150
        ]

        # заповнюємо зображення
        for index, value in enumerate(values):

            # обчислюємо координати
            x = index % 3
            y = index // 3

            # записуємо піксель
            image.putpixel(
                (x, y),
                (value, value, value)
            )

        # застосовуємо алгоритм
        result = histogram_equalization(image)

        # перевіряємо нові значення
        self.assertEqual(
            result.getpixel((0, 0)),
            (0, 0, 0)
        )

        self.assertEqual(
            result.getpixel((1, 1)),
            (128, 128, 128)
        )

        self.assertEqual(
            result.getpixel((2, 2)),
            (255, 255, 255)
        )


    # тест 5: порогова сегментація
    def test_threshold_segmentation(self):

        # створюємо зображення 3x3
        image = Image.new("RGB", (3, 3), (100, 100, 100))

        # встановлюємо поріг 128
        result = threshold_segmentation(image, 128)

        # оскільки 100 < 128, піксель має бути чорним
        self.assertEqual(
            result.getpixel((1, 1)),
            (0, 0, 0)
        )


    # тест 6: морфологічна ерозія
    def test_erosion(self):

        # створюємо біле зображення
        image = Image.new("RGB", (3, 3), (255, 255, 255))

        # центральний піксель робимо чорним
        image.putpixel((1, 1), (0, 0, 0))

        # застосовуємо ерозію з вікном 3x3
        result = morphology(image, "Ерозія", 3)

        # перевіряємо центральний піксель
        self.assertEqual(
            result.getpixel((1, 1)),
            (0, 0, 0)
        )

        # перевіряємо кутовий піксель
        self.assertEqual(
            result.getpixel((0, 0)),
            (0, 0, 0)
        )


    # тест 7: морфологічна дилатація
    def test_dilation(self):

        # створюємо чорне зображення
        image = Image.new("RGB", (3, 3), (0, 0, 0))

        # центральний піксель робимо білим
        image.putpixel((1, 1), (255, 255, 255))

        # застосовуємо дилатацію з вікном 3x3
        result = morphology(image, "Дилатація", 3)

        # перевіряємо центральний піксель
        self.assertEqual(
            result.getpixel((1, 1)),
            (255, 255, 255)
        )

        # перевіряємо кутовий піксель
        self.assertEqual(
            result.getpixel((0, 0)),
            (255, 255, 255)
        )


    # тест 8: неправильний розмір морфологічного вікна
    def test_invalid_morphology_size(self):

        # створюємо тестове зображення
        image = Image.new("RGB", (3, 3), (100, 100, 100))

        # перевіряємо, що розмір 4 викликає помилку
        with self.assertRaises(ValueError):

            morphology(image, "Ерозія", 4)


# запускаємо автоматичні тести
if __name__ == "__main__":
    unittest.main()