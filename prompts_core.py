# -*- coding: utf-8 -*-
"""
النواة المشتركة لبرنامج البرومات (prompts_core.py)
يحتوي على: إدارة البيانات، محرك البحث العربي المطوّر، الترجمة الآلية، الشرح الذكي، والتحسين لنماذج الذكاء الاصطناعي.
يعتمد بالكامل على مكتبات بايثون القياسية دون الحاجة لتثبيت أي حزم خارجية.
"""

import csv
import hashlib
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
CSV_PATH = BASE / "prompts.csv"
STORE_PATH = BASE / "prompts.json"
TMP_PATH = BASE / "prompts_new.tmp.csv"

RAW_URLS = [
    "https://raw.githubusercontent.com/f/prompts.chat/main/prompts.csv",
    "https://cdn.jsdelivr.net/gh/f/prompts.chat@main/prompts.csv",
    "https://prompts.chat/prompts.csv",
]

# قاموس التصنيفات مع الكلمات الدلالية
CATEGORIES = [
    ("إنشاء فيديو", ["video generation", "video prompt", "cinematic", "sora", "veo",
                     "runway", "storyboard", "short film", "youtube video", "video script", "animation"]),
    ("إنشاء صورة", ["image generation", "image prompt", "photo", "picture", "illustration",
                    "logo", "poster", "infographic", "gpt-image", "midjourney", "flux", "dalle", "drawing"]),
    ("برمجة وتطوير", ["code", "coding", "developer", "programmer", "python", "javascript",
                      "sql", "api", "devops", "html", "css", "react", "git", "debug", "software",
                      "backend", "frontend", "fullstack", "docker", "terminal", "linux", "algorithm"]),
    ("كتابة ومحتوى", ["write", "writer", "writing", "blog", "article", "copywriter",
                      "content", "poet", "story", "novel", "screenwriting", "journalist", "essay"]),
    ("تسويق ومبيعات", ["marketing", "seo", "advertising", "sales", "brand", "social media",
                       "copywriting", "leads", "product manager", "campaign", "email marketing", "ads"]),
    ("تعليم وتدريب", ["tutor", "teacher", "teaching", "lecturer", "educational", "school",
                      "student", "exam", "quiz", "learn", "course", "instructor", "academician"]),
    ("أعمال وإدارة", ["business", "manager", "management", "entrepreneur", "startup",
                      "accounting", "finance", "investment", "recruiter", "hr", "meeting",
                      "project", "consultant", "customer success", "strategy"]),
    ("صحة وتغذية", ["doctor", "medical", "dietitian", "nutrition", "fitness", "personal trainer",
                    "psychologist", "mental health", "nurse", "dental", "therapy"]),
    ("ترجمة ولغات", ["translator", "translation", "paraphraser", "grammar", "bilingual",
                     "interpret", "spellcheck", "summarize", "language"]),
    ("تصميم وواجهات", ["design", "ui", "ux", "css", "web design", "typography",
                       "designer", "architect", "creative", "interior", "figma"]),
    ("توظيف ومقابلات", ["interview", "resume", "cv", "cover letter", "recruiter", "career",
                        "salary", "job", "hiring", "applicant"]),
    ("أخرى", []),
]

# النماذج المدعومة في أداة التحسين
MODELS = {
    "ChatGPT / GPT-4o": "chatgpt",
    "Claude (Anthropic)": "claude",
    "Gemini (Google)": "gemini",
    "DeepSeek": "deepseek",
    "موديل عام / آخر": "generic",
}

# كلمات التوقف باللغتين
STOP_WORDS = {
    "a", "an", "the", "of", "for", "to", "and", "or", "in", "on", "with", "is", "are",
    "be", "i", "my", "me", "you", "can", "please", "want", "make", "that", "this", "it",
    "في", "على", "من", "الى", "إلى", "عن", "مع", "أريد", "اريد", "قم", "أنشئ", "انشئ",
    "اعمل", "أعمل", "كن", "تكون", "يكون", "لي", "كيف", "ما", "هل", "هذا", "هذه", "التي", "الذي",
}

# القاموس المرجعي الموسّع للترجمة التقنية والعامة (عربي -> إنجليزي)
RAW_AR_EN = {
    "مبرمج": ["developer", "programmer", "coding", "software engineer"],
    "مطور": ["developer", "programmer", "engineer"],
    "تطبيق": ["application", "app", "build", "mobile app"],
    "تطبيقات": ["applications", "apps"],
    "موقع": ["website", "web", "landing page"],
    "مواقع": ["websites", "web"],
    "برمجة": ["coding", "programming", "software", "development"],
    "كود": ["code", "coding", "software", "script"],
    "مشروع": ["project"],
    "بيانات": ["data", "database", "sql"],
    "قواعد بيانات": ["database", "sql", "nosql", "postgres"],
    "روبوت": ["bot", "robot", "agent"],
    "بوت": ["bot", "agent"],
    "ذكاء": ["ai", "machine learning", "artificial", "llm"],
    "اصطناعي": ["artificial intelligence", "ai"],
    "أمان": ["security", "cybersecurity", "hacker", "pentest"],
    "حماية": ["security", "cybersecurity", "protection"],
    "اختراق": ["hacker", "pentesting", "security", "exploit"],
    "تصميم": ["design", "ui", "ux", "css", "designer"],
    "واجهة": ["ui", "frontend", "interface"],
    "واجهات": ["ui", "ux", "frontend", "interfaces"],
    "متصفح": ["browser", "web"],
    "تسويق": ["marketing", "seo", "advertising", "growth"],
    "إعلان": ["advertising", "ad", "copywriting"],
    "اعلانات": ["advertising", "ads"],
    "كتابة": ["writing", "copywriting", "content", "writer"],
    "محرر": ["editor", "proofreader", "writer"],
    "مقال": ["article", "blog", "writing", "essay"],
    "مقالات": ["articles", "blogs", "essays"],
    "قصة": ["story", "writing", "fiction", "novel"],
    "رواية": ["novel", "story", "fiction"],
    "مترجم": ["translator", "translation", "interpret"],
    "ترجمة": ["translation", "translator"],
    "لغة": ["language", "linguistic", "translation"],
    "لغات": ["languages", "translation"],
    "إنجليزي": ["english"],
    "انجليزي": ["english"],
    "عربي": ["arabic"],
    "تحسين": ["optimize", "optimizer", "refactoring", "improve"],
    "تسريع": ["speed", "performance", "optimize"],
    "سرعة": ["optimize", "performance", "fast"],
    "طبيب": ["doctor", "medical", "physician"],
    "دكتور": ["doctor", "medical"],
    "صحة": ["health", "medical"],
    "علاج": ["treatment", "therapy", "doctor"],
    "تغذية": ["diet", "nutrition", "dietitian"],
    "لياقة": ["fitness", "workout", "trainer"],
    "سكربت": ["script", "automation", "python"],
    "بايثون": ["python"],
    "جافا": ["java", "javascript"],
    "تدريس": ["tutor", "teacher", "teaching"],
    "معلم": ["teacher", "tutor", "instructor"],
    "مدرس": ["teacher", "tutor"],
    "استاذ": ["professor", "lecturer", "teacher"],
    "طالب": ["student", "learner"],
    "امتحان": ["exam", "test", "quiz"],
    "اختبار": ["test", "quiz", "assess"],
    "إيميل": ["email", "newsletter"],
    "ايميل": ["email"],
    "بريد": ["email", "letter"],
    "رسالة": ["message", "letter", "email"],
    "عقد": ["contract", "legal", "lawyer"],
    "قانون": ["lawyer", "legal", "attorney"],
    "محامي": ["lawyer", "legal", "attorney"],
    "خبير": ["expert", "specialist", "consultant"],
    "مستشار": ["consultant", "advisor", "expert"],
    "محلل": ["analyst", "analysis"],
    "تحليل": ["analysis", "analyze", "analyst"],
    "هندسة": ["engineer", "architecture"],
    "مهندس": ["engineer"],
    "شعر": ["poetry", "poet"],
    "شاعر": ["poet", "poetry"],
    "دعم": ["support", "helpdesk", "customer service"],
    "خدمة عملاء": ["customer support", "customer service"],
    "شرح": ["explain", "explanation", "tutor"],
    "تلخيص": ["summarize", "summary", "digest"],
    "ملخص": ["summarize", "summary"],
    "سيرفر": ["server", "devops", "linux", "cloud"],
    "سيرفرات": ["servers", "devops"],
    "لينكس": ["linux", "terminal", "bash"],
    "محاسب": ["accountant", "accounting", "finance"],
    "محاسبة": ["accounting", "finance"],
    "مالية": ["finance", "financial", "accounting"],
    "رياضيات": ["math", "mathematics"],
    "شطرنج": ["chess"],
    "توظيف": ["recruiter", "hiring", "interview", "hr"],
    "مقابلة": ["interview", "interviewer"],
    "وظيفة": ["job", "career", "employment", "resume"],
    "سيرة ذاتية": ["resume", "cv", "cover letter"],
    "سيرة": ["resume", "cv"],
    "فكرة": ["idea", "creative", "brainstorm"],
    "افكار": ["ideas", "brainstorm", "creative"],
    "متجر": ["shop", "store", "ecommerce"],
    "تقرير": ["report", "reporting"],
    "فيديو": ["video", "cinematic", "youtube", "animation"],
    "صورة": ["image", "photo", "picture", "illustration", "logo"],
    "صور": ["images", "photos", "pictures"],
    "رسم": ["drawing", "artist", "illustrator"],
    "لعبة": ["game", "gamer", "gaming"],
    "ألعاب": ["games", "gaming"],
    "موسيقى": ["music", "composer", "melody"],
    "استثمار": ["investment", "invest", "trading", "stocks"],
    "أسهم": ["stocks", "finance", "trading"],
    "تداول": ["trading", "stocks", "crypto"],
    "مساعد": ["assistant", "helper", "copilot"],
    "وكيل": ["agent", "assistant"],
    "تعديل": ["edit", "proofreading", "modify"],
    "شيف": ["chef", "cooking", "recipes"],
    "طعام": ["food", "cooking", "recipe"],
    "طبخ": ["cooking", "chef"],
    "مطبخ": ["kitchen", "cooking"],
    "عقار": ["real estate", "property"],
    "اجتماع": ["meeting", "agenda"],
    "تعلم": ["learning", "tutor", "education"],
    "دروس": ["lesson", "tutor", "course"],
    "دورة": ["course", "tutorial"],
    "شركة": ["company", "business", "corporate", "startup"],
    "مشاكل": ["troubleshoot", "debug", "issues"],
    "مشكلة": ["problem", "issue", "bug"],
    "حل": ["solution", "solve", "fix"],
    "أخطاء": ["errors", "bugs", "debugging"],
    "خطأ": ["error", "bug", "debug"],
    "تصحيح": ["debug", "correction", "fix"],
    "توثيق": ["documentation", "docs", "technical writing"],
    "مستند": ["document", "documentation"],
    "منتج": ["product", "product manager"],
    "عميل": ["customer", "client", "customer success"],
    "مبيعات": ["sales", "seller"],
    "شحن": ["shipping", "logistics"],
    "سفر": ["travel", "trip", "tourist"],
    "سياحة": ["tourism", "travel", "guide"],
    "سيارة": ["car", "automotive"],
    "طفل": ["kid", "children", "parenting"],
    "أطفال": ["children", "kids"],
    "جامعة": ["university", "college", "academic"],
    "خطاب": ["letter", "speech", "cover letter"],
    "منشور": ["post", "social media", "tweet"],
    "تواصل": ["social media", "communication"],
    "انستقرام": ["instagram", "social media"],
    "تويتر": ["twitter", "x", "social media"],
    "يوتيوب": ["youtube", "video"],
    "شبكة": ["network", "networking"],
    "شبكات": ["networks", "networking"],
    "خوارزمية": ["algorithm", "data structure"],
    "خوارزميات": ["algorithms"],
    "خطة": ["plan", "planner", "strategy"],
    "جدول": ["table", "schedule", "calendar"],
    "مواعيد": ["schedule", "appointments"],
    "سياسة": ["policy", "politician", "diplomat"],
    "تنظيم": ["organize", "planner", "productivity"],
    "روتين": ["routine", "daily", "habit"],
    "بودكاست": ["podcast", "audio"],
    "سعر": ["price", "pricing"],
    "أسعار": ["pricing", "cost"],
}


# ==============================================================================
# معالجة وتطبيع النصوص العربية (Arabic NLP Normalization)
# ==============================================================================

def normalize_arabic(text: str) -> str:
    """
    تطبيع وتجريد النصوص العربية من التشكيل والهمزات والزوائد الصوتية
    لضمان دقة البحث والمطابقة مهما كانت صياغة المستخدم.
    """
    if not text:
        return ""
    # إزالة التشكيل والتنوين والشدّة والتطويل (الكشيدة)
    text = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", text)
    # توحيد كافة أشكال الألف إلى الألف البسيطة 'ا'
    text = re.sub(r"[إأآٱ]", "ا", text)
    # توحيد الياء المقصورة 'ى' إلى 'ي'
    text = re.sub(r"ى", "ي", text)
    # توحيد التاء المربوطة 'ة' إلى 'ه' لتطابق الصيغ المتنوعة
    text = re.sub(r"ة", "ه", text)
    return text.lower().strip()


def strip_arabic_prefixes(word: str) -> list[str]:
    """
    استخراج الكلمة الأصلية بعد تجريد سوابق اللغة العربية الشائعة:
    - أداة التعريف (الـ)
    - واو وفاء العطف (و، ف)
    - حروف الجر المتصلة (ب، ل، ك)
    """
    variants = [word]
    # إزالة أداة التعريف "ال" إذا كانت الكلمة أطول من 3 حروف
    if word.startswith("ال") and len(word) > 3:
        stem = word[2:]
        variants.append(stem)
        # إزالة زوائد ما بعد 'ال'
        if len(stem) > 3:
            variants.append(stem)

    # إزالة واو العطف "و" في بداية الكلمة
    if word.startswith("و") and len(word) > 3:
        w_stem = word[1:]
        variants.append(w_stem)
        if w_stem.startswith("ال") and len(w_stem) > 3:
            variants.append(w_stem[2:])

    # إزالة باء أو لام أو كاف الجر (بالـ، للـ، كالـ، بـ، لـ)
    for prefix in ("بال", "لل", "كال"):
        if word.startswith(prefix) and len(word) > 4:
            variants.append(word[len(prefix):])

    return list(dict.fromkeys(variants))


# بناء قاموس المعالجة الموحّد بنسخة مطبعة
_NORMALIZED_AR_EN = {}
for _k, _v in RAW_AR_EN.items():
    _norm_k = normalize_arabic(_k)
    if _norm_k not in _NORMALIZED_AR_EN:
        _NORMALIZED_AR_EN[_norm_k] = []
    for _val in _v:
        if _val not in _NORMALIZED_AR_EN[_norm_k]:
            _NORMALIZED_AR_EN[_norm_k].append(_val)


def expand_query(query: str) -> set[str]:
    """
    توسيع استعلام البحث العربي والإنجليزي، وتوليد كافة الكلمات المفتاحية
    والمرادفات الممكنة بعد التطبيع وفك السوابق.
    """
    raw_words = re.findall(r"[\w\u0621-\u064A#+]+", query.lower())
    terms = set()

    for w in raw_words:
        if w in STOP_WORDS or len(w) < 2:
            continue
        terms.add(w)

        # فحص الكلمة الأصلية
        norm_w = normalize_arabic(w)
        if norm_w in STOP_WORDS or len(norm_w) < 2:
            continue
        terms.add(norm_w)

        # استخراج المرادفات من القاموس لكافة تصريفات الكلمة
        variants = strip_arabic_prefixes(norm_w)
        for var in variants:
            terms.add(var)
            if var in _NORMALIZED_AR_EN:
                for target_term in _NORMALIZED_AR_EN[var]:
                    for sub in target_term.lower().split():
                        terms.add(sub)

    return terms


# ==============================================================================
# تصنيف وتشفير البرومات
# ==============================================================================

def key_of(act: str, prompt: str) -> str:
    """توليد مفتاح تجزئة مميز (MD5) للبرومبت لتتبعه دون تكرار."""
    return hashlib.md5((act.strip() + "\x00" + prompt.strip()).encode("utf-8")).hexdigest()


def classify_prompt(p: dict) -> str:
    """تصنيف البرومبت آلياً حسب محتواه ودوره."""
    if p.get("type") == "IMAGE":
        return "إنشاء صورة"
    text = (p.get("act", "") + " " + p.get("prompt", "")).lower()
    order = [
        "إنشاء فيديو", "إنشاء صورة", "برمجة وتطوير", "ترجمة ولغات",
        "صحة وتغذية", "توظيف ومقابلات", "تعليم وتدريب", "أعمال وإدارة",
        "تسويق ومبيعات", "تصميم وواجهات", "كتابة ومحتوى",
    ]
    rules = dict(CATEGORIES)
    for name in order:
        if any(k in text for k in rules.get(name, [])):
            return name
    return "أخرى"


def tokenize_prompt(p: dict) -> None:
    """توليد الكلمات المفتاحية المهيأة للفهرسة السريعة داخل البرومبت."""
    text = (p.get("act", "") + " " + p.get("prompt", "")).lower()
    p["tokens"] = set(re.findall(r"[a-z0-9#+]+", text))
    p["act_low"] = p.get("act", "").lower()


# ==============================================================================
# تقييم ومطابقة الاستعلام (Search Scoring Engine)
# ==============================================================================

def score_prompt(p: dict, terms: set[str]) -> int:
    """
    حساب درجة التطابق بين البرومبت وكلمات البحث مع إعطاء وزن مضاعف
    للتطابق في اسم الدور (Act).
    """
    score = 0
    act_low = p.get("act_low", "")
    tokens = p.get("tokens", set())

    for t in terms:
        if t in act_low:
            score += 6
        elif t in tokens:
            score += 3
        elif len(t) >= 4:
            # مطابقة البدايات (Prefix Matching) للكلمات المركبة والجمع
            for tk in tokens:
                if len(tk) >= 4 and (tk.startswith(t) or t.startswith(tk)):
                    score += 2
                    break
    return score


def search_prompts(prompts: list[dict], query: str, devs_only: bool = False,
                   category_filter: str | None = None) -> list[tuple[int, dict]]:
    """البحث في مصفوفة البرومات مع تطبيق الفلاتر والترتيب حسب أفضل مطابقة."""
    query = query.strip()
    target_list = prompts

    if devs_only:
        target_list = [p for p in target_list if p.get("for_devs")]

    if category_filter and category_filter != "all":
        target_list = [p for p in target_list if p.get("category") == category_filter]

    if not query:
        return [(0, p) for p in target_list]

    terms = expand_query(query)
    scored = []
    for p in target_list:
        s = score_prompt(p, terms)
        if s > 0:
            scored.append((s, p))

    scored.sort(key=lambda item: -item[0])
    return scored


# ==============================================================================
# إدارة المتغيرات التفاعلية (Interactive Template Variables)
# ==============================================================================

def extract_variables(prompt_text: str) -> list[dict]:
    """
    استخراج المتغيرات المحصورة بصيغة ${VariableName:DefaultValue} أو ${VariableName}
    المستخدمة بكثرة في مكتبة prompts.chat.
    """
    pattern = r"\$\{([^}]+)\}"
    matches = re.findall(pattern, prompt_text)
    variables = []
    seen = set()

    for m in matches:
        if m in seen:
            continue
        seen.add(m)
        parts = m.split(":", 1)
        name = parts[0].strip()
        default = parts[1].strip() if len(parts) > 1 else ""
        variables.append({
            "raw": f"${{{m}}}",
            "name": name,
            "default": default,
        })
    return variables


def substitute_variables(prompt_text: str, values: dict[str, str]) -> str:
    """استبدال المتغيرات بقيم المستخدم المحددة."""
    res = prompt_text
    for raw_tag, val in values.items():
        res = res.replace(raw_tag, val)
    return res


# ==============================================================================
# محرك الترجمة الفورية إلى العربية (Zero-Install Auto-Translation)
# ==============================================================================

_TRANSLATION_CACHE: dict[str, str] = {}


def translate_to_arabic(text: str, timeout: int = 8) -> str:
    """
    ترجمة نص البرومبت إلى العربية بشكل آمن وفوري عبر واجهة Google Translate
    باستخدام مكتبة urllib القياسية دون الحاجة لأي مكتبات خارجية.
    يتضمن نظام تخزين مؤقت (In-Memory Cache) لمنع تكرار الطلبات عبر الشبكة.
    """
    text = text.strip()
    if not text:
        return ""
    if text in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[text]

    # تقسيم النص الطويل إلى فقرات لتفادي قيود الطول
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    if not chunks:
        chunks = [text]

    translated_chunks = []
    base_url = "https://translate.googleapis.com/translate_a/single"

    for chunk in chunks:
        # إذا كانت الفقرة قصيرة جداً (مثل متغير أو رمز)
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "ar",
            "dt": "t",
            "q": chunk,
        }
        encoded_url = base_url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            encoded_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode("utf-8")
                parsed = json.loads(data)
                # تجميع أجزاء الترجمة
                chunk_result = "".join([segment[0] for segment in parsed[0] if segment and segment[0]])
                translated_chunks.append(chunk_result)
        except Exception as e:
            # في حال عدم وجود اتصال أو حدوث خطأ
            return f"[تعذرت الترجمة الآلية: تأكد من الاتصال بالإنترنت ({type(e).__name__})]\n\nالنص الأصلي:\n{text}"

    final_translation = "\n\n".join(translated_chunks)
    _TRANSLATION_CACHE[text] = final_translation
    return final_translation


# ==============================================================================
# مولد الشرح الذكي عالي الدقة للبرومات (High-Precision Arabic Explainer)
# ==============================================================================

_HEADLINE_CACHE: dict[str, str] = {}


def generate_precise_headline(p: dict) -> str:
    """
    توليد عنوان وصفي عالي الدقة ومباشر للبرومبت باللغة العربية
    يوضح الموضوع الفعلي والمهمة بدقة متناهية (مثل: برومبت لإنشاء فيديو لسيارة عند الغروب).
    """
    key = p.get("key", "")
    if key and key in _HEADLINE_CACHE:
        return _HEADLINE_CACHE[key]

    act = p.get("act", "").strip()
    prompt = p.get("prompt", "").strip()
    cat = p.get("category", "أخرى")
    p_type = p.get("type", "TEXT")
    p_low = prompt.lower()
    clean = re.sub(r"\$\{([^:}]+)(?::([^}]*))?\}", r"\1", prompt)
    clean = re.sub(r"\s+", " ", clean).strip()

    headline = ""

    # 1. إنشاء فيديو (مشاهد، رسوم متحركة، سينمائي)
    if cat == "إنشاء فيديو" or "video" in p_low or ("cinematic" in p_low and any(k in p_low for k in ["drone", "shot", "footage", "clip", "render"])):
        cleaned_visual = re.sub(
            r"^(?:a cinematic (?:drone )?video of|a video of|footage of|generate a video of|create a video of|video prompt:?|cinematic shot of|slow-motion video of)\s+",
            "", clean, flags=re.I
        )
        parts = [s.strip() for s in re.split(r"[\.\n,]", cleaned_visual) if len(s.strip()) > 3]
        subject = ", ".join(parts[:3]) if parts else cleaned_visual[:120]
        trans_subject = translate_to_arabic(subject)
        headline = f"برومبت لإنشاء فيديو لـ {trans_subject}"

    # 2. إنشاء صورة، تصوير، شعارات، ثلاثي الأبعاد
    elif p_type == "IMAGE" or cat == "إنشاء صورة" or any(k in p_low for k in ["photo of", "image of", "illustration of", "logo for", "portrait of", "vector design", "concept art"]):
        cleaned_visual = re.sub(
            r"^(?:a photo of|an image of|illustration of|a portrait of|a high-angle view of|generate an image of|create a photo of|logo for|vector illustration of)\s+",
            "", clean, flags=re.I
        )
        parts = [s.strip() for s in re.split(r"[\.\n,]", cleaned_visual) if len(s.strip()) > 3]
        subject = ", ".join(parts[:3]) if parts else cleaned_visual[:120]
        trans_subject = translate_to_arabic(subject)
        headline = f"برومبت لإنشاء صورة لـ {trans_subject}"

    # 3. الأدوار والمساعدين ومحاكاة النظم (مثل Terminal, Interviewer, Developer)
    else:
        m = re.search(r"^(?:I want you to act as (?:an?|the)|Imagine you are (?:an?|the)|Act as (?:an?|the))\s+([^.]+)\.\s*(.*)", clean, re.I)
        if m:
            role = m.group(1).strip()
            rest = m.group(2).strip()
            sentences = [s.strip() for s in re.split(r"[\.\n]", rest) if len(s.strip()) > 8]
            task = sentences[0] if sentences else role
            task = re.sub(r"^(?:I will|Your task is to|The objective is to|You will|Please)\s+", "", task, flags=re.I)
            trans_task = translate_to_arabic(task[:130])
            trans_role = translate_to_arabic(role)
            headline = f"برومبت للعمل كـ {trans_role}: {trans_task}"
        else:
            sentences = [s.strip() for s in re.split(r"[\.\n]", clean) if len(s.strip()) > 8]
            first = sentences[0] if sentences else act
            trans_first = translate_to_arabic(first[:130])
            headline = f"برومبت لـ {trans_first}"

    headline = headline.replace("\n", " ").strip()
    if key:
        _HEADLINE_CACHE[key] = headline
    return headline


def explain_prompt_arabic(p: dict, headline: str | None = None) -> str:
    """
    تحليل البرومبت آلياً وتوليد شرح هيكلي عالي الدقة باللغة العربية يوضح:
    - التوصيف الدقيق المباشر لموضوع ومهمة البرومبت (مثل: برومبت لإنشاء فيديو لسيارة عند الغروب)
    - طبيعة المخرجات وأسلوب عمل الذكاء الاصطناعي
    - القواعد والقيود الصارمة المفروضة على النموذج
    - المتغيرات التفاعلية المطلوبة
    - نصائح الاستخدام للحصول على أفضل استجابة
    """
    act = p.get("act", "")
    prompt = p.get("prompt", "")
    category = p.get("category", "أخرى")
    prompt_low = prompt.lower()
    key = p.get("key", "")

    # جلب العنوان الدقيق إن وُجد في الذاكرة المؤقتة أو استخدام العنوان الممرر
    if not headline:
        headline = _HEADLINE_CACHE.get(key)
    if not headline:
        # صياغة عنوان فوري سريع لحين اكتمال التحليل الدقيق
        if category == "إنشاء فيديو":
            headline = f"برومبت لإنشاء وتوليد فيديو سينمائي بالذكاء الاصطناعي ({act})"
        elif category == "إنشاء صورة" or p.get("type") == "IMAGE":
            headline = f"برومبت لإنشاء وتوليد صورة وتصميم بالذكاء الاصطناعي ({act})"
        else:
            headline = f"برومبت لتوجيه الذكاء الاصطناعي للعمل كـ {act} في سياق {category}"

    lines = []
    lines.append("🎯 **التوصيف الدقيق والمباشر للبرومبت:**")
    lines.append(f"👉 {headline}")
    lines.append("─" * 52)
    lines.append(f"📌 **الدور المسند:** {act}")
    lines.append(f"📂 **التصنيف:** {category}   |   **النوع:** {p.get('type', 'TEXT')}")
    lines.append("")

    # 1. طبيعة العمل والمخرجات
    lines.append("📋 **طبيعة العمل والمخرجات المتوقعة:**")
    if p.get("type") == "IMAGE" or category in ["إنشاء صورة", "إنشاء فيديو"]:
        lines.append("- يحدد بدقة العناصر البصرية للمشهد، زوايا الكاميرا والإضاءة والألوان لتوليد مخرجات فائقة الدقة والواقعية.")
    elif "terminal" in prompt_low or "console" in prompt_low:
        lines.append("- محاكاة بيئة سطر أوامر حقيقية، وتنفيذ أوامر النظام وعرض المخرجات الدقيقة فقط دون أي حوار جانبي.")
    elif "interviewer" in prompt_low:
        lines.append("- إجراء محاكاة مقابلة توظيف تفاعلية، يطرح فيها الأسئلة بالتتابع وينتظر إجابتك لتقييمك.")
    elif "translator" in prompt_low:
        lines.append("- ترجمة وتدقيق لغوي متقدم مع الارتقاء بالصياغة والمفردات إلى أسلوب أدبي واحترافي.")
    elif "developer" in prompt_low or "engineer" in prompt_low or "code" in prompt_low:
        lines.append("- تقمص دور مهندس برمجيات محترف لتقديم كود نظيف ومختبر ومعماريات برمجية مطابقة لأفضل المعايير.")
    else:
        lines.append(f"- يقدم استشارات وحلولاً متخصصة ومباشرة في مجال {category} استناداً إلى المعطيات التي تزوده بها.")

    # 2. القواعد والقيود المضمنة
    rules_detected = []
    if "do not write explanations" in prompt_low or "only reply" in prompt_low or "only code" in prompt_low:
        rules_detected.append("عدم كتابة أي مقدمات أو شروحات جانبية؛ إخراج المطلوب مباشرة.")
    if "one by one" in prompt_low or "wait for my answers" in prompt_low or "wait for my reply" in prompt_low:
        rules_detected.append("التفاعل خطوة بخطوة والسؤال تلو الآخر دون سرد الحوار كاملاً دفعة واحدة.")
    if "code block" in prompt_low:
        rules_detected.append("حصر المخرجات البرمجية داخل كتل كود منسقة وجاهزة للنسخ.")
    if "table" in prompt_low or "excel" in prompt_low or "json" in prompt_low:
        rules_detected.append("تنظيم البيانات والمخرجات في هيئة جداول أو هياكل بيانات محددة.")
    if "translate" in prompt_low:
        rules_detected.append("الالتزام بالترجمة الدقيقة مع مراعاة السياق وتصحيح الأخطاء اللغوية.")

    if rules_detected:
        lines.append("\n⚠️ **أهم الشروط والقيود المفروضة على النموذج:**")
        for r in rules_detected:
            lines.append(f"  • {r}")

    # 3. المتغيرات
    vars_list = extract_variables(prompt)
    if vars_list:
        lines.append("\n🧩 **المتغيرات المطلوب تعبئتها قبل البدء:**")
        for v in vars_list:
            def_str = f" (القيمة الافتراضية: {v['default']})" if v['default'] else ""
            lines.append(f"  • `{v['name']}`{def_str}")

    # 4. نصيحة الاستخدام
    lines.append("\n💡 **نصيحة للاستخدام الأمثل:**")
    if vars_list:
        lines.append("- انتقل إلى تبويب '🧩 المتغيرات التفاعلية' لتعبئة القيم بسهولة وتطبيقها بنقرة واحدة.")
    elif "my first sentence is" in prompt_low or "my first command is" in prompt_low:
        m = re.search(r'my first (?:sentence|command|request) is ["“\']?([^"”\']+)["“\']?', prompt_low)
        first_input = m.group(1).strip() if m else "المدخل الافتراضي"
        lines.append(f"- يبدأ البرومبت بأمر مقترح: `\"{first_input}\"`. استبدله بطلبك الخاص فوراً.")
    else:
        lines.append("- ضع هذا البرومبت في رسالة System أو كأول رسالة، ثم أرفق سياق طلبك المحدد مباشرة.")

    return "\n".join(lines)


# ==============================================================================
# أداة التحسين الذكي للنماذج (AI Prompt Enhancer)
# ==============================================================================

def build_enhanced_prompt(p: dict, model_key: str = "generic", language: str = "ar") -> str:
    """
    إعادة صياغة وهندسة البرومبت باحترافية ليناسب معايير وهياكل أفضل نماذج الذكاء الاصطناعي
    (مثل Claude XML tags، ChatGPT System/User separation، Gemini Chain-of-Thought، DeepSeek Step-by-Step).
    """
    act = p.get("act", "")
    prompt = p.get("prompt", "")

    if language == "en":
        # صياغة القالب بالإنجليزية بالكامل
        if model_key == "claude":
            tpl = (
                "<role>\n"
                f"You are an expert acting as: {act}\n"
                f"{prompt}\n"
                "</role>\n\n"
                "<context>\n"
                "(Provide your specific project background, domain constraints, or inputs here)\n"
                "</context>\n\n"
                "<instructions>\n"
                "1. Strictly adhere to the role definition and constraints specified above.\n"
                "2. If critical information is missing, ask one clarifying question before proceeding.\n"
                "3. Think step-by-step internally before producing the final response.\n"
                "4. Provide well-structured, production-ready output with clear sections.\n"
                "</instructions>\n\n"
                "<output_format>\n"
                "[Concise Title] -> [Main Output] -> [Next Actionable Steps]\n"
                "</output_format>"
            )
            return tpl
        else:
            sections = [
                f"# Role Definition\n{act}\n\n{prompt}",
                "# Context & Inputs\n(Paste your custom data, background, or requirements here)",
                "# Objectives\nApply the role and execute the tasks above effectively and thoroughly.",
                "# Operational Guidelines\n"
                "1. Adhere strictly to the defined role and rules.\n"
                "2. Maintain professional clarity, precision, and avoid hallucinations.\n"
                "3. Present the response with structured headers, bullet points, and clean formatting.",
                "# Expected Output\nSummary -> Detailed Execution -> Recommendations / Next Steps",
            ]
            if model_key == "chatgpt":
                sections.insert(0, "# System Message\nApply this role persona for all subsequent messages.")
            elif model_key == "gemini":
                sections.insert(0, "# Guidelines for Gemini\nThink through step-by-step before answering.")
            elif model_key == "deepseek":
                sections.insert(0, "# Reasoning Directive\nAnalyze requirements deeply and deliver verified answers.")
            return "\n\n".join(sections)

    # صياغة القالب بالعربية
    role_tail = {
        "chatgpt": "منظّم بصيغة Markdown، يُستخدم الدور كرسالة System ثم رسالة User بالطلب.",
        "claude": "الأقسام مغلّفة بأوسمة XML وفق أفضل ممارسات Anthropic Claude.",
        "gemini": "تعليمات واضحة خطوة بخطوة مع التأكيد على التفكير العميق والتنظيم.",
        "deepseek": "مُصمم للنماذج التحليلية والاستدلالية (Reasoning): تفكير تحليلي ثم إجابة دقيقة.",
        "generic": "قالب قياسي متوافق مع كافة نماذج الذكاء الاصطناعي الحديثة.",
    }.get(model_key, "قالب قياسي")

    if model_key == "claude":
        tpl = (
            f"<role>\n{act}\n{prompt}\n</role>\n\n"
            "<context>\n(ألحق هنا سياق طلبك الخاص: الموضوع، الجمهور، القيود، وأي بيانات)\n</context>\n\n"
            "<task>\nالمهمة: نفّذ الدور أعلاه بتطبيق كافة التعليمات على السياق الملحق.\n</task>\n\n"
            "<rules>\n"
            "1. التزم بالدور والقيود المحددة بدقة متناهية.\n"
            "2. اسأل عن أي معلومة ناقصة جوهرية قبل البدء (سؤال واحد محدد فقط).\n"
            "3. فكّر داخلياً خطوة بخطوة ثم قدّم النتيجة النهائية فقط بصياغة واضحة.\n"
            "4. اخرج نتيجة عملية جاهزة للاستخدام الفوري.\n"
            "</rules>\n\n"
            "<variables>\n- $input: مدخل المستخدم الأساسي\n- $format: صيغة الإخراج المفضلة\n</variables>\n\n"
            "<output>\nعنوان موجز ← المحتوى المطلوب بتنسيق احترافي ← قائمة 'الخطوات التالية المقترحة'\n</output>"
        )
        return tpl + f"\n\n---\nملاحظة توافق النموذج: {role_tail}"

    sections = [
        f"# الدور المتخصص\n{act}\n\n{prompt}",
        "# السياق والبيانات\n(ألحق هنا سياق طلبك الخاص: الموضوع، الجمهور المستهدف، القيود، وأي بيانات)",
        "# المهمة الأساسية\nنفّذ ما ورد في الدور أعلاه بدقة على السياق المعطى، وقدّم نتيجة عملية متكاملة.",
        "# القواعد والضوابط\n"
        "1. التزم بالدور والتعليمات المذكورة في نص البرومبت.\n"
        "2. فكّر أولاً خطوة بخطوة في أفضل صياغة وتنظيم.\n"
        "3. نسّق النتيجة باستخدام العناوين والقوائم البرمجية أو النقطية لسهولة القراءة.\n"
        "4. لا تختلق حقائق غير مؤكدة؛ وفي حال نقص معلومة أشر إلى الحاجة للتحقق.",
        "# المتغيرات\n- $input: مدخل المستخدم\n- $audience: الجمهور\n- $format: صيغة الإخراج",
        "# صيغة الإخراج المعتمدة\nعنوان رئيسي ← المحتوى التنفيذي المباشر ← خطوات تالية مقترحة",
    ]
    if model_key == "chatgpt":
        sections.insert(0, "# System Instruction\nاستخدم هذا النص كرسالة System، ثم وجّه طلبك في رسالة User.")
    elif model_key == "gemini":
        sections.insert(0, "# توجيه لنموذج Gemini\nاعمل خطوة بخطوة وقدّم استجابة عملية ومنظمة.")
    elif model_key == "deepseek":
        sections.insert(0, "# توجيه لنموذج DeepSeek\nحلّل المطلوب استدلالياً ثم استخرج الحل النهائي.")

    return "\n\n".join(sections) + f"\n\n---\nملاحظة توافق النموذج: {role_tail}"


# ==============================================================================
# إدارة مستودع البيانات وحفظ وتعديل البرومات (CRUD & Persistence)
# ==============================================================================

KEEP_KEYS = ("act", "prompt", "for_devs", "type", "key", "new", "added", "builtin", "category", "user_edited")


def load_csv_rows(path: Path) -> list[dict]:
    """قراءة ملف CSV الخاص بـ prompts.chat بأمان."""
    csv.field_size_limit(10 * 1024 * 1024)
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            act = (r.get("act") or "").strip()
            body = (r.get("prompt") or "").strip()
            if act and body:
                rows.append({
                    "act": act,
                    "prompt": body,
                    "for_devs": (r.get("for_devs") or "").upper() == "TRUE",
                    "type": (r.get("type") or "TEXT").strip() or "TEXT",
                })
    return rows


def prepare_row(r: dict) -> dict:
    """تجهيز وتصنيف وفهرسة سطر برومبت جديد."""
    if "key" not in r:
        r["key"] = key_of(r["act"], r["prompt"])
    if not r.get("category"):
        r["category"] = classify_prompt(r)
    tokenize_prompt(r)
    return r


def load_store() -> dict:
    """تحميل متجر البرومات والمفضلة من prompts.json مع تهيئة تلقائية إذا لم يتوفر."""
    if not STORE_PATH.exists():
        store = {"favorites": [], "prompts": []}
        rows = load_csv_rows(CSV_PATH)
        for r in rows:
            r["new"] = False
            r["added"] = 0
            r["builtin"] = True
            store["prompts"].append(prepare_row(r))
        save_store_sync(store)
        return store

    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        data = {"favorites": [], "prompts": []}

    for p in data.get("prompts", []):
        if not p.get("category"):
            p["category"] = classify_prompt(p)
        tokenize_prompt(p)
    return data


def save_store_sync(store: dict) -> None:
    """حفظ المتجر بأمان وبشكل فوري إلى ملف JSON."""
    data = {
        "favorites": store.get("favorites", []),
        "prompts": [{k: p.get(k) for k in KEEP_KEYS if k in p} for p in store.get("prompts", [])],
    }
    # الكتابة عبر ملف مؤقت لضمان سلامة البيانات من أي تلف مفاجئ
    tmp_out = STORE_PATH.with_suffix(".tmp.json")
    tmp_out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_out.replace(STORE_PATH)


def save_store_async(store: dict, on_done=None) -> None:
    """حفظ المتجر في خيط خلفي (Background Thread) لمنع تعليق واجهة المستخدم نهائياً."""
    def _worker():
        try:
            save_store_sync(store)
            if on_done:
                on_done(True)
        except Exception:
            if on_done:
                on_done(False)

    threading.Thread(target=_worker, daemon=True).start()


# عمليات التعديل والإضافة والحذف
def add_new_prompt(store: dict, act: str, prompt: str, category: str = "أخرى",
                   for_devs: bool = False, p_type: str = "TEXT") -> dict:
    """إضافة برومبت جديد خاص بالمستخدم."""
    item = {
        "act": act.strip(),
        "prompt": prompt.strip(),
        "category": category,
        "for_devs": for_devs,
        "type": p_type,
        "key": key_of(act, prompt),
        "new": True,
        "added": int(time.time()),
        "builtin": False,
        "user_edited": True,
    }
    prepare_row(item)
    # إضافة في المقدمة لسرعة الوصول
    store["prompts"].insert(0, item)
    save_store_async(store)
    return item


def update_existing_prompt(store: dict, key: str, new_act: str, new_prompt: str,
                           new_cat: str | None = None) -> bool:
    """تعديل نص واسم برومبت موجود وحفظ التغييرات."""
    for p in store["prompts"]:
        if p.get("key") == key:
            p["act"] = new_act.strip()
            p["prompt"] = new_prompt.strip()
            if new_cat:
                p["category"] = new_cat
            p["user_edited"] = True
            tokenize_prompt(p)
            save_store_async(store)
            return True
    return False


def delete_prompt(store: dict, key: str) -> bool:
    """حذف برومبت من المتجر وإزالته من المفضلة."""
    initial_len = len(store["prompts"])
    store["prompts"] = [p for p in store["prompts"] if p.get("key") != key]
    if key in store.get("favorites", []):
        store["favorites"].remove(key)
    if len(store["prompts"]) < initial_len:
        save_store_async(store)
        return True
    return False
