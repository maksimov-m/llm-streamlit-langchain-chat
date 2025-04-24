from langchain_core.messages import HumanMessage

from components.generate import BaseGenerator

from utils.state import State
from utils.prompts import router_instruction

from typing import Literal, List

from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


def create_route_model_class(data_sources: List[str]):
    """
    Фабрика классов для создания RouteQuery с динамическими значениями Literal
    """
    # Создаем общий Literal тип для всех полей
    DataSourceLiteral = Literal[tuple(data_sources)]  # type: ignore

    class DynamicRouteQuery(BaseModel):
        """Route a user query to the most relevant two datasource."""

        datasource_1: DataSourceLiteral = Field(  # type: ignore
                ...,
                description="Given a user question, choose which datasource would be most 1 relevant"
            )

        datasource_2: DataSourceLiteral = Field(  # type: ignore
            ...,
            description="Given a user question, choose which datasource would be most 2 relevant"
        )
        class Config:
                arbitrary_types_allowed = True

    return DynamicRouteQuery


class Router(BaseGenerator):
    def __init__(self, model, api_url, api_key) -> None:
        super().__init__(model, api_url, api_key)
        
        self.set_system_prompt(router_instruction)
        

    def route_query(self, state: State):
        # logger.warning(f"Message == {state["question"]}")
        
        message = HumanMessage(content=f""""{state['d_descriptions_domens']['descriptions']}, user's query: {state["question"]}""")

        DynamicRouteQuery = create_route_model_class(state['d_descriptions_domens']['domens'])
        self.set_json_schema(DynamicRouteQuery)

        result = self.generate_json_output([message])
        
        res = [result['datasource_1'], result['datasource_2']]

        return {"context_source": res}
