"""
Main Streamlit application for AI-Powered Recruitment Assistant
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.agents.resume_bot import ResumeBot
from src.agents.filter_ai import FilterAI
from src.agents.store_keeper import StoreKeeper
from src.agents.hr_bridge import HRBridge
from src.agents.time_bot import TimeBot
from src.agents.notify_bot import NotifyBot
from src.utils.helpers import generate_id, get_timestamp
from src.schema.data_models import Job, Candidate, Interview

st.set_page_config(
    page_title="AI Recruitment Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'agents' not in st.session_state:
    st.session_state.agents = {
        'resume_bot': ResumeBot(),
        'filter_ai': FilterAI(),
        'store_keeper': StoreKeeper(),
        'hr_bridge': HRBridge(),
        'time_bot': TimeBot(),
        'notify_bot': NotifyBot()
    }

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_job' not in st.session_state:
    st.session_state.current_job = None

def main():
    """Main application function"""
    st.title("🤖 AI-Powered Recruitment Assistant")
    st.markdown("*Streamline your hiring process with intelligent AI agents*")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Job Management", "Resume Collection", "Candidate Filtering", 
        "Interview Scheduling", "HR Interface", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Job Management":
        show_job_management()
    elif page == "Resume Collection":
        show_resume_collection()
    elif page == "Candidate Filtering":
        show_candidate_filtering()
    elif page == "Interview Scheduling":
        show_interview_scheduling()
    elif page == "HR Interface":
        show_hr_interface()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    """Show dashboard with system overview"""
    st.header("📊 Dashboard")
    
    store_keeper = st.session_state.agents['store_keeper']
    candidates = store_keeper.get_candidates()
    jobs = store_keeper.get_jobs()
    interviews = store_keeper.get_interviews()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", len(candidates))
    
    with col2:
        st.metric("Active Jobs", len([j for j in jobs if j.get('status') == 'active']))
    
    with col3:
        st.metric("Scheduled Interviews", len([i for i in interviews if i.get('status') == 'scheduled']))
    
    with col4:
        st.metric("Pending Reviews", len([c for c in candidates if c.get('status') == 'new']))
    
    st.subheader("Recent Activity")
    
    recent_activities = [
        {"time": "2 hours ago", "activity": "New candidate John Doe submitted resume"},
        {"time": "4 hours ago", "activity": "Interview scheduled with Jane Smith"},
        {"time": "1 day ago", "activity": "New job posting: Senior Developer"},
        {"time": "2 days ago", "activity": "Candidate filtering completed for Marketing Manager"}
    ]
    
    for activity in recent_activities:
        st.write(f"⏰ {activity['time']}: {activity['activity']}")

def show_job_management():
    """Show job management interface"""
    st.header("💼 Job Management")
    
    tab1, tab2 = st.tabs(["Create Job", "Manage Jobs"])
    
    with tab1:
        st.subheader("Create New Job")
        
        with st.form("job_form"):
            job_title = st.text_input("Job Title")
            job_description = st.text_area("Job Description", height=150)
            department = st.text_input("Department")
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry", "Mid", "Senior", "Executive"]
            )
            
            skills_input = st.text_area(
                "Required Skills (comma-separated)",
                placeholder="Python, React, SQL, Machine Learning"
            )
            
            requirements_input = st.text_area(
                "Requirements (comma-separated)",
                placeholder="Bachelor's degree, 3+ years experience"
            )
            
            submit_job = st.form_submit_button("Create Job")
            
            if submit_job and job_title and job_description:
                job = Job(
                    id=generate_id(),
                    title=job_title,
                    description=job_description,
                    requirements=requirements_input.split(',') if requirements_input else [],
                    skills_required=skills_input.split(',') if skills_input else [],
                    experience_level=experience_level,
                    department=department,
                    created_at=get_timestamp()
                )
                
                store_keeper = st.session_state.agents['store_keeper']
                result = store_keeper.store_job(job.to_dict())
                
                if result['success']:
                    st.success("Job created successfully!")
                    st.session_state.current_job = job.to_dict()
                else:
                    st.error(f"Error creating job: {result['message']}")
    
    with tab2:
        st.subheader("Existing Jobs")
        
        store_keeper = st.session_state.agents['store_keeper']
        jobs = store_keeper.get_jobs()
        
        if jobs:
            jobs_df = pd.DataFrame(jobs)
            st.dataframe(jobs_df, use_container_width=True)
            
            if st.button("Edit Selected Job"):
                selected_job_id = st.selectbox("Select Job to Edit", [j['id'] for j in jobs])
                if selected_job_id:
                    selected_job = next((j for j in jobs if j['id'] == selected_job_id), None)
                    if selected_job:
                        st.session_state.current_job = selected_job
                        st.experimental_rerun()
        else:
            st.info("No jobs found. Create your first job in the 'Create Job' tab.")

def show_resume_collection():
    """Show resume collection interface"""
    st.header("📄 Resume Collection")
    
    resume_bot = st.session_state.agents['resume_bot']
    
    tab1, tab2 = st.tabs(["Upload Resume", "Collected Resumes"])
    
    with tab1:
        st.subheader("Upload New Resume")
        
        store_keeper = st.session_state.agents['store_keeper']
        jobs = store_keeper.get_jobs()
        
        if jobs:
            selected_job = st.selectbox(
                "Select Job Position",
                options=[j['title'] for j in jobs],
                help="Choose the job position this resume is for"
            )
            
            uploaded_file = st.file_uploader(
                "Upload Resume",
                type=['pdf', 'doc', 'docx', 'txt'],
                help="Upload candidate's resume in PDF, DOC, DOCX, or TXT format"
            )
            
            if uploaded_file:
                st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
                
                if st.button("Process Resume"):
                    with st.spinner("Processing resume..."):
                        try:
                            job_data = next((j for j in jobs if j['title'] == selected_job), None)
                            
                            # Save uploaded file
                            file_path = f"data/resumes/{uploaded_file.name}"
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Prepare resume data
                            resume_data = {
                                'file_path': file_path,
                                'name': uploaded_file.name,
                                'job_data': job_data
                            }
                            
                            result = resume_bot.process_resume(resume_data)
                            
                            if result['success']:
                                st.success("Resume processed successfully!")
                                
                                st.subheader("Extracted Information")
                                candidate_info = result['candidate']
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Name:**", candidate_info.get('name', 'N/A'))
                                    st.write("**Email:**", candidate_info.get('email', 'N/A'))
                                    st.write("**Phone:**", candidate_info.get('phone', 'N/A'))
                                
                                with col2:
                                    st.write("**Experience:**", candidate_info.get('experience', 'N/A'))
                                    st.write("**Education:**", candidate_info.get('education', 'N/A'))
                                
                                st.write("**Skills:**", ', '.join(candidate_info.get('skills', [])))
                                
                                candidate = Candidate(
                                    id=generate_id(),
                                    name=candidate_info.get('name', 'Unknown'),
                                    email=candidate_info.get('email', ''),
                                    phone=candidate_info.get('phone', ''),
                                    experience=candidate_info.get('experience', ''),
                                    education=candidate_info.get('education', ''),
                                    skills=candidate_info.get('skills', []),
                                    job_id=job_data['id'] if job_data else None,
                                    created_at=get_timestamp()
                                )
                                
                                store_result = store_keeper.store_candidate(candidate.to_dict())
                                if store_result['success']:
                                    st.success("Candidate stored successfully!")
                                else:
                                    st.error(f"Error storing candidate: {store_result['message']}")
                            else:
                                st.error(f"Error processing resume: {result['message']}")
                        
                        except Exception as e:
                            st.error(f"Error processing resume: {str(e)}")
        else:
            st.warning("No jobs available. Please create a job first.")
    
    with tab2:
        st.subheader("Collected Resumes")
        
        store_keeper = st.session_state.agents['store_keeper']
        candidates = store_keeper.get_candidates()
        
        if candidates:
            candidates_df = pd.DataFrame(candidates)
            st.dataframe(candidates_df, use_container_width=True)
            
            if st.button("View Candidate Details"):
                selected_candidate_id = st.selectbox("Select Candidate", [c['id'] for c in candidates])
                if selected_candidate_id:
                    candidate = next((c for c in candidates if c['id'] == selected_candidate_id), None)
                    if candidate:
                        st.json(candidate)
        else:
            st.info("No resumes collected yet.")

def show_candidate_filtering():
    """Show candidate filtering interface"""
    st.header("🔍 Candidate Filtering")
    
    filter_ai = st.session_state.agents['filter_ai']
    store_keeper = st.session_state.agents['store_keeper']
    
    jobs = store_keeper.get_jobs()
    candidates = store_keeper.get_candidates()
    
    if not jobs:
        st.warning("No jobs available. Please create a job first.")
        return
    
    if not candidates:
        st.warning("No candidates available. Please upload resumes first.")
        return
    
    selected_job = st.selectbox(
        "Select Job Position",
        options=[j['title'] for j in jobs],
        help="Choose the job position to filter candidates for"
    )
    
    job_data = next((j for j in jobs if j['title'] == selected_job), None)
    
    if job_data:
        job_candidates = [c for c in candidates if c.get('job_id') == job_data['id']]
        
        if job_candidates:
            st.subheader(f"Candidates for {selected_job}")
            st.write(f"Total candidates: {len(job_candidates)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_experience = st.slider("Minimum Experience (years)", 0, 20, 0)
                required_skills = st.multiselect(
                    "Required Skills",
                    options=job_data.get('skills_required', []),
                    help="Select skills that candidates must have"
                )
            
            with col2:
                education_level = st.selectbox(
                    "Minimum Education Level",
                    ["Any", "High School", "Bachelor's", "Master's", "PhD"]
                )
                
                score_threshold = st.slider("Minimum Match Score", 0, 100, 50)
            
            if st.button("Filter Candidates"):
                with st.spinner("Filtering candidates..."):
                    filter_criteria = {
                        'min_experience': min_experience,
                        'required_skills': required_skills,
                        'education_level': education_level,
                        'score_threshold': score_threshold
                    }
                    
                    result = filter_ai.filter_candidates(job_candidates, job_data, filter_criteria)
                    
                    if result['success']:
                        filtered_candidates = result['filtered_candidates']
                        
                        st.subheader("Filtered Results")
                        st.write(f"Qualified candidates: {len(filtered_candidates)}")
                        
                        if filtered_candidates:
                            filtered_df = pd.DataFrame(filtered_candidates)
                            st.dataframe(filtered_df, use_container_width=True)
                            
                            if st.button("Export Filtered Candidates"):
                                csv = filtered_df.to_csv(index=False)
                                st.download_button(
                                    label="Download CSV",
                                    data=csv,
                                    file_name=f"filtered_candidates_{selected_job}.csv",
                                    mime="text/csv"
                                )
                        else:
                            st.info("No candidates match the specified criteria.")
                    else:
                        st.error(f"Error filtering candidates: {result['message']}")
        else:
            st.info(f"No candidates found for {selected_job}.")

def show_interview_scheduling():
    """Show interview scheduling interface"""
    st.header("📅 Interview Scheduling")
    
    time_bot = st.session_state.agents['time_bot']
    store_keeper = st.session_state.agents['store_keeper']
    
    tab1, tab2 = st.tabs(["Schedule Interview", "Manage Interviews"])
    
    with tab1:
        st.subheader("Schedule New Interview")
        
        candidates = store_keeper.get_candidates()
        
        if candidates:
            selected_candidate = st.selectbox(
                "Select Candidate",
                options=[f"{c['name']} ({c['email']})" for c in candidates]
            )
            
            candidate_data = next((c for c in candidates if f"{c['name']} ({c['email']})" == selected_candidate), None)
            
            if candidate_data:
                with st.form("interview_form"):
                    interview_date = st.date_input("Interview Date")
                    interview_time = st.time_input("Interview Time")
                    
                    interview_type = st.selectbox(
                        "Interview Type",
                        ["Phone", "Video", "In-Person"]
                    )
                    
                    interviewer = st.text_input("Interviewer Name")
                    notes = st.text_area("Notes", height=100)
                    
                    submit_interview = st.form_submit_button("Schedule Interview")
                    
                    if submit_interview:
                        interview_datetime = datetime.combine(interview_date, interview_time)
                        
                        interview = Interview(
                            id=generate_id(),
                            candidate_id=candidate_data['id'],
                            job_id=candidate_data.get('job_id', ''),
                            interviewer=interviewer,
                            scheduled_time=interview_datetime.isoformat(),
                            type=interview_type,
                            notes=notes,
                            created_at=get_timestamp()
                        )
                        
                        # Store the interview directly since we already have the Interview object
                        store_result = store_keeper.store_interview(interview.to_dict())
                        
                        if store_result['success']:
                            st.success("Interview scheduled successfully!")
                            
                            notify_bot = st.session_state.agents['notify_bot']
                            notify_result = notify_bot.send_interview_notification(
                                candidate_data, interview.to_dict()
                            )
                            
                            if notify_result['success']:
                                st.info("Notification sent to candidate.")
                            else:
                                st.warning("Interview scheduled but notification failed.")
                        else:
                            st.error(f"Error storing interview: {store_result['message']}")
        else:
            st.warning("No candidates available for interview scheduling.")
    
    with tab2:
        st.subheader("Scheduled Interviews")
        
        interviews = store_keeper.get_interviews()
        
        if interviews:
            interviews_df = pd.DataFrame(interviews)
            st.dataframe(interviews_df, use_container_width=True)
            
            if st.button("Manage Interview"):
                selected_interview_id = st.selectbox("Select Interview", [i['id'] for i in interviews])
                if selected_interview_id:
                    interview = next((i for i in interviews if i['id'] == selected_interview_id), None)
                    if interview:
                        st.json(interview)
                        
                        new_status = st.selectbox(
                            "Update Status",
                            ["scheduled", "completed", "cancelled", "rescheduled"]
                        )
                        
                        if st.button("Update Status"):
                            interview['status'] = new_status
                            result = store_keeper.update_interview(interview)
                            if result['success']:
                                st.success("Interview status updated!")
                            else:
                                st.error(f"Error updating interview: {result['message']}")
        else:
            st.info("No interviews scheduled yet.")

def show_hr_interface():
    """Show HR interface"""
    st.header("👥 HR Interface")
    
    hr_bridge = st.session_state.agents['hr_bridge']
    store_keeper = st.session_state.agents['store_keeper']
    
    tab1, tab2, tab3 = st.tabs(["Candidate Review", "Interview Feedback", "Final Decision"])
    
    with tab1:
        st.subheader("Candidate Review")
        
        candidates = store_keeper.get_candidates()
        
        if candidates:
            pending_candidates = [c for c in candidates if c.get('status') == 'new']
            
            if pending_candidates:
                selected_candidate = st.selectbox(
                    "Select Candidate for Review",
                    options=[f"{c['name']} ({c['email']})" for c in pending_candidates]
                )
                
                candidate_data = next((c for c in pending_candidates if f"{c['name']} ({c['email']})" == selected_candidate), None)
                
                if candidate_data:
                    st.subheader("Candidate Information")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Name:**", candidate_data.get('name', 'N/A'))
                        st.write("**Email:**", candidate_data.get('email', 'N/A'))
                        st.write("**Phone:**", candidate_data.get('phone', 'N/A'))
                    
                    with col2:
                        st.write("**Experience:**", candidate_data.get('experience', 'N/A'))
                        st.write("**Education:**", candidate_data.get('education', 'N/A'))
                    
                    st.write("**Skills:**", ', '.join(candidate_data.get('skills', [])))
                    
                    with st.form("review_form"):
                        rating = st.slider("Overall Rating", 1, 10, 5)
                        review_notes = st.text_area("Review Notes", height=100)
                        decision = st.selectbox(
                            "Decision",
                            ["pending", "approved", "rejected", "interview_required"]
                        )
                        
                        submit_review = st.form_submit_button("Submit Review")
                        
                        if submit_review:
                            review_data = {
                                'rating': rating,
                                'notes': review_notes,
                                'decision': decision,
                                'reviewed_at': get_timestamp()
                            }
                            
                            result = hr_bridge.review_candidate(candidate_data['id'], review_data)
                            
                            if result['success']:
                                st.success("Review submitted successfully!")
                                candidate_data['status'] = decision
                                candidate_data['review'] = review_data
                                store_keeper.update_candidate(candidate_data)
                            else:
                                st.error(f"Error submitting review: {result['message']}")
            else:
                st.info("No candidates pending review.")
        else:
            st.info("No candidates available for review.")
    
    with tab2:
        st.subheader("Interview Feedback")
        
        interviews = store_keeper.get_interviews()
        completed_interviews = [i for i in interviews if i.get('status') == 'completed']
        
        if completed_interviews:
            selected_interview = st.selectbox(
                "Select Interview for Feedback",
                options=[f"Interview {i['id'][:8]}..." for i in completed_interviews]
            )
            
            interview_data = next((i for i in completed_interviews if f"Interview {i['id'][:8]}..." == selected_interview), None)
            
            if interview_data:
                st.json(interview_data)
                
                with st.form("feedback_form"):
                    technical_rating = st.slider("Technical Skills", 1, 10, 5)
                    communication_rating = st.slider("Communication", 1, 10, 5)
                    culture_fit_rating = st.slider("Culture Fit", 1, 10, 5)
                    
                    feedback_notes = st.text_area("Feedback Notes", height=100)
                    recommendation = st.selectbox(
                        "Recommendation",
                        ["hire", "no_hire", "second_interview"]
                    )
                    
                    submit_feedback = st.form_submit_button("Submit Feedback")
                    
                    if submit_feedback:
                        feedback_data = {
                            'technical_rating': technical_rating,
                            'communication_rating': communication_rating,
                            'culture_fit_rating': culture_fit_rating,
                            'notes': feedback_notes,
                            'recommendation': recommendation,
                            'feedback_at': get_timestamp()
                        }
                        
                        result = hr_bridge.submit_interview_feedback(interview_data['id'], feedback_data)
                        
                        if result['success']:
                            st.success("Feedback submitted successfully!")
                            interview_data['feedback'] = feedback_data
                            store_keeper.update_interview(interview_data)
                        else:
                            st.error(f"Error submitting feedback: {result['message']}")
        else:
            st.info("No completed interviews available for feedback.")
    
    with tab3:
        st.subheader("Final Decision")
        
        candidates = store_keeper.get_candidates()
        interviews = store_keeper.get_interviews()
        
        candidates_with_interviews = []
        for candidate in candidates:
            candidate_interviews = [i for i in interviews if i.get('candidate_id') == candidate['id']]
            if candidate_interviews:
                candidate['interviews'] = candidate_interviews
                candidates_with_interviews.append(candidate)
        
        if candidates_with_interviews:
            selected_candidate = st.selectbox(
                "Select Candidate for Final Decision",
                options=[f"{c['name']} ({c['email']})" for c in candidates_with_interviews]
            )
            
            candidate_data = next((c for c in candidates_with_interviews if f"{c['name']} ({c['email']})" == selected_candidate), None)
            
            if candidate_data:
                st.subheader("Candidate Summary")
                st.json(candidate_data)
                
                with st.form("final_decision_form"):
                    final_decision = st.selectbox(
                        "Final Decision",
                        ["hire", "reject", "hold"]
                    )
                    
                    salary_offer = st.number_input("Salary Offer (if hired)", min_value=0)
                    decision_notes = st.text_area("Decision Notes", height=100)
                    
                    submit_decision = st.form_submit_button("Submit Final Decision")
                    
                    if submit_decision:
                        decision_data = {
                            'decision': final_decision,
                            'salary_offer': salary_offer if final_decision == 'hire' else None,
                            'notes': decision_notes,
                            'decided_at': get_timestamp()
                        }
                        
                        result = hr_bridge.make_final_decision(candidate_data['id'], decision_data)
                        
                        if result['success']:
                            st.success("Final decision submitted successfully!")
                            
                            notify_bot = st.session_state.agents['notify_bot']
                            notify_result = notify_bot.send_decision_notification(
                                candidate_data, decision_data
                            )
                            
                            if notify_result['success']:
                                st.info("Notification sent to candidate.")
                            else:
                                st.warning("Decision recorded but notification failed.")
                        else:
                            st.error(f"Error submitting decision: {result['message']}")
        else:
            st.info("No candidates with completed interviews available.")

def show_analytics():
    """Show analytics and reports"""
    st.header("📈 Analytics")
    
    store_keeper = st.session_state.agents['store_keeper']
    
    candidates = store_keeper.get_candidates()
    jobs = store_keeper.get_jobs()
    interviews = store_keeper.get_interviews()
    
    if not candidates and not jobs and not interviews:
        st.info("No data available for analytics.")
        return
    
    st.subheader("Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", len(candidates))
    
    with col2:
        st.metric("Total Jobs", len(jobs))
    
    with col3:
        st.metric("Total Interviews", len(interviews))
    
    with col4:
        hired_count = len([c for c in candidates if c.get('final_decision', {}).get('decision') == 'hire'])
        st.metric("Hired Candidates", hired_count)
    
    if candidates:
        st.subheader("Candidate Status Distribution")
        
        status_counts = {}
        for candidate in candidates:
            status = candidate.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            chart_data = pd.DataFrame(
                list(status_counts.items()),
                columns=['Status', 'Count']
            )
            st.bar_chart(chart_data.set_index('Status'))
    
    if jobs:
        st.subheader("Jobs by Department")
        
        dept_counts = {}
        for job in jobs:
            dept = job.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        if dept_counts:
            chart_data = pd.DataFrame(
                list(dept_counts.items()),
                columns=['Department', 'Count']
            )
            st.bar_chart(chart_data.set_index('Department'))
    
    st.subheader("Detailed Reports")
    
    if st.button("Generate Recruitment Report"):
        with st.spinner("Generating report..."):
            report = generate_recruitment_report(candidates, jobs, interviews)
            st.text_area("Recruitment Report", report, height=400)
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"recruitment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def generate_recruitment_report(candidates, jobs, interviews):
    """Generate a comprehensive recruitment report"""
    report = []
    report.append("RECRUITMENT REPORT")
    report.append("=" * 50)
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("SUMMARY")
    report.append("-" * 20)
    report.append(f"Total Candidates: {len(candidates)}")
    report.append(f"Total Jobs: {len(jobs)}")
    report.append(f"Total Interviews: {len(interviews)}")
    report.append("")
    
    if candidates:
        report.append("CANDIDATE ANALYSIS")
        report.append("-" * 20)
        
        status_counts = {}
        for candidate in candidates:
            status = candidate.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            report.append(f"{status.title()}: {count}")
        
        report.append("")
    
    if jobs:
        report.append("JOB ANALYSIS")
        report.append("-" * 20)

        dept_counts = {}
        for job in jobs:
            dept = job.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        for dept, count in dept_counts.items():
            report.append(f"{dept}: {count} jobs")
        report.append("")

    if interviews:
        report.append("INTERVIEW SUMMARY")
        report.append("-" * 20)

        interview_status_counts = {}
        for interview in interviews:
            status = interview.get('status', 'scheduled')
            interview_status_counts[status] = interview_status_counts.get(status, 0) + 1

        for status, count in interview_status_counts.items():
            report.append(f"{status.title()}: {count}")

    return "\n".join(report)


if __name__ == "__main__":
    main()