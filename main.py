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
parser.add_argument('--prompt', dest='prompt', type=str, help='Файл з конфігурацією для генерації постів, якщо не вказано, то буде використано за замовчуванням')
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

def main(): 
    # Ваш код тут
    print_banner_Anjela()
    pwd = get_password()
    api_key = get_api_key()
    num = get_num()
    delay = get_delay()
    prompt = get_system_prompt()
    if args.login and pwd and api_key:  
        tm = Treads_Management(args.login, pwd, api_key, num, delay, prompt)
        tm.start()
    else:
        print("Логін або пароль не вказані.")

if __name__ == "__main__":
    main()