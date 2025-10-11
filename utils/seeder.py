import pymysql
from faker import Faker
import bcrypt
import random
from datetime import datetime, timedelta
from db.db_connection import create_connection

fake = Faker()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def generate_unique_id_number(existing_ids, length=6):
    while True:
        id_number = ''.join(random.choices('0123456789', k=length))
        if id_number not in existing_ids:
            existing_ids.add(id_number)
            return id_number


def seed_admins(conn, count=5):
    existing_ids = {'test_admin_id'}  # Replace with your test admin ID
    cursor = conn.cursor()
    for _ in range(count):
        full_name = fake.name()
        id_number = generate_unique_id_number(existing_ids)
        password = hash_password('password123')  # Default password for dummy users
        cursor.execute(
            "INSERT INTO admins (full_name, id_number, password) VALUES (%s, %s, %s)",
            (full_name, id_number, password)
        )
    conn.commit()
    cursor.close()


def seed_instructors(conn, count=10):
    existing_ids = {'test_instructor_id'}  # Replace with your test instructor ID
    cursor = conn.cursor()
    for _ in range(count):
        full_name = fake.name()
        id_number = generate_unique_id_number(existing_ids)
        password = hash_password('password123')
        cursor.execute(
            "INSERT INTO instructors (full_name, id_number, password) VALUES (%s, %s, %s)",
            (full_name, id_number, password)
        )
    conn.commit()
    cursor.close()


def seed_students(conn, count=30):
    existing_ids = {'test_student_id'}  # Replace with your test student ID
    cursor = conn.cursor()
    strands = ['STEM', 'ABM', 'HUMSS', 'GAS']
    grade_levels = ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12']
    for _ in range(count):
        full_name = fake.name()
        id_number = generate_unique_id_number(existing_ids)
        password = hash_password('password123')
        strand = random.choice(strands)
        grade_level = random.choice(grade_levels)
        cursor.execute(
            "INSERT INTO students (full_name, strand, grade_level, id_number, password) VALUES (%s, %s, %s, %s, %s)",
            (full_name, strand, grade_level, id_number, password)
        )
    conn.commit()
    cursor.close()


def seed_books(conn, count=40):
    cursor = conn.cursor()
    categories = ['Fiction', 'Science', 'History', 'Technology', 'Arts', 'Education']
    statuses = ['Available', 'Borrowed', 'Overdue']
    existing_isbns = set()
    for _ in range(count):
        title = fake.catch_phrase()
        edition = f"{random.randint(1, 10)}th Edition"
        publication = fake.company()
        author = fake.name()
        isbn = fake.isbn13()
        while isbn in existing_isbns:
            isbn = fake.isbn13()
        existing_isbns.add(isbn)
        status = random.choice(statuses)
        # Generate a PDF file name explicitly
        reason_pdf_path = f"/pdfs/{fake.word()}_{random.randint(1000, 9999)}.pdf" if random.random() < 0.3 else None
        cursor.execute(
            "INSERT INTO books (category, title, edition, publication, author, isbn, status, reason_pdf_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (random.choice(categories), title, edition, publication, author, isbn, status, reason_pdf_path)
        )
    conn.commit()
    cursor.close()


def seed_borrowing_history(conn, count=15):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_type FROM (SELECT id, 'Student' AS user_type FROM students UNION SELECT id, 'Instructor' AS user_type FROM instructors) AS users")
    users = cursor.fetchall()
    cursor.execute("SELECT id FROM books")
    book_ids = [row[0] for row in cursor.fetchall()]

    conditions = ['Excellent', 'Good', 'Fair', '-']
    statuses = ['Active', 'Returned', 'Returned Late', 'Overdue']

    for _ in range(count):
        user = random.choice(users)
        user_id, user_type = user
        book_id = random.choice(book_ids)
        date_borrowed = fake.date_time_between(start_date='-1y', end_date='now')
        date_returned = None
        return_status = 'Active'
        condition = '-'
        fine = 0.00

        if random.random() < 0.6:  # 60% chance of having returned
            date_returned = date_borrowed + timedelta(days=random.randint(1, 30))
            return_status = random.choice(['Returned', 'Returned Late'])
            condition = random.choice(conditions)
            if return_status == 'Returned Late':
                fine = round(random.uniform(5.00, 50.00), 2)
            elif random.random() < 0.2:  # 20% chance of fine even if returned
                fine = round(random.uniform(5.00, 20.00), 2)
        elif random.random() < 0.2:  # 20% chance of overdue for active loans
            return_status = 'Overdue'
            fine = round(random.uniform(10.00, 100.00), 2)

        cursor.execute(
            """
            INSERT INTO borrowing_history (user_id, user_type, book_id, date_borrowed, date_returned, return_status, `condition`, fine)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, user_type, book_id, date_borrowed, date_returned, return_status, condition, fine)
        )
    conn.commit()
    cursor.close()


def main():
    conn = create_connection()
    if conn:
        print("Seeding database...")
        seed_admins(conn, count=5)
        seed_instructors(conn, count=10)
        seed_students(conn, count=30)
        seed_books(conn, count=40)
        seed_borrowing_history(conn, count=15)
        print("Seeding completed.")
        conn.close()
    else:
        print("Failed to connect to the database.")


if __name__ == "__main__":
    main()