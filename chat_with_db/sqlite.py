
import sqlite3

try:
    conn = sqlite3.connect(
        r"E:\chatbot\chat_with_db\student.db"
    )
    cursor = conn.cursor()

    print("Connected to database")

    table_structure = """
    CREATE TABLE IF NOT EXISTS students (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        class INTEGER
    )
    """

    cursor.execute(table_structure)
    print("Table created successfully")

    # Insert student records
    student_records = [
        ("Azra", 12),
        ("Ayesha", 10),
        ("Rahul", 11),
        ("Sara", 12),
        ("Aman", 10),
        ("Priya", 11),
        ("Zoya", 12),
        ("Rohan", 9)
    ]

    cursor.executemany(
        "INSERT INTO students (name, class) VALUES (?, ?)",
        student_records
    )

    # Save changes
    conn.commit()

    print("Student records inserted successfully")

    # Display records
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    for row in data:
        print(row)

except Exception as e:
    print("Error:", e)

