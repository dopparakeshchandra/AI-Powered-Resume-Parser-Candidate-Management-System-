import mysql.connector
import os
import random
import string


def get_db():
    """
    Create and return MySQL database connection
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            atabase=os.getenv("DB_NAME", "profile_details"))
        
        print("Database connected successfully")
        return connection

    except mysql.connector.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


def generate_password(length=8):
    """
    Generate a random password for new user
    
    Example output → "aB3$xK9m"
    """
    chars = (
        string.ascii_uppercase +   # A-Z
        string.ascii_lowercase +   # a-z
        string.digits +            # 0-9
        "!@#$"                     # special chars
    )
    return ''.join(random.choices(chars, k=length))




def save_profile(data, profile_status="Created"):
    """
    Save all extracted resume data to MySQL
    
    Saves to 6 tables:
    1. users
    2. auth_users
    3. skillset
    4. project_history
    5. certification
    6. awards

    Returns → user_id, password, email
    """
    db = get_db()
    cursor = db.cursor()

    try:
        u = data["users"]

        
        cursor.execute("""
            INSERT INTO users (
                first_name, last_name, date_of_birth,
                mobile_number, email_id, aadhar_number,
                pan_number, job_role, current_company,
                years_of_experience, profile_status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            u.get("first_name"),
            u.get("last_name"),
            u.get("date_of_birth"),
            u.get("mobile_number"),
            u.get("email_id"),
            u.get("aadhar_number"),
            u.get("pan_number"),
            u.get("job_role"),
            u.get("current_company"),
            u.get("years_of_experience"),
            u.get("profile_status")
            
        ))
        user_id = cursor.lastrowid
        print(f"User saved — ID: {user_id}")

      
        password = generate_password()
        cursor.execute("""
            INSERT INTO auth_users (
                user_id, email_id, user_password
            )
            VALUES (%s, %s, %s)
        """, (
            user_id,
            u.get("email_id"),
            password
        ))
        print(f" Auth saved — Password: {password}")

       
        for skill in data.get("skillset", []):
            cursor.execute("""
                INSERT INTO skillset (
                    user_id,
                    skill_name,
                    experence_level_in_skills
                )
                VALUES (%s, %s, %s)
            """, (
                user_id,
                skill.get("skill_name"),
                skill.get("experence_level_in_skills")
            ))
        print(f" Skills saved — "
              f"{len(data.get('skillset', []))} skills")

        for p in data.get("project_history", []):
            cursor.execute("""
                INSERT INTO project_history (
                    user_id, project_title,
                    project_description,
                    project_start_month, project_start_year,
                    project_end_month, project_end_year,
                    activites
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                user_id,
                p.get("project_title"),
                p.get("project_description"),
                p.get("project_start_month"),
                p.get("project_start_year"),
                p.get("project_end_month"),
                p.get("project_end_year"),
                p.get("activites")
            ))
        print(f" Projects saved — "
              f"{len(data.get('project_history', []))} projects")

    
        for c in data.get("certification", []):
            cursor.execute("""
                INSERT INTO certification (
                    user_id,
                    cerification_name,
                    year_of_certification
                )
                VALUES (%s, %s, %s)
            """, (
                user_id,
                c.get("cerification_name"),
                c.get("year_of_certification")
            ))
        print(f" Certifications saved — "
              f"{len(data.get('certification', []))} certs")

    
        for a in data.get("awards", []):
            cursor.execute("""
                INSERT INTO awards (
                    user_id,
                    award_name,
                    year_of_award,
                    company_name
                )
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                a.get("award_name"),
                a.get("year_of_award"),
                a.get("company_name")
            ))
        print(f" Awards saved — "
              f"{len(data.get('awards', []))} awards")

        db.commit()
        print("All data committed to database")
        return user_id, password, u.get("email_id")

    except Exception as e:
        db.rollback()
        print(f" Error — rolled back: {e}")
        raise e

    finally:
        cursor.close()
        db.close()


def fetch_profile(user_id):
    """
    Fetch complete profile data for display
    Returns all data from all 5 tables
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        
        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM skillset WHERE user_id = %s",
            (user_id,)
        )
        skills = cursor.fetchall()

       
        cursor.execute(
            "SELECT * FROM project_history WHERE user_id = %s",
            (user_id,)
        )
        projects = cursor.fetchall()

        
        cursor.execute(
            "SELECT * FROM certification WHERE user_id = %s",
            (user_id,)
        )
        certs = cursor.fetchall()

        
        cursor.execute(
            "SELECT * FROM awards WHERE user_id = %s",
            (user_id,)
        )
        awards = cursor.fetchall()

        return user, skills, projects, certs, awards

    finally:
        cursor.close()
        db.close()


def update_profile(user_id, updated_data):
    """
    Update user profile fields
    Called when user edits missing fields
    """
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE users SET
                first_name          = %s,
                last_name           = %s,
                date_of_birth       = %s,
                mobile_number       = %s,
                job_role            = %s,
                current_company     = %s,
                years_of_experience = %s
            WHERE user_id = %s
        """, (
            updated_data.get("first_name"),
            updated_data.get("last_name"),
            updated_data.get("date_of_birth"),
            updated_data.get("mobile_number"),
            updated_data.get("job_role"),
            updated_data.get("current_company"),
            updated_data.get("years_of_experience"),
            user_id
        ))

        db.commit()
        print(f" Profile updated for user_id: {user_id}")

    finally:
        cursor.close()
        db.close()



def update_profile_status(user_id, status):
    """
    Update lifecycle status of profile

    Allowed values:
    'Created' | 'Reviewed' | 'Open to Work' | 'Not Interested'
    """
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE users
            SET profile_status = %s
            WHERE user_id = %s
        """, (status, user_id))

        db.commit()
        print(f"Status updated → {status}")

    finally:
        cursor.close()
        db.close()



def check_login(email, password):
    """
    Verify login credentials
    Returns user_id if valid, None if invalid
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.user_id
            FROM auth_users a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.email_id = %s
            AND a.user_password = %s
        """, (email, password))

        user = cursor.fetchone()
        return user["user_id"] if user else None

    finally:
        cursor.close()
        db.close()