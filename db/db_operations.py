import pymysql
import bcrypt
from datetime import datetime
from db.db_connection import create_connection

class DatabaseOperations:
    def __init__(self):
        self.conn = create_connection()
        if self.conn is None:
            raise Exception("Failed to connect to database")

    def close_connection(self):
        if self.conn:
            self.conn.close()

    # --- User Operations ---
    def register_user(self, role, full_name, id_number, password, strand=None, grade_level=None):
        cursor = self.conn.cursor()
        try:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if role == "Student":
                query = """
                    INSERT INTO students (full_name, strand, grade_level, id_number, password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (full_name, strand, grade_level, id_number, hashed_pw))
            elif role == "Instructor":
                query = """
                    INSERT INTO instructors (full_name, id_number, password)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (full_name, id_number, hashed_pw))
            elif role == "Admin":
                query = """
                    INSERT INTO admins (full_name, id_number, password)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (full_name, id_number, hashed_pw))
            self.conn.commit()
            return True
        except pymysql.Error as e:
            print(f"Database error during registration: {e}")
            return False
        finally:
            cursor.close()

    def login_user(self, role, id_number, password):
        cursor = self.conn.cursor()
        try:
            table = {"Student": "students", "Instructor": "instructors", "Admin": "admins"}[role]
            query = f"SELECT password, full_name, id FROM {table} WHERE id_number = %s"
            cursor.execute(query, (id_number,))
            result = cursor.fetchone()
            if result:
                stored_hash = result[0].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return {"id": result[2], "full_name": result[1]}
            return None
        except pymysql.Error as e:
            print(f"Database error during login: {e}")
            return None
        finally:
            cursor.close()

    # --- Book Operations ---
    def add_book(self, category, title, edition, publication, author, isbn, reason_pdf_path=None):
        cursor = self.conn.cursor()
        try:
            query = """
                INSERT INTO books (category, title, edition, publication, author, isbn, reason_pdf_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Available')
            """
            cursor.execute(query, (category, title, edition, publication, author, isbn, reason_pdf_path))
            self.conn.commit()
            return True
        except pymysql.Error as e:
            print(f"Database error during book addition: {e}")
            return False
        finally:
            cursor.close()

    def get_all_books(self):
        cursor = self.conn.cursor()
        try:
            query = "SELECT id, category, title, author, edition, isbn, publication, status FROM books"
            cursor.execute(query)
            return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Database error during fetching books: {e}")
            return []
        finally:
            cursor.close()

    def search_books_by_category(self, category):
        cursor = self.conn.cursor()
        try:
            query = "SELECT id, category, title, author, edition, isbn, publication, status FROM books WHERE category = %s"
            cursor.execute(query, (category,))
            return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Database error during book search: {e}")
            return []
        finally:
            cursor.close()

    def update_book(self, book_id, category, title, edition, publication, author, isbn, reason_pdf_path=None):
        cursor = self.conn.cursor()
        try:
            query = """
                UPDATE books
                SET category = %s, title = %s, edition = %s, publication = %s, author = %s, isbn = %s, reason_pdf_path = %s
                WHERE id = %s
            """
            cursor.execute(query, (category, title, edition, publication, author, isbn, reason_pdf_path, book_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except pymysql.Error as e:
            print(f"Database error during book update: {e}")
            return False
        finally:
            cursor.close()

    # --- Borrowing Operations ---
    def borrow_book(self, user_id, user_type, book_id, borrow_date):
        cursor = self.conn.cursor()
        try:
            # Check borrowing limit
            cursor.execute(
                "SELECT COUNT(*) FROM borrowing_history WHERE user_id = %s AND user_type = %s AND return_status IN ('Active', 'Overdue')",
                (user_id, user_type)
            )
            active_books = cursor.fetchone()[0]
            if active_books >= 5:
                return False, "Cannot borrow more than 5 books at a time"

            # Check book availability
            cursor.execute("SELECT status FROM books WHERE id = %s", (book_id,))
            result = cursor.fetchone()
            if not result or result[0] != "Available":
                return False, "Book is not available"

            # Update book status
            cursor.execute("UPDATE books SET status = 'Borrowed' WHERE id = %s", (book_id,))

            # Record borrowing
            cursor.execute(
                "INSERT INTO borrowing_history (user_id, user_type, book_id, date_borrowed, return_status) "
                "VALUES (%s, %s, %s, %s, 'Active')",
                (user_id, user_type, book_id, borrow_date)
            )
            self.conn.commit()
            return True, "Book borrowed successfully"
        except pymysql.Error as e:
            print(f"Database error during borrowing: {e}")
            self.conn.rollback()
            return False, str(e)
        finally:
            cursor.close()

    def return_book(self, record_id, book_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE borrowing_history SET return_status = 'Returned', date_returned = %s WHERE id = %s",
                (datetime.now(), record_id)
            )
            cursor.execute("UPDATE books SET status = 'Available' WHERE id = %s", (book_id,))
            self.conn.commit()
            return True, "Book returned successfully"
        except pymysql.Error as e:
            print(f"Database error during return: {e}")
            self.conn.rollback()
            return False, str(e)
        finally:
            cursor.close()

    def get_borrowing_history(self, user_id=None, user_type=None):
        cursor = self.conn.cursor()
        try:
            if user_id and user_type:
                query = """
                    SELECT bh.id, bh.user_id, bh.user_type, bh.book_id, b.title, bh.date_borrowed, 
                           bh.date_returned, bh.return_status, bh.`condition`, bh.fine, b.category
                    FROM borrowing_history bh
                    JOIN books b ON bh.book_id = b.id
                    WHERE bh.user_id = %s AND bh.user_type = %s
                """
                cursor.execute(query, (user_id, user_type))
            else:
                query = """
                    SELECT bh.id, bh.user_id, bh.user_type, bh.book_id, b.title, bh.date_borrowed, 
                           bh.date_returned, bh.return_status, bh.`condition`, bh.fine, b.category
                    FROM borrowing_history bh
                    JOIN books b ON bh.book_id = b.id
                """
                cursor.execute(query)
            return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Database error during fetching borrowing history: {e}")
            return []
        finally:
            cursor.close()

    def get_all_users(self, user_type=None):
        cursor = self.conn.cursor()
        try:
            if user_type == "Student":
                query = "SELECT id, full_name, strand AS course, grade_level AS year, id_number FROM students"
                cursor.execute(query)
            elif user_type == "Instructor":
                query = "SELECT id, full_name, '' AS course, 'Faculty' AS year, id_number FROM instructors"
                cursor.execute(query)
            else:
                query = """
                    SELECT id, full_name, strand AS course, grade_level AS year, id_number FROM students
                    UNION
                    SELECT id, full_name, '' AS course, 'Faculty' AS year, id_number FROM instructors
                """
                cursor.execute(query)
            users = cursor.fetchall()
            return [{"no": i+1, "type": "STUDENT" if user[2] else "INSTRUCTOR", "name": user[1], "course": user[2], "year": user[3], "id": user[4]} for i, user in enumerate(users)]
        except pymysql.Error as e:
            print(f"Database error during fetching users: {e}")
            return []
        finally:
            cursor.close()