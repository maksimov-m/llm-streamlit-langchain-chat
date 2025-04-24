import json


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.prompts import base_generator_model

from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    answer:str = Field(
        description="Answer the question"
    )

class BaseGenerator:
    def __init__(self, model, api_url, api_key) -> None:
        self.__llm = ChatOpenAI(
            model=model,
            base_url=api_url,
            api_key=api_key,
            temperature=0,
            extra_body={"guided_json": BaseSchema.model_json_schema()}
        )

        self.__system_prompt = ChatPromptTemplate.from_messages([
                ("system", base_generator_model),
                MessagesPlaceholder("messages")
            ])

        self.__generate = self.__llm

    def set_temperature(self, temp):
        self.__llm.temperature = temp
    
    def set_system_prompt(self, system_prompt):
        self.__system_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("messages")
            ])
        
        self.__generate = self.__system_prompt | self.__llm

    def set_json_schema(self, schema):
        self.__llm.extra_body = {"guided_json": schema.model_json_schema()}

    def set_generate(self, generate):
        self.__generate = generate

    def get_llm(self):
        return self.__llm
    
    def get_system_prompt(self):
        return self.__system_prompt
        
    def generate_json_output(self, messages):
        response = self.__generate.invoke(messages)
        
        result = json.loads(response.content)

        return result
    
    def generate_text_output(self, messages):
        llm = self.__llm
        llm.extra_body = None

        generate = self.__system_prompt | llm

        return generate.invoke(messages)
