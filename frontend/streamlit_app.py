import streamlit as st
import requests
import json
import time
import os

# API configuration
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="DeskMate AI Agent",
    page_icon="🤖",
    layout="wide"
)

def init_session_state():
    if 'jobs' not in st.session_state:
        st.session_state.jobs = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

def call_api(endpoint, method="GET", data=None):
    """Helper function to call API endpoints"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to DeskMate API. Make sure the backend is running.")
        return None

def main():
    st.title("🤖 DeskMate - Local AI Agent")
    st.markdown("Your local-first AI assistant for file processing and task automation")
    
    init_session_state()
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose Mode",
        ["Chat with Agent", "File Management", "Job History"]
    )
    
    if app_mode == "Chat with Agent":
        chat_with_agent()
    elif app_mode == "File Management":
        file_management()
    elif app_mode == "Job History":
        job_history()

def chat_with_agent():
    st.header("💬 Chat with DeskMate Agent")
    
    # Command input
    command = st.text_area(
        "Enter your command:",
        placeholder="e.g., 'Summarize my document.pdf', 'Draft an email about meeting', 'Run ls command'",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Process Command", type="primary"):
            if command:
                process_command(command)
            else:
                st.warning("Please enter a command")
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.jobs = []
    
    # Display recent jobs
    if st.session_state.jobs:
        st.subheader("Recent Commands")
        for job in reversed(st.session_state.jobs[-5:]):  # Show last 5
            display_job_result(job)

def process_command(command):
    """Process a command through the agent"""
    with st.spinner("Processing your command..."):
        result = call_api("/api/v1/agent/query", "POST", {"command": command})
        
        if result:
            # Store job in session state with proper structure
            job_data = {
                "command": command,
                "job_id": result.get("job_id", "unknown"),
                "result": result
            }
            st.session_state.jobs.append(job_data)
            
            # Display results
            st.success("Command processed successfully!")
            display_job_result(job_data)

def display_job_result(job):
    """Display job results in a structured way"""
    # Safe command display
    command_text = job.get('command', 'Unknown command')
    display_text = f"Command: {command_text[:50]}..." if len(command_text) > 50 else f"Command: {command_text}"
    
    with st.expander(display_text):
        result_data = job.get('result', {})
        
        # Handle both string and dict results
        if isinstance(result_data, str):
            try:
                result_data = json.loads(result_data)
            except:
                st.write("**Raw Result:**")
                st.text(result_data)
                return
        
        # Display intent
        intent = result_data.get('intent', {})
        st.write(f"**Intent:** `{intent.get('intent', 'Unknown')}`")
        
        if intent.get('confirmation_required'):
            st.warning("⚠️ This action requires confirmation")
        
        # Display assumptions if any
        assumptions = intent.get('assumptions', [])
        if assumptions:
            st.write("**Assumptions:**")
            for assumption in assumptions:
                st.write(f"- {assumption}")
        
        # Display steps and results
        st.write("**Execution Plan:**")
        results = result_data.get('results', [])
        
        if not results:
            st.info("No execution steps were performed")
            return
            
        for i, step_result in enumerate(results):
            step = step_result.get('action', 'Unknown')
            result = step_result.get('result', {})
            
            with st.expander(f"Step {i+1}: {step}", expanded=True):
                if result.get('success'):
                    st.success("✅ Step completed successfully")
                    output = result.get('output', {})
                    
                    if step == "read_file":
                        if output.get('content'):
                            st.text_area("File Content", output['content'], height=200, key=f"file_{i}")
                        elif output.get('error'):
                            st.error(f"Error: {output['error']}")
                    
                    elif step == "summarize":
                        if output.get('summary'):
                            st.text_area("Summary", output['summary'], height=150, key=f"summary_{i}")
                            st.write(f"Original length: {output.get('original_length', 0)} words")
                            st.write(f"Summary length: {output.get('summary_length', 0)} words")
                    
                    elif step == "generate_email":
                        if output.get('email_draft'):
                            st.text_area("Email Draft", output['email_draft'], height=300, key=f"email_{i}")
                            if st.button("Copy Email Draft", key=f"copy_{i}"):
                                st.code(output['email_draft'])
                    
                    elif step == "run_shell":
                        if output.get('output'):
                            st.code(output['output'])
                        if output.get('error'):
                            st.error(f"Command error: {output['error']}")
                    
                    elif step == "answer_question":
                        if output.get('answer'):
                            st.info(output['answer'])
                    
                    # Show raw output for debugging
                    if st.checkbox(f"Show raw output for step {i+1}", key=f"raw_{i}"):
                        st.json(output)
                else:
                    st.error(f"❌ Step failed: {result.get('error', 'Unknown error')}")

def file_management():
    st.header("📁 File Management")
    
    # File upload
    st.subheader("Upload Files")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, TXT)",
        type=['pdf', 'txt']
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Upload File"):
                upload_file_to_api(uploaded_file)
    
    # List uploaded files
    st.subheader("Uploaded Files")
    files_list = call_api("/api/v1/files/list")
    
    if files_list:
        for file_info in files_list:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{file_info['filename']}**")
                st.caption(f"Path: {file_info['file_path']}")
                st.caption(f"Uploaded: {file_info['uploaded_at']}")
            with col2:
                if st.button("Use File", key=f"use_{file_info['filename']}"):
                    st.info(f"File '{file_info['filename']}' selected. Use commands like 'Summarize {file_info['filename']}'")
            with col3:
                if st.button("View Info", key=f"info_{file_info['filename']}"):
                    st.json(file_info)
    else:
        st.info("No files uploaded yet")

def upload_file_to_api(uploaded_file):
    """Upload file to the backend API"""
    try:
        # Prepare the file for upload
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE}/api/v1/files/upload", files=files)
        
        if response.status_code == 200:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            st.session_state.uploaded_files.append(uploaded_file.name)
        else:
            st.error(f"Upload failed: {response.text}")
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")

def job_history():
    st.header("📊 Job History")
    
    jobs_list = call_api("/api/v1/jobs/")
    
    if jobs_list:
        for job in jobs_list:
            command_text = job.get('command', 'Unknown command')
            display_text = f"{job['job_id'][:8]}... - {command_text[:50]}..." if len(command_text) > 50 else f"{job['job_id'][:8]}... - {command_text}"
            
            with st.expander(display_text):
                st.write(f"**Command:** {command_text}")
                st.write(f"**Status:** {job['status']}")
                st.write(f"**Created:** {job['created_at']}")
                
                if job['result']:
                    if st.button("View Details", key=job['job_id']):
                        try:
                            result_data = json.loads(job['result'])
                            # Create a temporary job structure for display
                            temp_job = {
                                "command": command_text,
                                "result": result_data
                            }
                            display_job_result(temp_job)
                        except:
                            st.text(job['result'])
    else:
        st.info("No job history found")

if __name__ == "__main__":
    main()