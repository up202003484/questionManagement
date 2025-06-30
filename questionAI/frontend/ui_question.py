import streamlit as st
from backend.embedding import embed_text, find_similar_questions
from backend.ai import classify_question_category, classify_question_priority, generate_question_suggestions, classify_taxonomy, classify_question_meta
from backend.backlog import load_backlog, save_to_backlog, get_last_saved_question, create_snapshot
from utils.helper import current_timestamp
import os
import requests

def capture_question_ui():
    st.header("Capture New Question")

    if "question_text" not in st.session_state:
        st.session_state.question_text = ""

    if "name" not in st.session_state:
        st.error("User not authenticated. Please log in.")
        return
    if "proceed_with_similar" not in st.session_state:
        st.session_state.proceed_with_similar = False

    if st.button("📲 Load Question from Mobile App"):
        try:
            response = requests.get("https://receiver-api-314832503242.europe-west1.run.app/latest")
            if response.status_code == 200:
                mobile_question = response.json().get("question_text", "").strip()
                if mobile_question:
                    st.session_state.question_text = mobile_question
                    st.success("Question loaded from mobile app:")
                    st.code(mobile_question)
                else:
                    st.warning("No question found.")
            else:
                st.error("Failed to retrieve question.")
        except Exception as e:
            st.error(f"Error: {e}")
    
    author_name = st.session_state.name
    question_text = st.text_input("Enter your question", value=st.session_state.question_text)
    

    if question_text and not st.session_state.proceed_with_similar:
        with st.spinner("Checking for similar questions..."):
            similar = find_similar_questions(question_text, load_backlog())
            if similar:
                st.warning("Similar questions detected:")
                for q, score in similar:
                    st.markdown(f"- {q} _(similarity: {score:.2f})_")

                if similar[0][1] >= 0.99:
                    st.warning("This question is almost identical to an existing one.")
                    st.info("Cancelling this question...")
                    st.stop()

                st.info("Do you still want to continue with this question?")
                col1, col2 = st.columns(2)
                if col1.button("❌ Cancel"):
                    st.success("Question capture cancelled.")
                    st.session_state.proceed_with_similar = False
                    return
                if col2.button("✅ Submit Anyway"):
                    st.session_state.proceed_with_similar = True
                    st.rerun()
            else:
                st.success("No similar questions found. You can proceed.")
                proceed_to_classification(question_text, author_name)

    elif question_text and st.session_state.proceed_with_similar:
        proceed_to_classification(question_text, author_name)

    # Reset proceed flag if text input is cleared
    if not question_text and st.session_state.proceed_with_similar:
        st.session_state.proceed_with_similar = False


def proceed_to_classification(question_text, author_name):
    with st.spinner("Classifying question..."):
        # Classify question category and priority
        # suggested_category = classify_question_category(question_text)
        # suggested_priority = classify_question_priority(question_text)
        # taxonomy = classify_taxonomy(question_text)
        suggested_category, suggested_priority, taxonomy = classify_question_meta(question_text)


    # Allow user to choose category and priority
    # category = st.selectbox("Suggested Category", [suggested_category, "Architecture", "Performance", "Security", "Integration", "Maintainability", "Testing", "Devops", "Other"])
    # if category == "Choose another...":
    #     category = st.selectbox("Choose a category", ["architecture", "performance", "security", "integration", "maintainability", "testing", "devops"])

    category = st.selectbox(
        "Category",
        [suggested_category] + [
            cat for cat in ["Architecture", "Performance", "Security", "Integration", "Maintainability", "Testing", "Devops", "Other"]
            if cat.lower() != suggested_category.lower()
        ]
    )

    priority = st.selectbox(
        "Priority",
        [suggested_priority] + [
            p for p in ["Low", "Medium", "High"]
            if p.lower() != suggested_priority.lower()
        ]
    )


    # priority = st.selectbox("Suggested Priority", [suggested_priority, "Choose another..."])
    # if priority == "Choose another...":
    #     priority = st.selectbox("Choose a priority", ["Low", "Medium", "High"])

    if st.button("Save Question"):
        # Create question object and save it to the backlog
        with st.spinner("Saving question..."):
            embedding = embed_text(question_text)
            new_question = {
                "question": question_text,
                "owner": author_name,
                "status": "Open",
                "category": category,
                "priority": priority,
                "created_at": current_timestamp(),
                "embedding": embedding,  # embedding is now a list of floats
                "discussion": [],
                "taxonomy": taxonomy
            }
            save_to_backlog(new_question)  # Save to SQLite
            create_snapshot()
            saved_question = get_last_saved_question()

            if saved_question:
                st.success("Question saved successfully!")
                # st.rerun()

                #print(saved_question)  # You can print the full details here
            else:
                st.warning("Question was not saved.")
