from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage

from components.generate import BaseGenerator
from utils.prompts import reflection_instruction
from utils.state import State

class ReflectionSchema(BaseModel):
    knowledge_gap:str = Field(
        description="Identify knowledge gaps in the model's answer"
    )
    questions:str = Field(
        description="Write questions to better clarify the model's answer"
    )

class Reflector(BaseGenerator):
    def __init__(self, model, api_url, api_key) -> None:
        super().__init__(model, api_url, api_key)

        self.set_system_prompt(reflection_instruction)
        self.set_json_schema(ReflectionSchema)

    def reflection(self, state:State):
        question = state['question']
        answer = state['messages'][-1].content
        context = state['context']

        message = HumanMessage(f"""1. User question: {question},
            2. Model answer: {answer}, 
            3. Identify a knowledge gap based on  context: {context}'""")
        
        
        result = self.generate_json_output([message])

        
        state['reflection_loop'] += 1
        
        return {
            'messages': HumanMessage(content=result['knowledge_gap'] + "\n" + result['questions']), 
            'reflection_loop': state['reflection_loop'], 
        }