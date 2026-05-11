import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

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


def generate_pdf_report(student, enrollments, history, available_keys):
    """Generate a PDF report of the student's enrollment data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Student Enrollment Report", styles['Title']))
    story.append(Spacer(1, 12))

    # Student Info
    story.append(Paragraph(f"Student: {student['name']}", styles['Heading2']))
    story.append(Paragraph(f"Email: {student['email']}", styles['Normal']))
    story.append(Paragraph(f"User ID: {student['user_id']}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Summary
    enrolled_count = len([e for e in history if e['status'] != STATUS_UNENROLLED])
    unenrolled_count = len([e for e in history if e['status'] == STATUS_UNENROLLED])
    story.append(Paragraph("Summary", styles['Heading2']))
    story.append(Paragraph(f"Courses Enrolled: {enrolled_count}", styles['Normal']))
    story.append(Paragraph(f"Courses Unenrolled: {unenrolled_count}", styles['Normal']))
    story.append(Paragraph(f"Total Records: {len(history)}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Current Enrollments
    if enrollments:
        story.append(Paragraph("Current Enrollments", styles['Heading2']))
        data = [['Course ID', 'Course Name', 'Instructor', 'Enrolled At']]
        for e in enrollments:
            data.append([e['course_id'], e['course_name'], e['instructor'], e['enrolled_at']])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    # Enrollment History
    if history:
        story.append(Paragraph("Enrollment History", styles['Heading2']))
        data = [['Course ID', 'Course Name', 'Status', 'Enrolled At']]
        for h in history:
            data.append([h['course_id'], h['course_name'], h['status'], h['enrolled_at']])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    # Available Course Keys
    if available_keys:
        story.append(Paragraph("Available Course Keys", styles['Heading2']))
        data = [['Course ID', 'Course Name', 'Instructor', 'Enrollment Key']]
        for k in available_keys:
            data.append([k['course_id'], k['course_name'], k['instructor'], k['enrollment_key']])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer


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

st.header("Export PDF Report")
if st.button("Generate and Download PDF Report"):
    pdf_buffer = generate_pdf_report(student, current_enrollments, history, available)
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="enrollment_report.pdf",
        mime="application/pdf",
        key="download_pdf"
    )
