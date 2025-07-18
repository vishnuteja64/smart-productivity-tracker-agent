from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from models import TrackerState, Task

load_dotenv()
llm = ChatGroq(model_name="llama3-8b-8192", temperature=0.3)

def add_task_node(state: TrackerState) -> TrackerState:
    return state

def advisor_node(state: TrackerState) -> TrackerState:
    tasks_text = "\n".join([f"{t.title} ({t.priority}, {t.hours}h)" for t in state.task_list])
    msg = llm.invoke([HumanMessage(content=f"Here are today's tasks:\n{tasks_text}\nSuggest how to optimize.")])
    state.suggestions = msg.content
    return state

def summary_node(state: TrackerState) -> TrackerState:
    completed = [t for t in state.task_list if t.status == "Completed"]
    total_hours = sum(t.hours for t in completed)
    state.summary = f"✅ Completed {len(completed)} tasks.\n⏱️ Total time: {total_hours} hrs.\n\n🧠 Suggestions: {state.suggestions}"
    return state

graph = StateGraph(TrackerState)
graph.add_node("AddTask", add_task_node)
graph.add_node("Advisor", advisor_node)
graph.add_node("Summary", summary_node)

graph.set_entry_point("AddTask")
graph.add_edge("AddTask", "Advisor")
graph.add_edge("Advisor", "Summary")
graph.add_edge("Summary", END)

runnable_graph = graph.compile()
