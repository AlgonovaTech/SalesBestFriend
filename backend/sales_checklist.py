"""
Sales Call Checklist & Stage Detection
Based on best practices for EdTech/SaaS sales calls
"""

from typing import Dict, List, Optional

# Checklist structure based on typical sales call flow
SALES_CHECKLIST = {
    "greeting": {
        "name": "Greeting & Rapport",
        "items": [
            {"id": "intro_yourself", "text": "Introduce yourself and company"},
            {"id": "ask_availability", "text": "Check if they have time for the call"},
            {"id": "set_agenda", "text": "Set agenda and expectations"},
            {"id": "build_rapport", "text": "Build initial rapport (small talk)"},
        ]
    },
    "discovery": {
        "name": "Discovery & Profiling",
        "items": [
            {"id": "current_situation", "text": "Understand current situation"},
            {"id": "pain_points", "text": "Identify pain points and challenges"},
            {"id": "goals", "text": "Discover goals and desired outcomes"},
            {"id": "decision_process", "text": "Understand decision-making process"},
            {"id": "budget_timeline", "text": "Qualify budget and timeline"},
            {"id": "stakeholders", "text": "Identify all stakeholders"},
        ]
    },
    "presentation": {
        "name": "Solution Presentation",
        "items": [
            {"id": "tailor_solution", "text": "Tailor solution to their needs"},
            {"id": "demo_key_features", "text": "Demo key features relevant to pain points"},
            {"id": "show_value", "text": "Show clear value and ROI"},
            {"id": "provide_examples", "text": "Provide case studies/examples"},
            {"id": "check_understanding", "text": "Check understanding and engagement"},
        ]
    },
    "objections": {
        "name": "Objection Handling",
        "items": [
            {"id": "address_price", "text": "Address price concerns"},
            {"id": "address_time", "text": "Address time/implementation concerns"},
            {"id": "address_competition", "text": "Differentiate from competitors"},
            {"id": "address_risks", "text": "Address perceived risks"},
            {"id": "confirm_resolution", "text": "Confirm objection is resolved"},
        ]
    },
    "closing": {
        "name": "Closing & Next Steps",
        "items": [
            {"id": "summary", "text": "Summarize key benefits and fit"},
            {"id": "ask_for_commitment", "text": "Ask for commitment or next step"},
            {"id": "schedule_followup", "text": "Schedule specific follow-up action"},
            {"id": "send_materials", "text": "Confirm materials to send"},
            {"id": "thank_them", "text": "Thank them for their time"},
        ]
    }
}


def detect_stage_from_text(text: str) -> str:
    """
    Detect current call stage from transcript text
    Supports multiple languages (English, Bahasa Indonesia)
    
    Args:
        text: Recent transcript text
        
    Returns:
        Stage name (greeting, discovery, presentation, objections, closing)
    """
    text_lower = text.lower()
    
    # Greeting indicators (English + Bahasa Indonesia)
    greeting_keywords = [
        'hello', 'hi', 'good morning', 'good afternoon', 'nice to meet',
        'thank you for joining', 'thanks for taking the time', 'do you have time',
        'halo', 'hai', 'selamat pagi', 'selamat siang', 'senang bertemu',
        'terima kasih sudah', 'apakah ada waktu', 'perkenalkan'
    ]
    
    # Discovery indicators (English + Bahasa Indonesia)
    discovery_keywords = [
        'tell me about', 'what are you currently', 'what challenges',
        'what\'s your biggest', 'how do you currently', 'what would you like',
        'what are your goals', 'who else', 'what\'s your timeline', 'budget',
        'ceritakan', 'apa yang', 'tantangan', 'kesulitan', 'tujuan',
        'siapa lagi', 'kapan', 'anggaran', 'kebutuhan', 'masalah'
    ]
    
    # Presentation indicators (English + Bahasa Indonesia)
    presentation_keywords = [
        'let me show you', 'i\'d like to demonstrate', 'our platform',
        'this feature', 'you can see', 'what this does', 'for example',
        'case study', 'other clients',
        'saya tunjukkan', 'saya demonstrasikan', 'platform kami',
        'fitur ini', 'bisa lihat', 'ini berfungsi', 'contohnya',
        'studi kasus', 'klien lain'
    ]
    
    # Objection indicators (English + Bahasa Indonesia)
    objection_keywords = [
        'too expensive', 'too costly', 'can\'t afford', 'price',
        'don\'t have time', 'already using', 'competitor', 'not sure',
        'need to think', 'risky', 'concern', 'but', 'however',
        'terlalu mahal', 'tidak mampu', 'harga', 'mahal',
        'tidak ada waktu', 'sudah pakai', 'kompetitor', 'tidak yakin',
        'harus mikir', 'risiko', 'khawatir', 'tapi', 'namun'
    ]
    
    # Closing indicators (English + Bahasa Indonesia)
    closing_keywords = [
        'next steps', 'move forward', 'get started', 'when can we',
        'follow up', 'send you', 'agreement', 'contract', 'onboarding',
        'thank you', 'great talking',
        'langkah selanjutnya', 'lanjut', 'mulai', 'kapan bisa',
        'tindak lanjut', 'kirim', 'perjanjian', 'kontrak',
        'terima kasih', 'senang ngobrol'
    ]
    
    # Score each stage
    scores = {
        'greeting': sum(1 for kw in greeting_keywords if kw in text_lower),
        'discovery': sum(1 for kw in discovery_keywords if kw in text_lower),
        'presentation': sum(1 for kw in presentation_keywords if kw in text_lower),
        'objections': sum(1 for kw in objection_keywords if kw in text_lower),
        'closing': sum(1 for kw in closing_keywords if kw in text_lower),
    }
    
    # Get stage with highest score
    max_stage = max(scores.items(), key=lambda x: x[1])
    
    # Default to discovery if no clear signal
    if max_stage[1] == 0:
        return 'discovery'
    
    return max_stage[0]


def check_checklist_item(item_id: str, text: str) -> bool:
    """
    Check if a checklist item has been addressed in the text
    Supports multiple languages (English, Bahasa Indonesia)
    
    STRICT MODE: Requires multiple keywords or strong context clues
    (not just one keyword occurrence)
    
    Args:
        item_id: Checklist item ID
        text: Transcript text
        
    Returns:
        True if item appears to be addressed (strict matching)
    """
    text_lower = text.lower()
    
    # Mapping of item IDs to keywords (English + Bahasa Indonesia)
    item_keywords = {
        # Greeting
        'intro_yourself': [
            'my name is', 'i\'m', 'calling from', 'with',
            'nama saya', 'perkenalkan', 'saya dari', 'dari perusahaan'
        ],
        'ask_availability': [
            'do you have', 'is this a good time', 'can we talk',
            'apakah ada waktu', 'ada waktu', 'bisa bicara', 'bisa ngobrol'
        ],
        'set_agenda': [
            'today we\'ll', 'i\'d like to', 'agenda', 'plan is',
            'hari ini kita akan', 'saya ingin', 'agendanya', 'rencananya'
        ],
        'build_rapport': [
            'how are you', 'how\'s your day', 'weather', 'weekend',
            'apa kabar', 'bagaimana kabarnya', 'gimana kabarnya', 'cuaca'
        ],
        
        # Discovery - require MORE keywords for detection
        'current_situation': [
            'currently', 'right now', 'at the moment', 'today', 'today',
            'saat ini', 'sekarang', 'kondisi sekarang', 'situasi sekarang'
        ],
        'pain_points': [
            'challenge', 'problem', 'difficult', 'struggle', 'pain', 'issue',
            'tantangan', 'masalah', 'kesulitan', 'kendala', 'hambatan'
        ],
        'goals': [
            'goal', 'want to', 'would like to', 'hoping to', 'achieve', 'target',
            'tujuan', 'ingin', 'mau', 'harapan', 'berharap', 'mencapai'
        ],
        'decision_process': [
            'who else', 'decision', 'approval', 'stakeholder', 'involve',
            'siapa lagi', 'keputusan', 'persetujuan', 'yang terlibat'
        ],
        'budget_timeline': [
            'budget', 'timeline', 'when', 'cost', 'price',
            'anggaran', 'biaya', 'harga', 'kapan', 'waktu'
        ],
        'stakeholders': [
            'team', 'who else', 'others', 'involved',
            'tim', 'siapa lagi', 'yang lain', 'terlibat'
        ],
        
        # Presentation
        'tailor_solution': [
            'based on what you said', 'specifically', 'for you', 'tailored',
            'berdasarkan yang anda bilang', 'khusus untuk', 'sesuai kebutuhan'
        ],
        'demo_key_features': [
            'let me show', 'feature', 'can do', 'allows you', 'here\'s',
            'saya tunjukkan', 'fitur', 'bisa', 'memungkinkan'
        ],
        'show_value': [
            'save', 'benefit', 'value', 'roi', 'return', 'advantage',
            'hemat', 'manfaat', 'nilai', 'keuntungan', 'hasil'
        ],
        'provide_examples': [
            'example', 'case study', 'other client', 'customer',
            'contoh', 'studi kasus', 'klien lain', 'pelanggan'
        ],
        'check_understanding': [
            'make sense', 'questions', 'clear', 'understand',
            'jelas', 'paham', 'mengerti', 'ada pertanyaan'
        ],
        
        # Objections
        'address_price': [
            'price', 'cost', 'expensive', 'afford', 'investment', 'budget',
            'harga', 'biaya', 'mahal', 'terlalu mahal', 'investasi'
        ],
        'address_time': [
            'time', 'implementation', 'setup', 'onboard', 'schedule',
            'waktu', 'implementasi', 'tidak ada waktu', 'sibuk'
        ],
        'address_competition': [
            'compare', 'versus', 'different', 'alternative', 'better',
            'bandingkan', 'dibanding', 'beda', 'alternatif', 'kompetitor'
        ],
        'address_risks': [
            'risk', 'concern', 'worry', 'guarantee', 'support', 'help',
            'risiko', 'khawatir', 'jaminan', 'garansi', 'dukungan'
        ],
        'confirm_resolution': [
            'feel better', 'resolved', 'addressed', 'comfortable', 'good',
            'terselesaikan', 'teratasi', 'nyaman', 'baik-baik saja'
        ],
        
        # Closing
        'summary': [
            'so to summarize', 'in summary', 'recap', 'sum up',
            'jadi kesimpulannya', 'ringkasnya', 'ikhtisar'
        ],
        'ask_for_commitment': [
            'shall we', 'can we', 'can i send', 'can i set up', 'next step',
            'bisa kita', 'boleh saya', 'langkah berikutnya'
        ],
        'schedule_followup': [
            'schedule', 'calendar', 'next week', 'when', 'date', 'time',
            'jadwalkan', 'kalender', 'minggu depan', 'kapan'
        ],
        'send_materials': [
            'send', 'email', 'document', 'proposal', 'information',
            'kirim', 'email', 'dokumen', 'proposal', 'informasi'
        ],
        'thank_them': [
            'thank you', 'thanks', 'appreciate', 'grateful',
            'terima kasih', 'makasih', 'appreciate', 'berterima kasih'
        ],
    }
    
    if item_id not in item_keywords:
        return False
    
    keywords = item_keywords[item_id]
    
    # Count how many keywords are found in text
    keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
    
    # STRICT MODE: Require at least 2 keyword matches (not just 1)
    # This prevents false positives like "good" matching "how are you"
    min_required_matches = 2 if len(keywords) > 5 else 1
    
    return keyword_matches >= min_required_matches


def generate_next_step_recommendation(
    stage: str,
    checklist_progress: Dict[str, bool],
    client_info: Dict
) -> str:
    """
    Generate next step recommendation based on current stage and progress
    
    Args:
        stage: Current call stage
        checklist_progress: Dict of completed checklist items
        client_info: Client insight data
        
    Returns:
        Recommendation text
    """
    stage_recommendations = {
        'greeting': [
            "Build rapport with genuine small talk",
            "Set clear agenda for the call",
            "Confirm they have enough time to talk",
            "Transition to discovery: 'Tell me about your current situation...'"
        ],
        'discovery': [
            "Ask open-ended questions about pain points",
            "Listen actively and take notes on their challenges",
            "Probe deeper: 'Can you tell me more about...'",
            "Identify budget and timeline early",
            "Uncover all stakeholders involved in decision"
        ],
        'presentation': [
            "Connect features directly to their stated pain points",
            "Use specific examples relevant to their industry",
            "Show, don't tell - demo the key features",
            "Check understanding frequently: 'Does this make sense?'",
            "Emphasize ROI and tangible benefits"
        ],
        'objections': [
            "Acknowledge their concern without being defensive",
            "Ask clarifying questions to understand the real objection",
            "Provide evidence: case studies, testimonials, data",
            "Reframe: show how solution addresses the concern",
            "Confirm resolution before moving on"
        ],
        'closing': [
            "Summarize key benefits and fit with their needs",
            "Ask confidently for next step or commitment",
            "Create urgency with specific timeline or offer",
            "Schedule concrete follow-up action with date/time",
            "End with clear mutual agreement on next steps"
        ]
    }
    
    recommendations = stage_recommendations.get(stage, stage_recommendations['discovery'])
    
    # Find first uncompleted item in current stage
    stage_items = SALES_CHECKLIST.get(stage, {}).get('items', [])
    for item in stage_items:
        if not checklist_progress.get(item['id'], False):
            return f"📍 {item['text']}: {recommendations[0]}"
    
    # If all items in current stage done, suggest moving to next
    stage_order = ['greeting', 'discovery', 'presentation', 'objections', 'closing']
    current_idx = stage_order.index(stage) if stage in stage_order else 1
    
    if current_idx < len(stage_order) - 1:
        next_stage = stage_order[current_idx + 1]
        return f"✅ {SALES_CHECKLIST[stage]['name']} complete. Move to {SALES_CHECKLIST[next_stage]['name']}"
    
    return recommendations[0]


def get_checklist_structure() -> Dict:
    """Get the full checklist structure"""
    return SALES_CHECKLIST

