import streamlit as st
from tracker_agent import runnable_graph

st.set_page_config(page_title="Smart Task Tracker", layout="centered")
st.title("🧠 Smart Task Tracker Agent")

task = st.text_input("📌 Enter your task for today")

if st.button("➕ Add Task & Get Advice"):
    if task:
        initial_state = {"task": task, "task_list": [task]}
        result = runnable_graph.invoke(initial_state)
        st.success("✅ Task Tracked Successfully!")
        st.subheader("📊 Daily Summary")
        st.markdown(result["summary"])
    else:
        st.error("⚠️ Please enter a task first.")
