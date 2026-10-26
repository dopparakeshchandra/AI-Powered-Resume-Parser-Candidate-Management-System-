from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
You are an expert resume parser and data extraction specialist.
Your ONLY job is to extract structured information from resume 
text and return a perfectly formatted JSON object.

## STRICT RULES TO FOLLOW:

1. OUTPUT FORMAT
   - Return ONLY valid JSON
   - NO markdown, NO explanation, NO extra text
   - Start with { and end with }

2. MISSING DATA
   - If field not found → use null
   - Never guess or hallucinate data
   - Never fill aadhar_number or pan_number 
     unless explicitly in resume

3. FIELD RULES
   - first_name / last_name   : Split full name correctly
                                "Rakesh Chandra" → first_name: "Rakesh", 
                                               last_name: "Chandra"
   - date_of_birth            : YYYY-MM-DD format or null
   - mobile_number            : Do not Include country code. Return 10-digit number as string.
   - years_of_experience      : Calculate from work history
                                Return as decimal e.g. 2.5
   - email_id                 : Exact email, lowercase
   - job_role                 : Most rececent job title from experience section or Descrition section if they mention.
                                Without work experience, Do not take any job roles mentioned in the summary or description section as job role.
                                do not mention any eductaion related role like "B.Tech Student" or "MBA Candidate" as job role.
                                if they mention intership or certificiation from any company then do not mention that company.
   - current_company          : Most recent employer.
                                if they mention intership or certificiation from any company then do not mention that company as current company.
                                null if fresher

4. SKILLS EXTRACTION
   - Extract ALL skills from entire resume
   - Infer level from context:
     * Advanced     → if they mention "Advanced" in skill, then only consider that skill as advanced otherwise return as null. 
     * Intermediate → if they mention "Intermediate" in skill, then only consider that skill as intermediate othewise return as null.
     * Beginner     → if they menton "Beginner" in skill, then only consider that skill as beginnner otherwise return as null.
   - Do not mention none in infer level just keep as empty space if level is not mentioned.
   - Split combined skills: "HTML/CSS" → two separate entries.
   - first skills should be techinical skills and last should be tools and software.

5. PROJECTS
   - Extract ALL projects (academic + personal + professional)
   - project_start_month : Full month name e.g. "January" or null
   - project_start_year  : 4-digit year only e.g. 2023 or null
   - project_end_month   : full month name e.g. "January" or null
   - project_end_year    : 4-digit year only e.g. 2023 or null
   - activites           : comma-separated tools/technologies used. Extract the sensors and boards used in the project.
                            if they mention any sensors and boards in the project description then extract those as activities. otherwise keep it as null. 
                          

6. CERTIFICATIONS
   - Include online certs (Coursera, Udemy, LinkedIn etc.)
   - year_of_certification: 4-digit year only or null

7. AWARDS
   - Include hackathons, academic honors, recognition
   - company_name: Organization that gave award or null

## RETURN EXACTLY THIS JSON STRUCTURE:
{
  "users": {
    "first_name": "string or null",
    "last_name": "string or null",
    "date_of_birth": "YYYY-MM-DD or null",
    "mobile_number": "string or null",
    "email_id": "string or null",
    "aadhar_number": "string or null",
    "pan_number": "string or null",
    "job_role": "string or null",
    "current_company": "string or null",
    "years_of_experience": "decimal or integer or  null"
  
  },
  "skillset": [
    {
      "skill_name": "string",
      "experence_level_in_skills": "Beginner|Intermediate|Advanced"
    }
  ],
  "project_history": [
    {
      "project_title": "string or null",
      "project_description": "string or null",
      "project_start_month": "string or or integer or null",
      "project_start_year": "integer or null",
      "project_end_month": "string or integer or null",
      "project_end_year": "integer or null",
      "activites": "comma-separated string or null"
    }
  ],
  "certification": [
    {
      "cerification_name": "string",
      "year_of_certification": "integer or null"
    }
  ],
  "awards": [
    {
      "award_name": "string",
      "year_of_award": "integer or null",
      "company_name": "string or null"
    }
  ]
}
"""

USER_PROMPT_TEMPLATE = """
Parse the following resume and extract all information.
Return ONLY the JSON object, nothing else.

RESUME TEXT:
--------------
{resume_text}
--------------
"""

def parse_resume_data(resume_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": PROMPT
                },
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(
                        resume_text=resume_text
                    )
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,   
            max_tokens=2000
        )

        raw_extraction_data = response.choices[0].message.content

        # Log token usage — track API costs
        usage = response.usage
        print(f" Tokens used →"
              f" Input: {usage.prompt_tokens} |"
              f" Output: {usage.completion_tokens}")

        # Clean + parse JSON
        clean = raw_extraction_data.strip()\
                   .replace("```json", "")\
                   .replace("```", "")\
                   .strip()

        parsed = json.loads(clean)

        # Validate all required keys exist
        required_keys = [
            "users",
            "skillset",
            "project_history",
            "certification",
            "awards"
        ]
        for key in required_keys:
            if key not in parsed:
                parsed[key] = [] if key != "users" else {}
        # After parsing JSON — just before return parsed

        # Clean skill levels — fix casing only
        for skill in parsed.get("skillset", []):
            level = skill.get("experence_level_in_skills", "")

            # Just fix casing + spaces — nothing else
            level = str(level).strip().title()

            # If still not valid → set null
            if level not in ["Beginner", "Intermediate", "Advanced"]:
                level = None

            skill["experence_level_in_skills"] = level
      
        print(" Resume parsed successfully")
        return parsed

    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI returned invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Resume parsing failed: {e}")