"""
Seed comprehensive test data for ALL UI screens of Sales Best Friend.

Creates via Supabase Admin API:
- 2 new auth users (Sari Dewi, Andi Wijaya) with user_profiles
- 11 completed calls across 3 users with analyses, scores, tasks
- 8 scheduled calls with pre-call data
- Fixes calls_this_week by ensuring some calls are recent
- Adds transcript segments for additional calls

Run: cd backend && python -m scripts.seed_all_data
"""

import json
import os
import random
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ORG_ID = "a0000000-0000-0000-0000-000000000001"
TEAM_ID = "b0000000-0000-0000-0000-000000000001"
PLAYBOOK_VERSION_ID = "cd6a0e71-7a57-437f-8356-2768c406e490"
EXISTING_USER_ID = "1fd076ea-d986-4b1a-b90e-ebd3bfac2d82"

random.seed(42)
now = datetime.now(timezone.utc)


# ─── HTTP helpers ──────────────────────────────────────────────────────────────

def api_post(path: str, data: dict, extra_headers: dict | None = None) -> dict | list:
    payload = json.dumps(data).encode()
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        f"{SUPABASE_URL}{path}",
        data=payload,
        headers=headers,
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR {path}: {e.code} — {body[:300]}")
        return {}


def rest_post(table: str, data: dict | list) -> dict | list:
    return api_post(f"/rest/v1/{table}", data, {"Prefer": "return=representation"})


def rest_patch(table: str, filters: str, data: dict) -> dict:
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


def rest_get(table: str, params: str = "") -> list:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += f"?{params}"
    req = urllib.request.Request(url, headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR querying {table}: {e.code} — {body[:200]}")
        return []


def rest_delete(table: str, filters: str):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}?{filters}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
        method="DELETE",
    )
    try:
        urllib.request.urlopen(req, context=ctx)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR deleting {table}: {e.code} — {body[:200]}")


# ─── Scoring criteria ─────────────────────────────────────────────────────────

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
    scores = []
    p = overall_target / 100.0
    for name, max_score in SAMPLE_CRITERIA:
        score = 1 if random.random() < p else 0
        evidences = {
            "1. Greeting and introduction": "Greeted parent and child warmly at the start",
            "2. Explain agenda": "Explained the trial class structure",
            "3. Ask child's name and age": "Asked about the child's details",
            "4. Ask about schooling status": "Discussed current school situation",
            "5. Child's interests and motivation": "Explored what the child enjoys",
            "6. Parent's expectations": "Asked what parent hopes to achieve",
            "7. Previous learning experience": "Discussed prior education experience",
            "8. Schedule availability": "Checked available time slots",
            "9. Decision-making process": "Understood who makes the decision",
            "10. Budget discussion readiness": "Approached pricing topic",
            "11. Diagnostic introduction": "Introduced assessment activity",
            "12. Age-appropriate assessment": "Used suitable assessment for age",
            "13. Encourage child participation": "Engaged child in activities",
            "14. Explain assessment results": "Shared findings from assessment",
            "15. Connect results to program": "Linked assessment to course benefits",
            "16. Present program overview": "Described the course curriculum",
            "17. Explain learning methodology": "Explained teaching approach",
            "18. Share success stories": "Mentioned student success examples",
            "19. Handle objections effectively": "Addressed concerns raised",
            "20. Present pricing clearly": "Presented pricing and packages",
        }
        scores.append({
            "call_id": call_id,
            "criteria_name": name,
            "criteria_max_score": max_score,
            "score": score,
            "reasoning": f"{'Met' if score else 'Did not meet'} the criteria requirements during the call.",
            "evidence": evidences.get(name, "") if score else "",
        })
    return scores


def generate_transcript(call_id: str, duration_seconds: int) -> list:
    """Generate realistic trial class transcript segments."""
    segments = []
    templates = [
        ("Agent", "Selamat pagi, Bu. Terima kasih sudah meluangkan waktu untuk trial class hari ini."),
        ("Customer", "Pagi, Pak. Iya, kami sudah menunggu trial class ini."),
        ("Agent", "Baik, Bu. Izinkan saya jelaskan dulu agenda kita hari ini. Pertama, saya akan berkenalan dengan anak, lalu kita lakukan diagnostic test sederhana, dan terakhir saya jelaskan program yang cocok."),
        ("Customer", "Oke, silakan."),
        ("Agent", "Siapa nama anaknya, Bu? Dan berapa usianya sekarang?"),
        ("Customer", "Namanya Deni, umurnya 8 tahun, kelas 2 SD."),
        ("Agent", "Wah, kelas 2 ya. Di sekolahnya, mata pelajaran apa yang paling disukai Deni?"),
        ("Customer", "Deni suka matematika. Nilainya selalu bagus di sekolah."),
        ("Agent", "Bagus sekali. Apakah Deni pernah ikut les atau bimbingan belajar sebelumnya?"),
        ("Customer", "Pernah ikut bimbel lokal, tapi kurang challenging katanya."),
        ("Agent", "Saya mengerti, Bu. Kalau di rumah, Deni biasanya suka bermain apa?"),
        ("Customer", "Suka main game di tablet dan suka puzzle juga."),
        ("Agent", "Baik. Sekarang saya mau tanya ke Deni ya. Deni, coba kita main game matematika yuk!"),
        ("Customer", "Oke, kak!"),
        ("Agent", "Bagus, Deni! Coba sekarang, 7 dikali 8 berapa?"),
        ("Customer", "56!"),
        ("Agent", "Hebat! Cepat sekali. Sekarang yang lebih menantang ya. Kalau 123 ditambah 78 berapa?"),
        ("Customer", "Hmm... 201!"),
        ("Agent", "Pintar! Deni memang punya bakat matematika yang kuat. Bu, berdasarkan assessment tadi, Deni sudah di atas level rata-rata untuk usianya."),
        ("Customer", "Wah, senang dengarnya. Lalu program apa yang cocok?"),
        ("Agent", "Untuk Deni yang sudah advance, kami rekomendasikan program Math Olympiad Preparation. Program ini dirancang khusus untuk anak yang sudah di atas level kelas."),
        ("Customer", "Itu jadwalnya kapan ya?"),
        ("Agent", "Kita ada kelas Selasa dan Kamis sore, jam 3 sampai 4:30. Apakah jadwal itu cocok?"),
        ("Customer", "Kamis bisa, tapi Selasa agak susah karena ada kegiatan sekolah."),
        ("Agent", "Tidak apa-apa, Bu. Kami juga punya sesi Sabtu pagi jam 9. Bisa pilih 2 sesi yang paling cocok."),
        ("Customer", "Kalau Kamis dan Sabtu bisa ya. Berapa biayanya?"),
        ("Agent", "Untuk program Math Olympiad, biayanya Rp 500.000 per bulan untuk 8 sesi. Kami juga ada paket 3 bulan dengan diskon 15%."),
        ("Customer", "Hmm, lumayan juga ya. Bisa dipikir-pikir dulu?"),
        ("Agent", "Tentu, Bu. Tapi saya informasikan bahwa kelas Kamis-Sabtu tinggal 3 slot lagi. Kalau minat, bisa saya hold dulu slotnya sampai besok."),
        ("Customer", "Iya, tolong di-hold dulu ya. Saya diskusi dulu sama suami."),
        ("Agent", "Baik, Bu. Saya akan follow up besok sore ya. Terima kasih banyak untuk waktunya. Sampai jumpa, Deni!"),
        ("Customer", "Terima kasih, Pak. Dadah!"),
    ]

    seg_duration = duration_seconds / len(templates)
    for i, (speaker, text) in enumerate(templates):
        start = i * seg_duration
        end = start + seg_duration - 0.5
        segments.append({
            "call_id": call_id,
            "segment_index": i,
            "start_seconds": round(start, 2),
            "end_seconds": round(end, 2),
            "text": text,
            "speaker": speaker,
            "confidence": round(random.uniform(0.85, 0.99), 3),
        })

    return segments


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Seeding COMPREHENSIVE test data for Sales Best Friend")
    print("=" * 60)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1: Create auth users via Supabase Admin API
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- Step 1: Creating auth users ---")

    NEW_USERS = [
        {
            "email": "sari.dewi@salesbestfriend.test",
            "full_name": "Sari Dewi",
            "role": "sales_rep",
        },
        {
            "email": "andi.wijaya@salesbestfriend.test",
            "full_name": "Andi Wijaya",
            "role": "sales_rep",
        },
    ]

    user_ids = {
        "Niko Pratama": EXISTING_USER_ID,
    }

    for u in NEW_USERS:
        # Check if profile already exists
        existing = rest_get("user_profiles", f"full_name=eq.{urllib.parse.quote(u['full_name'])}")
        if existing:
            uid = existing[0]["id"]
            user_ids[u["full_name"]] = uid
            print(f"  User {u['full_name']} already exists: {uid[:12]}...")
            continue

        # Create auth user via Supabase Admin API
        result = api_post("/auth/v1/admin/users", {
            "email": u["email"],
            "password": "TestPassword123!",
            "email_confirm": True,
            "user_metadata": {
                "full_name": u["full_name"],
            },
        })

        if not result or "id" not in result:
            print(f"  Failed to create auth user {u['full_name']}: {result}")
            continue

        uid = result["id"]
        user_ids[u["full_name"]] = uid
        print(f"  Created auth user: {u['full_name']} ({uid[:12]}...)")

        # Create user_profile
        profile_result = rest_post("user_profiles", {
            "id": uid,
            "organization_id": ORG_ID,
            "team_id": TEAM_ID,
            "full_name": u["full_name"],
            "role": u["role"],
            "language_preference": "id",
            "timezone": "Asia/Jakarta",
        })

        if profile_result:
            print(f"  Created profile for {u['full_name']}")
        else:
            print(f"  Profile creation failed for {u['full_name']}")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2: Ensure Niko profile is correct
    # ──────────────────────────────────────────────────────────────────────────
    rest_patch("user_profiles", f"id=eq.{EXISTING_USER_ID}", {
        "full_name": "Niko Pratama",
        "role": "admin",
    })
    print("  Updated Niko Pratama profile")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3: Create completed calls with analyses, scores, tasks
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- Step 2: Creating completed calls ---")

    CALL_DATA = [
        # Niko's calls (3 already exist from prev seed, add a few more recent)
        ("Niko Pratama", "Trial Class - Lina Roblox Advanced", 0, 75,
         "Strong trial for Lina's Roblox game dev. Good assessment and clear pricing. Parent was engaged throughout.",
         ["Excellent rapport with child", "Thorough diagnostic assessment", "Clear pricing presentation"],
         ["Could have explored more about schedule flexibility", "Didn't ask about referral potential"]),
        ("Niko Pratama", "Trial Class - Bayu Math Fun", 1, 82,
         "Outstanding trial class for Bayu. Perfect structure and enthusiastic delivery. Parent signed up on the spot.",
         ["Perfect greeting and agenda setting", "Engaging diagnostic activities", "Confident pricing discussion", "Secured enrollment"],
         ["Minor: could have mentioned referral bonus"]),

        # Sari Dewi's calls
        ("Sari Dewi", "Trial Class - Siti Roblox", 1, 78,
         "Excellent trial class for 9yo Siti. Strong rapport building and clear program explanation. Parent impressed.",
         ["Warm and professional greeting", "Excellent rapport with child", "Thorough assessment"],
         ["Follow-up plan could be more specific"]),
        ("Sari Dewi", "Trial Class - Rizky Visual Prog", 3, 72,
         "Visual programming session for 6yo Rizky. Good engagement but missed some parent questions.",
         ["Good child engagement", "Age-appropriate activities"],
         ["Missed parent's budget concern", "Should address objections earlier"]),
        ("Sari Dewi", "Trial Class - Nisa Python Intro", 4, 65,
         "Python intro for 10yo Nisa. Solid technical assessment but needed more objection handling.",
         ["Strong technical knowledge", "Good assessment structure"],
         ["Weak objection handling", "Didn't share success stories"]),
        ("Sari Dewi", "Trial Class - Fajar Math Olympiad", 0, 85,
         "Outstanding Math Olympiad trial. Perfect diagnostic, engaged parent, and closed the sale. Best performance this week.",
         ["Flawless greeting and agenda", "Excellent diagnostic test", "Confident pricing", "Secured enrollment"],
         ["None significant"]),
        ("Sari Dewi", "Trial Class - Kevin Coding", 6, 58,
         "Coding class trial for 11yo Kevin. Adequate but lacked enthusiasm and follow-up plan.",
         ["Covered most agenda items"],
         ["Low energy throughout", "No follow-up scheduled", "Didn't share success stories"]),

        # Andi Wijaya's calls
        ("Andi Wijaya", "Trial Class - Ayu Scratch", 1, 38,
         "Scratch trial for 5yo Ayu. Struggled with online format. Several criteria missed. Needs coaching.",
         ["Attempted to engage child"],
         ["No clear agenda explained", "Skipped diagnostic entirely", "No pricing discussion", "Call ended abruptly"]),
        ("Andi Wijaya", "Trial Class - Bima Math", 3, 45,
         "Math trial for 7yo Bima. Average performance. Needs improvement in closing and structure.",
         ["Basic greeting was fine", "Asked about child's interests"],
         ["Weak structure", "No success stories shared", "Pricing was unclear", "No follow-up plan"]),
        ("Andi Wijaya", "Trial Class - Cinta Drawing", 5, 30,
         "Art & coding trial for 6yo Cinta. Poor structure. Missed key assessment steps. Urgent coaching needed.",
         ["Friendly tone"],
         ["No agenda explained", "Skipped assessment", "No pricing at all", "Parent seemed confused", "Very short call"]),
        ("Andi Wijaya", "Trial Class - Reno Scratch Jr", 0, 48,
         "Scratch Jr trial for 5yo Reno. Some improvement over previous calls but still needs work on structure.",
         ["Better greeting than before", "Tried diagnostic activity"],
         ["Assessment was disorganized", "Pricing discussion weak", "No follow-up scheduling"]),
    ]

    for full_name, title, days_ago, score, summary, went_well, needs_improve in CALL_DATA:
        uid = user_ids.get(full_name)
        if not uid:
            print(f"  Skipping '{title}' — user {full_name} not found")
            continue

        # Check if exists
        existing = rest_get("calls", f"title=eq.{urllib.parse.quote(title)}&user_id=eq.{uid}")
        if existing:
            print(f"  Call '{title}' exists, skipping")
            continue

        call_id = str(uuid4())
        created = (now - timedelta(days=days_ago, hours=random.randint(1, 8))).isoformat()
        duration = random.randint(900, 2400)

        call_result = rest_post("calls", {
            "id": call_id,
            "organization_id": ORG_ID,
            "team_id": TEAM_ID,
            "user_id": uid,
            "playbook_version_id": PLAYBOOK_VERSION_ID,
            "title": title,
            "status": "completed",
            "source": "upload",
            "language": "id",
            "processing_step": "done",
            "duration_seconds": duration,
            "created_at": created,
        })

        if not call_result:
            continue
        if isinstance(call_result, list) and call_result:
            call_id = call_result[0]["id"]

        print(f"  Created call: {title} (score:{score}, user:{full_name})")

        # Analysis
        rest_post("call_analyses", {
            "call_id": call_id,
            "summary": summary,
            "what_went_well": went_well,
            "needs_improvement": needs_improve,
            "goals_identified": ["Find suitable learning program for child", "Establish learning schedule"],
            "pain_points": ["Concern about online learning effectiveness", "Budget considerations"],
            "interest_signals": ["Child shows interest in technology", "Parent values structured learning"],
            "buyer_profile_summary": f"Indonesian parent seeking quality tech/math education. {'High' if score > 70 else 'Medium' if score > 50 else 'Low'} engagement level.",
            "overall_score": score,
            "model_used": "claude-via-openrouter",
        })

        # Scores
        for s in generate_scores(call_id, score):
            rest_post("call_scores", s)

        # Tasks
        task_titles_pool = [
            ("Follow up with parent about enrollment", "high"),
            ("Send program brochure via WhatsApp", "medium"),
            ("Schedule second trial session", "medium"),
            ("Share student success stories", "low"),
            ("Prepare personalized learning plan", "high"),
            ("Send pricing comparison document", "medium"),
        ]
        chosen_tasks = random.sample(task_titles_pool, k=random.randint(2, 3))
        for task_title, priority in chosen_tasks:
            rest_post("call_tasks", {
                "call_id": call_id,
                "user_id": uid,
                "title": task_title,
                "status": random.choice(["pending", "pending", "pending", "completed"]),
                "priority": priority,
            })

        # Transcript (for some calls)
        if days_ago <= 1:  # Only generate transcripts for recent calls
            segments = generate_transcript(call_id, duration)
            for seg in segments:
                rest_post("call_transcripts", seg)
            print(f"    + {len(segments)} transcript segments")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4: Update scheduled calls dates to be current (today/tomorrow)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- Step 3: Refreshing scheduled calls dates ---")

    jkt = timezone(timedelta(hours=7))
    today = datetime.now(jkt).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    scheduled_updates = [
        ("Trial Class — Raka (Scratch)", today.replace(hour=9, minute=0)),
        ("Trial Class — Deni (Math Advanced)", today.replace(hour=10, minute=30)),
        ("Trial Class — Putri (Scratch Beginner)", today.replace(hour=13, minute=0)),
        ("Trial Class — Ari (Math Beginner)", today.replace(hour=14, minute=30)),
        ("Trial Class — Siti (Roblox Studio)", today.replace(hour=16, minute=0)),
        ("Trial Class — Rizky (Visual Programming)", tomorrow.replace(hour=9, minute=0)),
        ("Trial Class — Nisa (Python)", tomorrow.replace(hour=11, minute=0)),
        ("Trial Class — Fajar (Math Olympiad)", day_after.replace(hour=14, minute=0)),
    ]

    for title, sched_time in scheduled_updates:
        encoded_title = urllib.parse.quote(title)
        existing = rest_get("calls", f"title=eq.{encoded_title}&status=eq.scheduled")
        if existing:
            call = existing[0]
            pre_call = call.get("pre_call_data", {}) or {}
            pre_call["scheduled_at"] = sched_time.isoformat()
            rest_patch("calls", f"id=eq.{call['id']}", {
                "started_at": sched_time.isoformat(),
                "pre_call_data": pre_call,
            })
            print(f"  Updated {title} → {sched_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  Not found: {title}")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 5: Summary
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SEED COMPLETE — Summary")
    print("=" * 60)

    users = rest_get("user_profiles", "select=id,full_name,role")
    calls = rest_get("calls", "select=id,status,user_id,title")
    analyses = rest_get("call_analyses", "select=call_id,overall_score")
    scores = rest_get("call_scores", "select=call_id")
    tasks = rest_get("call_tasks", "select=id,status")
    transcripts = rest_get("call_transcripts", "select=call_id")

    completed = [c for c in calls if c["status"] == "completed"]
    scheduled = [c for c in calls if c["status"] == "scheduled"]
    unique_transcript_calls = len(set(t["call_id"] for t in transcripts))
    pending_tasks = len([t for t in tasks if t["status"] == "pending"])

    print(f"\nUsers:            {len(users)}")
    for u in users:
        user_calls = len([c for c in completed if c["user_id"] == u["id"]])
        print(f"  {u['full_name']:20} ({u['role']:10}) — {user_calls} completed calls")
    print(f"\nTotal calls:      {len(calls)}")
    print(f"  Completed:      {len(completed)}")
    print(f"  Scheduled:      {len(scheduled)}")
    print(f"Analyses:         {len(analyses)}")
    print(f"Score records:    {len(scores)}")
    print(f"Tasks:            {len(tasks)} ({pending_tasks} pending)")
    print(f"Transcript calls: {unique_transcript_calls}")
    print(f"\nAvg scores by user:")
    for u in users:
        user_call_ids = [c["id"] for c in completed if c["user_id"] == u["id"]]
        user_analyses = [a for a in analyses if a["call_id"] in user_call_ids]
        if user_analyses:
            avg = sum(a["overall_score"] for a in user_analyses) / len(user_analyses)
            print(f"  {u['full_name']:20} — {avg:.1f}")


if __name__ == "__main__":
    main()
