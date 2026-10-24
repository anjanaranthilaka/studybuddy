"""
app.py - Streamlit Web Interface for StudyBuddy AI.
Provides chat memory, live tool trace expanders, and persistent database dashboards.
"""
import streamlit as st
import json
from agents.agent import StudyBuddyAgent
from database.db import init_db, get_topic_analytics, get_latest_study_plan

st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🎓",
    layout="wide"
)

# Initialize database schema
init_db()

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = StudyBuddyAgent()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==============================================================================
# Sidebar: Persistent Database Analytics & Revision Schedule
# ==============================================================================
with st.sidebar:
    st.title("🎓 StudyBuddy Dashboard")
    st.caption("Local LLM Agent using Ollama & SQLite")
    
    if st.button("🔄 Clear Conversation Memory", use_container_width=True):
        st.session_state.agent.reset_conversation()
        st.session_state.chat_messages = []
        st.rerun()

    st.divider()
    st.subheader("📊 Learning Progress")
    analytics = get_topic_analytics()

    if analytics:
        for item in analytics:
            pct = item["avg_pct_score"] or 0.0
            status_color = "🟢" if pct >= 70.0 else "🔴"
            st.markdown(
                f"**{item['topic'].title()}** {status_color}\n"
                f"- Avg Score: {pct}%\n"
                f"- Attempts: {item['attempts_count']}"
            )
    else:
        st.info("No quiz attempts recorded yet.")

    st.divider()
    st.subheader("📅 Active Revision Plan")
    plan = get_latest_study_plan()

    if plan:
        st.write(f"**Topics:** {', '.join(plan['topics'])}")
        st.write(f"**Target:** {plan['available_minutes_per_day']} mins/day over {plan['days']} days")
        with st.expander("View Full Schedule"):
            for day in plan["schedule"]:
                st.markdown(f"**Day {day['day']}: {day['primary_topic']}**")
                for task in day["tasks"]:
                    st.write(f"- {task}")
    else:
        st.info("No active study plan saved yet.")

# ==============================================================================
# Main Chat Area
# ==============================================================================
st.header("StudyBuddy AI Assistant")
st.markdown("Your autonomous study tutor. Ask questions, request quizzes, or generate revision plans.")

# Render previous messages from session state
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "traces" in msg and msg["traces"]:
            with st.expander("🛠️ Tool Execution Trace", expanded=False):
                for trace in msg["traces"]:
                    st.markdown(f"**Tool:** `{trace['tool']}`")
                    st.markdown("**Arguments:**")
                    st.json(trace["arguments"])
                    st.markdown("**Result:**")
                    st.json(trace["result"])

# User Input
if prompt := st.chat_input("Ask a question, request a quiz, or build a study plan..."):
    # Render user query
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    # Prepare assistant response container
    with st.chat_message("assistant"):
        traces = []
        status_placeholder = st.empty()
        response_placeholder = st.empty()

        # Step through agent loop generator
        for step in st.session_state.agent.chat_step(prompt):
            step_type = step.get("type")

            if step_type == "status":
                status_placeholder.info(step.get("content"))
            elif step_type == "tool_call":
                current_call = {
                    "tool": step.get("tool"),
                    "arguments": step.get("arguments"),
                    "result": None
                }
                traces.append(current_call)
                status_placeholder.info(f"Executing tool `{step.get('tool')}`...")
            elif step_type == "tool_result":
                if traces:
                    traces[-1]["result"] = step.get("result")
            elif step_type == "final_response":
                status_placeholder.empty()
                response_content = step.get("content")
                response_placeholder.markdown(response_content)

                # Show tool trace expander if tools were invoked
                if traces:
                    with st.expander("🛠️ Tool Execution Trace", expanded=False):
                        for trace in traces:
                            st.markdown(f"**Tool:** `{trace['tool']}`")
                            st.markdown("**Arguments:**")
                            st.json(trace["arguments"])
                            st.markdown("**Result:**")
                            st.json(trace["result"])

                # Persist in session state
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response_content,
                    "traces": traces
                })
            elif step_type == "error":
                status_placeholder.error(step.get("content"))

    # Rerun to update sidebar statistics if database tools were executed
    if traces:
        st.rerun()
