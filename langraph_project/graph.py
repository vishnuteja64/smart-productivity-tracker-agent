from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from datetime import date

from models import TrackerState, Task

# Load environment and initialize LLM
load_dotenv()
llm = ChatGroq(model_name="llama3-8b-8192", temperature=0.3)

# Node: AddTask (placeholder, input handled in app.py)
def add_task_node(state: TrackerState) -> TrackerState:
    return state

# Node: Advisor (LLM-based suggestions)
def advisor_node(state: TrackerState) -> TrackerState:
    tasks_text = "\n".join([
        f"{t.title} ({t.priority}, {t.hours}h | {t.date.strftime('%Y-%m-%d')})"
        for t in state.task_list
    ])
    msg = llm.invoke([
        HumanMessage(
            content=f"Here are today's tasks:\n{tasks_text}\nSuggest how to optimize."
        )
    ])
    state.suggestions = msg.content
    return state

# Node: Summary (builds daily summary)
def summary_node(state: TrackerState) -> TrackerState:
    completed = [t for t in state.task_list if t.status == "Completed"]
    total_hours = sum(t.hours for t in completed)
    comments = [t.completion_comment for t in completed if t.completion_comment]
    state.summary = (
        f"✅ Completed {len(completed)} tasks."
        f"\n⏱️ Total time: {total_hours} hrs."
        f"\n💬 Comments: {('; '.join(comments) if comments else 'None')}"
        f"\n🧠 Suggestions: {state.suggestions}"
    )
    return state

# Build graph
graph = StateGraph(TrackerState)
graph.add_node("AddTask", add_task_node)
graph.add_node("Advisor", advisor_node)
graph.add_node("Summary", summary_node)

graph.set_entry_point("AddTask")
graph.add_edge("AddTask", "Advisor")
graph.add_edge("Advisor", "Summary")
graph.add_edge("Summary", END)

# Compile runnable graph
runnable_graph = graph.compile()