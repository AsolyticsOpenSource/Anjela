import time
import argparse
from treads_management import Treads_Management


#pip freeze > requirements.txt

parser = argparse.ArgumentParser()
parser.add_argument('--login', dest='login', type=str, help='Логін аккаунту соціальної мережі')
parser.add_argument('--pwd', dest='pwd', type=str, help='Імя текстового файлу з паролем')
parser.add_argument('--api', dest='api', type=str, help='Імя текстового файлу з токеном OpenAI') 
parser.add_argument('--num', dest='num', type=str, help='Кількість постів в серії (за заповчуванням 7)')
parser.add_argument('--delay', dest='delay', type=str, help='Затримка між серією постів в хвилинах (за заповчуванням 21 хвилина)')
args = parser.parse_args()
"""
driver = webdriver.Firefox()
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element(By.NAME, "q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)

time.sleep(10)
assert "No results found." not in driver.page_source
driver.close()
"""

def get_password() -> str:
    try:
        with open(args.pwd, 'r', encoding='utf-8') as file:
            password = file.read().strip()
            return password
    except FileNotFoundError:
        print("Файл з паролем не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з паролем: {e}")
    return None

def get_api_key() -> str:
    try:
        with open(args.api, 'r', encoding='utf-8') as file:
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        print("Файл з токеном OpenAI не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з токеном OpenAI: {e}")
    return None

def get_num() -> int:
    try:
        if args.num:
            num = int(args.num)
            if num > 0:
                return num
            else:
                print("Кількість постів має бути додатнім числом.")
        else:
            return 7  # Значення за замовчуванням
    except ValueError:
        print("Помилка: Кількість постів має бути цілим числом.")
    return 7  # Значення за замовчуванням

def get_delay() -> int:
    try:
        if args.delay:
            delay = int(args.delay)
            if delay > 0:
                return delay * 60
            else:
                print("Затримка має бути додатнім числом.")
        else:
            return 21 * 60  # Значення за замовчуванням (21 хвилина в секундах)
    except ValueError:
        print("Помилка: Затримка має бути цілим числом.")
    return 21 * 60  # Значення за замовчуванням (21 хвилина в секундах)

def main(): 
    # Ваш код тут
    pwd = get_password()
    api_key = get_api_key()
    num = get_num()
    delay = get_delay()
    if args.login and pwd and api_key:  
        tm = Treads_Management(args.login, pwd, api_key, num, delay)
        tm.start()
    else:
        print("Логін або пароль не вказані.")

if __name__ == "__main__":
    main()