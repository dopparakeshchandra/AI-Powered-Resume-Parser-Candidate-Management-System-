def calculate_profile_score(user, skills, projects, certs, awards):
    """
    Calculate profile completeness score out of 100

    Scoring Breakdown:
    ──────────────────────────────
    Personal Info  → 30 points
    Skills         → 20 points
    Projects       → 20 points
    Certifications → 15 points
    Experience     → 15 points
    ──────────────────────────────
    Total          → 100 points
    """

    score = 0

    # ── 1. PERSONAL INFO — 30 points ─────
    personal_fields = [
        user.get("first_name"),
        user.get("last_name"),
        user.get("email_id"),
        user.get("mobile_number"),
        user.get("job_role"),
        user.get("current_company"),
        user.get("date_of_birth")
    ]
    filled = sum(
        1 for f in personal_fields
        if f and str(f) != "None"
    )
    personal_score = int((filled / len(personal_fields)) * 30)
    score += personal_score
    print(f"📊 Personal Info Score : {personal_score}/30")

    # ── 2. SKILLS — 20 points ────────────
    skill_count = len(skills)
    if skill_count >= 5:
        skill_score = 20
    elif skill_count >= 3:
        skill_score = 15
    elif skill_count >= 1:
        skill_score = 10
    else:
        skill_score = 0
    score += skill_score
    print(f"📊 Skills Score        : {skill_score}/20"
          f" ({skill_count} skills)")

    # ── 3. PROJECTS — 20 points ──────────
    project_count = len(projects)
    if project_count >= 3:
        project_score = 20
    elif project_count >= 2:
        project_score = 15
    elif project_count >= 1:
        project_score = 10
    else:
        project_score = 0
    score += project_score
    print(f"📊 Projects Score      : {project_score}/20"
          f" ({project_count} projects)")

    # ── 4. CERTIFICATIONS — 15 points ────
    cert_count = len(certs)
    if cert_count >= 2:
        cert_score = 15
    elif cert_count >= 1:
        cert_score = 10
    else:
        cert_score = 0
    score += cert_score
    print(f"📊 Certs Score         : {cert_score}/15"
          f" ({cert_count} certs)")

    # ── 5. EXPERIENCE — 15 points ────────
    try:
        exp = float(user.get("years_of_experience") or 0)
        if exp >= 5:
            exp_score = 15
        elif exp >= 2:
            exp_score = 10
        elif exp >= 1:
            exp_score = 5
        else:
            exp_score = 0
    except:
        exp_score = 0
    score += exp_score
    print(f"📊 Experience Score    : {exp_score}/15")

    # ── FINAL SCORE ───────────────────────
    final_score = min(score, 100)
    print(f"📊 Total Score         : {final_score}/100")
    return final_score


# ─────────────────────────────────────────
# PROFILE STATUS BASED ON SCORE
# ─────────────────────────────────────────
def get_profile_status(score):
    """
    Determine lifecycle status based on score

    Score 0  - 40  → Created
    Score 41 - 70  → Reviewed
    Score 71 - 100 → Open to Work
    """
    if score >= 71:
        status = "Open to Work"
    elif score >= 41:
        status = "Reviewed"
    else:
        status = "Created"

    print(f"📊 Profile Status      : {status}")
    return status


# ─────────────────────────────────────────
# SCORE LABEL + COLOR FOR UI
# ─────────────────────────────────────────
def get_score_label(score):
    """
    Returns label and color for Streamlit UI display

    Returns → (label, color)
    """
    if score >= 71:
        return "Excellent Profile 🌟", "green"
    elif score >= 41:
        return "Good Profile 👍", "orange"
    else:
        return "Incomplete Profile ⚠️", "red"