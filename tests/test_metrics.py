import unittest
import math
import sys
from pathlib import Path

from PIL import Image


# додаємо папку проєкту до шляхів пошуку модулів
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))


# імпортуємо функції для перевірки
from metrics import calculate_mse, calculate_psnr, calculate_ssim


# створюємо клас автоматичних тестів
class TestImageMetrics(unittest.TestCase):

    # перевірка MSE для однакових зображень
    def test_mse_identical(self):

        # створюємо перше зображення
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))

        # створюємо друге однакове зображення
        image2 = Image.new("RGB", (3, 3), (100, 100, 100))

        # обчислюємо MSE
        result = calculate_mse(image1, image2)

        # перевіряємо результат
        self.assertEqual(result, 0)


    # перевірка MSE для різних зображень
    def test_mse_different(self):

        # створюємо перше зображення
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))

        # створюємо друге зображення
        image2 = Image.new("RGB", (3, 3), (110, 110, 110))

        # обчислюємо MSE
        result = calculate_mse(image1, image2)

        # різниця між пікселями дорівнює 10
        # квадрат різниці дорівнює 100
        self.assertEqual(result, 100)


    # перевірка PSNR для однакових зображень
    def test_psnr_identical(self):

        # створюємо однакові зображення
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))
        image2 = Image.new("RGB", (3, 3), (100, 100, 100))

        # обчислюємо PSNR
        result = calculate_psnr(image1, image2)

        # перевіряємо нескінченне значення
        self.assertTrue(math.isinf(result))


    # перевірка PSNR для різних зображень
    def test_psnr_different(self):

        # створюємо два зображення
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))
        image2 = Image.new("RGB", (3, 3), (110, 110, 110))

        # обчислюємо PSNR
        result = calculate_psnr(image1, image2)

        # очікуване значення за формулою
        expected = 10 * math.log10(255 ** 2 / 100)

        # перевіряємо результат
        self.assertAlmostEqual(result, expected, places=6)


    # перевірка Global SSIM для однакових зображень
    def test_ssim_identical(self):

        # створюємо однакові зображення
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))
        image2 = Image.new("RGB", (3, 3), (100, 100, 100))

        # обчислюємо Global SSIM
        result = calculate_ssim(image1, image2)

        # для однакових зображень очікуємо 1
        self.assertAlmostEqual(result, 1.0, places=6)


    # перевірка Global SSIM для різних зображень
    def test_ssim_different(self):

        # створюємо два різні зображення
        image1 = Image.new("RGB", (3, 3), (50, 50, 50))
        image2 = Image.new("RGB", (3, 3), (150, 150, 150))

        # обчислюємо Global SSIM
        result = calculate_ssim(image1, image2)

        # перевіряємо, що подібність менша за 1
        self.assertLess(result, 1.0)


    # перевірка помилки для різних розмірів
    def test_mse_different_sizes(self):

        # створюємо зображення різних розмірів
        image1 = Image.new("RGB", (3, 3), (100, 100, 100))
        image2 = Image.new("RGB", (5, 5), (100, 100, 100))

        # перевіряємо виникнення помилки
        with self.assertRaises(ValueError):

            calculate_mse(image1, image2)


# запускаємо тести
if __name__ == "__main__":
    unittest.main()