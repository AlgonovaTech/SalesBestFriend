"""
Seed playbooks, scoring criteria, and handbooks for 3 countries.

Creates:
- 3 Teams: Indonesia, Vietnam, Philippines
- 3 Playbooks (one per team/country)
- 3 Published PlaybookVersions with:
  - guidelines_content (methodology)
  - scoring_criteria (20 criteria each)
  - call_structure (stages + checklist items)
  - client_card_fields
- 9 Playbook Documents (3 per playbook: product handbook, analysis criteria, call guide)

Run: cd backend && python -m scripts.seed_playbooks
"""

import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
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
EXISTING_TEAM_ID = "b0000000-0000-0000-0000-000000000001"
TEST_USER_ID = "4bb830d7-fe4c-4b4c-8f96-6513457f0a81"

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


# ═══════════════════════════════════════════════════════════════════════════════
# DATA DEFINITIONS FOR 3 COUNTRIES
# ═══════════════════════════════════════════════════════════════════════════════


TEAMS = [
    {
        "id": EXISTING_TEAM_ID,  # Reuse existing team
        "name": "Indonesia Sales",
        "country": "Indonesia",
        "language": "id",
    },
    {
        "id": str(uuid4()),
        "name": "Vietnam Sales",
        "country": "Vietnam",
        "language": "vi",
    },
    {
        "id": str(uuid4()),
        "name": "Philippines Sales",
        "country": "Philippines",
        "language": "en",
    },
]


# ─── SCORING CRITERIA (shared structure, localized) ──────────────────────────

SCORING_CRITERIA_INDONESIA = [
    {"name": "Greeting & Introduction", "max_score": 5, "weight": 1.0, "description": "Sapa dengan hangat, perkenalkan diri dan Algonova. Konfirmasi nama anak dan orang tua."},
    {"name": "Explain Agenda", "max_score": 5, "weight": 1.0, "description": "Jelaskan tahapan trial class dengan jelas: profiling, diagnostic, presentasi, negosiasi."},
    {"name": "Child Name & Age", "max_score": 5, "weight": 1.0, "description": "Konfirmasi nama, usia, dan tingkat sekolah anak."},
    {"name": "Schooling Status", "max_score": 5, "weight": 1.0, "description": "Tanyakan status sekolah, kurikulum, dan prestasi anak."},
    {"name": "Child Interests", "max_score": 5, "weight": 1.0, "description": "Eksplorasi minat anak: game favorit, hobi, aktivitas harian."},
    {"name": "Parent Expectations", "max_score": 5, "weight": 1.2, "description": "Gali harapan orang tua: skill development, career prep, creative thinking."},
    {"name": "Learning Experience", "max_score": 5, "weight": 1.0, "description": "Tanyakan pengalaman belajar sebelumnya: les, kursus, self-learning."},
    {"name": "Schedule Availability", "max_score": 5, "weight": 0.8, "description": "Tanyakan ketersediaan jadwal: hari, jam, durasi yang diinginkan."},
    {"name": "Decision Process", "max_score": 5, "weight": 1.0, "description": "Pahami siapa yang mengambil keputusan dan timeline-nya."},
    {"name": "Budget Readiness", "max_score": 5, "weight": 1.0, "description": "Eksplorasi kesiapan budget tanpa terlalu direct."},
    {"name": "Diagnostic Introduction", "max_score": 5, "weight": 1.0, "description": "Perkenalkan aktivitas diagnostic dengan antusias dan jelas."},
    {"name": "Age-Appropriate Assessment", "max_score": 5, "weight": 1.0, "description": "Gunakan assessment yang sesuai usia dan level anak."},
    {"name": "Child Engagement", "max_score": 5, "weight": 1.2, "description": "Libatkan anak secara aktif: pujian, dorongan, interaksi dua arah."},
    {"name": "Explain Results", "max_score": 5, "weight": 1.0, "description": "Jelaskan hasil assessment dengan bahasa yang mudah dipahami orang tua."},
    {"name": "Connect to Program", "max_score": 5, "weight": 1.2, "description": "Hubungkan hasil assessment dengan program yang direkomendasikan."},
    {"name": "Program Overview", "max_score": 5, "weight": 1.0, "description": "Presentasikan program secara jelas: kurikulum, durasi, metode."},
    {"name": "Learning Methodology", "max_score": 5, "weight": 1.0, "description": "Jelaskan metode belajar: project-based, interactive, personalized."},
    {"name": "Success Stories", "max_score": 5, "weight": 1.0, "description": "Bagikan cerita sukses murid yang relevan dengan profil anak."},
    {"name": "Objection Handling", "max_score": 5, "weight": 1.5, "description": "Tangani keberatan (harga, waktu, kualitas) dengan empati dan data."},
    {"name": "Pricing Presentation", "max_score": 5, "weight": 1.5, "description": "Presentasikan harga dengan percaya diri, jelaskan value proposition."},
]

SCORING_CRITERIA_VIETNAM = [
    {"name": "Loi Chao & Gioi Thieu", "max_score": 5, "weight": 1.0, "description": "Chao don nong nhiet, gioi thieu ban than va truong. Xac nhan ten phu huynh va hoc sinh."},
    {"name": "Trinh Bay Chuong Trinh Buoi Hoc", "max_score": 5, "weight": 1.0, "description": "Giai thich ro rang cac buoc cua buoi hoc thu: tim hieu, danh gia, gioi thieu, thao luan."},
    {"name": "Ten & Tuoi Hoc Sinh", "max_score": 5, "weight": 1.0, "description": "Xac nhan ten, tuoi va cap hoc cua hoc sinh."},
    {"name": "Tinh Trang Hoc Tap", "max_score": 5, "weight": 1.0, "description": "Hoi ve truong hoc, chuong trinh hoc va thanh tich."},
    {"name": "So Thich Hoc Sinh", "max_score": 5, "weight": 1.0, "description": "Tim hieu so thich: game yeu thich, hoat dong ngoai khoa, mon hoc ua thich."},
    {"name": "Ky Vong Phu Huynh", "max_score": 5, "weight": 1.2, "description": "Tim hieu ky vong cua phu huynh: phat trien ky nang, dinh huong nghe nghiep, tu duy sang tao."},
    {"name": "Kinh Nghiem Hoc Tap", "max_score": 5, "weight": 1.0, "description": "Hoi ve kinh nghiem hoc them truoc day."},
    {"name": "Lich Hoc", "max_score": 5, "weight": 0.8, "description": "Xac nhan lich hoc phu hop: ngay, gio, thoi luong."},
    {"name": "Quy Trinh Quyet Dinh", "max_score": 5, "weight": 1.0, "description": "Tim hieu ai la nguoi ra quyet dinh va thoi gian du kien."},
    {"name": "Ngan Sach", "max_score": 5, "weight": 1.0, "description": "Tim hieu muc ngan sach mot cach te nhi."},
    {"name": "Gioi Thieu Bai Danh Gia", "max_score": 5, "weight": 1.0, "description": "Gioi thieu hoat dong danh gia voi su nhiet tinh."},
    {"name": "Danh Gia Phu Hop Tuoi", "max_score": 5, "weight": 1.0, "description": "Su dung bai danh gia phu hop voi do tuoi va trinh do."},
    {"name": "Su Tham Gia Cua Hoc Sinh", "max_score": 5, "weight": 1.2, "description": "Dong vien, khen ngoi va tuong tac hai chieu voi hoc sinh."},
    {"name": "Giai Thich Ket Qua", "max_score": 5, "weight": 1.0, "description": "Trinh bay ket qua danh gia bang ngon ngu de hieu cho phu huynh."},
    {"name": "Ket Noi Voi Chuong Trinh", "max_score": 5, "weight": 1.2, "description": "Lien ket ket qua danh gia voi chuong trinh phu hop."},
    {"name": "Tong Quan Chuong Trinh", "max_score": 5, "weight": 1.0, "description": "Trinh bay chuong trinh ro rang: noi dung, thoi luong, phuong phap."},
    {"name": "Phuong Phap Giang Day", "max_score": 5, "weight": 1.0, "description": "Giai thich phuong phap: hoc theo du an, tuong tac, ca nhan hoa."},
    {"name": "Cau Chuyen Thanh Cong", "max_score": 5, "weight": 1.0, "description": "Chia se cau chuyen thanh cong cua hoc vien tuong tu."},
    {"name": "Xu Ly Phan Doi", "max_score": 5, "weight": 1.5, "description": "Xu ly phan doi (gia, thoi gian, chat luong) voi su dong cam va du lieu."},
    {"name": "Trinh Bay Gia", "max_score": 5, "weight": 1.5, "description": "Trinh bay gia tu tin, nhan manh gia tri chuong trinh."},
]

SCORING_CRITERIA_PHILIPPINES = [
    {"name": "Greeting & Introduction", "max_score": 5, "weight": 1.0, "description": "Warm greeting, self-introduction and school intro. Confirm parent and child name."},
    {"name": "Session Agenda", "max_score": 5, "weight": 1.0, "description": "Clearly explain the trial class stages: profiling, assessment, presentation, discussion."},
    {"name": "Child Name & Age", "max_score": 5, "weight": 1.0, "description": "Confirm child's name, age, and grade level."},
    {"name": "School Background", "max_score": 5, "weight": 1.0, "description": "Ask about school, curriculum type (local/international), and academic performance."},
    {"name": "Child's Interests", "max_score": 5, "weight": 1.0, "description": "Explore interests: favorite games, hobbies, extracurricular activities."},
    {"name": "Parent Expectations", "max_score": 5, "weight": 1.2, "description": "Understand parent's goals: skill development, future career, creative thinking, STEM readiness."},
    {"name": "Prior Learning", "max_score": 5, "weight": 1.0, "description": "Ask about previous tutoring, online courses, or self-learning experience."},
    {"name": "Schedule Preference", "max_score": 5, "weight": 0.8, "description": "Check available schedule: preferred days, times, session duration."},
    {"name": "Decision Process", "max_score": 5, "weight": 1.0, "description": "Understand who decides (parent alone, both parents, grandparent) and timeline."},
    {"name": "Budget Awareness", "max_score": 5, "weight": 1.0, "description": "Tactfully explore budget expectations and payment preferences."},
    {"name": "Assessment Introduction", "max_score": 5, "weight": 1.0, "description": "Introduce diagnostic activity with enthusiasm and clear instructions."},
    {"name": "Age-Appropriate Tasks", "max_score": 5, "weight": 1.0, "description": "Use assessment tasks appropriate for the child's age and skill level."},
    {"name": "Child Engagement", "max_score": 5, "weight": 1.2, "description": "Actively engage child: praise, encouragement, two-way interaction."},
    {"name": "Results Explanation", "max_score": 5, "weight": 1.0, "description": "Explain assessment results in parent-friendly language with specific examples."},
    {"name": "Program Fit", "max_score": 5, "weight": 1.2, "description": "Connect assessment results to the recommended program clearly."},
    {"name": "Program Overview", "max_score": 5, "weight": 1.0, "description": "Present program clearly: curriculum, duration, methodology, expected outcomes."},
    {"name": "Teaching Method", "max_score": 5, "weight": 1.0, "description": "Explain methodology: project-based, interactive, personalized learning paths."},
    {"name": "Success Stories", "max_score": 5, "weight": 1.0, "description": "Share relevant student success stories matching the child's profile."},
    {"name": "Objection Handling", "max_score": 5, "weight": 1.5, "description": "Handle concerns (price, time, quality, online vs in-person) with empathy and data."},
    {"name": "Pricing Clarity", "max_score": 5, "weight": 1.5, "description": "Present pricing confidently, emphasize value, offer payment options."},
]


# ─── CALL STRUCTURE ──────────────────────────────────────────────────────────

def make_call_structure(lang: str) -> list:
    """Generate call structure stages for a given language."""
    if lang == "id":
        return [
            {"id": "greeting", "name": "Greeting & Preparation", "startOffsetSeconds": 0, "durationSeconds": 180,
             "items": [
                 {"id": "open_greet", "type": "say", "content": "Sapa dengan hangat dan perkenalkan diri", "extended_description": "Greet parent and child warmly, introduce yourself and Algonova.", "semantic_keywords": {"required": ["halo", "selamat", "nama saya", "algonova"], "forbidden": ["nanti", "tunggu"]}},
                 {"id": "confirm_names", "type": "say", "content": "Konfirmasi nama anak dan orang tua", "extended_description": "Verify both parent's and child's names.", "semantic_keywords": {"required": ["nama", "anak", "mama", "papa"], "forbidden": ["nanti"]}},
                 {"id": "explain_agenda", "type": "say", "content": "Jelaskan agenda trial class", "extended_description": "Outline the session steps clearly.", "semantic_keywords": {"required": ["agenda", "tahapan", "pertama", "kedua"], "forbidden": ["nanti"]}},
             ]},
            {"id": "profiling", "name": "Profiling", "startOffsetSeconds": 180, "durationSeconds": 420,
             "items": [
                 {"id": "ask_age", "type": "discuss", "content": "Tanyakan usia dan tingkat sekolah", "extended_description": "Ask about child's age and grade level.", "semantic_keywords": {"required": ["umur", "usia", "kelas", "tahun"], "forbidden": ["nanti"]}},
                 {"id": "ask_interests", "type": "discuss", "content": "Tanyakan minat dan hobi anak", "extended_description": "Explore child's interests and hobbies.", "semantic_keywords": {"required": ["suka", "hobi", "game", "favorit"], "forbidden": ["nanti"]}},
                 {"id": "ask_parent_goals", "type": "discuss", "content": "Tanyakan harapan orang tua", "extended_description": "Understand what parent hopes to achieve.", "semantic_keywords": {"required": ["harapan", "tujuan", "ingin", "goal"], "forbidden": ["nanti"]}},
             ]},
            {"id": "diagnostic", "name": "Diagnostic & Assessment", "startOffsetSeconds": 600, "durationSeconds": 600,
             "items": [
                 {"id": "intro_diagnostic", "type": "say", "content": "Perkenalkan aktivitas diagnostic", "extended_description": "Introduce the assessment activity with enthusiasm.", "semantic_keywords": {"required": ["coba", "diagnostic", "aktivitas", "test"], "forbidden": []}},
                 {"id": "run_assessment", "type": "discuss", "content": "Lakukan assessment sesuai usia", "extended_description": "Conduct age-appropriate assessment.", "semantic_keywords": {"required": ["coba", "jawab", "klik", "langkah"], "forbidden": []}},
                 {"id": "explain_results", "type": "say", "content": "Jelaskan hasil assessment", "extended_description": "Explain results in parent-friendly language.", "semantic_keywords": {"required": ["hasil", "result", "assessment", "bagus"], "forbidden": ["nanti"]}},
             ]},
            {"id": "presentation", "name": "Program Presentation", "startOffsetSeconds": 1200, "durationSeconds": 600,
             "items": [
                 {"id": "present_program", "type": "say", "content": "Presentasikan program yang cocok", "extended_description": "Present the recommended program.", "semantic_keywords": {"required": ["program", "kelas", "kurikulum", "course"], "forbidden": ["nanti"]}},
                 {"id": "share_success", "type": "say", "content": "Bagikan cerita sukses murid", "extended_description": "Share relevant student success stories.", "semantic_keywords": {"required": ["murid", "berhasil", "prestasi", "sukses"], "forbidden": []}},
                 {"id": "connect_needs", "type": "say", "content": "Hubungkan dengan kebutuhan anak", "extended_description": "Connect program to child's specific needs.", "semantic_keywords": {"required": ["cocok", "sesuai", "kebutuhan", "anak"], "forbidden": []}},
             ]},
            {"id": "negotiation", "name": "Negotiation & Closing", "startOffsetSeconds": 1800, "durationSeconds": 600,
             "items": [
                 {"id": "present_pricing", "type": "say", "content": "Presentasikan harga dan paket", "extended_description": "Present pricing clearly and confidently.", "semantic_keywords": {"required": ["harga", "biaya", "paket", "investasi"], "forbidden": ["mahal", "murah"]}},
                 {"id": "handle_objections", "type": "discuss", "content": "Tangani keberatan dengan empati", "extended_description": "Address objections with empathy and data.", "semantic_keywords": {"required": ["keberatan", "masalah", "khawatir", "pertimbangan"], "forbidden": ["tidak bisa"]}},
                 {"id": "close_call", "type": "say", "content": "Akhiri dengan profesional", "extended_description": "Close the call professionally.", "semantic_keywords": {"required": ["terima kasih", "follow up", "selanjutnya"], "forbidden": []}},
             ]},
        ]
    elif lang == "vi":
        return [
            {"id": "greeting", "name": "Chao Don & Chuan Bi", "startOffsetSeconds": 0, "durationSeconds": 180,
             "items": [
                 {"id": "open_greet", "type": "say", "content": "Chao don nong nhiet va gioi thieu ban than", "extended_description": "Greet parent and child warmly in Vietnamese.", "semantic_keywords": {"required": ["xin chao", "chao", "ten toi", "algonova"], "forbidden": ["de sau"]}},
                 {"id": "confirm_names", "type": "say", "content": "Xac nhan ten hoc sinh va phu huynh", "extended_description": "Verify names of student and parent.", "semantic_keywords": {"required": ["ten", "con", "phu huynh"], "forbidden": ["de sau"]}},
                 {"id": "explain_agenda", "type": "say", "content": "Trinh bay chuong trinh buoi hoc", "extended_description": "Outline session agenda.", "semantic_keywords": {"required": ["chuong trinh", "buoc", "dau tien", "tiep theo"], "forbidden": ["de sau"]}},
             ]},
            {"id": "profiling", "name": "Tim Hieu Hoc Sinh", "startOffsetSeconds": 180, "durationSeconds": 420,
             "items": [
                 {"id": "ask_age", "type": "discuss", "content": "Hoi tuoi va cap hoc", "extended_description": "Ask about student's age and grade.", "semantic_keywords": {"required": ["tuoi", "lop", "nam", "hoc"], "forbidden": ["de sau"]}},
                 {"id": "ask_interests", "type": "discuss", "content": "Tim hieu so thich", "extended_description": "Explore student's interests.", "semantic_keywords": {"required": ["thich", "game", "hoat dong", "mon hoc"], "forbidden": ["de sau"]}},
                 {"id": "ask_parent_goals", "type": "discuss", "content": "Tim hieu ky vong phu huynh", "extended_description": "Understand parent expectations.", "semantic_keywords": {"required": ["ky vong", "mong muon", "muc tieu"], "forbidden": ["de sau"]}},
             ]},
            {"id": "diagnostic", "name": "Danh Gia & Kiem Tra", "startOffsetSeconds": 600, "durationSeconds": 600,
             "items": [
                 {"id": "intro_diagnostic", "type": "say", "content": "Gioi thieu bai danh gia", "extended_description": "Introduce assessment activity.", "semantic_keywords": {"required": ["danh gia", "bai tap", "thu"], "forbidden": []}},
                 {"id": "run_assessment", "type": "discuss", "content": "Thuc hien danh gia phu hop tuoi", "extended_description": "Run age-appropriate assessment.", "semantic_keywords": {"required": ["thu", "lam", "tra loi", "bai"], "forbidden": []}},
                 {"id": "explain_results", "type": "say", "content": "Giai thich ket qua", "extended_description": "Explain results clearly.", "semantic_keywords": {"required": ["ket qua", "diem", "gioi", "tot"], "forbidden": ["de sau"]}},
             ]},
            {"id": "presentation", "name": "Gioi Thieu Chuong Trinh", "startOffsetSeconds": 1200, "durationSeconds": 600,
             "items": [
                 {"id": "present_program", "type": "say", "content": "Gioi thieu chuong trinh phu hop", "extended_description": "Present recommended program.", "semantic_keywords": {"required": ["chuong trinh", "khoa hoc", "lop", "noi dung"], "forbidden": ["de sau"]}},
                 {"id": "share_success", "type": "say", "content": "Chia se cau chuyen thanh cong", "extended_description": "Share student success stories.", "semantic_keywords": {"required": ["hoc vien", "thanh cong", "dat duoc"], "forbidden": []}},
                 {"id": "connect_needs", "type": "say", "content": "Lien ket voi nhu cau hoc sinh", "extended_description": "Connect to student needs.", "semantic_keywords": {"required": ["phu hop", "can", "nhu cau", "hoc sinh"], "forbidden": []}},
             ]},
            {"id": "negotiation", "name": "Dam Phan & Ket Thuc", "startOffsetSeconds": 1800, "durationSeconds": 600,
             "items": [
                 {"id": "present_pricing", "type": "say", "content": "Trinh bay hoc phi va goi hoc", "extended_description": "Present pricing clearly.", "semantic_keywords": {"required": ["hoc phi", "gia", "goi", "phi"], "forbidden": ["dat"]}},
                 {"id": "handle_objections", "type": "discuss", "content": "Xu ly phan doi", "extended_description": "Handle objections with empathy.", "semantic_keywords": {"required": ["lo lang", "van de", "ngai"], "forbidden": ["khong duoc"]}},
                 {"id": "close_call", "type": "say", "content": "Ket thuc chuyen nghiep", "extended_description": "Close call professionally.", "semantic_keywords": {"required": ["cam on", "hen gap lai", "tiep theo"], "forbidden": []}},
             ]},
        ]
    else:  # English / Philippines
        return [
            {"id": "greeting", "name": "Greeting & Preparation", "startOffsetSeconds": 0, "durationSeconds": 180,
             "items": [
                 {"id": "open_greet", "type": "say", "content": "Greet warmly and introduce yourself", "extended_description": "Warm greeting, introduce yourself and the school.", "semantic_keywords": {"required": ["hello", "hi", "good morning", "my name", "algonova"], "forbidden": ["later"]}},
                 {"id": "confirm_names", "type": "say", "content": "Confirm parent and child names", "extended_description": "Verify both names.", "semantic_keywords": {"required": ["name", "child", "parent", "mom", "dad"], "forbidden": ["later"]}},
                 {"id": "explain_agenda", "type": "say", "content": "Explain session agenda", "extended_description": "Outline the session steps.", "semantic_keywords": {"required": ["agenda", "steps", "first", "then", "session"], "forbidden": ["later"]}},
             ]},
            {"id": "profiling", "name": "Profiling", "startOffsetSeconds": 180, "durationSeconds": 420,
             "items": [
                 {"id": "ask_age", "type": "discuss", "content": "Ask age and grade level", "extended_description": "Confirm child's age and school grade.", "semantic_keywords": {"required": ["age", "grade", "years old", "school"], "forbidden": ["later"]}},
                 {"id": "ask_interests", "type": "discuss", "content": "Explore interests and hobbies", "extended_description": "Find out what child enjoys.", "semantic_keywords": {"required": ["like", "enjoy", "hobby", "game", "favorite"], "forbidden": ["later"]}},
                 {"id": "ask_parent_goals", "type": "discuss", "content": "Understand parent goals", "extended_description": "What does the parent hope to achieve?", "semantic_keywords": {"required": ["hope", "goal", "want", "expect"], "forbidden": ["later"]}},
             ]},
            {"id": "diagnostic", "name": "Diagnostic & Assessment", "startOffsetSeconds": 600, "durationSeconds": 600,
             "items": [
                 {"id": "intro_diagnostic", "type": "say", "content": "Introduce the assessment activity", "extended_description": "Introduce assessment with enthusiasm.", "semantic_keywords": {"required": ["try", "activity", "assessment", "fun"], "forbidden": []}},
                 {"id": "run_assessment", "type": "discuss", "content": "Run age-appropriate assessment", "extended_description": "Conduct suitable assessment.", "semantic_keywords": {"required": ["try", "answer", "click", "step"], "forbidden": []}},
                 {"id": "explain_results", "type": "say", "content": "Explain assessment results", "extended_description": "Share findings with parent.", "semantic_keywords": {"required": ["results", "score", "great", "well"], "forbidden": ["later"]}},
             ]},
            {"id": "presentation", "name": "Program Presentation", "startOffsetSeconds": 1200, "durationSeconds": 600,
             "items": [
                 {"id": "present_program", "type": "say", "content": "Present recommended program", "extended_description": "Present the best-fit program.", "semantic_keywords": {"required": ["program", "course", "curriculum", "class"], "forbidden": ["later"]}},
                 {"id": "share_success", "type": "say", "content": "Share student success stories", "extended_description": "Mention relevant success stories.", "semantic_keywords": {"required": ["student", "success", "achieved", "learned"], "forbidden": []}},
                 {"id": "connect_needs", "type": "say", "content": "Connect to child's needs", "extended_description": "Link program to child's profile.", "semantic_keywords": {"required": ["fit", "match", "need", "child"], "forbidden": []}},
             ]},
            {"id": "negotiation", "name": "Negotiation & Closing", "startOffsetSeconds": 1800, "durationSeconds": 600,
             "items": [
                 {"id": "present_pricing", "type": "say", "content": "Present pricing and packages", "extended_description": "Show pricing clearly.", "semantic_keywords": {"required": ["price", "cost", "package", "investment"], "forbidden": ["expensive", "cheap"]}},
                 {"id": "handle_objections", "type": "discuss", "content": "Handle objections with empathy", "extended_description": "Address concerns empathetically.", "semantic_keywords": {"required": ["concern", "worry", "hesitate", "think"], "forbidden": ["can't"]}},
                 {"id": "close_call", "type": "say", "content": "Close professionally", "extended_description": "End the call professionally.", "semantic_keywords": {"required": ["thank", "follow up", "next step"], "forbidden": []}},
             ]},
        ]


# ─── CLIENT CARD FIELDS ──────────────────────────────────────────────────────

CLIENT_CARD_FIELDS = [
    {"id": "child_name", "label": "Child's Name", "hint": "Name and age", "multiline": False, "category": "child_info"},
    {"id": "child_interests", "label": "Interests", "hint": "Games, activities, subjects", "multiline": True, "category": "child_info"},
    {"id": "child_experience", "label": "Prior Experience", "hint": "Coding or tech experience", "multiline": True, "category": "child_info"},
    {"id": "parent_goal", "label": "Parent's Goal", "hint": "What parent wants", "multiline": True, "category": "parent_info"},
    {"id": "learning_motivation", "label": "Motivation", "hint": "Why enrolling now", "multiline": True, "category": "parent_info"},
    {"id": "main_pain_point", "label": "Pain Point", "hint": "Primary concern", "multiline": True, "category": "needs"},
    {"id": "desired_outcome", "label": "Desired Outcome", "hint": "Success criteria", "multiline": True, "category": "needs"},
    {"id": "objections", "label": "Objections", "hint": "Concerns raised", "multiline": True, "category": "concerns"},
    {"id": "budget_constraint", "label": "Budget", "hint": "Budget situation", "multiline": False, "category": "concerns"},
    {"id": "schedule_constraint", "label": "Schedule", "hint": "Available times", "multiline": False, "category": "concerns"},
]


# ─── GUIDELINES CONTENT ──────────────────────────────────────────────────────

GUIDELINES_INDONESIA = """# Trial Class Sales Playbook — Indonesia

## Filosofi
Setiap trial class adalah kesempatan untuk menunjukkan value Algonova. Bukan sekadar demo produk, tapi pengalaman belajar yang meyakinkan orang tua.

## Prinsip Utama
1. **Child-first approach** — Libatkan anak secara aktif, bukan hanya bicara dengan orang tua
2. **Data-driven recommendation** — Gunakan hasil diagnostic untuk rekomendasi yang personal
3. **Empathetic selling** — Pahami kekhawatiran, jangan push. Tunjukkan value.
4. **Professional closure** — Selalu tutup dengan next step yang jelas

## Produk
- **Scratch / Scratch Jr** — Usia 5-8 tahun, visual programming dengan drag-drop blocks
- **Roblox Studio** — Usia 8-12 tahun, game development dan 3D world building
- **Python / Web Dev** — Usia 10-15 tahun, text-based coding untuk yang lebih advance
- **Math Program** — Semua usia, dari Math Fun sampai Olympiad Preparation

## Harga (2026)
- Group Class: Rp 400.000/bulan (8 sesi)
- Premium Class: Rp 750.000/bulan (8 sesi, max 4 siswa)
- Private Class: Rp 1.200.000/bulan (8 sesi, 1-on-1)
- Diskon 15% untuk paket 3 bulan, 25% untuk 6 bulan

## Handling Objections
- "Mahal" → Bandingkan per-sesi (~Rp 50.000) vs les privat offline (~Rp 200.000)
- "Online tidak efektif" → Tunjukkan project murid, interactive platform
- "Anak tidak tertarik" → Referensi hasil diagnostic, engagement selama trial
"""

GUIDELINES_VIETNAM = """# Trial Class Sales Playbook — Vietnam

## Triet Ly
Moi buoi hoc thu la co hoi the hien gia tri cua Algonova. Khong chi la demo san pham, ma la trai nghiem hoc tap thuyet phuc phu huynh.

## Nguyen Tac Chinh
1. **Lay hoc sinh lam trung tam** — Thu hut hoc sinh tham gia, khong chi noi chuyen voi phu huynh
2. **Khuyen nghi dua tren du lieu** — Su dung ket qua danh gia de dua ra khuyen nghi ca nhan
3. **Ban hang dong cam** — Hieu lo lang, khong ep. The hien gia tri.
4. **Ket thuc chuyen nghiep** — Luon ket thuc voi buoc tiep theo ro rang

## San Pham
- **Scratch / Scratch Jr** — 5-8 tuoi, lap trinh truc quan voi keo tha
- **Roblox Studio** — 8-12 tuoi, phat trien game va xay dung the gioi 3D
- **Python / Web Dev** — 10-15 tuoi, lap trinh van ban cho hoc sinh nang cao
- **Chuong Trinh Toan** — Moi lua tuoi, tu Toan Vui den Luyen Thi Olympic

## Hoc Phi (2026)
- Lop Nhom: 500.000 VND/buoi (goi 8 buoi: 3.500.000 VND)
- Lop Nang Cao: 800.000 VND/buoi (toi da 4 hoc sinh)
- Lop Ca Nhan: 1.200.000 VND/buoi (1-kem-1)
- Giam 15% cho goi 3 thang, 25% cho 6 thang

## Xu Ly Phan Doi
- "Dat qua" → So sanh moi buoi (~500k) vs gia su tai nha (~800k)
- "Hoc online khong hieu qua" → Cho xem du an hoc sinh, nen tang tuong tac
- "Con khong quan tam" → Tham chieu ket qua danh gia, su tham gia trong buoi thu
"""

GUIDELINES_PHILIPPINES = """# Trial Class Sales Playbook — Philippines

## Philosophy
Every trial class is a chance to demonstrate Algonova's value. Not just a product demo, but a learning experience that convinces parents.

## Core Principles
1. **Child-first approach** — Engage the child actively, not just talk to parents
2. **Data-driven recommendation** — Use diagnostic results for personalized recommendations
3. **Empathetic selling** — Understand concerns, don't push. Show value.
4. **Professional closure** — Always close with a clear next step

## Products
- **Scratch / Scratch Jr** — Ages 5-8, visual programming with drag-drop blocks
- **Roblox Studio** — Ages 8-12, game development and 3D world building
- **Python / Web Dev** — Ages 10-15, text-based coding for advanced students
- **Math Program** — All ages, from Math Fun to Olympiad Preparation

## Pricing (2026)
- Group Class: PHP 2,500/month (8 sessions)
- Premium Class: PHP 4,500/month (8 sessions, max 4 students)
- Private Class: PHP 7,500/month (8 sessions, 1-on-1)
- 15% discount for 3-month package, 25% for 6-month

## Handling Objections
- "Too expensive" → Compare per-session (~PHP 312) vs private tutor (~PHP 800)
- "Online isn't effective" → Show student projects, interactive platform
- "My child won't be interested" → Reference diagnostic results, engagement during trial
- "Let me think about it" → Offer to hold slot, send WhatsApp recap, follow up next day
"""


# ─── HANDBOOK DOCUMENTS ──────────────────────────────────────────────────────

def make_documents(lang: str) -> list:
    """Generate 3 documents per playbook."""
    if lang == "id":
        return [
            {
                "document_type": "analysis",
                "title": "QC Analysis Criteria — Indonesia",
                "description": "Detailed scoring criteria for QC analysis of Indonesian trial class calls",
                "sort_order": 1,
                "content": """## Kriteria Analisis QC — Trial Class Indonesia

### Kategori Penilaian

**1. Opening & Rapport (Skor 1-5)**
- Apakah tutor menyapa dengan hangat?
- Apakah tutor memperkenalkan diri dan Algonova?
- Apakah nama anak dan orang tua dikonfirmasi?

**2. Profiling Quality (Skor 1-5)**
- Apakah informasi usia, sekolah, minat dikumpulkan?
- Apakah harapan orang tua digali dengan baik?
- Apakah pertanyaan terbuka dan menggali?

**3. Diagnostic Execution (Skor 1-5)**
- Apakah aktivitas assessment sesuai usia?
- Apakah anak engaged selama assessment?
- Apakah hasil assessment dijelaskan dengan jelas?

**4. Presentation & Closing (Skor 1-5)**
- Apakah program yang direkomendasikan sesuai profil anak?
- Apakah harga dipresentasikan dengan percaya diri?
- Apakah keberatan ditangani dengan empati?
- Apakah ada clear next step?

### Red Flags
- Tidak menyapa anak langsung
- Melewatkan diagnostic sepenuhnya
- Tidak membahas harga sama sekali
- Panggilan terlalu singkat (< 20 menit)
- Tidak ada follow-up yang dijadwalkan
""",
            },
            {
                "document_type": "call",
                "title": "Product Handbook — Scratch & Scratch Jr",
                "description": "Product knowledge untuk kelas Scratch dan Scratch Jr",
                "sort_order": 2,
                "content": """## Handbook: Scratch & Scratch Jr

### Scratch Jr (Usia 5-7)
- Platform: ScratchJr app (tablet/iPad)
- Konsep: Drag-and-drop visual blocks, storytelling, simple animations
- Durasi sesi: 45 menit
- Kurikulum: 24 sesi (3 bulan)
- Output: Anak bisa membuat cerita interaktif dan animasi sederhana

### Scratch (Usia 8-12)
- Platform: scratch.mit.edu (web browser)
- Konsep: Event-driven programming, variables, loops, conditionals
- Durasi sesi: 60 menit
- Kurikulum: 32 sesi (4 bulan basic, lanjut advanced)
- Output: Game sederhana, animasi interaktif, quiz app

### Key Selling Points
1. Dikembangkan oleh MIT — kredibilitas tinggi
2. Visual & fun — anak belajar tanpa merasa "les"
3. Progressive — dari Scratch Jr ke Scratch ke Python
4. Community — ribuan project yang bisa dijadikan inspirasi

### FAQ
- "Terlalu muda untuk coding?" → Scratch Jr dirancang untuk usia 5+, fokus pada logical thinking
- "Bisa offline?" → Scratch Jr bisa offline, Scratch perlu internet
- "Apa bedanya dengan YouTube tutorial?" → Kurikulum terstruktur + mentor 1:1/kelompok kecil
""",
            },
            {
                "document_type": "call",
                "title": "Product Handbook — Roblox Studio",
                "description": "Product knowledge untuk kelas Roblox Studio game development",
                "sort_order": 3,
                "content": """## Handbook: Roblox Studio

### Target
- Usia: 8-14 tahun
- Platform: Roblox Studio (desktop app)
- Bahasa pemrograman: Lua scripting

### Kurikulum
**Level 1 — World Builder (8 sesi)**
- Terrain editing, object placement
- Basic UI design
- Publish pertama ke Roblox

**Level 2 — Game Mechanics (12 sesi)**
- Scripting dasar Lua
- Events & triggers
- Leaderboards & scoring

**Level 3 — Advanced Dev (16 sesi)**
- Multiplayer game logic
- Data persistence
- Monetization basics

### Key Selling Points
1. Anak sudah kenal Roblox — engagement tinggi
2. Dari player menjadi creator — mindset shift
3. Bisa publish game yang dimainkan jutaan orang
4. Roblox dev = skill yang marketable (Roblox economy $1B+)

### Pricing Comparison
- Kursus Roblox offline: Rp 300.000-500.000/sesi
- Algonova Group: ~Rp 50.000/sesi
- Algonova Private: ~Rp 150.000/sesi (masih 3x lebih murah)
""",
            },
        ]
    elif lang == "vi":
        return [
            {
                "document_type": "analysis",
                "title": "Tieu Chi Phan Tich QC — Vietnam",
                "description": "Tieu chi danh gia chi tiet cho buoi hoc thu tai Viet Nam",
                "sort_order": 1,
                "content": """## Tieu Chi Phan Tich QC — Buoi Hoc Thu Vietnam

### Hang Muc Danh Gia

**1. Mo Dau & Xay Dung Quan He (1-5)**
- Giao vien co chao don nong nhiet?
- Co gioi thieu ban than va Algonova?
- Ten hoc sinh va phu huynh co duoc xac nhan?

**2. Chat Luong Tim Hieu (1-5)**
- Thong tin tuoi, truong, so thich co duoc thu thap?
- Ky vong phu huynh co duoc tim hieu ky?
- Cau hoi co mo va sau?

**3. Thuc Hien Danh Gia (1-5)**
- Hoat dong danh gia co phu hop tuoi?
- Hoc sinh co tham gia tich cuc?
- Ket qua co duoc giai thich ro rang?

**4. Trinh Bay & Ket Thuc (1-5)**
- Chuong trinh khuyen nghi co phu hop voi hoc sinh?
- Hoc phi co duoc trinh bay tu tin?
- Phan doi co duoc xu ly dong cam?
- Co buoc tiep theo ro rang?

### Dau Hieu Canh Bao
- Khong noi chuyen truc tiep voi hoc sinh
- Bo qua danh gia hoan toan
- Khong thao luan hoc phi
- Cuoc goi qua ngan (< 20 phut)
""",
            },
            {
                "document_type": "call",
                "title": "Handbook San Pham — Scratch & Scratch Jr",
                "description": "Kien thuc san pham cho lop Scratch",
                "sort_order": 2,
                "content": """## Handbook: Scratch & Scratch Jr

### Scratch Jr (5-7 tuoi)
- Nen tang: ScratchJr app (tablet/iPad)
- Khai niem: Keo tha khoi hinh, ke chuyen, hoat hinh don gian
- Thoi luong: 45 phut/buoi
- Giao trinh: 24 buoi (3 thang)

### Scratch (8-12 tuoi)
- Nen tang: scratch.mit.edu
- Khai niem: Lap trinh su kien, bien, vong lap, dieu kien
- Thoi luong: 60 phut/buoi
- Giao trinh: 32 buoi (4 thang co ban + nang cao)

### Diem Ban Hang Chinh
1. Phat trien boi MIT — uy tin cao
2. Truc quan va vui — hoc ma khong cam thay la "di hoc them"
3. Tien bo — tu Scratch Jr den Scratch den Python
""",
            },
            {
                "document_type": "call",
                "title": "Handbook San Pham — Roblox Studio",
                "description": "Kien thuc san pham cho lop Roblox Studio",
                "sort_order": 3,
                "content": """## Handbook: Roblox Studio

### Doi Tuong
- Tuoi: 8-14
- Nen tang: Roblox Studio (desktop)
- Ngon ngu: Lua scripting

### Giao Trinh
**Cap 1 — Xay Dung The Gioi (8 buoi)**
- Chinh sua dia hinh, dat vat the
- Thiet ke UI co ban
- Xuat ban game dau tien

**Cap 2 — Co Che Game (12 buoi)**
- Scripting Lua co ban
- Su kien & trigger
- Bang xep hang & tinh diem

**Cap 3 — Phat Trien Nang Cao (16 buoi)**
- Logic game nhieu nguoi choi
- Luu tru du lieu
- Co ban ve kiem tien

### Diem Ban Hang
1. Tre da biet Roblox — muc do tham gia cao
2. Tu nguoi choi thanh nguoi sang tao
3. Co the xuat ban game cho hang trieu nguoi choi
""",
            },
        ]
    else:  # English / Philippines
        return [
            {
                "document_type": "analysis",
                "title": "QC Analysis Criteria — Philippines",
                "description": "Detailed scoring criteria for QC analysis of Philippines trial class calls",
                "sort_order": 1,
                "content": """## QC Analysis Criteria — Trial Class Philippines

### Scoring Categories

**1. Opening & Rapport (Score 1-5)**
- Did the tutor greet warmly?
- Was there a clear self-introduction and school introduction?
- Were parent and child names confirmed?

**2. Profiling Quality (Score 1-5)**
- Was age, school, and interest information gathered?
- Were parent expectations explored thoroughly?
- Were questions open-ended and probing?

**3. Diagnostic Execution (Score 1-5)**
- Was the assessment age-appropriate?
- Was the child actively engaged during assessment?
- Were results explained clearly to the parent?

**4. Presentation & Closing (Score 1-5)**
- Was the recommended program a good fit for the child's profile?
- Was pricing presented confidently?
- Were objections handled with empathy?
- Was there a clear next step?

### Red Flags
- Not addressing the child directly
- Skipping diagnostic entirely
- No pricing discussion at all
- Call too short (< 20 minutes)
- No follow-up scheduled
""",
            },
            {
                "document_type": "call",
                "title": "Product Handbook — Scratch & Scratch Jr",
                "description": "Product knowledge for Scratch and Scratch Jr classes",
                "sort_order": 2,
                "content": """## Handbook: Scratch & Scratch Jr

### Scratch Jr (Ages 5-7)
- Platform: ScratchJr app (tablet/iPad)
- Concepts: Drag-and-drop visual blocks, storytelling, simple animations
- Session: 45 minutes
- Curriculum: 24 sessions (3 months)
- Output: Child can create interactive stories and simple animations

### Scratch (Ages 8-12)
- Platform: scratch.mit.edu (web browser)
- Concepts: Event-driven programming, variables, loops, conditionals
- Session: 60 minutes
- Curriculum: 32 sessions (4 months basic + advanced)
- Output: Simple games, interactive animations, quiz apps

### Key Selling Points
1. Developed by MIT — high credibility
2. Visual & fun — kids learn without feeling like "lessons"
3. Progressive — from Scratch Jr to Scratch to Python
4. Community — thousands of projects for inspiration

### FAQ
- "Too young for coding?" → Scratch Jr designed for ages 5+, focuses on logical thinking
- "Works offline?" → Scratch Jr works offline, Scratch needs internet
- "How is this different from YouTube?" → Structured curriculum + mentor support
""",
            },
            {
                "document_type": "call",
                "title": "Product Handbook — Roblox Studio",
                "description": "Product knowledge for Roblox Studio game development classes",
                "sort_order": 3,
                "content": """## Handbook: Roblox Studio

### Target
- Ages: 8-14
- Platform: Roblox Studio (desktop app)
- Language: Lua scripting

### Curriculum
**Level 1 — World Builder (8 sessions)**
- Terrain editing, object placement
- Basic UI design
- First publish to Roblox

**Level 2 — Game Mechanics (12 sessions)**
- Basic Lua scripting
- Events & triggers
- Leaderboards & scoring

**Level 3 — Advanced Dev (16 sessions)**
- Multiplayer game logic
- Data persistence
- Monetization basics

### Key Selling Points
1. Kids already know Roblox — high engagement
2. From player to creator — mindset shift
3. Can publish games played by millions
4. Roblox dev = marketable skill (Roblox economy worth $1B+)

### Pricing Comparison (Philippines)
- Offline Roblox course: PHP 500-800/session
- Algonova Group: ~PHP 312/session
- Algonova Private: ~PHP 937/session (still cheaper than offline)
""",
            },
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Seeding PLAYBOOKS for 3 Countries")
    print("=" * 60)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1: Ensure teams exist
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- Step 1: Creating/updating teams ---")

    team_ids = {}
    for team_data in TEAMS:
        team_id = team_data["id"]
        country = team_data["country"]

        # Check if team exists
        existing = rest_get("teams", f"id=eq.{team_id}")
        if existing:
            # Update name/language if needed
            rest_patch("teams", f"id=eq.{team_id}", {
                "name": team_data["name"],
                "country": team_data["country"],
                "language": team_data["language"],
            })
            team_ids[country] = team_id
            print(f"  Updated team: {team_data['name']} ({team_id[:12]}...)")
            continue

        # Create new team
        result = rest_post("teams", {
            "id": team_id,
            "organization_id": ORG_ID,
            "name": team_data["name"],
            "country": team_data["country"],
            "language": team_data["language"],
        })
        if result:
            if isinstance(result, list) and result:
                team_ids[country] = result[0]["id"]
            else:
                team_ids[country] = team_id
            print(f"  Created team: {team_data['name']} ({team_id[:12]}...)")
        else:
            team_ids[country] = team_id
            print(f"  Team creation may have failed for {team_data['name']}")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2: Create playbooks + versions + documents
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- Step 2: Creating playbooks ---")

    playbook_configs = [
        {
            "country": "Indonesia",
            "name": "Trial Class — Indonesia",
            "description": "Playbook untuk trial class penjualan di Indonesia. Bahasa Indonesia. Termasuk Scratch, Roblox, Python, dan Math.",
            "lang": "id",
            "guidelines": GUIDELINES_INDONESIA,
            "scoring": SCORING_CRITERIA_INDONESIA,
        },
        {
            "country": "Vietnam",
            "name": "Trial Class — Vietnam",
            "description": "Playbook cho buoi hoc thu ban hang tai Viet Nam. Tieng Viet. Bao gom Scratch, Roblox, Python va Toan.",
            "lang": "vi",
            "guidelines": GUIDELINES_VIETNAM,
            "scoring": SCORING_CRITERIA_VIETNAM,
        },
        {
            "country": "Philippines",
            "name": "Trial Class — Philippines",
            "description": "Trial class sales playbook for the Philippines market. English. Includes Scratch, Roblox, Python, and Math programs.",
            "lang": "en",
            "guidelines": GUIDELINES_PHILIPPINES,
            "scoring": SCORING_CRITERIA_PHILIPPINES,
        },
    ]

    for config in playbook_configs:
        country = config["country"]
        team_id = team_ids.get(country)
        if not team_id:
            print(f"  Skipping {country} — no team ID")
            continue

        # Check if playbook already exists for this team
        existing_pb = rest_get("playbooks", f"team_id=eq.{team_id}&name=eq.{urllib.parse.quote(config['name'])}")
        if existing_pb:
            playbook_id = existing_pb[0]["id"]
            print(f"  Playbook '{config['name']}' exists: {playbook_id[:12]}...")
        else:
            # Create playbook
            pb_result = rest_post("playbooks", {
                "organization_id": ORG_ID,
                "team_id": team_id,
                "name": config["name"],
                "description": config["description"],
                "is_active": True,
                "created_by": TEST_USER_ID,
            })
            if not pb_result:
                print(f"  Failed to create playbook for {country}")
                continue
            if isinstance(pb_result, list) and pb_result:
                playbook_id = pb_result[0]["id"]
            else:
                playbook_id = pb_result.get("id", "")
            print(f"  Created playbook: {config['name']} ({playbook_id[:12]}...)")

        # Check if version exists
        existing_versions = rest_get("playbook_versions", f"playbook_id=eq.{playbook_id}")
        if existing_versions:
            version_id = existing_versions[0]["id"]
            print(f"    Version exists: v{existing_versions[0]['version_number']}")
        else:
            # Create version
            call_structure = make_call_structure(config["lang"])
            version_result = rest_post("playbook_versions", {
                "playbook_id": playbook_id,
                "version_number": 1,
                "guidelines_content": config["guidelines"],
                "call_structure": call_structure,
                "client_card_fields": CLIENT_CARD_FIELDS,
                "scoring_criteria": config["scoring"],
                "published_at": now.isoformat(),
                "created_by": TEST_USER_ID,
            })
            if not version_result:
                print(f"    Failed to create version for {country}")
                continue
            if isinstance(version_result, list) and version_result:
                version_id = version_result[0]["id"]
            else:
                version_id = version_result.get("id", "")
            print(f"    Created version v1 ({version_id[:12]}...) — PUBLISHED")

        # Create documents
        existing_docs = rest_get("playbook_documents", f"playbook_id=eq.{playbook_id}")
        if existing_docs:
            print(f"    {len(existing_docs)} documents already exist, skipping")
        else:
            documents = make_documents(config["lang"])
            for doc in documents:
                doc_result = rest_post("playbook_documents", {
                    "playbook_id": playbook_id,
                    **doc,
                })
                if doc_result:
                    print(f"    + Document: {doc['title']}")
                else:
                    print(f"    ! Failed: {doc['title']}")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3: Summary
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SEED COMPLETE — Summary")
    print("=" * 60)

    teams = rest_get("teams", f"organization_id=eq.{ORG_ID}&select=id,name,country,language")
    playbooks = rest_get("playbooks", f"organization_id=eq.{ORG_ID}&select=id,name,team_id,is_active")
    versions = rest_get("playbook_versions", "select=id,playbook_id,version_number,published_at")
    documents = rest_get("playbook_documents", "select=id,playbook_id,document_type,title")

    print(f"\nTeams: {len(teams)}")
    for t in teams:
        print(f"  {t['name']:25} ({t['country']}, {t['language']})")

    print(f"\nPlaybooks: {len(playbooks)}")
    for pb in playbooks:
        team_name = next((t["name"] for t in teams if t["id"] == pb.get("team_id")), "—")
        pb_versions = [v for v in versions if v["playbook_id"] == pb["id"]]
        pb_docs = [d for d in documents if d["playbook_id"] == pb["id"]]
        published = any(v.get("published_at") for v in pb_versions)
        print(f"  {pb['name']:35} | {team_name:20} | {len(pb_versions)} version(s) | {len(pb_docs)} docs | {'Published' if published else 'Draft'}")

    print(f"\nTotal documents: {len(documents)}")
    for doc in documents:
        print(f"  [{doc['document_type']:10}] {doc['title']}")


if __name__ == "__main__":
    main()
