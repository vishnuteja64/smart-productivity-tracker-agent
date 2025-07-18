from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LLM Setup
llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192")

# ---- TOOL ----
@tool
def add_task(task: str, priority: str = "medium"):
    """
    Add a task with a given priority to the task list.
    """
    return f"✅ Task Added: '{task}' with priority '{priority}'"

# ---- NODES ----
def add_task_node(state):
    task = state.get("task")
    result = add_task.run(task)
    return {
        **state,
        "task_list": state.get("task_list", []) + [task],
        "history": state.get("history", "") + "\n" + result
    }

def advisor_node(state):
    tasks = state["task_list"]
    msg = llm.invoke([
        HumanMessage(
            content=f"Here are my tasks for the day: {tasks}. Suggest how I can optimize my day or improve focus."
        )
    ])
    return {**state, "suggestions": msg.content}

def summary_node(state):
    tasks = state["task_list"]
    suggestions = state["suggestions"]
    summary = f"""
    📅 Daily Summary:
    - Tasks done: {len(tasks)}
    - Suggestions: {suggestions}
    """
    return {**state, "summary": summary}

# ---- GRAPH ----
class TrackerState(dict):
    task_list: list
    suggestions: str
    summary: str
    history: str

graph = StateGraph(TrackerState)

graph.add_node("AddTask", add_task_node)
graph.add_node("Advisor", advisor_node)
graph.add_node("Summary", summary_node)

graph.set_entry_point("AddTask")
graph.add_edge("AddTask", "Advisor")
graph.add_edge("Advisor", "Summary")
graph.add_edge("Summary", END)

# Compile graph
runnable_graph = graph.compile()
