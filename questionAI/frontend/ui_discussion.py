import streamlit as st
from backend.backlog import load_backlog, update_discussion, update_question_status,update_question_prio, clear_discussion_for_question
from backend.ai import generate_ai_response, describe_image
import datetime
import os
import uuid
from PIL import Image
allowed_roles_status = ["admin", "decision_maker"]
allowed_roles_prio = ["admin", "question_owner", "product_owner"]
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def discussion_board():
    st.title("Discussion Board")
    user_name = st.session_state.get("name", "Unknown User")
    user_role = st.session_state.get("user_role", "default")
    questions = load_backlog()
    if not questions:
        st.info("No questions available.")
        return

    question_texts = [q['question'] for q in questions]
    selected_question_text = st.selectbox("Select a question to discuss", question_texts)
    selected_question = next(q for q in questions if q['question'] == selected_question_text)

    st.subheader("Question")
    st.markdown(f"> {selected_question['question']}")

    import datetime

    st.subheader("Discussion Thread")

    if selected_question.get("discussion"):
        for entry in selected_question["discussion"]:
            author = entry["source"]
            message = entry["message"]
            timestamp = entry.get("created_at", "")

            # Optional: Convert ISO timestamp to readable format
            try:
                ts = float(timestamp)
                time_str = datetime.datetime.fromtimestamp(ts).strftime("%b %d, %Y %H:%M")
            except:
                time_str = timestamp  # fallback if format is wrong

            if author == "system":
                st.markdown(f"""
                    <div style="background-color:#fff3cd; padding:10px; border-left: 5px solid #ffc107; margin-bottom:10px; border-radius:5px;">
                        <strong>Status Update</strong> <span style="color: gray; font-size: 0.85em;">({time_str})</span><br>
                        {message}
                    </div>
                """, unsafe_allow_html=True)
                continue



            is_current_user = author == user_name
            # Simple avatar icon: Emoji for AI, initials for user
            avatar = "🤖 Assistant" if author == "AI" else f"🧑 {author}"

            bubble_style = """
                background-color: {bg};
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
                max-width: 70%;
            """

            container_style = f"""
                display: flex;
                justify-content: {"flex-end" if is_current_user else "flex-start"};
            """

            bg_color = "#d0e7ff" if is_current_user else "#f0f2f6"

            st.markdown(f"""
                <div style="{container_style}">
                    <div style="{bubble_style.format(bg=bg_color)}">
                        <div style="font-weight: bold;">{avatar} <span style="color: gray; font-size: 0.85em;">({time_str})</span></div>
                        <div style="margin-top: 5px;">{message}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No discussion yet.")

    st.divider()

    # Single input for message
    message = st.text_input("Write your message", key="message_input")

    col1, col2 = st.columns(2)
    
    # Button to add a message to the discussion
    with col1:
        if st.button("Add to Discussion") and message:
            update_discussion(selected_question["id"], user_name, message)
            st.success("Comment added to the discussion.")
            st.rerun()

    # Button to ask the AI
    with col2:
        if st.button("Ask AI") and message:
            with st.spinner("Generating AI response..."):

                image_context = ""
                full_prompt = f"{message}{image_context}"

                ai_answer = generate_ai_response(
                    message=full_prompt,
                    question_context=selected_question['question'],
                    discussion_history=selected_question["discussion"],
                    user_role=user_role
                )

                update_discussion(selected_question["id"], user_name, message)
                update_discussion(selected_question["id"], "AI", ai_answer)

            st.success("AI has responded.")
            st.rerun()


    st.divider()

    uploaded_image = st.file_uploader("Select an Image for the AI to analyse and add to the Discussion", type=["jpg", "jpeg", "png"])
    image_path, image_description = None, None

    if uploaded_image:
        image_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{uploaded_image.name}")
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        st.image(uploaded_image, caption="Uploaded Image", width=300)

        if st.button("Describe Image") and uploaded_image:
            with st.spinner("Describing image..."):
                if image_path:
                    image_description = describe_image(image_path)
                    image_context = f"\n\nThe user has also uploaded an image that can be described as:\n{image_description}"
                    system_image_note = f"<strong>Image uploaded:</strong> {image_description}"
                    update_discussion(selected_question["id"], "system", system_image_note)
                    st.rerun()
                else:
                    st.error("Please upload an image first.")

                    

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if user_role in allowed_roles_status:

                    # Show the selectbox for status change
                    new_status = st.selectbox(
                        "Select new status:",
                        options=["Open", "Assumption", "Resolved", "Deferred"],
                        index=["Open", "Assumption", "Resolved", "Deferred"].index(st.session_state[f"status_{selected_question['id']}"]),
                        key=f"status_select_{selected_question['id']}"
                    )
                    st.session_state[f"status_{selected_question['id']}"] = new_status
                    if new_status != selected_question['status']:
                        if st.button(f"Confirm Status Change", key=f"confirm_status_{selected_question['id']}"):
                            status_message = f"Status changed to **{new_status}** by {user_name}"
                            update_discussion(selected_question['id'], "system", status_message)
                            update_question_status(selected_question['id'], new_status)
                            st.success(f"Status for question '{selected_question['question']}' updated to '{new_status}'.")
                            st.session_state[f"status_{selected_question['id']}"] = new_status
                            st.rerun()
        else:
            st.write("You do not have permission to change the status of this question.")
    with col2:
        if user_role in allowed_roles_prio:
                # Show the selectbox for priority change
                new_priority = st.selectbox(
                    "Select new priority:",
                    options=["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(st.session_state.get(f"priority_{selected_question['id']}", selected_question['priority'])),
                    key=f"priority_select_{selected_question['id']}"
                )
            
                st.session_state[f"priority_{selected_question['id']}"] = new_priority
                if new_priority != selected_question['priority']:
                    if st.button(f"Confirm Priority Change", key=f"confirm_priority_{selected_question['id']}"):
                        prio_message = f"Priority changed to **{new_priority}** by {user_name}"
                        update_discussion(selected_question['id'], "system", prio_message)
                        update_question_prio(selected_question['id'], new_priority)
                        st.success(f"Priority for question '{selected_question['question']}' updated to '{new_priority}'.")
                        st.session_state[f"priority_{selected_question['id']}"] = new_priority
                        st.rerun()
        else:
            st.write("You do not have permission to change the priority of this question.")


    # Button to clear discussion
    admin_user = ["admin"]
    if user_role in admin_user:
        st.divider()
        st.subheader("Admin Actions")
        with st.expander("🧨 Dangerous Admin Actions for This Question", expanded=False):
            st.warning(f"This will permanently delete the entire discussion thread for the selected question:\n\n> _{selected_question['question']}_")
            if st.button("🗑️ Delete Discussion", key=f"delete_discussion_{selected_question['id']}"):
                clear_discussion_for_question(selected_question["id"])
                st.success("Discussion thread deleted.")
                st.rerun()