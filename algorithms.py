import unittest
import sys
from pathlib import Path
from PIL import Image


# визначаємо головну папку проєкту
PROJECT_DIR = Path(__file__).resolve().parent.parent

# додаємо папку проєкту до шляхів імпорту
sys.path.insert(0, str(PROJECT_DIR))


def grayscale(image):
    """Перетворює зображення у відтінки сірого."""
    result = Image.new("RGB", image.size)

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))[:3]
            value = round(0.299 * r + 0.587 * g + 0.114 * b)
            result.putpixel((x, y), (value, value, value))

    return result


def brightness(image, value):
    """Змінює яскравість усіх каналів пікселів."""
    result = Image.new("RGB", image.size)

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))[:3]
            result.putpixel(
                (x, y),
                (
                    max(0, min(255, r + value)),
                    max(0, min(255, g + value)),
                    max(0, min(255, b + value)),
                ),
            )

    return result


def histogram_equalization(image):
    """Вирівнює гістограму яскравості зображення."""
    grayscale_image = grayscale(image)
    width, height = grayscale_image.size
    histogram = [0] * 256

    for y in range(height):
        for x in range(width):
            gray = grayscale_image.getpixel((x, y))[0]
            histogram[gray] += 1

    cdf = [0] * 256
    cumulative = 0
    cdf_min = None
    for value, count in enumerate(histogram):
        cumulative += count
        cdf[value] = cumulative
        if count > 0 and cdf_min is None:
            cdf_min = cumulative

    total = width * height
    result = Image.new("RGB", (width, height))

    if cdf_min is None or total == cdf_min:
        return grayscale_image

    for y in range(height):
        for x in range(width):
            gray = grayscale_image.getpixel((x, y))[0]
            new_value = round((cdf[gray] - cdf_min) * 255 / (total - cdf_min))
            new_value = max(0, min(255, new_value))
            result.putpixel((x, y), (new_value, new_value, new_value))

    return result


def threshold_segmentation(image, threshold):
    """Перетворює пікселі на білий або чорний за заданим порогом."""
    gray = grayscale(image)
    result = Image.new("RGB", gray.size)

    for y in range(gray.height):
        for x in range(gray.width):
            value = 255 if gray.getpixel((x, y))[0] >= threshold else 0
            result.putpixel((x, y), (value, value, value))

    return result


def morphology(image, operation, size):
    """Застосовує морфологічну ерозію або дилатацію."""
    if size <= 0 or size % 2 == 0:
        raise ValueError("Розмір морфологічного вікна має бути непарним додатним числом")

    if operation not in ("Ерозія", "Дилатація"):
        raise ValueError("Непідтримувана морфологічна операція")

    result = Image.new("RGB", image.size)
    radius = size // 2

    for y in range(image.height):
        for x in range(image.width):
            pixels = []
            for ky in range(max(0, y - radius), min(image.height, y + radius + 1)):
                for kx in range(max(0, x - radius), min(image.width, x + radius + 1)):
                    pixels.append(image.getpixel((kx, ky))[:3])

            if operation == "Ерозія":
                value = tuple(min(pixel[channel] for pixel in pixels) for channel in range(3))
            else:
                value = tuple(max(pixel[channel] for pixel in pixels) for channel in range(3))

            result.putpixel((x, y), value)

    return result


