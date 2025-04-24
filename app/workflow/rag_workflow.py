import time

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph


from components.router import Router
from components.llm import LLM
from components.retriever import Retriever
from components.reranker import Reranker
from components.rewriter import RewriterQuestion
from components.reflection import Reflector
from components.generate import BaseGenerator

from utils.trim_messages import trim_message_history
from utils.state import State

class RAGWorkflow:
    def __init__(self, config_1, config_2) -> None:

        self.generator = LLM(**config_1)
        self.router = Router(**config_1)
        self.retriever = Retriever(**config_2)
        self.reranker = Reranker()
        self.reflector = Reflector(**config_1)
        self.rewriter = RewriterQuestion(**config_1)

        # self.grader = grader

        self.base_generator = BaseGenerator(**config_1)

        self.graph = self.create_graph()

    def generate_conversation_title(self, messages):
        result = self.base_generator.generate_text_output(messages)
        return result.content


    def create_graph(self):
        builder = StateGraph(State)
        
        builder.add_node('router', self.router.route_query)
        builder.add_node('retrieve', self.retriever.retrieve)
        builder.add_node('rerank', self.reranker.bm25_reranker)
        builder.add_node('generate', self.generator.generate)
        builder.add_node('reflection', self.reflector.reflection)

        builder.add_edge(START, 'router')
        builder.add_edge('router', 'retrieve')
        builder.add_edge('retrieve', 'rerank')

        
        builder.add_edge('rerank', 'generate')
        builder.add_conditional_edges(
            'generate',
            self.should_continue
        )
        builder.add_edge('reflection', 'generate')


        graph = builder.compile(checkpointer=MemorySaver())
        return graph

    def send_message(self, messages, temperature, chat_id, d_descriptions_domen):
        self.generator.set_temperature(temperature)

        messages = trim_message_history(messages)

        question = self.rewriter.rewrite_question(messages)
        messages[-1]['content'] = question

        result = self.graph.invoke(
            input={
                "question": question,
                "messages": messages,
                "d_descriptions_domens": d_descriptions_domen
            },
            config={
                "configurable": {
                    "thread_id": chat_id,
                }
            }
        )

        answer = result['messages'][-1].content
        for token in answer:
            yield token
            time.sleep(0.02)
        
    def should_continue(self, state:State):
        if state['reflection_loop'] <= 1 and state['is_need_reflection']:
            return 'reflection'
        else:
            return END