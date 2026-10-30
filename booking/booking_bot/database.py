import sqlite3

DB_NAME = r"E:\chatbot\booking\booking_bot\hospital.db"


def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                session TEXT NOT NULL,
                queue_number INTEGER NOT NULL
            )
        """)

    return "Tables created successfully!"