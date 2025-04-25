
from openai import OpenAI
import traceback
from prompt import SYSTEM_PROMPT, LANGUAGE_PROMPT
class LLM_Wrapper:
    def __init__(self, api_key:str):
        self.model_name = "gpt-4.1-mini"
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, user_post: str) -> str:
        print(f"Post: {user_post}")
        # Placeholder for generating a response
        language = self.detect_language(user_post)
        print(f"Language: {language}")
        result_text = None
        try:
            response = self.client.responses.create(
                model=self.model_name,
                instructions=SYSTEM_PROMPT.format(language),
                input=user_post,
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
                model=self.model_name,
                instructions=LANGUAGE_PROMPT,
                input=text,
            )
            return response.output_text
        except:
            traceback.print_exc()
        return "English"