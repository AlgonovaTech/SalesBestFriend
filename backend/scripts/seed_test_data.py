"""
Seed realistic test data into Supabase for all UI screens.

Creates:
- 3 additional user profiles (for team analytics leaderboard)
- 5 additional completed calls with analyses & scores
- 8 scheduled calls with pre-call client info

Run: cd backend && python -m scripts.seed_test_data
"""

import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# SSL context (skip verification for local Python 3.13)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Constants
ORG_ID = "a0000000-0000-0000-0000-000000000001"
TEAM_ID = "b0000000-0000-0000-0000-000000000001"
PLAYBOOK_VERSION_ID = "cd6a0e71-7a57-437f-8356-2768c406e490"
EXISTING_USER_ID = "1fd076ea-d986-4b1a-b90e-ebd3bfac2d82"  # tech@alg.team
EXISTING_CALL_ID = "4d8e4dfa-850c-4a35-a3ad-8a031aaf3197"


def supabase_post(table: str, data: dict | list) -> dict | list:
    """Insert into Supabase table via REST API."""
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=payload,
        headers={
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR inserting into {table}: {e.code} — {body[:300]}")
        return {}


def supabase_patch(table: str, filters: str, data: dict) -> dict:
    """Update Supabase table via REST API."""
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}?{filters}",
        data=payload,
        headers={
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        method="PATCH",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR patching {table}: {e.code} — {body[:300]}")
        return {}


def supabase_get(table: str, params: str = "") -> list:
    """Query Supabase table."""
    # Ensure URL is properly encoded
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += f"?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
        },
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR querying {table}: {e.code} — {body[:200]}")
        return []


# --- Helper data ---

SAMPLE_CRITERIA = [
    ("1. Greeting and introduction", 1),
    ("2. Explain agenda", 1),
    ("3. Ask child's name and age", 1),
    ("4. Ask about schooling status", 1),
    ("5. Child's interests and motivation", 1),
    ("6. Parent's expectations", 1),
    ("7. Previous learning experience", 1),
    ("8. Schedule availability", 1),
    ("9. Decision-making process", 1),
    ("10. Budget discussion readiness", 1),
    ("11. Diagnostic introduction", 1),
    ("12. Age-appropriate assessment", 1),
    ("13. Encourage child participation", 1),
    ("14. Explain assessment results", 1),
    ("15. Connect results to program", 1),
    ("16. Present program overview", 1),
    ("17. Explain learning methodology", 1),
    ("18. Share success stories", 1),
    ("19. Handle objections effectively", 1),
    ("20. Present pricing clearly", 1),
]


def generate_scores(call_id: str, overall_target: float) -> list:
    """Generate criterion scores that average to roughly the target."""
    import random
    scores = []
    for name, max_score in SAMPLE_CRITERIA:
        # Weight toward target score (0-1 range for max_score=1)
        p = overall_target / 100.0
        score = 1 if random.random() < p else 0
        scores.append({
            "call_id": call_id,
            "criteria_name": name,
            "criteria_max_score": max_score,
            "score": score,
            "reasoning": f"{'Met' if score else 'Did not meet'} the criteria requirements during the call.",
            "evidence": "",
        })
    return scores


def main():
    print("=" * 60)
    print("Seeding test data for Sales Best Friend")
    print("=" * 60)

    # =========================================================================
    # 1. Create additional user profiles
    # =========================================================================
    print("\n--- Creating user profiles ---")

    # First, update existing user's name
    supabase_patch("user_profiles", f"id=eq.{EXISTING_USER_ID}", {
        "full_name": "Niko Pratama",
        "role": "admin",
    })
    print("  Updated existing user → Niko Pratama (admin)")

    # Create 2 more users via Supabase auth + profiles
    # Since we can't create auth users via REST easily, we'll create profiles directly
    # These users won't be able to login but will appear in analytics
    EXTRA_USERS = [
        {
            "id": str(uuid4()),
            "full_name": "Sari Dewi",
            "role": "sales_rep",
        },
        {
            "id": str(uuid4()),
            "full_name": "Andi Wijaya",
            "role": "sales_rep",
        },
    ]

    for u in EXTRA_USERS:
        # Check if exists
        existing = supabase_get("user_profiles", f"full_name=eq.{urllib.parse.quote(u['full_name'])}")
        if existing:
            u["id"] = existing[0]["id"]
            print(f"  User {u['full_name']} already exists: {u['id']}")
            continue

        result = supabase_post("user_profiles", {
            "id": u["id"],
            "organization_id": ORG_ID,
            "team_id": TEAM_ID,
            "full_name": u["full_name"],
            "role": u["role"],
            "language_preference": "id",
            "timezone": "Asia/Jakarta",
        })
        if result:
            print(f"  Created user: {u['full_name']} ({u['id'][:8]}...)")
        else:
            print(f"  Failed to create user: {u['full_name']}")

    # =========================================================================
    # 2. Create additional completed calls with analyses
    # =========================================================================
    print("\n--- Creating additional calls ---")

    now = datetime.now(timezone.utc)
    import random
    random.seed(42)

    CALL_DATA = [
        # (user_index, title, days_ago, score, summary)
        (0, "Trial Class - Deni Math Advanced", 2, 68, "Good trial class for 8-year-old Deni. Salesperson covered most agenda items and conducted thorough assessment."),
        (0, "Trial Class - Putri Scratch", 5, 55, "Scratch programming introduction for 7-year-old Putri. Decent profiling but missed pricing discussion."),
        (0, "Trial Class - Ari Beginner Math", 7, 42, "Basic math trial for 6-year-old Ari. Call ended abruptly, several criteria missed."),
        (1, "Trial Class - Siti Roblox", 1, 78, "Excellent trial class for 9-year-old Siti. Strong rapport building and clear program explanation."),
        (1, "Trial Class - Rizky Visual Prog", 3, 72, "Visual programming session for 6-year-old Rizky. Good engagement and parent communication."),
        (1, "Trial Class - Nisa Python Intro", 4, 65, "Python introduction for 10-year-old Nisa. Solid technical assessment but needed more objection handling."),
        (1, "Trial Class - Fajar Math Olympiad", 6, 82, "Outstanding trial class for Math Olympiad preparation. Thorough assessment and pricing discussion."),
        (1, "Trial Class - Kevin Coding", 8, 58, "Coding class trial for 11-year-old Kevin. Adequate but lacked enthusiasm and follow-up plan."),
        (2, "Trial Class - Ayu Scratch", 1, 35, "Scratch trial for 5-year-old Ayu. Struggled with online format, many criteria missed."),
        (2, "Trial Class - Bima Math", 3, 45, "Math trial for 7-year-old Bima. Average performance, needs improvement in closing."),
        (2, "Trial Class - Cinta Drawing", 5, 30, "Art & coding trial for 6-year-old Cinta. Poor structure, missed key assessment steps."),
    ]

    user_ids = [EXISTING_USER_ID, EXTRA_USERS[0]["id"], EXTRA_USERS[1]["id"]]

    for user_idx, title, days_ago, score, summary in CALL_DATA:
        user_id = user_ids[user_idx]
        call_id = str(uuid4())
        created = (now - timedelta(days=days_ago)).isoformat()

        # Check if call with this title already exists for this user
        existing_calls = supabase_get("calls", f"title=eq.{urllib.parse.quote(title)}&user_id=eq.{user_id}")
        if existing_calls:
            print(f"  Call '{title}' already exists, skipping")
            continue

        # Create call
        call_result = supabase_post("calls", {
            "id": call_id,
            "organization_id": ORG_ID,
            "team_id": TEAM_ID,
            "user_id": user_id,
            "playbook_version_id": PLAYBOOK_VERSION_ID,
            "title": title,
            "status": "completed",
            "source": "upload",
            "language": "id",
            "processing_step": "done",
            "duration_seconds": random.randint(900, 2400),
            "created_at": created,
        })

        if not call_result:
            continue
        if isinstance(call_result, list):
            call_id = call_result[0]["id"]
        print(f"  Created call: {title} (score: {score})")

        # Create analysis
        what_went_well = [
            "Proper greeting and introduction",
            "Asked relevant profiling questions",
            "Demonstrated program features clearly",
        ]
        needs_improvement = [
            "Follow-up scheduling could be stronger",
            "Price presentation needs more confidence",
            "Should address objections more proactively",
        ]

        supabase_post("call_analyses", {
            "call_id": call_id,
            "summary": summary,
            "what_went_well": what_went_well[:2 + (score > 60)],
            "needs_improvement": needs_improvement[:2 + (score < 50)],
            "goals_identified": ["Find suitable learning program for child"],
            "pain_points": ["Concern about online learning effectiveness"],
            "interest_signals": ["Child shows interest in technology"],
            "buyer_profile_summary": f"Indonesian parent seeking quality education for their child",
            "overall_score": score,
            "model_used": "claude-via-openrouter",
        })

        # Create scores
        scores = generate_scores(call_id, score)
        for s in scores:
            supabase_post("call_scores", s)

        # Create tasks
        supabase_post("call_tasks", {
            "call_id": call_id,
            "user_id": user_id,
            "title": f"Follow up with parent about enrollment",
            "status": "pending",
            "priority": "high",
        })
        supabase_post("call_tasks", {
            "call_id": call_id,
            "user_id": user_id,
            "title": f"Send program brochure via WhatsApp",
            "status": "pending",
            "priority": "medium",
        })

    # =========================================================================
    # 3. Create scheduled calls with pre-call data
    # =========================================================================
    print("\n--- Creating scheduled calls ---")

    # Use Jakarta timezone (UTC+7)
    jkt = timezone(timedelta(hours=7))
    today = datetime.now(jkt).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    SCHEDULED_CALLS = [
        # Today's calls
        {
            "time": today.replace(hour=9, minute=0),
            "title": "Trial Class — Raka (Scratch)",
            "pre_call_data": {
                "client_name": "Bu Sari Rahayu",
                "client_phone": "+62 812-3456-7890",
                "client_email": "sari.rahayu@gmail.com",
                "child_name": "Raka",
                "child_age": 5,
                "recommended_course": "Scratch / Visual Programming",
                "recommended_reason": "Anak tertarik game dan puzzle, usia cocok untuk pengenalan visual programming. Sudah ikut kelas coding dasar.",
                "source_channel": "Instagram DM",
                "lead_source": "Social Media Ad",
                "school_level": "TK B",
                "interests": ["coding", "puzzle", "games", "Hot Wheels"],
                "notes": "Ibu background engineering, tertarik dengan logical thinking development.",
                "previous_interactions": "Mengisi form di website 3 hari lalu. Sudah chatting via Instagram.",
            },
            "user_id": EXISTING_USER_ID,
        },
        {
            "time": today.replace(hour=10, minute=30),
            "title": "Trial Class — Deni (Math Advanced)",
            "pre_call_data": {
                "client_name": "Pak Andi Susanto",
                "client_phone": "+62 813-2222-3333",
                "child_name": "Deni",
                "child_age": 8,
                "recommended_course": "Math Advanced (Olympiad Prep)",
                "recommended_reason": "Anak sudah di level atas kelas. Nilai math di sekolah selalu 95+. Butuh tantangan lebih.",
                "source_channel": "Website Form",
                "lead_source": "Google Search",
                "school_level": "SD Kelas 2",
                "interests": ["math", "chess", "science"],
                "notes": "Ayah ingin anak ikut kompetisi math. Sudah coba bimbel lokal tapi kurang challenging.",
            },
            "user_id": EXISTING_USER_ID,
        },
        {
            "time": today.replace(hour=13, minute=0),
            "title": "Trial Class — Putri (Scratch Beginner)",
            "pre_call_data": {
                "client_name": "Bu Diana Putri",
                "client_phone": "+62 857-1111-2222",
                "child_name": "Putri",
                "child_age": 7,
                "recommended_course": "Scratch Beginner",
                "recommended_reason": "Belum pernah coding sama sekali. Suka menggambar dan bercerita — Scratch animation cocok.",
                "source_channel": "Referral",
                "lead_source": "Word of Mouth",
                "school_level": "SD Kelas 1",
                "interests": ["drawing", "storytelling", "YouTube"],
                "notes": "Direferensikan oleh Bu Sari. Ibu khawatir screen time tapi tertarik kalau produktif.",
            },
            "user_id": EXISTING_USER_ID,
        },
        {
            "time": today.replace(hour=14, minute=30),
            "title": "Trial Class — Ari (Math Beginner)",
            "pre_call_data": {
                "client_name": "Pak Budi Hartono",
                "client_phone": "+62 878-4444-5555",
                "child_name": "Ari",
                "child_age": 6,
                "recommended_course": "Math Beginner (Fun Math)",
                "recommended_reason": "Anak sering bilang 'math susah'. Perlu pendekatan fun dan visual untuk bangun confidence.",
                "source_channel": "WhatsApp",
                "lead_source": "Facebook Ad",
                "school_level": "SD Kelas 1",
                "interests": ["Minecraft", "building blocks", "dinosaurs"],
                "notes": "Ayah single parent, jadwal fleksibel sore hari. Budget medium.",
            },
            "user_id": EXISTING_USER_ID,
        },
        {
            "time": today.replace(hour=16, minute=0),
            "title": "Trial Class — Siti (Roblox Studio)",
            "pre_call_data": {
                "client_name": "Bu Rina Sari",
                "client_phone": "+62 812-6666-7777",
                "child_name": "Siti",
                "child_age": 9,
                "recommended_course": "Roblox Studio / Game Development",
                "recommended_reason": "Anak sudah main Roblox setiap hari. Sudah coba bikin game sederhana sendiri. Siap untuk structured learning.",
                "source_channel": "TikTok",
                "lead_source": "Social Media Ad",
                "school_level": "SD Kelas 3",
                "interests": ["Roblox", "gaming", "YouTube content"],
                "notes": "Ibu guru SD, sangat supportive. Ingin channeling hobby gaming ke skill produktif.",
            },
            "user_id": EXISTING_USER_ID,
        },
        # Tomorrow's calls
        {
            "time": tomorrow.replace(hour=9, minute=0),
            "title": "Trial Class — Rizky (Visual Programming)",
            "pre_call_data": {
                "client_name": "Bu Maya Anggraini",
                "client_phone": "+62 821-8888-9999",
                "child_name": "Rizky",
                "child_age": 6,
                "recommended_course": "Visual Programming / Scratch Jr",
                "recommended_reason": "Usia 6 tahun, belum bisa baca lancar. ScratchJr dengan drag-drop blocks lebih cocok.",
                "source_channel": "Instagram",
                "lead_source": "Influencer Referral",
                "school_level": "TK B",
                "interests": ["tablet games", "coloring", "animals"],
                "notes": "Tertarik setelah lihat review influencer. Tanya soal trial gratis.",
            },
            "user_id": EXISTING_USER_ID,
        },
        {
            "time": tomorrow.replace(hour=11, minute=0),
            "title": "Trial Class — Nisa (Python)",
            "pre_call_data": {
                "client_name": "Pak Hendra Kusuma",
                "client_phone": "+62 815-1010-2020",
                "child_name": "Nisa",
                "child_age": 10,
                "recommended_course": "Python Programming",
                "recommended_reason": "Sudah lulus Scratch, siap ke text-based programming. Anak cepat belajar.",
                "source_channel": "Website Form",
                "lead_source": "Google Search",
                "school_level": "SD Kelas 4",
                "interests": ["Scratch projects", "math", "reading"],
                "notes": "Alumni Scratch kelas lain. Ayah programmer, ingin anak lanjut ke Python.",
            },
            "user_id": EXISTING_USER_ID,
        },
        # Day after tomorrow
        {
            "time": day_after.replace(hour=14, minute=0),
            "title": "Trial Class — Fajar (Math Olympiad)",
            "pre_call_data": {
                "client_name": "Bu Lestari Wati",
                "client_phone": "+62 822-3030-4040",
                "child_name": "Fajar",
                "child_age": 7,
                "recommended_course": "Math Olympiad Preparation",
                "recommended_reason": "Anak juara 1 math di sekolah. Ibu ingin persiapan kompetisi tingkat kota.",
                "source_channel": "Referral",
                "lead_source": "Parent Community",
                "school_level": "SD Kelas 2",
                "interests": ["math puzzles", "rubik's cube", "chess"],
                "notes": "Ibu sangat ambitious. Sudah riset beberapa program. Price sensitive tapi willing to invest if quality.",
            },
            "user_id": EXISTING_USER_ID,
        },
    ]

    for sc in SCHEDULED_CALLS:
        scheduled_time = sc["time"]
        title = sc["title"]

        # Check if already exists
        existing = supabase_get("calls", f"title=eq.{urllib.parse.quote(title)}&status=eq.scheduled")
        if existing:
            print(f"  Scheduled call '{title}' already exists, skipping")
            continue

        pre_call_data = sc["pre_call_data"]
        pre_call_data["scheduled_at"] = scheduled_time.isoformat()

        call_result = supabase_post("calls", {
            "organization_id": ORG_ID,
            "team_id": TEAM_ID,
            "user_id": sc["user_id"],
            "playbook_version_id": PLAYBOOK_VERSION_ID,
            "title": title,
            "status": "scheduled",
            "source": "browser",
            "language": "id",
            "pre_call_data": pre_call_data,
            "started_at": scheduled_time.isoformat(),
        })

        if call_result:
            print(f"  Created scheduled call: {title} @ {scheduled_time.strftime('%Y-%m-%d %H:%M')}")

    # =========================================================================
    # 4. Link existing test call to a scheduled call context
    # =========================================================================
    print("\n--- Updating existing test call with pre-call data ---")

    supabase_patch("calls", f"id=eq.{EXISTING_CALL_ID}", {
        "pre_call_data": {
            "client_name": "Bu Sari Rahayu",
            "client_phone": "+62 812-3456-7890",
            "child_name": "Raka",
            "child_age": 5,
            "recommended_course": "Scratch / Visual Programming",
            "recommended_reason": "Anak tertarik game dan puzzle, usia cocok untuk pengenalan visual programming.",
            "source_channel": "Instagram DM",
            "lead_source": "Social Media Ad",
            "school_level": "TK B",
            "interests": ["coding", "puzzle", "games"],
            "notes": "Ibu background engineering. Sudah chatting via Instagram.",
            "scheduled_at": (now - timedelta(hours=2)).isoformat(),
        },
    })
    print("  Updated existing test call with pre-call data")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Seed data complete!")
    print("=" * 60)

    # Count totals
    calls = supabase_get("calls", "select=id,status")
    scheduled = [c for c in calls if c.get("status") == "scheduled"]
    completed = [c for c in calls if c.get("status") == "completed"]
    users = supabase_get("user_profiles", "select=id,full_name")

    print(f"\nTotal users:           {len(users)}")
    print(f"Total calls:           {len(calls)}")
    print(f"  - Completed:         {len(completed)}")
    print(f"  - Scheduled:         {len(scheduled)}")

    for u in users:
        print(f"\n  {u['full_name']}:")
        user_calls = supabase_get("calls", f"user_id=eq.{u['id']}&status=eq.completed&select=id")
        user_sched = supabase_get("calls", f"user_id=eq.{u['id']}&status=eq.scheduled&select=id")
        print(f"    Completed calls: {len(user_calls)}")
        print(f"    Scheduled calls: {len(user_sched)}")


if __name__ == "__main__":
    import urllib.parse
    main()
