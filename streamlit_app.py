import streamlit as st

from enrollment_starter import (
    CURRENT_STUDENT,
    STATUS_UNENROLLED,
    create_tables,
    seed_sample_data,
    get_available_course_keys,
    get_student_enrollments,
    get_student_enrollment_history,
    enroll_with_key,
    soft_unenroll_student,
    export_database_snapshot,
)

st.set_page_config(page_title="Enrollment Manager", page_icon="🎓", layout="wide")

create_tables()
seed_sample_data()

st.title("AI-Assisted Project Enrollment Manager")
st.write("A lightweight Streamlit UI for enrolling students in practice courses.")

student = CURRENT_STUDENT
st.sidebar.header("Current Student")
st.sidebar.write(f"**Name:** {student['name']}")
st.sidebar.write(f"**Email:** {student['email']}")
st.sidebar.write(f"**User ID:** {student['user_id']}")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Enroll with a Course Key")
    with st.form("enroll_form"):
        enrollment_key = st.text_input("Enter an enrollment key", value="")
        submit = st.form_submit_button("Enroll")

        if submit:
            if not enrollment_key:
                st.error("Please enter an enrollment key.")
            else:
                result = enroll_with_key(student["user_id"], student["email"], enrollment_key.strip())
                if result:
                    st.success(f"Enrolled in {result['course_id']} - {result['course_name']}.")
                else:
                    st.error("Enrollment failed. Check the key and try again.")

    st.header("Available Course Keys")
    available = get_available_course_keys()
    for course in available:
        st.markdown(
            f"**{course['course_id']}**  
            {course['course_name']}  
            Instructor: {course['instructor']}  
            Key: `{course['enrollment_key']}`"
        )

with col2:
    st.header("Summary")
    history = get_student_enrollment_history(student["user_id"])
    enrolled = [record for record in history if record["status"] != STATUS_UNENROLLED]
    unenrolled = [record for record in history if record["status"] == STATUS_UNENROLLED]

    st.metric("Courses Enrolled", len(enrolled))
    st.metric("Total Records", len(history))
    st.metric("Courses Unenrolled", len(unenrolled))

st.header("Current Enrollments")
current_enrollments = get_student_enrollments(student["user_id"])
if current_enrollments:
    for record in current_enrollments:
        course_id = record["course_id"]
        cols = st.columns([3, 2])
        cols[0].markdown(
            f"**{course_id}** — {record['course_name']}  
            Instructor: {record['instructor']}  
            Enrolled at: {record['enrolled_at']}"
        )
        if cols[1].button("Unenroll", key=f"unenroll_{course_id}"):
            success = soft_unenroll_student(student["user_id"], course_id)
            if success:
                st.success(f"Soft-unenrolled from {course_id}.")
                st.experimental_rerun()
            else:
                st.error("Unable to unenroll. Try again.")
else:
    st.info("No current enrollments found.")

st.header("Enrollment History")
if history:
    st.table(
        [
            {
                "Course ID": record["course_id"],
                "Course Name": record["course_name"],
                "Status": record["status"],
                "Enrolled At": record["enrolled_at"],
            }
            for record in history
        ]
    )
else:
    st.info("Enrollment history is empty.")

if st.button("Export Snapshot"):
    export_database_snapshot()
    st.success("Database snapshot exported.")
    st.write("Saved to `student_enrollment_snapshot.json`.")
