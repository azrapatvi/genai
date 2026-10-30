from langchain_core.tools import tool
from utils import find_doctor,normalize_doctor_name
from database import DB_NAME
import sqlite3

@tool
def check_availability(dr_name: str, session: str):
    """Check a doctor's working hours for the morning or evening session."""

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        doctor = find_doctor(cursor, dr_name)

        if doctor is None:
            return f"Sorry, {dr_name} was not found!"

        # Always use the original name stored in DB
        dr_name = doctor[1]

        morning_start = doctor[2]
        morning_end = doctor[3]
        evening_start = doctor[6]
        evening_end = doctor[7]

        session = session.lower().strip()

        if session == "morning":
            return (
                f"{dr_name} is available in the morning "
                f"from {morning_start} to {morning_end}."
            )

        elif session == "evening":
            return (
                f"{dr_name} is available in the evening "
                f"from {evening_start} to {evening_end}."
            )

        else:
            return "Please choose either morning or evening."

    finally:
        conn.close()


@tool
def book_appointment(
    patient_name: str,
    phone: str,
    dr_name: str,
    appointment_date: str,
    session: str
):
    """Book a hospital appointment after patient confirmation."""

    session = session.strip().lower()

    if session not in ("morning", "evening"):
        return "Please choose morning or evening."

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        doctor = find_doctor(cursor, dr_name)

        if doctor is None:
            return f"Sorry, {dr_name} was not found!"

        # Use the standardized name from the doctors table
        dr_name = doctor[1]

        cursor.execute("""
            SELECT COALESCE(MAX(queue_number), 0) + 1
            FROM appointments
            WHERE doctor_name = ?
              AND appointment_date = ?
              AND session = ?
        """, (dr_name, appointment_date, session))

        queue_number = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO appointments (
                patient_name, phone, doctor_name,
                appointment_date, session, queue_number
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_name.strip(),
            phone.strip(),
            dr_name,
            appointment_date,
            session,
            queue_number
        ))

        conn.commit()

        return (
            f"Appointment booked successfully! "
            f"Queue number: {queue_number}. "
            f"Doctor: {dr_name}. "
            f"Date: {appointment_date}. "
            f"Session: {session}. "
            "Your exact consultation time is not guaranteed."
        )

    except sqlite3.Error as e:
        conn.rollback()
        return f"Unable to book the appointment: {e}"

    finally:
        conn.close()


@tool
def find_appointments(phone: str) -> str:
    """Find existing appointments using the patient's phone number."""

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT appointment_id, patient_name, doctor_name,
                   appointment_date, session, queue_number
            FROM appointments
            WHERE phone = ?
            ORDER BY appointment_date
        """, (phone.strip(),))

        appointments = cursor.fetchall()

        if not appointments:
            return "No appointments found for this phone number."

        result = []

        for appointment in appointments:
            result.append(
                f"Appointment ID: {appointment[0]}, "
                f"Patient: {appointment[1]}, "
                f"Doctor: {appointment[2]}, "
                f"Date: {appointment[3]}, "
                f"Session: {appointment[4]}, "
                f"Queue number: {appointment[5]}"
            )

        return "\n".join(result)

    finally:
        conn.close()


@tool
def update_appointment(
    appointment_id: int,
    patient_name: str,
    phone: str,
    dr_name: str,
    appointment_date: str,
    session: str
) -> str:
    """Update an appointment after patient confirmation."""

    session = session.strip().lower()

    if session not in ("morning", "evening"):
        return "Please choose morning or evening."

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT appointment_id
            FROM appointments
            WHERE appointment_id = ?
        """, (appointment_id,))

        if cursor.fetchone() is None:
            return f"No appointment found with ID {appointment_id}."

        doctor = find_doctor(cursor, dr_name)

        if doctor is None:
            return f"Sorry, {dr_name} was not found."

        # Always use the standardized database name
        dr_name = doctor[1]

        cursor.execute("""
            SELECT COALESCE(MAX(queue_number), 0) + 1
            FROM appointments
            WHERE doctor_name = ?
              AND appointment_date = ?
              AND session = ?
              AND appointment_id != ?
        """, (dr_name, appointment_date, session, appointment_id))

        queue_number = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE appointments
            SET patient_name = ?,
                phone = ?,
                doctor_name = ?,
                appointment_date = ?,
                session = ?,
                queue_number = ?
            WHERE appointment_id = ?
        """, (
            patient_name.strip(),
            phone.strip(),
            dr_name,
            appointment_date,
            session,
            queue_number,
            appointment_id
        ))

        conn.commit()

        return (
            f"Appointment updated successfully! "
            f"Appointment ID: {appointment_id}. "
            f"Patient: {patient_name}. "
            f"Doctor: {dr_name}. "
            f"Date: {appointment_date}. "
            f"Session: {session}. "
            f"New queue number: {queue_number}. "
            "The exact consultation time is not guaranteed."
        )

    except sqlite3.Error as e:
        conn.rollback()
        return f"Unable to update the appointment: {e}"

    finally:
        conn.close()
