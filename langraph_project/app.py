import streamlit as st
from models import Task, TrackerState
from graph import runnable_graph
from datetime import date
import json
from pathlib import Path

st.set_page_config(page_title="🧠 Smart Task Advisor", layout="centered")
st.title("📋 Daily Task Tracker with AI")

DATA_FILE = Path("tasks.json")

# Load or initialize state
if "state" not in st.session_state:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            data = json.load(f)
            st.session_state.state = TrackerState(**data)
    else:
        st.session_state.state = TrackerState()

# --- Add Task Form ---
with st.form("task_form"):
    title = st.text_input("📝 Task")
    priority = st.selectbox("📌 Priority", ["High", "Medium", "Low"])
    hours = st.number_input("⏱️ Estimated Hours", min_value=0.5, step=0.5)
    task_date = st.date_input("📅 Task Date", value=date.today())
    comment = st.text_area("🗒️ Task Comment (Optional)", height=50)
    submitted = st.form_submit_button("➕ Add Task")

    if submitted and title:
        task = Task(
            title=title,
            priority=priority,
            hours=hours,
            date=task_date,
            comment=comment or None
        )
        st.session_state.state.task_list.append(task)
        st.success("✅ Task added!")

# Save function
def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.state.dict(), f, default=str, indent=2)

# --- Process with AI ---
if st.button("✅ Process & Get Suggestions"):
    result = runnable_graph.invoke(st.session_state.state.dict())
    st.session_state.state = TrackerState(**result)
    save_tasks()
    st.success("✅ AI Suggestions updated.")

# --- Display Tasks ---
if st.session_state.state.task_list:
    st.subheader("🗂️ Your Tasks")
    for idx, task in enumerate(st.session_state.state.task_list):
        with st.expander(
            f"{task.title} | {task.priority} | ⏱️ {task.hours} hrs | 📅 {task.date.strftime('%Y-%m-%d')}"
        ):
            st.markdown(f"**📌 Priority:** {task.priority}")
            st.markdown(f"**⏱️ Estimated Hours:** {task.hours}")
            st.markdown(f"**📅 Task Date:** {task.date}")
            st.markdown(f"**📝 Comment:** {task.comment or 'No comment'}")
            st.markdown(f"**📍 Status:** {task.status}")

            # Status update
            new_status = st.selectbox(
                f"Update Status", ["Not Completed", "Completed"],
                index=["Not Completed", "Completed"].index(task.status),
                key=f"status_{idx}"
            )
            if new_status != task.status:
                st.session_state.state.task_list[idx].status = new_status
                reason = st.text_area(
                    f"🧾 Completion Comment", value=task.completion_comment or "",
                    key=f"completion_{idx}"
                )
                st.session_state.state.task_list[idx].completion_comment = reason

            # Delete
            if st.button("🗑️ Delete", key=f"del_{idx}"):
                st.session_state.state.task_list.pop(idx)
                save_tasks()
                st.experimental_rerun()

    # Always save after any changes
    save_tasks()

    # Suggestions & Summary
    st.subheader("🧠 AI Suggestions")
    st.markdown(st.session_state.state.suggestions or "No suggestions yet.")

    st.subheader("📊 Daily Summary")
    st.markdown(st.session_state.state.summary or "No summary yet.")
