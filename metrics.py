import numpy as np
import math


# функція підготовки зображень
def prepare_images(original, processed):

    # перетворюємо оригінал у масив чисел
    image1 = np.array(original, dtype=np.float64)

    # перетворюємо результат у масив чисел
    image2 = np.array(processed, dtype=np.float64)

    # перевіряємо розміри зображень
    if image1.shape != image2.shape:
        raise ValueError("Зображення мають різні розміри")

    # перевіряємо наявність пікселів
    if image1.size == 0:
        raise ValueError("Зображення порожні")

    return image1, image2


# обчислення середньоквадратичної похибки
def calculate_mse(original, processed):

    # отримуємо масиви пікселів
    image1, image2 = prepare_images(original, processed)

    # обчислюємо різницю між пікселями
    difference = image1 - image2

    # підносимо різницю до квадрата
    squared_difference = difference ** 2

    # обчислюємо середнє значення
    mse = np.mean(squared_difference)

    return float(mse)


# обчислення пікового відношення сигналу до шуму
def calculate_psnr(original, processed):

    # обчислюємо MSE
    mse = calculate_mse(original, processed)

    # якщо зображення однакові
    if mse == 0:
        return float("inf")

    # обчислюємо PSNR
    psnr = 10 * math.log10((255 ** 2) / mse)

    return psnr


# обчислення глобального індексу структурної подібності
def calculate_ssim(original, processed):

    # переводимо зображення у відтінки сірого для порівняння
    image1 = np.array(original.convert("L"), dtype=np.float64)
    image2 = np.array(processed.convert("L"), dtype=np.float64)

    # перевіряємо розміри
    if image1.shape != image2.shape:
        raise ValueError("Зображення мають різні розміри")

    if image1.size == 0:
        raise ValueError("Зображення порожні")

    # обчислюємо середню яскравість
    mu1 = np.mean(image1)
    mu2 = np.mean(image2)

    # обчислюємо дисперсії
    sigma1 = np.mean((image1 - mu1) ** 2)
    sigma2 = np.mean((image2 - mu2) ** 2)

    # обчислюємо коваріацію
    sigma12 = np.mean(
        (image1 - mu1) * (image2 - mu2)
    )

    # задаємо константи стабілізації
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    # обчислюємо чисельник формули
    numerator = (
        (2 * mu1 * mu2 + c1) *
        (2 * sigma12 + c2)
    )

    # обчислюємо знаменник
    denominator = (
        (mu1 ** 2 + mu2 ** 2 + c1) *
        (sigma1 + sigma2 + c2)
    )

    # обчислюємо SSIM
    ssim = numerator / denominator

    return float(ssim)