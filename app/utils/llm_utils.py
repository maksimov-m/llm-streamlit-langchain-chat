from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from openai import OpenAIError
import time
class LLMAgent:
    def __init__(self, model, model_provider, api_url, api_key):
        self.llm = init_chat_model(
            model=model,
            model_provider=model_provider,
            base_url=api_url,
            api_key=api_key,
        )
        
        self.graph = self.create_graph()
    
    def call_model(self, state: MessagesState):
        response = self.llm.invoke(state["messages"])
        return {"messages": response}

    def create_graph(self):
        builder = StateGraph(state_schema=MessagesState)
        builder.add_node('call_model', self.call_model)
        builder.add_edge(START, 'call_model')
        graph = builder.compile(checkpointer=MemorySaver())
        return graph
    
    def validate_model(self):
        try:
            self.llm.invoke("test")
            return True
        except OpenAIError:
            return False
        
    def send_message(self, messages, temperature, chat_id):
        self.llm.temperature = temperature
        stream = self.graph.stream(
            input={"messages": messages}, 
            config= {
                "configurable": {
                    "thread_id": chat_id,
                    }
            },
            stream_mode="messages"
        )
        
        for msg, metadata in stream:
            yield msg.content
            time.sleep(0.02)
