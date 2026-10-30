import re

def normalize_doctor_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_doctor(cursor, dr_name):

    user_name = normalize_doctor_name(dr_name)

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    for doctor in doctors:

        db_name = normalize_doctor_name(doctor[1])

        if user_name == db_name:
            return doctor

    return None