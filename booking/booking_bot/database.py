
import sqlite3

DB_NAME = r"E:\chatbot\booking\booking_bot\hospital.db"


def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                morning_start TEXT,
                morning_end TEXT,
                break_start TEXT,
                break_end TEXT,
                evening_start TEXT,
                evening_end TEXT
            )
        """)

        # Insert doctors if they do not already exist
        doctors = [
            ("dr_sharma", "11:00", "13:00", "13:00",
             "14:00", "14:00", "20:00"),

            ("dr_khan", "10:00", "13:00", "13:00",
             "14:00", "14:00", "19:00")
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO doctors (
                name, morning_start, morning_end,
                break_start, break_end,
                evening_start, evening_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, doctors)

        # Appointments table with status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                session TEXT NOT NULL,
                queue_number INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Booked'
            )
        """)

        # Migration for an existing database
        columns = [
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(appointments)"
            ).fetchall()
        ]

        if "status" not in columns:
            cursor.execute("""
                ALTER TABLE appointments
                ADD COLUMN status TEXT NOT NULL DEFAULT 'Booked'
            """)

    return "Tables created successfully!"


if __name__ == "__main__":
    print(create_tables())

    # Verify appointment columns
    with sqlite3.connect(DB_NAME) as conn:
        columns = conn.execute(
            "PRAGMA table_info(appointments)"
        ).fetchall()

        print("\nAppointments table columns:")
        for column in columns:
            print(column[1])
