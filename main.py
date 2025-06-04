import time
import argparse
from treads_management import Treads_Management


#pip freeze > requirements.txt

parser = argparse.ArgumentParser()
parser.add_argument('--login', dest='login', type=str, help='Логін аккаунту соціальної мережі')
parser.add_argument('--pwd', dest='pwd', type=str, help='Імя текстового файлу з паролем')
parser.add_argument('--api', dest='api', type=str, help='Імя текстового файлу з токеном OpenAI')
parser.add_argument('--subject', dest='subject', type=str, help='Шлях до файлу з темою для перевірки релевантності твітів')
parser.add_argument('--num', dest='num', type=str, help='Кількість постів в серії (за заповчуванням 7)')
parser.add_argument('--delay', dest='delay', type=str, help='Затримка між серією постів в хвилинах (за заповчуванням 21 хвилина)')
parser.add_argument('--prompt', dest='prompt', type=str, help='Файл з конфігурацією для генерації постів, якщо не вказано, то буде використано за замовчуванням')
parser.add_argument('--freq', dest='freq', type=float, help='Частота з якою аватар буде публікувати пости в годинах (за заповчуванням 0 годин - вимкнуто)', default=0)
parser.add_argument('--topic', dest='topic', type=str, help='Тема на яку аватар буде публікувати пости (треба вказати шлях до файлу з темою)')
parser.add_argument('--surfing', dest='surfing', type=str, help='Логін користувача, чиї дописи ви хочете вподобати та прокоментувати, в стрічці')
parser.add_argument('--sur_count', dest='sur_count', type=int, help='Скільки постів потрібно переглянути в пошуках цілі (число за замовчуванням 333)', default=333)
parser.add_argument('--sur_prompt', dest='sur_prompt', type=str, help='Шлях до файлу де вказано ситемний промпт для коментування (якщо не вказати буде дефолтний)')
parser.add_argument('--feed_keywords', dest='feed_keywords', type=str, help='Шлях до файлу з ключовими словами, ці ключові слова будуть використовуватись для пошуку постів для коментування в стрічці новин')
parser.add_argument('--kt', dest='kt', action='store_true', help='Для коментарів по ключовим словам в стрічці використовувати файл prompt, за замовчуванням використовується sur_prompt')
parser.add_argument('--keywords', dest='keywords', type=str, help='Шлях до файлу з ключовими словами, ці ключові слова будуть використовуватись для пошуку постів для коментування в ситемі пошуку соціальної мережі')
args = parser.parse_args()

def print_banner_Anjela():
    banner = r"""
   █████╗ ███╗   ██╗      ██╗███████╗██╗      █████╗
  ██╔══██╗████╗  ██║      ██║██╔════╝██║     ██╔══██╗
  ███████║██╔██╗ ██║      ██║█████╗  ██║     ███████║
  ██╔══██║██║╚██╗██║██   ██║ ██╔══╝  ██║     ██╔══██║
  ██║  ██║██║ ╚████║╚█████╔╝ ███████╗███████╗██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚════╝  ╚══════╝╚══════╝╚═╝  ╚═╝
"""
    print('\033[91m' + banner + '\033[0m')

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

def get_system_prompt() -> str:
    try:
        with open(args.prompt, 'r', encoding='utf-8') as file:
            system_prompt = file.read().strip()
            return system_prompt
    except FileNotFoundError:
        print("Файл з конфігурацією не знайдено. Буде використано за замовчуванням")
    except Exception as e:
        print(f"Промпт не задано, буде використано за замовчуванням.")
    return None

def get_topic() -> str:
    try:
        with open(args.topic, 'r', encoding='utf-8') as file:
            topic = file.read().strip()
            return topic
    except FileNotFoundError:
        print("Файл з темою не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з темою: {e}")
    return None

def get_subject() -> str:
    try:
        if args.subject:
            with open(args.subject, 'r', encoding='utf-8') as file:
                subject = file.read().strip()
                return subject
        return None
    except FileNotFoundError:
        print("Файл з темою для перевірки релевантності не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з темою для перевірки релевантності: {e}")
    return None

def get_freq() -> int:
    try:
        if args.freq:
            freq = float(args.freq)
            if freq >= 0:
                return freq
            else:
                print("Частота має бути невід'ємним числом.")
        else:
            return 0  # Значення за замовчуванням (вимкнуто)
    except ValueError:
        print("Помилка: Частота має бути числом.")
    return 0  # Значення за замовчуванням (вимкнуто)

def get_surfing() -> str:
    return args.surfing

def get_sur_count() -> int:
    return args.sur_count

def get_sur_prompt() -> str:
    try:
        if args.sur_prompt:
            with open(args.sur_prompt, 'r', encoding='utf-8') as file:
                sur_prompt = file.read().strip()
                return sur_prompt
        return None
    except FileNotFoundError:
        print("Файл з системним промптом для коментування не знайдено (surfing prompt).")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з промптом (surfing prompt): {e}")
    return None

def get_feed_keywords() -> list[str]:
    if not args.feed_keywords:
        return []
    try:
        with open(args.feed_keywords, 'r', encoding='utf-8') as file:
            keywords = [line.strip().replace('+', " ") for line in file if line.strip()]
            return keywords
    except FileNotFoundError:
        print("Файл з ключовими словами не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з ключовими словами: {e}")
    return []

def get_keywords() -> list[str]:
    if not args.keywords:
        return []
    try:
        with open(args.keywords, 'r', encoding='utf-8') as file:
            keywords = [line.strip() for line in file if line.strip()]
            return keywords
    except FileNotFoundError:
        print("Файл з ключовими словами для пошуку не знайдено.")
    except Exception as e:
        print(f"Помилка при зчитуванні файлу з ключовими словами для пошуку: {e}")
    return []

def main():
    # Ваш код тут
    print_banner_Anjela()
    pwd = get_password()
    api_key = get_api_key()
    num = get_num()
    delay = get_delay()
    prompt = get_system_prompt()
    freq = get_freq()
    topic = get_topic() if freq > 0 else None 
    subject = get_subject()
    surfing = get_surfing()
    surfing_sys_prompt = get_sur_prompt()
    surfing_count = get_sur_count()
    feed_keywords = get_feed_keywords()
    keywords = get_keywords()

    if args.login and pwd and api_key:
        tm = Treads_Management(args.login, pwd, api_key, num, delay, prompt, freq, topic, subject, surfing, surfing_sys_prompt, surfing_count, feed_keywords, args.kt, keywords)
        tm.start()
    else:
        print("Логін або пароль не вказані.")

if __name__ == "__main__":
    main()
