
from openai import OpenAI
import traceback
from db_tweets import Tweets_DataBase
from prompt import SYSTEM_PROMPT, LANGUAGE_PROMPT, BIO_PROMPT, TOPIC_PROMPT, SELECT_POST_PROMPT, NEW_POSTS, SYSTEM_PROMPT_SHORT_REPLY

class LLM_Wrapper:
    def __init__(self, api_key:str, prompt:str | None = None):
        self.model_name_4o_mini = "gpt-4o-mini"
        self.model_name_4_1_mini = "gpt-4.1-mini"
        self.model_name_o4_mini = "o4-mini"
        self.model_name_4_1 = "gpt-4.1"
        self.client = OpenAI(api_key=api_key)
        self.prompt = prompt

    def generate_response(self, user_post: str) -> str | None:
        print(f"Post: {user_post}")
        # Placeholder for generating a response
        language = self.detect_language(user_post)
        print(f"Language: {language}")
        result_text = None
        try:
            response = self.client.responses.create(
                model=self.model_name_4o_mini,
                instructions= self.prompt.format(language) if self.prompt != None else SYSTEM_PROMPT.format(language),
                input=user_post,
                temperature=2.0,
            )
            # completion = openai.ChatCompletion.create(
            #     model = self.model_name,
            #     messages = messages
            # )
            # print(f"Completion: {completion}")
            result_text = response.output_text
        except:
            traceback.print_exc()
        print(f"Response: {result_text}")
        return result_text

    def detect_language(self, text: str) -> str:
        # Placeholder for language detection
        try:
            response = self.client.responses.create(
                model=self.model_name_4o_mini,
                instructions=LANGUAGE_PROMPT,
                input=text,
            )
            return response.output_text
        except:
            traceback.print_exc()
        return "English"

    def generate_user_post(self, topic: str, bio: str, posts: list[str]) -> str | None:
        # Формуємо історію постів у потрібному форматі
        posts = [post for post in posts if post is not None]
        if not posts:
            history = "No history yet."
        else:
            history = "\n\n".join(
                ["Post " + str(i+1) + ":\n" + post.replace('\n', '') for i, post in enumerate(posts)]
            )
        try:
            response = self.client.responses.create(
                model=self.model_name_4_1,
                instructions=BIO_PROMPT.format(bio),
                input=TOPIC_PROMPT.format(history, topic),
                temperature=2.0
            )
            return self.select_top_post(response.output_text)
        except:
            traceback.print_exc()
        return None

    def select_top_post(self, posts: str) -> str | None:
        # Placeholder for selecting the top post
        try:
            response = self.client.responses.create(
                model=self.model_name_o4_mini,
                instructions=SELECT_POST_PROMPT,
                input=NEW_POSTS.format(posts),
            )
            return response.output_text
        except:
            traceback.print_exc()
        return None

    def short_reply(self, text_post:str, sys_prompt:str | None):
        try:
            response = self.client.responses.create(
                model=self.model_name_4_1_mini,
                instructions=sys_prompt if sys_prompt else SYSTEM_PROMPT_SHORT_REPLY,
                input=text_post,
                temperature=2.0,
            )
            return response.output_text
        except:
            traceback.print_exc()
        return None
