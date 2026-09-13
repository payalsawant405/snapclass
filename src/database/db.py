from src.database.config import supabase
import bcrypt


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_pass(pwd):
    return bcrypt.hashpw(
        pwd.encode(),
        bcrypt.gensalt()
    ).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(
        pwd.encode(),
        hashed.encode()
    )


# =========================================================
# TEACHER FUNCTIONS
# =========================================================

def check_teacher_exists(username):
    """
    Check whether teacher username already exists.
    Returns True if username is already taken.
    """

    response = (
        supabase
        .table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )

    return len(response.data) > 0


def create_teacher(username, password, name):

    data = {
        "username": username,
        "password": hash_pass(password),
        "name": name
    }

    response = (
        supabase
        .table("teachers")
        .insert(data)
        .execute()
    )

    return response.data


def teacher_login(username, password):

    response = (
        supabase
        .table("teachers")
        .select("*")
        .eq("username", username)
        .execute()
    )

    if response.data:

        teacher = response.data[0]

        if check_pass(
            password,
            teacher["password"]
        ):
            return teacher

    return None


# =========================================================
# STUDENT FUNCTIONS
# =========================================================

def get_all_students():

    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data


def create_student(
    new_name,
    face_embedding=None,
    voice_embedding=None
):

    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }

    response = (
        supabase
        .table("students")
        .insert(data)
        .execute()
    )

    return response.data


# =========================================================
# SUBJECT FUNCTIONS
# =========================================================

def create_subject(
    subject_code,
    name,
    section,
    teacher_id
):

    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }

    response = (
        supabase
        .table("subjects")
        .insert(data)
        .execute()
    )

    return response.data


def get_teacher_subjects(teacher_id):

    # IMPORTANT:
    # Supabase table name is attendance_log
    # NOT attendance_logs

    response = (
        supabase
        .table("subjects")
        .select(
            "*, subject_students(count), attendance_log(timestamp)"
        )
        .eq(
            "teacher_id",
            teacher_id
        )
        .execute()
    )

    subjects = response.data


    for sub in subjects:

        # -----------------------------
        # Total Students
        # -----------------------------

        subject_students = sub.get(
            "subject_students",
            []
        )

        if subject_students:

            sub["total_students"] = (
                subject_students[0].get(
                    "count",
                    0
                )
            )

        else:

            sub["total_students"] = 0


        # -----------------------------
        # Total Classes
        # -----------------------------

        attendance = sub.get(
            "attendance_log",
            []
        )

        timestamps = [
            log.get("timestamp")
            for log in attendance
            if log.get("timestamp")
        ]

        unique_sessions = len(
            set(timestamps)
        )

        sub["total_classes"] = unique_sessions


        # Remove temporary nested data
        sub.pop(
            "subject_students",
            None
        )

        sub.pop(
            "attendance_log",
            None
        )


    return subjects


# =========================================================
# ENROLL STUDENT
# =========================================================

def enroll_student_to_subject(
    student_id,
    subject_id
):

    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }

    response = (
        supabase
        .table("subject_students")
        .insert(data)
        .execute()
    )

    return response.data


# =========================================================
# UNENROLL STUDENT
# =========================================================

def unenroll_student_to_subject(
    student_id,
    subject_id
):

    response = (
        supabase
        .table("subject_students")
        .delete()
        .eq(
            "student_id",
            student_id
        )
        .eq(
            "subject_id",
            subject_id
        )
        .execute()
    )

    return response.data


# =========================================================
# GET STUDENT SUBJECTS
# =========================================================

def get_student_subjects(student_id):

    response = (
        supabase
        .table("subject_students")
        .select("*, subjects(*)")
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    return response.data


# =========================================================
# GET STUDENT ATTENDANCE
# =========================================================

def get_student_attendance(student_id):

    response = (
        supabase
        .table("attendance_log")
        .select("*, subjects(*)")
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    return response.data


# =========================================================
# CREATE ATTENDANCE
# =========================================================

def create_attendance(logs):

    response = (
        supabase
        .table("attendance_log")
        .insert(logs)
        .execute()
    )

    return response.data


# =========================================================
# GET ATTENDANCE FOR TEACHER
# =========================================================

def get_attendance_for_teacher(teacher_id):

    response = (
        supabase
        .table("attendance_log")
        .select(
            "*, subjects!inner(*)"
        )
        .eq(
            "subjects.teacher_id",
            teacher_id
        )
        .execute()
    )

    return response.data

