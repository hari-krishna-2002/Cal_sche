import streamlit as st
from task_extractor_core import extract_tasks
from calendar_helper import init_calendar_config, create_event

st.set_page_config(page_title="Task Extractor", layout="wide")

# Inject custom CSS to mimic your HTML UI
st.markdown("""
    <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #e2dede;
    }
    .block-container {
      padding: 40px;
    }
    .task-box {
      background-color: #fff;
      padding: 10px;
      margin-top: 15px;
      border-radius: 5px;
      border-left: 5px solid #007bff;
    }
    .button-style {
      background-color: #8cb8e7;
      border: none;
      border-radius: 10px;
      padding: 10px 30px;
      font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📅 Calendar Scheduler")

# --- Calendar Setup ---
st.markdown("### 🛠 Google Calendar Setup")
with st.container():
    with st.form("calendar_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            calendar_id = st.text_input("Calendar ID", placeholder="your@gmail.com")
        with col2:
            service_account_file = st.file_uploader("Upload service_account.json", type="json")
        submit_btn = st.form_submit_button("🆗 Load Calendar")

        if submit_btn:
            if not calendar_id or not service_account_file:
                st.warning("Please provide both Calendar ID and JSON file.")
            else:
                try:
                    json_data = service_account_file.getvalue().decode("utf-8")
                    init_calendar_config(json_data, calendar_id)
                    st.success("✅ Calendar configured successfully.")
                except Exception as e:
                    st.error(f"❌ Failed to configure calendar: {e}")

# --- Task Scheduling ---
st.markdown("### 📝 Schedule Tasks")
with st.container():
    with st.form("task_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            uploaded_text_file = st.file_uploader("Upload a List of Tasks File (.txt)", type="txt", key="txtfile")
        with col2:
            manual_text = st.text_area("Or paste List of Tasks here", height=150)

        schedule_btn = st.form_submit_button("📆 Schedule Calendar")

    if schedule_btn:
        text_to_process = ""
        if uploaded_text_file:
            text_to_process = uploaded_text_file.read().decode("utf-8")
        elif manual_text:
            text_to_process = manual_text.strip()

        if not text_to_process:
            st.warning("Please upload or enter task text.")
        else:
            with st.spinner("🔍 Extracting tasks..."):
                tasks = extract_tasks(text_to_process)

            st.success(f"✅ {len(tasks)} Task(s) Extracted")
            for i, task in enumerate(tasks, 1):
                with st.container():
                    st.markdown(f"<div class='task-box'>", unsafe_allow_html=True)
                    st.markdown(f"**Task {i}**")
                    st.markdown(f"- **Task**: {task['task']}")
                    st.markdown(f"- **Due Date**: {task['due_date']}")
                    st.markdown(f"- **Priority**: {task['priority']}")
                    st.markdown(f"- **Category**: {task['category']}")
                    st.markdown(f"- _Original_: {task['original']}")

                    result = None
                    if calendar_id and service_account_file:
                        result = create_event(
                            task_text=task["task"],
                            due_date=task["due_date"],
                            description=f"Original: {task['original']} | Priority: {task['priority']} | Category: {task['category']}"
                        )
                    if result and "htmlLink" in result:
                        st.markdown(f"📅 [View Event in Calendar]({result['htmlLink']})")
                    st.markdown("</div>", unsafe_allow_html=True)
