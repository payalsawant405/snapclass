import streamlit as st

from src.home_screen import home_screen
from src.teacher_screen import teacher_screen
from src.student_screen import student_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    st.set_page_config(
        page_title="SnapClass - Making Attendance faster using AI",
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )

    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # Get join code FIRST
    join_code = st.query_params.get("join-code")

    # If student joins through a link, switch to student mode first
    if join_code and st.session_state["login_type"] != "student":
        st.session_state["login_type"] = "student"
        st.rerun()

    # Show appropriate screen
    match st.session_state["login_type"]:

        case "teacher":
            teacher_screen()

        case "student":
            student_screen()

        case None:
            home_screen()

    # Auto enroll after student is logged in
    if (
        join_code
        and st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):
        auto_enroll_dialog(join_code)


if __name__ == "__main__":
    main()