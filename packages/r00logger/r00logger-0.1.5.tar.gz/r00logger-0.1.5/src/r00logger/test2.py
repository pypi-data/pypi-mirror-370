import time
import logging
import sys
# Импортируем наш кастомный логгер и его функции
from r00logger import log, set_level, log_script

# --- Функции для Loguru (остаются как есть) ---
@log_script
def build_test():
    log.trace("Сборка тестов") # Будет проигнорировано при уровне DEBUG
    log.debug("Начинаем компиляцию")
    patch_test(options={'cache': False})
    log.warning("Done")
    log.error("Test OK")
    log.critical("Critical failure simulation")
    log.success("Build successful!")

@log_script
def patch_test(mode='fast', options=None):
    if options is None:
        options = {'cache': True}
    log.trace("Патч тестов") # Будет проигнорировано при уровне DEBUG
    log.debug(f"Компиляция в режиме: {mode!r}")
    log.info(f"Опции: {options!r}")
    time.sleep(0.001) # Уменьшим sleep для скорости теста

# --- Аналогичные функции для стандартного logging ---
# Глобальный логгер для стандартного теста
std_logger = logging.getLogger('StdBenchmark')

def std_patch_test(mode='fast', options=None):
    if options is None:
        options = {'cache': True}
    # log.trace -> logging.debug
    std_logger.debug("Патч тестов")
    std_logger.debug(f"Компиляция в режиме: {mode!r}")
    std_logger.info(f"Опции: {options!r}")
    time.sleep(0.001) # Уменьшим sleep для скорости теста

def std_build_test():
    # log.trace -> logging.debug
    std_logger.debug("Сборка тестов")
    std_logger.debug("Начинаем компиляцию")
    std_patch_test(options={'cache': False})
    std_logger.warning("Done")
    std_logger.error("Test OK")
    std_logger.critical("Critical failure simulation")
    # log.success -> logging.info
    std_logger.info("Build successful!")

# --- Настройка стандартного logging ---
def setup_standard_logging():
    # Убираем существующие обработчики, если есть (на всякий случай)
    for handler in std_logger.handlers[:]:
        std_logger.removeHandler(handler)
    std_logger.setLevel(logging.DEBUG) # Уровень DEBUG
    handler = logging.StreamHandler(sys.stdout)
    # Простой формат, чтобы минимизировать его влияние на скорость
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    std_logger.addHandler(handler)
    # Предотвращаем дублирование, если логгер корневой
    std_logger.propagate = False

if __name__ == '__main__':
    N = 1000 # Количество итераций для замера

    print(f"--- Запуск бенчмарка ({N} итераций) ---")

    # --- Бенчмарк Loguru ---
    print("\n[1] Запуск Loguru с кастомной настройкой...")
    set_level('DEBUG') # Устанавливаем уровень DEBUG для сравнения
    log.info(f"Начинаем тест Loguru (вывод будет показан только для первой итерации)...")

    # "Прогрев" (не замеряем первую итерацию)
    build_test()
    print("Прогрев Loguru завершен.")

    # Замер
    t0_loguru = time.perf_counter()
    for _ in range(N):
        build_test()
    t1_loguru = time.perf_counter()
    dt_loguru = t1_loguru - t0_loguru
    print(f"\nLoguru завершил {N} итераций.")

    # --- Бенчмарк стандартного logging ---
    print("\n[2] Запуск стандартного logging...")
    setup_standard_logging()
    std_logger.info(f"Начинаем тест standard logging (вывод будет показан только для первой итерации)...")

    # "Прогрев"
    std_build_test()
    print("Прогрев standard logging завершен.")

    # Замер
    t0_std = time.perf_counter()
    for _ in range(N):
        std_build_test()
    t1_std = time.perf_counter()
    dt_std = t1_std - t0_std
    print(f"\nStandard logging завершил {N} итераций.")

    # --- Результаты ---
    print("\n--- Результаты бенчмарка ---")
    print(f"Время Loguru (кастомный): {dt_loguru:.4f} секунд")
    print(f"Время standard logging:    {dt_std:.4f} секунд")

    if dt_std > 0:
        ratio = dt_loguru / dt_std
        print(f"\nLoguru медленнее стандартного logging в {ratio:.2f} раз на данном тесте.")
    else:
        print("\nНе удалось вычислить соотношение (время standard logging <= 0).")

    print("\nПримечание: Скорость зависит от сложности формата, количества обработчиков,")
    print("логики декоратора/патчера и конкретных операций логирования.")