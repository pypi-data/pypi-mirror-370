import time
from r00logger import log, set_level, log_script

# --- Пример использования ---
#@log_script
def build_test():
    log.trace("Сборка тестов")
    log.debug("Начинаем компиляцию")
    patch_test(options={'cache': False})
    log.warning("Done")
    log.error("Test OK")
    log.critical("Critical failure simulation")
    log.success("Build successful!") # Добавим success для теста цвета

#@log_script
def patch_test(mode='fast', options=None):
    if options is None:
        options = {'cache': True}
    log.trace("Патч тестов")
    log.debug(f"Компиляция в режиме: {mode!r}")
    patch_test2()
    log.info(f"Опции: {options!r}")
    time.sleep(0.05)

#@log_script
def patch_test2(mode='fast', options=None):
    log.trace("Патч тестов PATCH TEST 2")
    return "FUCK ME"



if __name__ == '__main__':
    set_level('TRACE')
    build_test()

