import streamlit as st
from models import Task, TrackerState
from graph import runnable_graph
from datetime import date
import json
from pathlib import Path

st.set_page_config(page_title="🧠 Smart Task Advisor", layout="centered")
st.title("📋 Daily Task Tracker with AI")

DATA_FILE = Path("tasks.json")

# Helpers: save/load JSON with date handling
def save_tasks(state: TrackerState):
    def default(o):
        from datetime import date as _date
        if isinstance(o, _date):
            return o.isoformat()
        return o
    with open(DATA_FILE, "w") as f:
        json.dump(state.dict(), f, default=default, indent=2)


def load_tasks() -> TrackerState:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            data = json.load(f)
            # Pydantic will parse date strings into date objects
            return TrackerState(**data)
    return TrackerState()

# Load or initialize state
if "state" not in st.session_state:
    st.session_state.state = load_tasks()

# --- Add Task Form ---
with st.form("task_form"):
    title = st.text_input("📝 Task")
    priority = st.selectbox("📌 Priority", ["High", "Medium", "Low"])
    hours = st.number_input("⏱️ Estimated Hours", min_value=0.5, step=0.5)
    task_date = st.date_input("📅 Task Date", value=date.today())
    comment = st.text_area("🗒️ Task Comment (Optional)", height=50)
    submitted = st.form_submit_button("➕ Add Task")

    if submitted and title:
        new_task = Task(
            title=title,
            priority=priority,
            hours=hours,
            date=task_date,
            comment=comment or None
        )
        st.session_state.state.task_list.append(new_task)
        save_tasks(st.session_state.state)
        st.success("✅ Task added!")

# --- Process with AI ---
if st.button("✅ Process & Get Suggestions"):
    result = runnable_graph.invoke(st.session_state.state.dict())
    st.session_state.state = TrackerState(**result)
    save_tasks(st.session_state.state)
    st.success("✅ AI Suggestions updated.")

# --- Display Tasks ---
if st.session_state.state.task_list:
    st.subheader("🗂️ Your Tasks")
    for idx, task in enumerate(st.session_state.state.task_list):
        # Ensure date attribute is date object
        task_date = task.date if isinstance(task.date, date) else date.fromisoformat(task.date)
        with st.expander(
            f"{task.title} | {task.priority} | ⏱️ {task.hours} hrs | 📅 {task_date}"
        ):
            st.markdown(f"**📌 Priority:** {task.priority}")
            st.markdown(f"**⏱️ Estimated Hours:** {task.hours}")
            st.markdown(f"**📅 Task Date:** {task_date}")
            st.markdown(f"**📝 Comment:** {task.comment or 'No comment'}")
            st.markdown(f"**📍 Status:** {task.status}")

            # Status update
            new_status = st.selectbox(
                f"Update Status #{idx}", ["Not Completed", "Completed"],
                index=["Not Completed", "Completed"].index(task.status),
                key=f"status_{idx}"
            )
            if new_status != task.status:
                st.session_state.state.task_list[idx].status = new_status
                if new_status == "Completed":
                    completion = st.text_area(
                        f"🧾 Completion Comment #{idx}",
                        value=task.completion_comment or "",
                        key=f"completion_{idx}"
                    )
                    st.session_state.state.task_list[idx].completion_comment = completion
                save_tasks(st.session_state.state)

            # Delete
            if st.button("🗑️ Delete", key=f"del_{idx}"):
                st.session_state.state.task_list.pop(idx)
                save_tasks(st.session_state.state)
                st.experimental_rerun()

    # Suggestions & Summary
    st.subheader("🧠 AI Suggestions")
    st.markdown(st.session_state.state.suggestions or "No suggestions yet.")

    st.subheader("📊 Daily Summary")
    st.markdown(st.session_state.state.summary or "No summary yet.")
```
