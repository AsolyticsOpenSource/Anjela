from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from keywords import keywords
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
from llm_wrapper import LLM_Wrapper
from db_tweets import Tweets_DataBase
import random
import traceback

import time
import json
import os
import sys

class Treads_Management:

    def __init__(self, login:str, password:str, api_key:str, num:int, delay:int, prompt:str, freq:float, topic:str | None, subject:str, surfing:str, surfing_sys_prompt:str, surfing_count:int, feed_keywords:list[str], kt, custom_keywords:list[str]):
        self.login = login
        self.password = password
        self.cookies_file = f"cookies/{login}_cookies.json"  # Файл для збереження cookie
        profile = webdriver.FirefoxProfile()
        profile.set_preference("intl.accept_languages", "en-US, en")
        profile.update_preferences()
        options = webdriver.FirefoxOptions()
        options.profile = profile
        self.browser = webdriver.Firefox(options=options)
        self.maximum_number_of_posts_in_a_row = num
        self.delay_between_posts = delay  # в секундах
        self.llm = LLM_Wrapper(api_key, prompt)
        self.db = Tweets_DataBase()
        self.freq = freq
        self.topic = topic
        self.subject = subject
        self.surfing_login = surfing
        self.surfing_sys_prompt = surfing_sys_prompt
        self.surfing_count = surfing_count
        self.feed_keywords = feed_keywords
        self.kt = kt
        self.keywords = custom_keywords

    def start(self):
        self.browser.implicitly_wait(10)
        self.browser.get("https://www.threads.net")
        # Якщо файл з cookies існує - завантажуємо їх
        self.restore_session_cookies()

    def login_to_social_network(self):
        # Allow the use of cookies from Threads by Instagram on this browser?
        try:
            elem = self.browser.find_element(By.XPATH, '//div[text()="Decline optional cookies"]')
            elem.click()
        except Exception as e:
            print("Cookies element not found:", e)

        # Continue with Instagram
        elem = self.browser.find_element(By.XPATH, '//*[contains(text(), "Continue with Instagram")]')
        elem.click()

        time.sleep(16)

        elem = self.browser.find_element(By.XPATH, "//input[@aria-label='Phone number, username, or email']")
        elem.send_keys(self.login)
        time.sleep(3)

        # Password
        elem = self.browser.find_element(By.XPATH, "//input[@aria-label='Password']")
        elem.send_keys(self.password)
        elem.send_keys(Keys.ENTER)

        time.sleep(7)

        try:
            elem = self.browser.find_element(By.XPATH, '//*[contains(text(), "Save info")]')
            elem.click()
        except Exception as e:
            time.sleep(48)

        # Чекаємо, щоб встигло виконатися входження
        time.sleep(27)
        # Зберігаємо cookies після успішного входу
        self.save_cookies()
        #self.browser.close()
        self.start_the_cycle()

    def save_cookies(self):
        os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
        cookies = self.browser.get_cookies()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f)

    def restore_session_cookies(self):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                try:
                    self.browser.add_cookie(cookie)
                except Exception as e:
                    print("Error adding cookie:", e)
            self.browser.refresh()
            time.sleep(3)
            self.start_the_cycle()
        else:
            time.sleep(3)
            self.login_to_social_network()

    def go_to_search(self):
        # Використання CSS-селектора для натискання на посилання з href="/search"
        search_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/search']"))
        )
        search_link.click()

        self.content_overview()

    def start_the_cycle(self):
        while True:
            try:
                self.go_to_search()
                self.go_to_home()
                try:
                    self.publish_post_to_the_main_page()
                except:
                    print("Home page not found, unpredictable behavior account.")
                    self.go_to_home()
                self.surfing_the_news_feed()
                time.sleep(self.delay_between_posts)
            except Exception as e:
                print("Error in the main loop (60 sec):", e)
                time.sleep(7)
                self.go_to_home()
                time.sleep(60)  # Затримка перед повторною спробою

    def go_to_home(self):
        self.browser.get("https://www.threads.net")

    def get_text_post(self, element) -> WebElement:
        # x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7
        post_text = element.find_element(
             By.XPATH,
                './/div['
                'contains(@class, "x1a6qonq") and '
                'contains(@class, "x6ikm8r") and '
                'contains(@class, "x10wlt62") and '
                'contains(@class, "xj0a0fe") and '
                'contains(@class, "x126k92a") and '
                'contains(@class, "x6prxxf") and '
                'contains(@class, "x7r5mf7")'
                ']'
        )
        return post_text

    def content_overview(self):
        search_field = self.browser.find_element(By.XPATH, "//input[@placeholder='Search']")
        keyword = random.choice(self.keywords) if self.keywords else random.choice(keywords)
        search_field.send_keys(keyword)
        search_field.send_keys(Keys.ENTER)

        time.sleep(5)

        is_next = self.view_the_post()

        if is_next:
            tab_recent = self.browser.find_element(By.XPATH, '//*[contains(text(), "Recent")]')
            tab_recent.click()
            self.view_the_post()
        pass

    def get_post_href(self, element) -> str:
        a_element = element.find_element(
            By.XPATH,
            './/a['
            'contains(@class, "x1i10hfl") and '
            'contains(@class, "xjbqb8w") and '
            'contains(@class, "x1ejq31n") and '
            'contains(@class, "xd10rxx") and '
            'contains(@class, "x1sy0etr") and '
            'contains(@class, "x17r0tee") and '
            'contains(@class, "x972fbf") and '
            'contains(@class, "xcfux6l") and '
            'contains(@class, "x1qhh985") and '
            'contains(@class, "xm0m39n") and '
            'contains(@class, "x9f619") and '
            'contains(@class, "x1ypdohk") and '
            'contains(@class, "xt0psk2") and '
            'contains(@class, "xe8uvvx") and '
            'contains(@class, "xdj266r") and '
            'contains(@class, "x11i5rnm") and '
            'contains(@class, "xat24cr") and '
            'contains(@class, "x1mh8g0r") and '
            'contains(@class, "xexx8yu") and '
            'contains(@class, "x4uap5") and '
            'contains(@class, "x18d9i69") and '
            'contains(@class, "xkhd6sd") and '
            'contains(@class, "x16tdsg8") and '
            'contains(@class, "x1hl2dhg") and '
            'contains(@class, "xggy1nq") and '
            'contains(@class, "x1a2a7pz") and '
            'contains(@class, "x1lku1pv") and '
            'contains(@class, "x12rw4y6") and '
            'contains(@class, "xrkepyr") and '
            'contains(@class, "x1citr7e") and '
            'contains(@class, "x37wo2f")'
            ']'
        )
        post_href = a_element.get_attribute("href")
        return post_href

    def publish_post(self, post:WebElement, text_post:str, url:str) -> bool:

        if (not self.db.contains_tweet(url)) and (not url.__contains__(f"/@{self.login}/")):

            
            if self.subject != None and not self.llm.determine_relevance_of_tweet(post_text=text_post, subject=self.subject):
                print(f"Post not relevant to the subject, skipping")
                return False

            try:
                button_reply = post.find_element(By.CSS_SELECTOR, 'svg[aria-label="Reply"]')
                button_reply.click()

                message = WebDriverWait(self.browser, 120).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 'div[aria-label="Empty text field. Type to compose a new post."]'
                    ))
                )
                # message = self.browser.find_element(
                #     By.CSS_SELECTOR, 'div[aria-label="Empty text field. Type to compose a new post."]'
                # )

                # actions = ActionChains(self.browser)
                # for char in text:
                #     actions.send_keys(char)
                #     time.sleep(0.1)  # невелика затримка між символами
                # actions.perform()

                time.sleep(1)


                # post_button.click()
                response = self.llm.generate_response(text_post)
                if response:
                    pyperclip.copy(response)
                    if sys.platform == 'darwin':
                        message.send_keys(Keys.COMMAND, 'v')
                    else:
                        message.send_keys(Keys.CONTROL, 'v')
                    print(f"Name: {self.login}")
                    time.sleep(3)

                    btns = WebDriverWait(self.browser, 5).until(
                            EC.presence_of_all_elements_located((
                                By.XPATH,
                                './/span['
                                'contains(@class, "x1rg5ohu") and '
                                'contains(@class, "x1f5funs") and '
                                'contains(@class, "x1uosm7l") and '
                                'contains(@class, "x1bl4301")'
                                ']'
                            ))
                        )

                    if len(btns) > 1:
                        btns[-1].click()
                        self.wait_for_publication()
                        self.db.insert_tweet(url, text_post, response)
                    else:
                        post_button = self.browser.find_element(By.XPATH, "//div[normalize-space(text())='Post']")
                        post_button.click()
                        self.wait_for_publication()
                        self.db.insert_tweet(url, text_post, response)
                return True
            except Exception as e:
                print("Error publishing post:", e)
        return False

    def wait_for_publication(self):
        try:
            # Wait for either success or failure message
            element = WebDriverWait(self.browser, 120).until(
                EC.any_of(
                    EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Posted']")),
                    EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Post failed to upload']"))
                )
            )

            # Check which element was found
            if element.text == "Posted":
                print("Post successfully published")
            elif element.text == "Post failed to upload":
                print("Post failed to upload")
                print("Досягнуто ліміт публікацій!")
                print("Завершую роботу програми...\n\n")
                self.browser.quit()
                sys.exit()
        except:
            print("Виникла помилка під час очікування публікації\n\n")

    def view_the_post(self) -> bool:
        #x1ypdohk x1n2onr6 xvuun6i x3qs2gp x1w8tkb5 x8xoigl xz9dl7a
        elements = self.browser.find_elements(
            By.XPATH,
            '//div['
            'contains(@class, "x1ypdohk") and '
            'contains(@class, "x1n2onr6") and '
            'contains(@class, "xvuun6i") and '
            'contains(@class, "x3qs2gp") and '
            'contains(@class, "x1w8tkb5") and '
            'contains(@class, "x8xoigl") and '
            'contains(@class, "xz9dl7a")'
            ']'
        )
        #Лінія: x1vf43f7 xm3z3ea x1x8b98j x131883w x16mih1h x5yr21d x10l6tqk xfo62xy
        number_of_published_comments = 0
        for element in elements:
            line = element.find_elements(
                By.XPATH,
                './/div['
                'contains(@class, "x1vf43f7") and '
                'contains(@class, "xm3z3ea") and '
                'contains(@class, "x1x8b98j") and '
                'contains(@class, "x131883w") and '
                'contains(@class, "x16mih1h") and '
                'contains(@class, "x5yr21d") and '
                'contains(@class, "x10l6tqk") and '
                'contains(@class, "xfo62xy")'
                ']'
            )

            if len(line) == 0:
                time.sleep(7)
                post_text = self.get_text_post(element)
                url = self.get_post_href(element)
                text = post_text.text
                if text.endswith("Translate"):
                    text = text[:-len("Translate")].strip()

                if number_of_published_comments >= self.maximum_number_of_posts_in_a_row:
                    return False

                self.browser.execute_script(
                    "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });", element
                )

                is_publish = self.publish_post(element, text, url)
                if is_publish:
                    number_of_published_comments += 1
        return True

    def publish_post_to_the_main_page(self):
        time.sleep(27)

        if self.freq == 0 or self.topic == None:
            return
        if not self.db.is_last_post_older_than(self.login, self.freq):
            print("Пост нещодавно опублікований, пропускаємо...")
            return

        bio = self.get_bio()
        # Використання CSS-селектора для натискання на посилання з href="/search"
        post_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Post']"))
        )
        post_button.click()

        message = WebDriverWait(self.browser, 120).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'div[aria-label="Empty text field. Type to compose a new post."]'
            ))
        )

        posts = self.db.get_only_posts(self.login)

        response =  self.llm.generate_user_post(topic=self.topic, bio=bio, posts=posts)

        post_button = self.browser.find_elements(By.XPATH, "//div[normalize-space(text())='Post']")

        if response:
            pyperclip.copy(response)
            if sys.platform == 'darwin':
                message.send_keys(Keys.COMMAND, 'v')
            else:
                message.send_keys(Keys.CONTROL, 'v')
            time.sleep(3)
            post_button[1].click()
            self.wait_for_publication()
            self.db.insert_user_post(self.login, response)
        self.go_to_home()

    def get_bio(self) -> str:
        # Отримуємо біо з бази даних
        profile = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='/@{self.login}']"))
        )
        profile.click()

        div_bio = self.browser.find_element(By.XPATH, "//div[contains(@class, 'xw7yly9')]")
        bio = div_bio.text
        time.sleep(7)
        return bio

    def surfing_the_news_feed(self):
        # Process news feed by scrolling each element into view individually
        if not self.surfing_login and not self.feed_keywords:
            return

        scroll_pause = 3
        processed_elements = 0
        elements_processed_since_last_check = 0
        max_elements_without_scroll = self.surfing_count

        while True:
            # Get current elements
            elements = self.browser.find_elements(
                By.XPATH,
                '//div['
                'contains(@class, "x1ypdohk") and '
                'contains(@class, "x1n2onr6") and '
                'contains(@class, "xvuun6i") and '
                'contains(@class, "x3qs2gp") and '
                'contains(@class, "x1w8tkb5") and '
                'contains(@class, "x8xoigl") and '
                'contains(@class, "xz9dl7a")'
                ']'
            )

            # Process each element by scrolling it into view
            for i, element in enumerate(elements):
                if i < processed_elements:
                    continue  # Skip already processed elements

                # Scroll element into view (top of viewport)
                self.browser.execute_script(
                    "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });",
                    element
                )

                # Wait for any dynamic content to load
                time.sleep(scroll_pause)

                if self.surfing_login:
                    self.author_check(post=element, previous=elements[i-1] if i > 0 else None)

                if self.feed_keywords:
                    self.keywords_check(post=element, previous=elements[i-1] if i > 0 else None)

                # Check if we need to break due to element limit
                elements_processed_since_last_check += 1
                if elements_processed_since_last_check >= max_elements_without_scroll:
                    print("Checking for new content after scrolling multiple elements")
                    elements_processed_since_last_check = 0
                    break

                processed_elements += 1

                # Optional: limit maximum number of elements to process
                if processed_elements > 100:  # Adjust based on needs
                    print("Reached maximum number of elements to process")
                    return True

            # If no new elements were processed in this iteration
            if elements_processed_since_last_check == 0:
                print("No new elements found after scrolling")
                return True

            elements_processed_since_last_check = 0
            time.sleep(scroll_pause)

        return True

    def author_check(self, post:WebElement, previous:WebElement | None) -> bool:
        if previous:
            #Лінія: x1vf43f7 xm3z3ea x1x8b98j x131883w x16mih1h x5yr21d x10l6tqk xfo62xy
            element_line = previous.find_elements(
                By.XPATH,
                './/div['
                'contains(@class, "x1vf43f7") and '
                'contains(@class, "xm3z3ea") and '
                'contains(@class, "x1x8b98j") and '
                'contains(@class, "x131883w") and '
                'contains(@class, "x16mih1h") and '
                'contains(@class, "x5yr21d") and '
                'contains(@class, "x10l6tqk") and '
                'contains(@class, "xfo62xy")'
                ']'
            )
            if len(element_line) > 0: return False

        url = self.get_post_href(post)

        if (not self.db.has_user_commented(login=self.login, tweet_url=url)) and (url.__contains__(f"/@{self.surfing_login}/")):
            time.sleep(11)
            post_text = self.get_text_post(post).text
            if post_text.endswith("Translate"):
                post_text = post_text[:-len("Translate")].strip()
            self.like_and_reply(post=post, url=url, post_text=post_text, sys_prompt=self.surfing_sys_prompt)
            return True
        return False

    def like_and_reply(self, post:WebElement, url:str, post_text:str, sys_prompt:str | None):

        button_like = post.find_element(By.CSS_SELECTOR, 'svg[aria-label="Like"]')
        button_like.click()

        time.sleep(5)

        if self.to_write_comment():
            button_reply = post.find_element(By.CSS_SELECTOR, 'svg[aria-label="Reply"]')
            button_reply.click()

            message = WebDriverWait(self.browser, 120).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 'div[aria-label="Empty text field. Type to compose a new post."]'
                ))
            )

            response = self.llm.short_reply(text_post=post_text, sys_prompt=sys_prompt)

            if response:
                pyperclip.copy(response)
                if sys.platform == 'darwin':
                    message.send_keys(Keys.COMMAND, 'v')
                else:
                    message.send_keys(Keys.CONTROL, 'v')
                time.sleep(5)

                # x1rg5ohu x1f5funs x1uosm7l x1bl4301

                try:
                    elements = WebDriverWait(self.browser, 5).until(
                        EC.presence_of_all_elements_located((
                            By.XPATH,
                            './/span['
                            'contains(@class, "x1rg5ohu") and '
                            'contains(@class, "x1f5funs") and '
                            'contains(@class, "x1uosm7l") and '
                            'contains(@class, "x1bl4301")'
                            ']'
                        ))
                    )
                    if elements:
                        btn_reply = elements[-1]
                        btn_reply.click()
                    else:
                        raise Exception("No reply buttons found")
                    self.wait_for_publication()
                    self.db.insert_comment(login=self.login, url=url)
                except:
                    post_buttons = self.browser.find_elements(By.XPATH, "//div[normalize-space(text())='Post']")
                    if len(post_buttons) > 1:
                        post_buttons[1].click()
                    else:
                        post_buttons[0].click()

                    self.wait_for_publication()
                    self.db.insert_comment(login=self.login, url=url)
        else:
            self.db.insert_comment(login=self.login, url=url)
        pass

    def to_write_comment(self) -> bool:
        return random.random() < 0.9

    def keywords_check(self, post:WebElement, previous:WebElement | None) -> bool:
        if previous:
            #Лінія: x1vf43f7 xm3z3ea x1x8b98j x131883w x16mih1h x5yr21d x10l6tqk xfo62xy
            element_line = previous.find_elements(
                By.XPATH,
                './/div['
                'contains(@class, "x1vf43f7") and '
                'contains(@class, "xm3z3ea") and '
                'contains(@class, "x1x8b98j") and '
                'contains(@class, "x131883w") and '
                'contains(@class, "x16mih1h") and '
                'contains(@class, "x5yr21d") and '
                'contains(@class, "x10l6tqk") and '
                'contains(@class, "xfo62xy")'
                ']'
            )
            if len(element_line) > 0: return False

        url = self.get_post_href(post)

        post_text = self.get_text_post(post).text
        if post_text.endswith("Translate"):
            post_text = post_text[:-len("Translate")].strip()

        if (not self.db.has_user_commented(login=self.login, tweet_url=url)) and (self.check_keywords_in_post(post_text)):
            time.sleep(11)
            sp = None
            if self.kt:
                language = self.detect_language(post_text)
                sp = self.llm.prompt.format(language)
            else:
                sp = self.surfing_sys_prompt
            self.like_and_reply(post=post, url=url, post_text=post_text, sys_prompt=sp)
            return True
        return False

    def check_keywords_in_post(self, post_text: str) -> bool:
        #Check if post_text contains any keyword from feed_keywords (case-insensitive)
        for keyword in self.feed_keywords:
            if keyword.lower() in post_text.lower():
                print(f"keyword: {keyword}")
                return True
        return False
