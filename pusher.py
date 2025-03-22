from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import asyncio  # Для работы с асинхронностью
import telegram

# Указываем путь к драйверу через Service
driver = webdriver.Chrome(service=service)

# Telegram-бот
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Словарь для сопоставления data-key с именами пользователей
user_map = {
    "7E6493F74116": "Малая",
}

# Хранение текущего состояния подключённых устройств
current_users = set()

async def send_telegram_message(message):
    """Отправка сообщения в Telegram."""
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

async def main():
    global current_users  # Указываем, что используем глобальную переменную
    try:
        # Открываем страницу авторизации роутера
        driver.get("http://192.168.0.1")

        # Явное ожидание появления поля для ввода пароля
        wait = WebDriverWait(driver, 30)
        print("Ожидание поля для ввода пароля...")
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        print("Поле для ввода пароля найдено.")

        # Вводим пароль

        # Находим кнопку "LOG IN" и нажимаем на нее
        print("Ожидание кнопки 'LOG IN'...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='button-button' and @title='LOG IN']")))
        print("Кнопка 'LOG IN' найдена. Нажимаем...")
        login_button.click()

        # Ждем, пока элемент с текстом "Clients" станет доступным для клика
        print("Ожидание элемента 'Clients'...")
        clients_text = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[@class='map-item-text map-clients-text']//span[text()='Clients']")))
        print("Элемент 'Clients' найден. Нажимаем...")
        clients_text.click()

        # Ждем, чтобы страница обновилась или загрузилась новая информация
        print("Ожидание обновления страницы...")
        await asyncio.sleep(5)

        # Основной цикл для проверки подключённых устройств
        while True:
            print("Проверка подключённых устройств...")
            devices = driver.find_elements(By.XPATH, "//tr[contains(@class, 'grid-content-tr')]")
            new_users = set()

            for device in devices:
                try:
                    # Извлекаем data-key
                    data_key = device.get_attribute("data-key")
                    if data_key:
                        new_users.add(data_key)
                except Exception as e:
                    print(f"Ошибка при обработке устройства: {e}")

            # Сравниваем текущее состояние с предыдущим
            added_users = new_users - current_users
            removed_users = current_users - new_users

            # Уведомляем только о тех, кто есть в user_map
            for user in added_users:
                if user in user_map:
                    await send_telegram_message(f"{user_map[user]} дома")

            for user in removed_users:
                if user in user_map:
                    await send_telegram_message(f"{user_map[user]} ушел по делам")

            # Обновляем текущее состояние
            current_users = new_users

            # Ждём 30 секунд перед следующей проверкой
            await asyncio.sleep(10)

    finally:
        # Закрываем браузер после выполнения
        print("Закрытие браузера...")
        driver.quit()

# Запуск асинхронной функции
asyncio.run(main())