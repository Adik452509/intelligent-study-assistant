import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main_assistant import StudyAssistant

#page config
st.set_page_config(
  page_title="Study Assistant",
  page_icon="📚",
  layout="wide",
)

# Initialize the Study Assistant
if 'assistant' not in st.session_state:
    st.session_state.assistant = StudyAssistant() 
if 'profile' not in st.session_state:
    st.session_state.profile = None 

assistant = st.session_state.assistant

#sidebar
st.sidebar.title("📚 Study Assistant")
page = st.sidebar.radio(
    "Navigation",
    ["👤 Profile", "💬 Ask AI", "📅 Study Planner", "📊 Tracker"]
)

# === PAGE 1: PROFILE ===

if page == "👤 Profile":
    st.title("👤 Create Your Profile")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pace = st.selectbox(
                "Learning Pace",
                ["slow", "moderate", "fast"],
                index=1
            )
            
            pattern = st.selectbox(
                "Study Pattern",
                ["pomodoro", "deep_work", "short_burst"],
                help="Pomodoro: 25min | Deep Work: 90min | Short: 15min"
            )
            
            hours = st.slider("Daily Available Hours", 1, 12, 3)

        with col2:
              times = st.multiselect(
                "Preferred Study Times",
                ["morning", "afternoon", "evening", "night"],
                default=["evening"]
            )
            
              weak_input = st.text_area(
                "Weak Areas (one per line)",
                placeholder="Neural Networks\nBackpropagation"
            )
        
        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            weak_areas = [w.strip() for w in weak_input.split("\n") if w.strip()]

            st.session_state.profile = {
                "learning_pace": pace,
                "study_pattern": pattern,
                "daily_available_hours": hours,
                "preferred_times": times,
                "weak_areas": weak_areas
            }
            
            st.success("✅ Profile Saved!")
    #show current profile
    if st.session_state.profile:
        st.divider()
        st.subheader("Current Profile")
        st.json(st.session_state.profile)

# === PAGE 2: ASK AI ===
elif page == "💬 Ask AI":
    st.title("💬 Ask Study Questions")

    question = st.text_input("Ask anything about your studies:")

    if st.button("Ask AI", type="primary"):
        if question:
            with st.spinner("AI is thinking..."):
                answer = assistant.ask_question(question)
                st.success(answer)

# === PAGE 3: STUDY PLANNER ===
# === PAGE 3: STUDY PLANNER ===
elif page == "📅 Study Planner":
    st.title("📅 Generate Study Plan")
    
    if not st.session_state.profile:
        st.warning("⚠️ Please create your profile first!")
        if st.button("Go to Profile"):
            st.rerun()
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.text_input("Subject", "Machine Learning")
            
            topics_input = st.text_area(
                "Topics (one per line)",
                "Linear Regression\nNeural Networks\nDecision Trees",
                height=150
            )
            
            topics = [t.strip() for t in topics_input.split("\n") if t.strip()]
            
            # Difficulty for each topic
            st.subheader("Set Difficulty")
            difficulties = {}
            
            if topics:
                num_cols = min(3, len(topics))
                cols = st.columns(num_cols)
                
                for i, topic in enumerate(topics):
                    with cols[i % num_cols]:
                        diff = st.selectbox(
                            topic,
                            ["easy", "medium", "hard"],
                            key=f"diff_{i}",
                            index=1
                        )
                        difficulties[topic] = diff
        
        with col2:
            deadline = st.number_input("Days until deadline", 1, 90, 7)
            
            st.info(f"""
            **Your Profile:**
            - Pace: {st.session_state.profile['learning_pace']}
            - Pattern: {st.session_state.profile['study_pattern']}
            - Daily: {st.session_state.profile['daily_available_hours']}h
            """)
        
        if st.button("🚀 Generate Plan", type="primary"):
            if not topics:
                st.error("❌ Please enter at least one topic!")
            else:
                with st.spinner("Creating your personalized plan..."):
                    try:
                        plan = assistant.create_personalized_plan(
                            student_profile=st.session_state.profile,
                            subject=subject,
                            topics=topics,
                            deadline_days=deadline,
                            difficulty_levels=difficulties
                        )
                        
                        if plan.get('feasible'):
                            st.success("✅ Plan Generated!")
                            plan_text = assistant.get_plan_summary(plan)
                            st.text(plan_text)
                            
                            # Download button
                            st.download_button(
                                "📥 Download Plan",
                                plan_text,
                                file_name=f"study_plan_{subject.lower().replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error(f"❌ {plan.get('message', 'Plan not feasible')}")
                            
                            if 'suggestions' in plan:
                                st.subheader("💡 Suggestions:")
                                for suggestion in plan['suggestions']:
                                    st.write(f"- {suggestion}")
                    
                    except Exception as e:
                        st.error(f"❌ Error generating plan: {str(e)}")
# === PAGE 4: TRACKER ===
# === PAGE 4: TRACKER ===
elif page == "📊 Tracker":
    st.title("📊 Productivity Tracker")
    
    # Log session
    with st.expander("📝 Log Study Session", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject = st.text_input("Subject", "Machine Learning")
            topic = st.text_input("Topic", "Neural Networks")
        
        with col2:
            duration = st.number_input("Duration (min)", 15, 180, 60)
            difficulty = st.slider("Difficulty (1-5)", 1, 5, 3)
        
        with col3:
            focus = st.slider("Focus Level (1-10)", 1, 10, 7)
        
        if st.button("✅ Log Session", type="primary"):
            try:
                msg = assistant.log_session(subject, topic, duration, difficulty, focus)
                st.success(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Error logging session: {str(e)}")
    
    st.divider()
    
    # Display stats
    st.subheader("📊 Today's Progress")
    
    try:
        stats = assistant.get_today_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hours Studied", f"{stats.get('total_hours', 0)}h")
        with col2:
            st.metric("Sessions", stats.get('sessions', 0))
        with col3:
            # Fix for streak
            try:
                streak_data = assistant.tracker.get_study_streak()
                if isinstance(streak_data, dict):
                    streak = streak_data.get('current_streak', 0)
                else:
                    streak = streak_data
            except:
                streak = 0
            
            st.metric("Study Streak", f"{streak} days 🔥")
        
        # Show subjects
        if stats.get('subjects'):
            st.subheader("📚 Subjects Covered Today")
            for subj in stats['subjects']:
                st.write(f"- {subj}")
    
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")
# Footer
st.sidebar.divider()
st.sidebar.info("💡 Tip: Use daily for best results!")






          