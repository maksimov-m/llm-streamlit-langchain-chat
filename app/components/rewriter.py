from pydantic import BaseModel, Field

from components.generate import BaseGenerator


class RewrittenQuestion(BaseModel):
    is_clarifying:bool = Field(
        description="Is this question clarifying or is this a normal conversation? Return True if it clarifying and False for normal"
    )
    question:str = Field(
        description="Re-word the question if it is clarifying, to improve the vector database search based on the post history, or leave it unchanged if it is just plain conversational"
    )

class RewriterQuestion(BaseGenerator):
    def __init__(self, model, api_url, api_key):
        super().__init__(model, api_url, api_key)

        self.set_json_schema(RewrittenQuestion)
        # self.set_system_prompt(rewriter_question_instruction)

    def rewrite_question(self, messages):
        question = messages[-1]['content']
        length = len(messages)

        if length > 5:
            length = 5

        messages[-1]['content'] = f"""Reformulate the question, 
        if it seems to be clarifying for vector database search. Use the message history.
        If the user decides to communicate with you out of context, don't change their query

        Return must be reformulated question without reasoning or user query without changing.
        
        Question: {messages[-1]['content']}

        Messages history: {messages[-length:]}"""


        result = self.generate_json_output(messages)

        if result['is_clarifying']:
            return result['question']
        else:
            return question
