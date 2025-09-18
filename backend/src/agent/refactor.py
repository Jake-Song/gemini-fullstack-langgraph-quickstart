from agent.configuration import Configuration
from agent.state import (
    OverallState, 
    ReflectionState,
    QueryGenerationState, 
    WebSearchState, 
    SearchStateOutput) 
from agent.tools_and_schemas import (
    SearchQueryList, 
    Reflection
)
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class HumanMessage(BaseModel):
    role: str = "user"
    content: str

class AIMessage(BaseModel):
    role: str = "assistant"
    content: str

class WebSearchAgent:
    def __init__(self):
        from google.genai import Client
        client = Client()
        self.client = client
        self.config = Configuration()
        self.state = OverallState(
            messages=[],
            search_query=[],
            web_research_result=[],
            sources_gathered=[],
            initial_search_query_count=0,
            max_research_loops=0,
            research_loop_count=0,
            reasoning_model=None,
        )

    def generate(self, model: str, query: str) -> str:
        response = self.client.models.generate_content(
            model=model, 
            contents=query
        )
        
        ai_message = AIMessage(content=response.text)
        self.state["messages"].append(ai_message)
        return response.text

    def generate_structured(self, model: str, query: str, schema: str) -> str:
        response = self.client.models.generate_content(
            model=model, 
            contents=query,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )
        
        ai_message = AIMessage(content=response.text)
        self.state["messages"].append(ai_message)
        return response.parsed

    async def run(self, state: OverallState) -> dict:
        # check for custom initial search query count
        if state.get("initial_search_query_count") is None:
            self.state["initial_search_query_count"] = self.config.number_of_initial_queries
        else:
            self.state["initial_search_query_count"] = state["initial_search_query_count"]

        self.state["messages"].append(state["messages"])
        
        return await self.step()
                                
    async def step(self) -> dict:
        return await self.generate_query()
                 
    async def generate_query(self) -> dict:
               
        model = self.config.query_generator_model

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = query_writer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(self.state["messages"]),
            number_queries=self.state["initial_search_query_count"],
        )
        # Generate the search queries
        result = self.generate_structured(model, formatted_prompt, SearchQueryList)
        self.state["search_query"] = result.query

        return await self.continue_to_web_research({"search_query": result.query})
        
    async def continue_to_web_research(
        self, 
        state: QueryGenerationState | ReflectionState) -> dict:
        
        if state.get("search_query") is None:
            arr = state["follow_up_queries"]
            base = int(state["number_of_ran_queries"] or 0)
            tasks = [
                self.web_research({"search_query": q, "id": base + i})
                for i, q in enumerate(arr)
            ]
        else:
            arr = state["search_query"]
            tasks = [
                self.web_research({"search_query": q, "id": i})
                for i, q in enumerate(arr)
            ]

        await asyncio.gather(*tasks, return_exceptions=True)
        return await self.reflection()
                             
                
    async def web_research(self, state: WebSearchState):
        def _call():
            formatted = web_searcher_instructions.format(
                current_date=get_current_date(),
                research_topic=state["search_query"],
            )
            return self.client.models.generate_content(
                model=self.config.query_generator_model,
                contents=formatted,
                config={"tools": [{"google_search": {}}], "temperature": 0},
            )

        response = await asyncio.to_thread(_call)  # offload blocking call

        # resolve the urls to short urls for saving tokens and time
        resolved_urls = resolve_urls(
            response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
        )
        # Gets the citations and adds them to the generated text
        citations = get_citations(response, resolved_urls)
        modified_text = insert_citation_markers(response.text, citations)
        sources_gathered = [item for citation in citations for item in citation["segments"]]
        
        self.state["sources_gathered"] = self.state["sources_gathered"] + sources_gathered
        self.state["search_query"] = self.state["search_query"] + [state["search_query"]]
        self.state["web_research_result"] = self.state["web_research_result"] + [modified_text]
        
       
    async def reflection(self) -> dict:
        
        # Increment the research loop count and get the reasoning model
        self.state["research_loop_count"] = self.state.get("research_loop_count", 0) + 1
        if self.state.get("reasoning_model") is None:
            self.state["reasoning_model"] = self.config.reflection_model
        
        reasoning_model = self.state.get("reasoning_model") 

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = reflection_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(self.state["messages"]),
            summaries="\n\n---\n\n".join(self.state["web_research_result"]),
        )
       
        result = self.generate_structured(reasoning_model, formatted_prompt, Reflection)
        
        return await self.evaluate_research({
            "is_sufficient": result.is_sufficient,
            "knowledge_gap": result.knowledge_gap,
            "follow_up_queries": result.follow_up_queries,
            "research_loop_count": self.state["research_loop_count"],
            "number_of_ran_queries": len(self.state["search_query"]),
        })
    
    async def evaluate_research(self, state: ReflectionState) -> dict | None:
        if state.get("max_research_loops") is None:
            self.state["max_research_loops"] = self.config.max_research_loops
        else:
            self.state["max_research_loops"] = state["max_research_loops"]
        
        if state["is_sufficient"] or state["research_loop_count"] >= self.state["max_research_loops"]:
            return await self.finalize_answer()
        else:
            await self.continue_to_web_research(state)
            
    
    async def finalize_answer(self) -> dict:
    
        reasoning_model = self.state.get("reasoning_model") or self.config.answer_model

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = answer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(self.state["messages"]),
            summaries="\n---\n\n".join(self.state["web_research_result"]),
        )

        result = self.generate(reasoning_model, formatted_prompt)
        # print("finalize_answer", result)
        # Replace the short urls with the original urls and add all used urls to the sources_gathered
        unique_sources = []
        for source in self.state["sources_gathered"]:
            if source["short_url"] in result:
                result = result.replace(
                    source["short_url"], source["value"]
                )
                unique_sources.append(source)
        
        # clean up the state
        self.state["search_query"] = []
        self.state["web_research_result"] = []
        self.state["sources_gathered"] = []
        
        return {
            "messages": [AIMessage(content=result)],
            "sources_gathered": unique_sources,
        }          
            