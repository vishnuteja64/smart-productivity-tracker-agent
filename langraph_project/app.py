import streamlit as st
from models import Task, TrackerState
from graph import runnable_graph

st.set_page_config(page_title="🧠 Smart Task Advisor", layout="centered")

st.title("📋 Daily Task Tracker with AI")

if "state" not in st.session_state:
    st.session_state.state = TrackerState()

with st.form("task_form"):
    title = st.text_input("📝 Task")
    priority = st.selectbox("📌 Priority", ["High", "Medium", "Low"])
    hours = st.number_input("⏱️ Estimated Hours", min_value=0.5, step=0.5)
    submitted = st.form_submit_button("➕ Add Task")

    if submitted and title:
        task = Task(title=title, priority=priority, hours=hours)
        st.session_state.state.task_list.append(task)
        st.success("Task added!")

if st.button("✅ Process & Get Suggestions"):
    result = runnable_graph.invoke(st.session_state.state.dict())
    st.session_state.state = TrackerState(**result)

if st.session_state.state.task_list:
    st.subheader("🗂️ Your Tasks")
    for idx, task in enumerate(st.session_state.state.task_list):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{task.title}** | {task.priority} | ⏱️ {task.hours} hrs")
        with col2:
            new_status = st.selectbox(
                f"Status {idx+1}",
                ["Not Completed", "Completed"],
                index=["Not Completed", "Completed"].index(task.status),
                key=f"status_{idx}"
            )
            st.session_state.state.task_list[idx].status = new_status

    st.subheader("🧠 Suggestions")
    st.markdown(st.session_state.state.suggestions or "No suggestions yet.")

    st.subheader("📊 Daily Summary")
    st.markdown(st.session_state.state.summary or "No summary yet.")
