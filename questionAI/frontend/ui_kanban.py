import streamlit as st
from backend.backlog import load_backlog, clear_backlog
from frontend.ui_question_card import QuestionCard
import time
import re

def display_kanban_board():
    st.title("Questions' Backlog Board")
    user_role = st.session_state.get("user_role", "").lower()
    # ✅ Add CSS to make columns scrollable individually
    st.markdown("""
    <style>
        section.main > div {
            padding-bottom: 1rem;
        }
        [data-testid="column"] > div > div > div > div > div {
            max-height: 610px;  /* Adjust this for ~5 cards */
            overflow-y: auto;
            padding-right: 8px; /* Avoid clipping scroll bar */
        }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.get("authenticated", False):
        st.warning("You must be logged in to view the backlog.")
        return

    questions = load_backlog()
    if not questions:
        st.info("No questions found in the backlog.")
        return

    st.subheader("🔍 Smart Filter")

    # Layout: Chips first
    # with st.expander("Filters", expanded=False):
    #     st.markdown(
    #         """
    #         <style>
    #         /* Remove spacing between columns */
    #         div[data-testid="column"] {
    #             padding-left: 0 !important;
    #             padding-right: 0 !important;
    #             margin-right: -2px !important;
    #         }

    #         /* Make button containers tighter */
    #         .element-container {
    #             margin: 0 !important;
    #             padding: 0 !important;
    #         }

    #         /* Style the buttons to be compact and uniform */
    #         .stButton > button {
    #             background-color: #f0f2f6;
    #             color: #000;
    #             border-radius: 5px;
    #             padding: 4px 10px;
    #             font-size: 13px;
    #             margin: 0 !important;
    #         }
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )
    #     col1, col2, col3, col4, col5 = st.columns(5)
    #     with col1:
    #         if st.button("prio:", key="chip_prio"):
    #             st.session_state.smart_search += " prio:"
    #     with col2:
    #         if st.button("owner:", key="chip_owner"):
    #             st.session_state.smart_search += " owner:"
    #     with col3:
    #         if st.button("tag:", key="chip_tag"):
    #             st.session_state.smart_search += " tag:"
    #     with col4:
    #         if st.button("status:", key="chip_status"):
    #             st.session_state.smart_search += " status:"
    #     with col5:
    #         if st.button("category:", key="chip_category"):
    #             st.session_state.smart_search += " category:"

    # Initialize session state if not set
    if "smart_search" not in st.session_state:
        st.session_state["smart_search"] = ""

    # ✅ Use the session state directly as the input value
    search_query = st.text_input(
        "`Use filters like prio:High owner:Rui tag:Design status:Open category:Testing. Combine with commas for OR or spaces for AND. You can also search free text`",
        key="smart_search"
    )
    def parse_smart_filters(query: str) -> dict:
        pattern = r'(\w+):(".*?"|\S+)'  # captures prio:"Very High", user:alice
        matches = re.findall(pattern, query)
        filters = {}
        for key, val in matches:
            items = [v.strip().lower() for v in val.strip('"').split(",")]
            filters[key.lower()] = items
        return filters

    def matches_smart_filter(q, filters):
        def contains_any(value, keywords):
            return any(k in value.lower() for k in keywords)

        if 'prio' in filters:
            if not contains_any(q.get("priority", ""), filters["prio"]):
                return False
        if 'owner' in filters:
            if not contains_any(q.get("owner", ""), filters["owner"]):
                return False
        if 'tag' in filters:
            if not contains_any(q.get("taxonomy", ""), filters["tag"]):
                return False
        if 'status' in filters:
            if not contains_any(q.get("status", ""), filters["status"]):
                return False
        if 'category' in filters:
            if not contains_any(q.get("category", ""), filters["category"]):
                return False
        return True


    smart_filters = parse_smart_filters(search_query)
    keyword_only = re.sub(r'\w+:"[^"]*"|\w+:\S+', '', search_query).strip().lower()

    filtered_questions = []
    for q in questions:
        if smart_filters and not matches_smart_filter(q, smart_filters):
            continue
        if keyword_only and keyword_only not in q.get("question", "").lower():
            continue
        filtered_questions.append(q)

    # 🧩 Categorize by status
    statuses = ["Open", "Assumption", "Resolved", "Deferred"]
    status_categories = {status: [] for status in statuses}
    for q in filtered_questions:
        status_categories[q['status']].append(q)

    # 🧱 Draw scrollable columns
    columns = st.columns(len(statuses))
    col_map = dict(zip(statuses, columns))


    for status in statuses:
        with col_map[status]:
            st.subheader(status)
            if not status_categories[status]:
                st.caption("No questions in this category.")
            with st.container():
                st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
                for question in status_categories[status]:
                    QuestionCard.create_task_card(question)
                st.markdown('</div>', unsafe_allow_html=True)

    
    st.divider()
    # Optional refresh
    st.button("Refresh Board", on_click=refresh_board)
    allowed_roles_prio = ["admin"]
    if user_role in allowed_roles_prio:
        with st.expander("⚠️ Dangerous Admin Actions", expanded=False):
            st.warning("This will permanently delete all questions from the backlog.")
            if st.button("🔥 Delete ALL Questions"):               
                clear_backlog()
                st.success("All questions have been deleted.")
                st.rerun()

def refresh_board():
    """Dummy delay for refresh effect."""
    time.sleep(1)
