# Path: db.py
import os
import pymysql
from datetime import datetime, date, timedelta

# Automatically locate ca.pem in your project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_CERT_PATH = os.path.join(BASE_DIR, "ca.pem")

try:
    from local_config import DB_PASSWORD
except ImportError:
    DB_PASSWORD = ""

DB_CONFIG = {
    "host": "mantalaan-db-mantalaan-project.f.aivencloud.com",
    "port": 20885,
    "user": "avnadmin",
    "password": DB_PASSWORD,
    "database": "mantalaan_db",
    "cursorclass": pymysql.cursors.DictCursor,
    "ssl": {"ca": CA_CERT_PATH}
}

def get_connection():
    """Establish and return a new MySQL database connection to Aiven Cloud."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.Error as e:
        print(f"Database Connection Error: {e}")
        return None

# ==========================================
# AUTHENTICATION & USER MANAGEMENT
# ==========================================

def authenticate_user(username, password):
    """Authenticate a user, ensure they are active, and return their details including role name."""
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT u.user_id, u.role_id, u.username, u.full_name, u.email, u.status, r.role_name 
                FROM user u
                LEFT JOIN role r ON u.role_id = r.role_id
                WHERE u.username = %s AND u.password = %s
            """
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user and user.get('status') == 'Inactive':
                return None
                
            return user
    except pymysql.Error as e:
        print(f"Authentication Error: {e}")
        return None
    finally:
        conn.close()

def get_all_roles():
    """Fetch all roles for population in user management dropdowns."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = "SELECT role_id, role_name FROM role ORDER BY role_id ASC"
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching roles: {e}")
        return []
    finally:
        conn.close()

def get_all_users():
    """Fetch all users including their role name and status."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT u.user_id, u.username, u.full_name, u.email, u.role_id, r.role_name, u.status
                FROM user u
                LEFT JOIN role r ON u.role_id = r.role_id
                ORDER BY u.user_id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        conn.close()

def add_user_to_db(username, password, fullname, email, role_id, status="Active"):
    """Add a new user to the database with status."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists."

            query = """
                INSERT INTO user (username, password, full_name, email, role_id, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, password, fullname, email, role_id, status))
            conn.commit()
            return True, "User added successfully!"
    except pymysql.Error as e:
        print(f"Error adding user: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def update_user_in_db(user_id, username, password, fullname, email, role_id, status="Active"):
    """Update existing user information including status and return (success, message)."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            if password:
                query = """
                    UPDATE user 
                    SET username = %s, password = %s, full_name = %s, email = %s, role_id = %s, status = %s
                    WHERE user_id = %s
                """
                cursor.execute(query, (username, password, fullname, email, role_id, status, user_id))
            else:
                query = """
                    UPDATE user 
                    SET username = %s, full_name = %s, email = %s, role_id = %s, status = %s
                    WHERE user_id = %s
                """
                cursor.execute(query, (username, fullname, email, role_id, status, user_id))
            
            conn.commit()
            return True, "User updated successfully!"
    except pymysql.Error as e:
        print(f"Error updating user: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

# ==========================================
# CLIENT MANAGEMENT
# ==========================================

def get_all_clients():
    """Fetch all clients with their total publication counts ordered by ID descending."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT c.*, COUNT(p.publication_id) AS publication_count
                FROM client c
                LEFT JOIN publication p ON c.client_id = p.client_id
                GROUP BY c.client_id
                ORDER BY c.client_id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching clients: {e}")
        return []
    finally:
        conn.close()
        
def get_clients_for_combo():
    """Fetch lightweight active client data for UI dropdowns/comboboxes."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT client_id, client_name, status 
                FROM client 
                WHERE status = 'Active' 
                ORDER BY client_name ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching clients for dropdown: {e}")
        return []
    finally:
        conn.close()

def add_client_to_db(name, contact, case_no, pub_type, email="", address="", notes="", status="Active"):
    """Insert a new client into the database."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO client 
                (client_name, contact_number, case_number, publication_type, email, address, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, contact, case_no, pub_type, email, address, notes, status))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error inserting client: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_client_in_db(client_id, name, contact, case_no, pub_type, email="", address="", notes="", status="Active"):
    """Update existing client information."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE client 
                SET client_name = %s, contact_number = %s, case_number = %s, 
                    publication_type = %s, email = %s, address = %s, notes = %s, status = %s
                WHERE client_id = %s
            """
            cursor.execute(query, (name, contact, case_no, pub_type, email, address, notes, status, client_id))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error updating client: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def soft_delete_client_in_db(client_id):
    """Safely deactivate a client by updating their status to 'Inactive' instead of hard-deleting."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = "UPDATE client SET status = 'Inactive' WHERE client_id = %s"
            cursor.execute(query, (client_id,))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error deactivating client: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==========================================
# HELPER: DATE CALCULATION FOR MONDAYS
# ==========================================

def calculate_first_issue_date(date_received):
    """Calculates next week's Monday based on the received date."""
    if isinstance(date_received, str):
        start_date = datetime.strptime(date_received, "%Y-%m-%d").date()
    elif isinstance(date_received, datetime):
        start_date = date_received.date()
    elif isinstance(date_received, date):
        start_date = date_received
    else:
        start_date = date.today()

    dow = start_date.isoweekday()
    days_to_add = (7 - dow + 1)
    return start_date + timedelta(days=days_to_add)

# ==========================================
# PUBLICATION MANAGEMENT
# ==========================================

def get_all_publications():
    """Fetch all publications joined with client name and current issue schedule details."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    p.*,
                    c.client_name,
                    COALESCE(
                        (
                            SELECT MIN(issue_number) 
                            FROM publication_issue pi 
                            WHERE pi.publication_id = p.publication_id 
                              AND pi.status != 'Published' 
                              AND pi.publication_date >= CURDATE()
                        ),
                        (
                            SELECT MIN(issue_number) 
                            FROM publication_issue pi 
                            WHERE pi.publication_id = p.publication_id 
                              AND pi.status != 'Published'
                        ),
                        p.required_issues
                    ) AS current_issue,
                    COALESCE(
                        (
                            SELECT MIN(publication_date) 
                            FROM publication_issue pi 
                            WHERE pi.publication_id = p.publication_id 
                              AND pi.status != 'Published' 
                              AND pi.publication_date >= CURDATE()
                        ),
                        (
                            SELECT MAX(publication_date) 
                            FROM publication_issue pi 
                            WHERE pi.publication_id = p.publication_id
                        ),
                        p.date_received
                    ) AS scheduled_date
                FROM publication p
                LEFT JOIN client c ON p.client_id = c.client_id
                ORDER BY p.publication_id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching publications: {e}")
        return []
    finally:
        conn.close()

def get_publication_details(pub_id):
    """Fetch single publication details by ID."""
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.*, c.client_name 
                FROM publication p
                LEFT JOIN client c ON p.client_id = c.client_id
                WHERE p.publication_id = %s
            """
            cursor.execute(query, (pub_id,))
            return cursor.fetchone()
    except pymysql.Error as e:
        print(f"Error fetching publication details: {e}")
        return None
    finally:
        conn.close()

def add_publication_to_db(client_id, case_number, pub_type, date_received, req_issues, details, notes, status="In Progress"):
    """Create publication and generate weekly scheduled issues dynamically starting next week's Monday."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query_pub = """
                INSERT INTO publication 
                (client_id, case_number, publication_type, date_received, required_issues, legal_description, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_pub, (client_id, case_number, pub_type, date_received, req_issues, details, notes, status))
            pub_id = cursor.lastrowid

            first_monday = calculate_first_issue_date(date_received)
            num_issues = int(req_issues)
            query_issue = """
                INSERT INTO publication_issue (publication_id, issue_number, publication_date, status)
                VALUES (%s, %s, %s, %s)
            """
            for i in range(num_issues):
                issue_number = i + 1
                issue_date = first_monday + timedelta(weeks=i)
                cursor.execute(query_issue, (pub_id, issue_number, issue_date, "Scheduled"))

            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error inserting publication and issues: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_publication_in_db(pub_id, client_id, case_number, pub_type, date_received, req_issues, details, notes, status):
    """Update publication and regenerate issue schedules starting next week's Monday."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE publication 
                SET client_id = %s, case_number = %s, publication_type = %s, 
                    date_received = %s, required_issues = %s, legal_description = %s, 
                    notes = %s, status = %s
                WHERE publication_id = %s
            """
            cursor.execute(query, (client_id, case_number, pub_type, date_received, req_issues, details, notes, status, pub_id))

            cursor.execute("DELETE FROM publication_issue WHERE publication_id = %s", (pub_id,))

            first_monday = calculate_first_issue_date(date_received)
            num_issues = int(req_issues)
            query_issue = """
                INSERT INTO publication_issue (publication_id, issue_number, publication_date, status)
                VALUES (%s, %s, %s, %s)
            """
            for i in range(num_issues):
                issue_number = i + 1
                issue_date = first_monday + timedelta(weeks=i)
                cursor.execute(query_issue, (pub_id, issue_number, issue_date, "Scheduled"))

            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error updating publication and issues: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def soft_delete_publication_in_db(pub_id):
    """Safely deactivate a publication by updating its status to 'Inactive' instead of hard-deleting."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = "UPDATE publication SET status = 'Inactive' WHERE publication_id = %s"
            cursor.execute(query, (pub_id,))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error deactivating publication: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==========================================
# PUBLICATION ISSUE MANAGEMENT
# ==========================================

def get_publication_issues(pub_id):
    """Fetch all issues for a specific publication."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT * FROM publication_issue 
                WHERE publication_id = %s 
                ORDER BY issue_number ASC
            """
            cursor.execute(query, (pub_id,))
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching publication issues: {e}")
        return []
    finally:
        conn.close()

def get_all_publication_schedules():
    """Fetch all scheduled issues across all publications with client and case details."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    pi.issue_id,
                    pi.publication_id,
                    pi.issue_number,
                    pi.publication_date,
                    pi.status,
                    p.case_number,
                    c.client_name
                FROM publication_issue pi
                JOIN publication p ON pi.publication_id = p.publication_id
                LEFT JOIN client c ON p.client_id = c.client_id
                ORDER BY pi.publication_date DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching publication schedules: {e}")
        return []
    finally:
        conn.close()

def add_issue_to_db(publication_id, issue_number, publication_date, status="Scheduled"):
    """Manually add an issue to a publication and increment total count."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO publication_issue (publication_id, issue_number, publication_date, status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (publication_id, issue_number, publication_date, status))
            
            cursor.execute("""
                UPDATE publication 
                SET required_issues = required_issues + 1 
                WHERE publication_id = %s
            """, (publication_id,))

            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error adding manual issue: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_issue_in_db(issue_id, publication_date, status):
    """Update scheduled date or status for an existing issue."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE publication_issue 
                SET publication_date = %s, status = %s 
                WHERE issue_id = %s
            """
            cursor.execute(query, (publication_date, status, issue_id))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error updating issue: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_issue_from_db(issue_id, publication_id):
    """Delete an individual issue and decrement required_issues count."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM publication_issue WHERE issue_id = %s", (issue_id,))
            cursor.execute("""
                UPDATE publication 
                SET required_issues = GREATEST(0, required_issues - 1) 
                WHERE publication_id = %s
            """, (publication_id,))
            conn.commit()
            return True
    except pymysql.Error as e:
        print(f"Error deleting issue: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==========================================
# BILLING & PAYMENTS MANAGEMENT
# ==========================================

def get_publications_for_billing():
    """Fetch active publications formatted for Billing UI controls."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.publication_id, p.case_number, c.client_name 
                FROM publication p
                LEFT JOIN client c ON p.client_id = c.client_id
                WHERE p.status != 'Inactive'
                ORDER BY p.publication_id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching publications for billing combo: {e}")
        return []
    finally:
        conn.close()

def get_billing_details_by_pub(pub_id):
    """Calculate Total Amount, Amount Paid, and Balance for a publication."""
    conn = get_connection()
    if not conn:
        return {"total_amount": 0.00, "amount_paid": 0.00, "balance": 0.00}

    try:
        with conn.cursor() as cursor:
            query_pub = "SELECT total_amount FROM publication WHERE publication_id = %s"
            cursor.execute(query_pub, (pub_id,))
            pub = cursor.fetchone()
            
            raw_total = pub.get('total_amount') if pub else None
            total_amount = float(raw_total) if raw_total is not None else 3000.00

            query_paid = """
                SELECT COALESCE(SUM(p.amount), 0) as amount_paid 
                FROM payment p
                LEFT JOIN billing b ON p.billing_id = b.billing_id
                WHERE p.publication_id = %s OR b.publication_id = %s
            """
            cursor.execute(query_paid, (pub_id, pub_id))
            paid_res = cursor.fetchone()
            amount_paid = float(paid_res['amount_paid'] if paid_res else 0.00)

            balance = total_amount - amount_paid

            return {
                "total_amount": total_amount,
                "amount_paid": amount_paid,
                "balance": max(0.00, balance)
            }
    except pymysql.Error as e:
        print(f"Error fetching billing details: {e}")
        return {"total_amount": 0.00, "amount_paid": 0.00, "balance": 0.00}
    finally:
        conn.close()

def set_or_update_billing_amount(pub_id, total_amount):
    """Create or update the base billing total_amount for a publication."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE publication SET total_amount = %s WHERE publication_id = %s", (total_amount, pub_id))
            
            cursor.execute("SELECT billing_id FROM billing WHERE publication_id = %s", (pub_id,))
            billing_row = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(p.amount), 0) as total_paid 
                FROM payment p
                LEFT JOIN billing b ON p.billing_id = b.billing_id
                WHERE p.publication_id = %s OR b.publication_id = %s
            """, (pub_id, pub_id))
            paid_row = cursor.fetchone()
            total_paid = float(paid_row['total_paid'] if paid_row else 0.0)

            new_balance = max(0.0, float(total_amount) - total_paid)
            new_status = 'Paid' if new_balance == 0 else ('Partial' if total_paid > 0 else 'Unpaid')

            if billing_row:
                cursor.execute("""
                    UPDATE billing 
                    SET total_amount = %s, balance = %s, status = %s 
                    WHERE publication_id = %s
                """, (total_amount, new_balance, new_status, pub_id))
            else:
                cursor.execute("""
                    INSERT INTO billing (publication_id, total_amount, balance, status)
                    VALUES (%s, %s, %s, %s)
                """, (pub_id, total_amount, new_balance, new_status))

            conn.commit()
            return True, "Billing total updated successfully!"
    except pymysql.Error as e:
        print(f"Error updating billing amount: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def get_payment_history_by_pub(pub_id):
    """Fetch payment transactions for a given publication by linking billing or direct publication_id."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT DISTINCT 
                    p.payment_id, 
                    p.billing_id, 
                    p.publication_id, 
                    p.payment_date, 
                    p.amount, 
                    p.payment_method, 
                    p.or_number 
                FROM payment p
                LEFT JOIN billing b ON p.billing_id = b.billing_id
                WHERE p.publication_id = %s OR b.publication_id = %s
                ORDER BY p.payment_date DESC, p.payment_id DESC
            """
            cursor.execute(query, (pub_id, pub_id))
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching payment history: {e}")
        return []
    finally:
        conn.close()

def record_payment_in_db(pub_id, amount, payment_method, or_number, user_id=None):
    """Record a new payment transaction and recalculate balance."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            if not user_id:
                cursor.execute("SELECT user_id FROM user LIMIT 1")
                user_row = cursor.fetchone()
                if not user_row:
                    return False, "No valid user logged in."
                user_id = user_row.get("user_id")

            cursor.execute("SELECT billing_id, balance, total_amount FROM billing WHERE publication_id = %s", (pub_id,))
            billing_row = cursor.fetchone()

            if billing_row:
                billing_id = billing_row.get("billing_id")
            else:
                cursor.execute("SELECT total_amount FROM publication WHERE publication_id = %s", (pub_id,))
                pub_row = cursor.fetchone()
                init_total = float(pub_row.get('total_amount')) if pub_row and pub_row.get('total_amount') is not None else 3000.00

                cursor.execute("""
                    INSERT INTO billing (publication_id, total_amount, balance, status)
                    VALUES (%s, %s, %s, 'Unpaid')
                """, (pub_id, init_total, init_total))
                billing_id = cursor.lastrowid

            pay_amt = float(amount)

            cursor.execute("""
                INSERT INTO payment (
                    billing_id, 
                    received_by, 
                    payment_date, 
                    amount, 
                    payment_method, 
                    or_number, 
                    publication_id
                )
                VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
            """, (billing_id, user_id, pay_amt, payment_method, or_number, pub_id))

            recalculate_billing_balance(cursor, pub_id)

            conn.commit()
            return True, "Payment recorded successfully!"

    except pymysql.Error as e:
        print(f"Error recording payment: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def update_payment_in_db(payment_id, pub_id, amount, payment_method, or_number):
    """Update an existing payment entry and recalculate balance."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE payment 
                SET amount = %s, payment_method = %s, or_number = %s
                WHERE payment_id = %s
            """
            cursor.execute(query, (amount, payment_method, or_number, payment_id))

            recalculate_billing_balance(cursor, pub_id)

            conn.commit()
            return True, "Payment record updated successfully!"
    except pymysql.Error as e:
        print(f"Error updating payment: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def delete_payment_from_db(payment_id, pub_id):
    """Delete a payment entry and recalculate balance."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM payment WHERE payment_id = %s", (payment_id,))

            recalculate_billing_balance(cursor, pub_id)

            conn.commit()
            return True, "Payment deleted successfully!"
    except pymysql.Error as e:
        print(f"Error deleting payment: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def recalculate_billing_balance(cursor, pub_id):
    """Internal helper to recompute balance and status for billing."""
    cursor.execute("SELECT total_amount FROM publication WHERE publication_id = %s", (pub_id,))
    pub_row = cursor.fetchone()
    total_amount = float(pub_row.get('total_amount')) if pub_row and pub_row.get('total_amount') is not None else 3000.00

    cursor.execute("""
        SELECT COALESCE(SUM(p.amount), 0) as total_paid 
        FROM payment p
        LEFT JOIN billing b ON p.billing_id = b.billing_id
        WHERE p.publication_id = %s OR b.publication_id = %s
    """, (pub_id, pub_id))
    paid_row = cursor.fetchone()
    total_paid = float(paid_row['total_paid'] if paid_row else 0.0)

    new_balance = max(0.0, total_amount - total_paid)
    new_status = 'Paid' if new_balance == 0 else ('Partial' if total_paid > 0 else 'Unpaid')

    cursor.execute("""
        UPDATE billing 
        SET total_amount = %s, balance = %s, status = %s 
        WHERE publication_id = %s
    """, (total_amount, new_balance, new_status, pub_id))

# ==========================================
# DASHBOARD METRICS & DATA
# ==========================================

def get_dashboard_metrics():
    """Fetch statistical counts and daily collection totals for dashboard metrics cards."""
    conn = get_connection()
    if not conn:
        return {
            "pending_layout": 0,
            "upcoming_publications": 0,
            "unreleased_documents": 0,
            "total_collections_today": 0.00,
            "payments_today_count": 0
        }

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as cnt 
                FROM publication 
                WHERE status IN ('Pending', 'In Progress', 'Layout Verification')
            """)
            pending_layout = cursor.fetchone().get('cnt', 0)

            cursor.execute("""
                SELECT COUNT(*) as cnt 
                FROM publication_issue 
                WHERE status = 'Scheduled' AND publication_date >= CURDATE()
            """)
            upcoming_pubs = cursor.fetchone().get('cnt', 0)

            cursor.execute("""
                SELECT COUNT(DISTINCT p.publication_id) as cnt
                FROM publication p
                LEFT JOIN billing b ON p.publication_id = b.publication_id
                WHERE (p.status != 'Released' AND p.status != 'Inactive') OR b.balance > 0
            """)
            unreleased_docs = cursor.fetchone().get('cnt', 0)

            cursor.execute("""
                SELECT 
                    COALESCE(SUM(amount), 0.00) as total_today,
                    COUNT(*) as pay_count
                FROM payment
                WHERE DATE(payment_date) = CURDATE()
            """)
            pay_data = cursor.fetchone()
            total_today = float(pay_data.get('total_today', 0.00))
            pay_count = pay_data.get('pay_count', 0)

            return {
                "pending_layout": pending_layout,
                "upcoming_publications": upcoming_pubs,
                "unreleased_documents": unreleased_docs,
                "total_collections_today": total_today,
                "payments_today_count": pay_count
            }
    except pymysql.Error as e:
        print(f"Error fetching dashboard metrics: {e}")
        return {
            "pending_layout": 0,
            "upcoming_publications": 0,
            "unreleased_documents": 0,
            "total_collections_today": 0.00,
            "payments_today_count": 0
        }
    finally:
        conn.close()

def get_active_publication_schedules_dashboard(limit=5):
    """Fetch active multi-issue publications and their next scheduled run for the dashboard table."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    p.publication_id,
                    p.case_number,
                    c.client_name,
                    p.publication_type,
                    p.required_issues,
                    COALESCE(
                        (SELECT MIN(issue_number) 
                         FROM publication_issue pi 
                         WHERE pi.publication_id = p.publication_id 
                           AND pi.status != 'Published' 
                           AND pi.publication_date >= CURDATE()),
                        (SELECT MIN(issue_number) 
                         FROM publication_issue pi 
                         WHERE pi.publication_id = p.publication_id 
                           AND pi.status != 'Published'),
                        p.required_issues
                    ) AS current_issue_num,
                    COALESCE(
                        (SELECT MIN(publication_date) 
                         FROM publication_issue pi 
                         WHERE pi.publication_id = p.publication_id 
                           AND pi.status != 'Published' 
                           AND pi.publication_date >= CURDATE()),
                        (SELECT MAX(publication_date) 
                         FROM publication_issue pi 
                         WHERE pi.publication_id = p.publication_id),
                        p.created_at
                    ) AS next_date
                FROM publication p
                LEFT JOIN client c ON p.client_id = c.client_id
                WHERE p.status = 'In Progress'
                ORDER BY next_date ASC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching active publication schedules for dashboard: {e}")
        return []
    finally:
        conn.close()

# ==========================================
# DOCUMENT MANAGEMENT (OIC & Publisher Review)
# ==========================================

def get_all_documents():
    """Fetch all uploaded documents from the document table ordered by ID descending."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM document ORDER BY document_id DESC"
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching documents: {e}")
        return []
    finally:
        conn.close()

def update_document_status_in_db(document_id, status):
    """Update review status for a specific document in the document table."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            query = "UPDATE document SET status = %s WHERE document_id = %s"
            cursor.execute(query, (status, document_id))
            conn.commit()
            return True, "Document status updated successfully!"
    except pymysql.Error as e:
        print(f"Error updating document status: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

# ==========================================
# MONDAY PDF BLOB STORAGE MANAGEMENT
# ==========================================

def init_pdf_table():
    """Ensure the table for storing Monday PDF blobs exists with review status support."""
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monday_pdf_uploads (
                    upload_id INT AUTO_INCREMENT PRIMARY KEY,
                    publication_date DATE NOT NULL UNIQUE,
                    file_name VARCHAR(255) NOT NULL,
                    file_data LONGBLOB NOT NULL,
                    review_status VARCHAR(50) DEFAULT 'Pending',
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except pymysql.Error as e:
        print(f"Error creating PDF table: {e}")
    finally:
        conn.close()

init_pdf_table()

def save_monday_pdf_to_db(publication_date, file_name, file_binary_data):
    """Save or update a PDF binary blob for a specific Monday publication date and reset review_status to 'Pending'."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO monday_pdf_uploads (publication_date, file_name, file_data, review_status)
                VALUES (%s, %s, %s, 'Pending')
                ON DUPLICATE KEY UPDATE file_name = VALUES(file_name), file_data = VALUES(file_data), review_status = 'Pending'
            """
            cursor.execute(query, (publication_date, file_name, file_binary_data))
            conn.commit()
            return True, "PDF uploaded and stored successfully in database!"
    except pymysql.Error as e:
        print(f"Error saving PDF to DB: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def get_monday_pdf_from_db(publication_date):
    """Fetch stored PDF filename, binary data, and review status for a specific Monday date."""
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            query = "SELECT file_name, file_data, review_status FROM monday_pdf_uploads WHERE publication_date = %s"
            cursor.execute(query, (publication_date,))
            return cursor.fetchone()
    except pymysql.Error as e:
        print(f"Error fetching PDF from DB: {e}")
        return None
    finally:
        conn.close()

def delete_monday_pdf_from_db(publication_date):
    """Delete the stored Monday PDF record from the database for a given date."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            query = "DELETE FROM monday_pdf_uploads WHERE publication_date = %s"
            cursor.execute(query, (publication_date,))
            conn.commit()
            return True, "PDF deleted successfully from database!"
    except pymysql.Error as e:
        print(f"Error deleting PDF from DB: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()

def get_scheduled_publications_with_pdfs():
    """Fetch all uploaded Monday PDF records with individual rows for each associated case, client, and issue."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    m.upload_id AS schedule_id,
                    m.publication_date,
                    m.file_name,
                    COALESCE(m.review_status, 'Pending') AS review_status,
                    COALESCE(p.case_number, 'N/A') AS case_number,
                    COALESCE(c.client_name, 'N/A') AS client_name,
                    COALESCE(CONCAT(pi.issue_number, ' of ', p.required_issues), 'N/A') AS issue_number
                FROM monday_pdf_uploads m
                LEFT JOIN publication_issue pi ON m.publication_date = pi.publication_date
                LEFT JOIN publication p ON pi.publication_id = p.publication_id
                LEFT JOIN client c ON p.client_id = c.client_id
                ORDER BY m.publication_date DESC, p.case_number ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching scheduled publications with PDFs: {e}")
        return []
    finally:
        conn.close()

def update_publication_schedule_status(schedule_id, new_status):
    """Update the review status ('Approved' or 'Rejected') for an uploaded PDF record."""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cursor:
            query = "UPDATE monday_pdf_uploads SET review_status = %s WHERE upload_id = %s"
            cursor.execute(query, (new_status, schedule_id))
            conn.commit()
            return True, f"PDF status successfully updated to {new_status}!"
    except pymysql.Error as e:
        print(f"Error updating schedule status: {e}")
        conn.rollback()
        return False, f"Database Error: {e}"
    finally:
        conn.close()
        
def get_all_publications_with_billing_status():
    """Fetch all publications joined with billing status, amounts, payments, and client details."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    p.publication_id,
                    p.case_number,
                    p.publication_type,
                    p.date_received,
                    c.client_name,
                    COALESCE(b.total_amount, p.total_amount, 3000.00) AS total_amount,
                    COALESCE(pay_agg.amount_paid, 0.00) AS amount_paid,
                    GREATEST(0.00, COALESCE(b.total_amount, p.total_amount, 3000.00) - COALESCE(pay_agg.amount_paid, 0.00)) AS balance,
                    CASE 
                        WHEN GREATEST(0.00, COALESCE(b.total_amount, p.total_amount, 3000.00) - COALESCE(pay_agg.amount_paid, 0.00)) = 0.00 THEN 'Paid'
                        WHEN COALESCE(pay_agg.amount_paid, 0.00) > 0.00 THEN 'Partial'
                        ELSE 'Unpaid'
                    END AS billing_status
                FROM publication p
                LEFT JOIN client c ON p.client_id = c.client_id
                LEFT JOIN billing b ON p.publication_id = b.publication_id
                LEFT JOIN (
                    SELECT 
                        COALESCE(b_sub.publication_id, p_sub.publication_id) AS pub_id,
                        SUM(p_sub.amount) AS amount_paid
                    FROM payment p_sub
                    LEFT JOIN billing b_sub ON p_sub.billing_id = b_sub.billing_id
                    GROUP BY COALESCE(b_sub.publication_id, p_sub.publication_id)
                ) pay_agg ON pay_agg.pub_id = p.publication_id
                ORDER BY p.publication_id DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching publications with billing status: {e}")
        return []
    finally:
        conn.close()