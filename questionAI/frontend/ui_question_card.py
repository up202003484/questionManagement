# frontend/ui_question_card.py

import streamlit as st
import time
from backend.backlog import update_question_status, remove_question, update_question_prio

class QuestionCard:
    @staticmethod
    def create_task_card(question):
        """Create a card to display a question in the Kanban board."""
        # st.write(f"Question: {question['question']}")  # Directly print question for debugging
        with st.expander(question["question"]):
            st.write(f"Author: {question['owner']}")
            st.write(f"Category: {question['category']}")
            st.write(f"Tags: {question['taxonomy']}")
            st.write(f"Priority: {question['priority']}")
            st.write(f"Created at: {question['created_at']}")
            st.write(f"Status: {question['status']}")
            if f"status_{question['id']}" not in st.session_state:
                st.session_state[f"status_{question['id']}"] = question['status']

            # st.write("Current user role:", st.session_state.get("user_role"))
            allowed_roles_status = ["admin", "decision_maker"]
            allowed_roles_prio = ["admin", "question_owner", "product_owner"]
            user_role = st.session_state.get("user_role", "").lower()

            if user_role in allowed_roles_prio:
                # Show the selectbox for priority change
                new_priority = st.selectbox(
                    "Select new priority:",
                    options=["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(st.session_state.get(f"priority_{question['id']}", question['priority'])),
                    key=f"priority_select_{question['id']}"
                )
            
                st.session_state[f"priority_{question['id']}"] = new_priority

                # Show the Confirm button only if a new priority is selected
                if new_priority != question['priority']:
                    if st.button(f"Confirm Priority Change", key=f"confirm_priority_{question['id']}"):
                        update_question_prio(question['id'], new_priority)
                        st.success(f"Priority for question '{question['question']}' updated to '{new_priority}'.")
                        st.session_state[f"priority_{question['id']}"] = new_priority
                        st.rerun()
            else:
                st.write("You do not have permission to change the priority of this question.")
                
            if user_role in allowed_roles_status:

                # Show the selectbox for status change
                new_status = st.selectbox(
                    "Select new status:",
                    options=["Open", "Assumption", "Resolved", "Deferred"],
                    index=["Open", "Assumption", "Resolved", "Deferred"].index(st.session_state[f"status_{question['id']}"]),
                    key=f"status_select_{question['id']}"
                )
            
            

                st.session_state[f"status_{question['id']}"] = new_status

                # Show the Confirm button only if a new status is selected
                if new_status != question['status']:
                    if st.button(f"Confirm Status Change", key=f"confirm_status_{question['id']}"):
                        update_question_status(question['id'], new_status)
                        st.success(f"Status for question '{question['question']}' updated to '{new_status}'.")
                        # Update session state and rerun the app to reflect changes
                        st.session_state[f"status_{question['id']}"] = new_status
                        st.rerun()
            else:
                st.write("You do not have permission to change the status of this question.")

            if st.button(f"Remove Question", key=f"remove_question_{question['id']}"):
                # Confirmation dialog to remove the question
                if st.dialog("Are you sure you want to remove this question?"):
                    remove_question(question['id'])
                    st.success(f"Question '{question['question']}' removed successfully.")
                    st.rerun()  # Rerun to refresh the page after deletion
