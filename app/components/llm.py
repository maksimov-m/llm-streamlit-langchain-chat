from pydantic import BaseModel, Field

from components.generate import BaseGenerator
from utils.prompts import rag_generation_instruction

from utils.state import State

class LLMAnswerSchema(BaseModel):
    answer:str = Field(
        description="Answer the question based on context"
    )
    is_need_reflection:bool = Field(
        description="If the question is complex, you need to go for reflection. Answer True if it is necessary to reflect and False if it is not necessary to do so"
    )

class LLM(BaseGenerator):
    def __init__(self, model, api_url, api_key) -> None:
        super().__init__(model, api_url, api_key)

        self.set_system_prompt(rag_generation_instruction)
        self.set_json_schema(LLMAnswerSchema)


    def generate(self, state:State):
        length = len(state['messages'])
        if length > 5:
            length = 5

        state['messages'][-1].content = f"""Question: {state['question']}
            Context: {state['context']}

            Message history: {state['messages'][-length:]}
        """

        result = self.generate_json_output({'messages': state['messages']})

        if 'reflection_loop' not in state.keys():
            state['reflection_loop'] = 0
        
        return {"messages": result['answer'], "reflection_loop": state['reflection_loop'], "is_need_reflection": result['is_need_reflection']}

    
