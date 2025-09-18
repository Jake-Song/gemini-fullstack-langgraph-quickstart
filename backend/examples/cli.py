import argparse
from agent.refactor import HumanMessage
from agent.refactor import WebSearchAgent
import asyncio
import time

async def main() -> None:
    """Run the research agent from the command line."""
    parser = argparse.ArgumentParser(description="Run the LangGraph research agent")
    parser.add_argument("question", help="Research question")
    parser.add_argument(
        "--initial-queries",
        type=int,
        default=3,
        help="Number of initial search queries",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=2,
        help="Maximum number of research loops",
    )
    parser.add_argument(
        "--reasoning-model",
        default="gemini-2.5-pro",
        help="Model for the final answer",
    )
    args = parser.parse_args()

    state = {
        "messages": HumanMessage(content=args.question),
        "initial_search_query_count": args.initial_queries,
        "max_research_loops": args.max_loops,
        "reasoning_model": args.reasoning_model,
    }
    agent = WebSearchAgent()    
    start_time = time.time()
    loop = asyncio.get_running_loop()

    print(loop)
    task = asyncio.current_task(loop)
    print(task)
    result = await agent.run(state)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    messages = result.get("messages", [])
    if messages:
        print(messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())
    
    
    