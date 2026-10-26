import streamlit as st
import time
from pdf_extract import extract_text_from_pdf
from openai_parser import parse_resume_data
from Database import (
    save_profile,
    fetch_profile,
    check_login,
    update_profile,
    update_profile_status
)
from email_server import send_credentials
from score_utils import (
    calculate_profile_score,
    get_profile_status,
    get_score_label
)

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title = "AI Profile Onboarder",
    page_icon  = "🤖",
    layout     = "wide"
)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "upload"       # upload | login | profile
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False


# ─────────────────────────────────────────
# PAGE 1 — UPLOAD RESUME
# ─────────────────────────────────────────
def upload_page():
    st.title("🤖 AI Resume Profile Onboarder")
    st.write("Upload your resume PDF — AI will extract and create your profile automatically.")
    st.divider()

    uploaded_file = st.file_uploader(
        "📄 Upload PDF Resume",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("🚀 Process Resume", use_container_width=True):

            # ── Step 1: Extract Text ──────────
            with st.spinner("📖 Step 1/4 — Extracting text from PDF..."):
                resume_text = extract_text_from_pdf(uploaded_file)

            # ── Step 2: Parse with OpenAI ─────
            with st.spinner("🤖 Step 2/4 — AI parsing resume..."):
                profile_data = parse_resume_data(resume_text)

            # ── Step 3: Calculate Score ───────
            with st.spinner("📊 Step 3/4 — Calculating profile score..."):
                u        = profile_data["users"]
                skills   = profile_data.get("skillset", [])
                projs    = profile_data.get("project_history", [])
                certs    = profile_data.get("certification", [])
                awards   = profile_data.get("awards", [])
                score    = calculate_profile_score(
                    u, skills, projs, certs, awards
                )
                status   = get_profile_status(score)

            # ── Step 4: Save + Email ──────────
            with st.spinner("💾 Step 4/4 — Saving profile and sending email..."):
                user_id, password, email = save_profile(
                    profile_data,
                    profile_status=status
                )
                name = profile_data["users"].get(
                    "first_name", "Candidate"
                )
                send_credentials(email, password, name)

            # ── Success Message ───────────────
            st.success("✅ Profile created successfully!")
            st.divider()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Profile Score", f"{score}/100")
            with col2:
                st.metric("Profile Status", status)
            with col3:
                label, _ = get_score_label(score)
                st.metric("Label", label)

            st.info(
                f"📧 Login credentials sent to your Gmail!\n\n"
                f"**Candidate Email :** {email}\n\n"
                f"**Password        :** {password}"
            )

            # ── Auto Redirect to Login ────────
            st.success("🔄 Redirecting to login page in 2 seconds...")
            time.sleep(2)
            st.session_state.page = "login"
            st.rerun()


# ─────────────────────────────────────────
# PAGE 2 — LOGIN
# ─────────────────────────────────────────
def login_page():
    st.title("🔐 Candidate Login")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Login to Your Profile")
        st.write("")

        email    = st.text_input("📧 Email ID")
        password = st.text_input("🔑 Password", type="password")
        st.write("")

        if st.button("Login →", use_container_width=True):
            if not email or not password:
                st.error("❌ Please enter both email and password!")
            else:
                user_id = check_login(email, password)

                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = user_id
                    st.session_state.page      = "profile"
                    st.success("✅ Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")

        st.write("")
        st.write("---")
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()


# ─────────────────────────────────────────
# PAGE 3 — PROFILE DASHBOARD
# ─────────────────────────────────────────
def profile_page():
    user, skills, projects, certs, awards = fetch_profile(
        st.session_state.user_id
    )

    # ── Score + Header ───────────────────
    score        = calculate_profile_score(
        user, skills, projects, certs, awards
    )
    label, color = get_score_label(score)

    # ── Top Bar ───────────────────────────
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(
            f"👤 {user['first_name'] or ''} "
            f"{user['last_name'] or ''}"
        )
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id   = None
            st.session_state.page      = "upload"
            st.session_state.edit_mode = False
            st.rerun()

    # ── Score Bar ─────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Profile Score", f"{score}/100")
    with col2:
        st.metric("🔄 Status", user["profile_status"])
    with col3:
        st.metric("🏷️ Label", label)
    st.progress(score / 100)
    st.divider()

    # ─────────────────────────────────────
    # VIEW MODE
    # ─────────────────────────────────────
    if not st.session_state.edit_mode:

        # ── Personal Info ─────────────────
        st.subheader("📋 Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**First Name    :** {user['first_name'] or '—'}")
            st.write(f"**Last Name     :** {user['last_name'] or '—'}")
            st.write(f"**Email ID      :** {user['email_id'] or '—'}")
            st.write(f"**Mobile Number :** {user['mobile_number'] or '—'}")
        with col2:
            st.write(f"**Date of Birth :** {user['date_of_birth'] or '—'}")
            st.write(f"**Job Role      :** {user['job_role'] or '—'}")
            st.write(f"**Company       :** {user['current_company'] or '—'}")
            st.write(f"**Experience    :** {user['years_of_experience'] or '—'} years")
        st.divider()

        # ── Skills ────────────────────────
        st.subheader("🛠️ Skills")
        if skills:
            cols = st.columns(3)
            for i, skill in enumerate(skills):
                with cols[i % 3]:
                    level = skill["experence_level_in_skills"]
                    icon  = (
                        "🟢" if level == "Advanced"
                        else "🟡" if level == "Intermediate"
                        else "🔵"
                    )
                    st.write(
                        f"{icon} **{skill['skill_name']}**"
                        f" — {level}"
                    )
        else:
            st.write("No skills added yet.")
        st.divider()

        # ── Projects ──────────────────────
        st.subheader("📁 Projects")
        if projects:
            for p in projects:
                with st.expander(
                    f"🔹 {p['project_title'] or 'Untitled'}"
                ):
                    st.write(
                        f"**Description :** "
                        f"{p['project_description'] or '—'}"
                    )
                    st.write(
                        f"**Duration    :** "
                        f"{p['project_start_month'] or ''} "
                        f"{p['project_start_year'] or ''} → "
                        f"{p['project_end_month'] or ''} "
                        f"{p['project_end_year'] or ''}"
                    )
                    if p["activites"]:
                        st.write(
                            f"**Tools       :** {p['activites']}"
                        )
        else:
            st.write("No projects added yet.")
        st.divider()

        # ── Certifications ────────────────
        st.subheader("🏅 Certifications")
        if certs:
            for c in certs:
                st.write(
                    f"• **{c['cerification_name']}** "
                    f"({c['year_of_certification'] or '—'})"
                )
        else:
            st.write("No certifications added yet.")
        st.divider()

        # ── Awards ────────────────────────
        st.subheader("🏆 Awards")
        if awards:
            for a in awards:
                st.write(
                    f"• **{a['award_name']}** — "
                    f"{a['company_name'] or '—'} "
                    f"({a['year_of_award'] or '—'})"
                )
        else:
            st.write("No awards added yet.")
        st.divider()

        # ── Status Update ─────────────────
        st.subheader("🔄 Profile Status")
        new_status = st.selectbox(
            "Update your status:",
            [
                "Created",
                "Reviewed",
                "Open to Work",
                "Not Interested"
            ],
            index=[
                "Created",
                "Reviewed",
                "Open to Work",
                "Not Interested"
            ].index(user["profile_status"] or "Created")
        )
        if st.button("Update Status"):
            update_profile_status(
                st.session_state.user_id,
                new_status
            )
            st.success(f"✅ Status updated to: {new_status}")
            st.rerun()
        st.divider()

        # ── Edit Button ───────────────────
        if st.button(
            "✏️ Edit Profile",
            use_container_width=True
        ):
            st.session_state.edit_mode = True
            st.rerun()

    # ─────────────────────────────────────
    # EDIT MODE
    # ─────────────────────────────────────
    else:
        st.subheader("✏️ Edit Profile")
        st.info("Update your details below and click Save.")

        with st.form("edit_form"):

            # ── Personal Info ─────────────
            st.markdown("#### 📋 Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input(
                    "First Name",
                    value=user["first_name"] or ""
                )
                email_id = st.text_input(
                    "Email ID",
                    value=user["email_id"] or ""
                )
                job_role = st.text_input(
                    "Job Role",
                    value=user["job_role"] or ""
                )
                experience = st.text_input(
                    "Years of Experience",
                    value=str(user["years_of_experience"] or "")
                )
            with col2:
                last_name = st.text_input(
                    "Last Name",
                    value=user["last_name"] or ""
                )
                mobile = st.text_input(
                    "Mobile Number",
                    value=user["mobile_number"] or ""
                )
                company = st.text_input(
                    "Current Company",
                    value=user["current_company"] or ""
                )
                dob = st.text_input(
                    "Date of Birth (YYYY-MM-DD)",
                    value=str(user["date_of_birth"] or "")
                )

            st.divider()

            # ── Form Buttons ──────────────
            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True
                )
            with col2:
                cancel = st.form_submit_button(
                    "❌ Cancel",
                    use_container_width=True
                )

            # ── Save Logic ────────────────
            if save:
                updated_data = {
                    "first_name"         : first_name,
                    "last_name"          : last_name,
                    "email_id"           : email_id,
                    "mobile_number"      : mobile,
                    "date_of_birth"      : dob,
                    "job_role"           : job_role,
                    "current_company"    : company,
                    "years_of_experience": experience
                }
                update_profile(
                    st.session_state.user_id,
                    updated_data
                )

                # Recalculate score after update
                new_score  = calculate_profile_score(
                    updated_data, skills,
                    projects, certs, awards
                )
                new_status = get_profile_status(new_score)
                update_profile_status(
                    st.session_state.user_id,
                    new_status
                )

                st.success(
                    f"✅ Profile saved! "
                    f"Score: {new_score}/100 | "
                    f"Status: {new_status}"
                )
                st.session_state.edit_mode = False
                time.sleep(1)
                st.rerun()

            # ── Cancel Logic ──────────────
            if cancel:
                st.session_state.edit_mode = False
                st.rerun()


# ─────────────────────────────────────────
# MAIN ROUTER — 3 pages
# ─────────────────────────────────────────
def main():
    if st.session_state.page == "upload":
        upload_page()

    elif st.session_state.page == "login":
        login_page()

    elif st.session_state.page == "profile":
        if st.session_state.logged_in:
            profile_page()
        else:
            st.session_state.page = "login"
            st.rerun()

main()