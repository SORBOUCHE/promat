# -*- coding: utf-8 -*-
"""
مصحح اتجاه الخط والنصوص العربية في أنتي جرافيتي (Antigravity Arabic BiDi & Typography Fixer)
أداة سطح مكتب احترافية لحل مشاكل اتجاه النصوص، انزياح علامات الترقيم، الكلمات الإنجليزية المتداخلة،
النصوص المقلوبة، والحروف المقطعة في بيئات LTR وAntigravity.
"""

import os
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# محارف التوجيه والتحكم في خوارزمية اليونيكود (Unicode BiDi Formatting Marks)
RLM = '\u200F'  # Right-to-Left Mark (علامة إجبار الاتجاه من اليمين لليسار)
LRM = '\u200E'  # Left-to-Right Mark (علامة إجبار الاتجاه من اليسار لليمين)
ALM = '\u061C'  # Arabic Letter Mark
LRE = '\u202A'  # Left-to-Right Embedding
RLE = '\u202B'  # Right-to-Left Embedding
PDF = '\u202C'  # Pop Directional Formatting

ARABIC_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')

# ألوان التصميم العصري (Slate & Indigo Palette)
BG_DARK = "#0f172a"          # Slate 900
BG_CARD = "#1e293b"          # Slate 800
BG_LIGHT = "#f8fafc"         # Slate 50
TEXT_MAIN = "#0f172a"
TEXT_MUTED = "#64748b"
ACCENT = "#4f46e5"           # Indigo 600
ACCENT_HOVER = "#4338ca"
EMERALD = "#10b981"          # Emerald 500
AMBER = "#f59e0b"            # Amber 500
BORDER_COLOR = "#e2e8f0"


def is_arabic_text(text: str) -> bool:
    """التحقق مما إذا كان النص يحتوي على محارف عربية."""
    return bool(ARABIC_RE.search(text))


def fix_antigravity_bidi(text: str) -> str:
    """
    تصحيح اتجاه النصوص العربية في بيئات LTR مثل Antigravity:
    1. تثبيت علامات الترقيم في نهاية الأسطر لمنع قفزها إلى أقصى اليسار.
    2. معالجة الأقواس المقلوبة `( )` و `[ ]` و `{ }` وحمايتها بعلامات RLM.
    3. عزل الكلمات الإنجليزية والأرقام والأكواد المختلطة داخل الجمل العربية لمنع تشويه الترتيب.
    4. معالجة النقاط والقوائم النقطية والرقمية.
    """
    if not text:
        return ""

    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        if not line.strip() or not is_arabic_text(line):
            fixed_lines.append(line)
            continue

        l = line

        # 1. تصحيح الأقواس المعكوسة المحاطة بنص عربي
        l = re.sub(r'(\([^\)]+\))', RLM + r'\1' + RLM, l)
        l = re.sub(r'(\[[^\]]+\])', RLM + r'\1' + RLM, l)
        l = re.sub(r'(\{[^\}]+\})', RLM + r'\1' + RLM, l)

        # 2. عزل الكلمات اللاتينية والأكواد غير المحاطة بـ backticks
        # حتى لا تعكس اتجاه الكلمات العربية المجاورة لها
        l = re.sub(
            r'(?<=[\u0600-\u06FF])\s+([a-zA-Z0-9_\-\.\/]+)\s+(?=[\u0600-\u06FF])',
            r' ' + RLM + LRM + r'\1' + LRM + RLM + r' ',
            l
        )

        # 3. تثبيت علامة الترقيم في نهاية السطر
        # في بيئات LTR، النقطة أو علامة الاستفهام أو القوس في نهاية السطر تقفز لأول السطر
        if re.search(r'[\.\,\!\?\:\;\؟\،\)\}\]\'\"\`]$', l):
            l = l + RLM

        # 4. القوائم النقطية والترقيم
        if re.match(r'^\s*[-*•]\s+', l):
            l = re.sub(r'^(\s*[-*•]\s+)', r'\1' + RLM, l)
        elif re.match(r'^\s*\d+\.\s+', l):
            l = re.sub(r'^(\s*\d+\.\s+)', r'\1' + RLM, l)

        fixed_lines.append(l)

    return '\n'.join(fixed_lines)


def unreverse_arabic_text(text: str) -> str:
    """
    إصلاح النصوص العربية المقلوبة حرفاً بحرف
    (التي تظهر أحياناً معكوسة من برامج غير داعمة: ة ي ب ر ع ل ا أو ةيبرعلا -> العربية).
    """
    if not text:
        return ""
    lines = text.split('\n')
    out = []
    for line in lines:
        if is_arabic_text(line):
            # إذا كان السطر يضم كلمات عربية مقلوبة، نقوم بعكس المحارف مع الحفاظ على الأرقام
            words = line.split(' ')
            rev_words = []
            for w in words:
                if is_arabic_text(w):
                    rev_words.append(w[::-1])
                else:
                    rev_words.append(w)
            # عكس تسلسل الكلمات ليطابق اتجاه القراءة
            rev_words.reverse()
            out.append(' '.join(rev_words))
        else:
            out.append(line)
    return '\n'.join(out)


def reconnect_letters(text: str) -> str:
    """
    تشبيك الحروف العربية المتقطعة التي تفصل بينها مسافات مفردة
    (مثل: ا ل س ل ا م -> السلام).
    """
    if not text:
        return ""
    # إزالة المسافة المفردة الفاصلة بين حرفين عربيين
    pattern = r'(?<=[\u0600-\u06FF])\s(?=[\u0600-\u06FF])'
    return re.sub(pattern, '', text)


def wrap_html_rtl(text: str) -> str:
    """
    تغليف النص في بطاقة HTML منسقة بـ RTL وخط عربي أنيق
    تصلح للعرض الفوري في ألواح وملفات Markdown وSidecars في Antigravity.
    """
    escaped = (text.replace('&', '&amp;')
               .replace('<', '&lt;')
               .replace('>', '&gt;')
               .replace('\n', '<br>\n'))
    return (
        '<div dir="rtl" style="direction: rtl; text-align: right; '
        'font-family: \'Segoe UI\', Tahoma, Arial, sans-serif; '
        'line-height: 1.8; font-size: 15px; color: #1e293b; '
        'background: #ffffff; padding: 18px 22px; border-radius: 10px; '
        'border: 1px solid #e2e8f0; unicode-bidi: isolate;">\n'
        f'{escaped}\n'
        '</div>'
    )


class ArabicBidiFixerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("مصحح الخط العربي في أنتي جرافيتي (Antigravity Arabic BiDi Fixer)")
        self.geometry("1140x720")
        self.minsize(920, 560)
        self.configure(bg=BG_LIGHT)

        self.font_size = 11
        self.auto_clip_active = False
        self.last_clip_text = ""
        self.clip_thread = None

        self.setup_ui()
        self.update_font()

        # تفعيل المراقبة التلقائية للحافظة فور تشغيل البرنامج
        self.after(400, self.toggle_clip_monitor)

    @property
    def startup_file_path(self):
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "AntigravityArabicBiDiFixer.bat"
        return None

    def is_startup_enabled(self):
        p = self.startup_file_path
        return p is not None and p.exists()

    def toggle_windows_startup(self):
        p = self.startup_file_path
        if not p:
            return
        if self.startup_var.get():
            try:
                script_path = Path(__file__).resolve()
                pythonw = Path(sys.executable).parent / "pythonw.exe"
                if not pythonw.exists():
                    pythonw = Path(sys.executable)
                cmd = f'@echo off\nstart "" "{pythonw}" "{script_path}"\n'
                p.write_text(cmd, encoding="utf-8")
                self.show_toast("✓ تم تفعيل التشغيل التلقائي مع إقلاع ويندوز")
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر إضافة التشغيل التلقائي: {e}", parent=self)
                self.startup_var.set(False)
        else:
            try:
                if p.exists():
                    p.unlink()
                self.show_toast("تم إلغاء التشغيل التلقائي مع ويندوز")
            except Exception:
                pass

    def setup_ui(self):
        # 1. شريط الرأس (Header Bar)
        head = tk.Frame(self, bg=BG_DARK, height=60, padx=18, pady=10)
        head.pack(fill="x")

        # شعار وعنوان الأداة
        logo_f = tk.Frame(head, bg=BG_DARK)
        logo_f.pack(side="right")
        tk.Label(logo_f, text="◆ مصحح الخط العربي", bg=BG_DARK, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(side="right")
        tk.Label(logo_f, text="لبيئات أنتي جرافيتي (Antigravity)", bg=BG_DARK, fg="#94a3b8",
                 font=("Segoe UI", 9)).pack(side="right", padx=8)

        # تحكم حجم الخط
        f_ctrl = tk.Frame(head, bg=BG_DARK)
        f_ctrl.pack(side="left")
        tk.Label(f_ctrl, text="حجم الخط:", bg=BG_DARK, fg="#cbd5e1",
                 font=("Segoe UI", 9)).pack(side="left", padx=4)
        tk.Button(f_ctrl, text="A+", bg=BG_CARD, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=8, pady=2, cursor="hand2",
                  command=self.increase_font).pack(side="left", padx=2)
        tk.Button(f_ctrl, text="A-", bg=BG_CARD, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=8, pady=2, cursor="hand2",
                  command=self.decrease_font).pack(side="left", padx=2)

        # ميزة مراقبة الحافظة التلقائية (مفعلة افتراضياً)
        self.clip_var = tk.BooleanVar(value=True)
        self.clip_chk = tk.Checkbutton(head, text="⚡ تصحيح تلقائي عند النسخ (Live Clipboard)",
                                       variable=self.clip_var, bg=BG_DARK, fg="#7dd3fc",
                                       activebackground=BG_DARK, activeforeground="white",
                                       selectcolor=BG_CARD, font=("Segoe UI", 9, "bold"),
                                       cursor="hand2", command=self.toggle_clip_monitor)
        self.clip_chk.pack(side="left", padx=12)

        # خيار التشغيل التلقائي مع ويندوز
        self.startup_var = tk.BooleanVar(value=self.is_startup_enabled())
        tk.Checkbutton(head, text="🚀 تشغيل مع ويندوز", variable=self.startup_var,
                       bg=BG_DARK, fg="#cbd5e1", activebackground=BG_DARK, activeforeground="white",
                       selectcolor=BG_CARD, font=("Segoe UI", 9), cursor="hand2",
                       command=self.toggle_windows_startup).pack(side="left", padx=6)

        # 2. شريط أدوات العمليات السريعة (Action Toolbar)
        tools_bar = tk.Frame(self, bg="white", padx=14, pady=8, highlightbackground=BORDER_COLOR, highlightthickness=1)
        tools_bar.pack(fill="x")

        # زر التصحيح الأساسي
        tk.Button(tools_bar, text="🚀 تصحيح الاتجاه والترقيم (Fix BiDi)", bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=5, cursor="hand2",
                  command=self.action_fix_bidi).pack(side="right", padx=4)

        # أزرار المعالجات الإضافية
        tk.Button(tools_bar, text="🔄 إصلاح النص المقلوب (Un-reverse)", bg="#3b82f6", fg="white", relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=5, cursor="hand2",
                  command=self.action_unreverse).pack(side="right", padx=4)

        tk.Button(tools_bar, text="🔗 تشبيك الحروف المقطعة", bg="#0284c7", fg="white", relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=5, cursor="hand2",
                  command=self.action_reconnect).pack(side="right", padx=4)

        tk.Button(tools_bar, text="📄 تغليف كـ HTML RTL", bg=AMBER, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=5, cursor="hand2",
                  command=self.action_wrap_html).pack(side="right", padx=4)

        # أدوات الحافظة
        tk.Button(tools_bar, text="📋 لصق من الحافظة", bg="#f1f5f9", fg=TEXT_MAIN, relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=5, cursor="hand2",
                  command=self.paste_input).pack(side="left", padx=4)

        tk.Button(tools_bar, text="✕ مسح الكل", bg="#fee2e2", fg="#dc2626", relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=5, cursor="hand2",
                  command=self.clear_all).pack(side="left", padx=4)

        # 3. منطقة النصوص الرئيسية (Dual-Pane Splitter)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=12, pady=10)

        # اللوحة اليسرى: النص المصحح (النتيجة)
        out_card = tk.Frame(paned, bg="white", highlightbackground=BORDER_COLOR, highlightthickness=1)
        paned.add(out_card, weight=1)

        out_head = tk.Frame(out_card, bg="#f1f5f9", padx=10, pady=6)
        out_head.pack(fill="x")
        tk.Label(out_head, text="✓ النص المصحح والجاهز للعرض والنسخ", bg="#f1f5f9", fg=EMERALD,
                 font=("Segoe UI", 10, "bold")).pack(side="right")
        tk.Button(out_head, text="📋 نسخ النتيجة", bg=EMERALD, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=12, pady=2, cursor="hand2",
                  command=self.copy_output).pack(side="left")

        self.txt_out = tk.Text(out_card, wrap="word", bg="white", fg=TEXT_MAIN,
                               relief="flat", padx=14, pady=12)
        self.txt_out.pack(side="left", fill="both", expand=True)
        sb_out = ttk.Scrollbar(out_card, orient="vertical", command=self.txt_out.yview)
        self.txt_out.configure(yscrollcommand=sb_out.set)
        sb_out.pack(side="right", fill="y")

        # اللوحة اليمنى: النص الأصلي (المدخل)
        in_card = tk.Frame(paned, bg="white", highlightbackground=BORDER_COLOR, highlightthickness=1)
        paned.add(in_card, weight=1)

        in_head = tk.Frame(in_card, bg="#f1f5f9", padx=10, pady=6)
        in_head.pack(fill="x")
        tk.Label(in_head, text="النص الأصلي (من أنتي جرافيتي أو أي مصدر):", bg="#f1f5f9", fg=TEXT_MUTED,
                 font=("Segoe UI", 10, "bold")).pack(side="right")
        self.char_lbl = tk.Label(in_head, text="0 حرف", bg="#f1f5f9", fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.char_lbl.pack(side="left")

        self.txt_in = tk.Text(in_card, wrap="word", bg="#f8fafc", fg=TEXT_MAIN,
                              relief="flat", padx=14, pady=12)
        self.txt_in.pack(side="left", fill="both", expand=True)
        sb_in = ttk.Scrollbar(in_card, orient="vertical", command=self.txt_in.yview)
        self.txt_in.configure(yscrollcommand=sb_in.set)
        sb_in.pack(side="right", fill="y")
        self.txt_in.bind("<<Modified>>", self.on_input_modified)

        # 4. شريط الحالة السفلي (Status Bar)
        foot = tk.Frame(self, bg="white", height=32, padx=14, pady=4,
                        highlightbackground=BORDER_COLOR, highlightthickness=1)
        foot.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(foot, text="جاهز. أدخل أو الصق النص ثم اختر العملية المطلوبة.",
                                   bg="white", fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.status_lbl.pack(side="right")

        self.toast_lbl = tk.Label(foot, text="", bg="white", fg=EMERALD, font=("Segoe UI", 9, "bold"))
        self.toast_lbl.pack(side="left")

        # نص افتراضي توضيحي
        default_sample = (
            "مرحبا بك في أنتي جرافيتي (Antigravity IDE 2.0)!\n"
            "هذا النص يوضح كيف يتم تصحيح انزياح علامات الترقيم والأقواس مثل (Python 3.12) والنقاط في نهاية الجمل.\n"
            "- النقطة الأولى: تصحيح الاتجاه مع الكلمات الإنجليزية مثل fetch() أو async/await.\n"
            "- النقطة الثانية: ضمان ظهور علامة الاستفهام ؟ والنقطة . في مكانها السليم دون انقلاب."
        )
        self.txt_in.insert("1.0", default_sample)
        self.action_fix_bidi()

    def update_font(self):
        font_spec = ("Segoe UI", self.font_size)
        self.txt_in.configure(font=font_spec)
        self.txt_out.configure(font=font_spec)

    def increase_font(self):
        if self.font_size < 24:
            self.font_size += 1
            self.update_font()

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 1
            self.update_font()

    def on_input_modified(self, _event=None):
        if self.txt_in.edit_modified():
            text = self.txt_in.get("1.0", "end-1c")
            self.char_lbl["text"] = f"{len(text)} حرف"
            self.txt_in.edit_modified(False)

    def set_output(self, text, message="تمت المعالجة بنجاح ✓"):
        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("1.0", text)
        self.show_toast(message)

    def show_toast(self, text):
        self.toast_lbl["text"] = text
        self.after(3000, lambda: self.toast_lbl.config(text=""))

    def action_fix_bidi(self):
        raw = self.txt_in.get("1.0", "end-1c")
        if not raw.strip():
            return
        fixed = fix_antigravity_bidi(raw)
        self.set_output(fixed, "تم تصحيح اتجاه النص وعلامات الترقيم والأقواس بنجاح ✓")

    def action_unreverse(self):
        raw = self.txt_in.get("1.0", "end-1c")
        if not raw.strip():
            return
        unrev = unreverse_arabic_text(raw)
        self.set_output(unrev, "تم إصلاح النص المقلوب وعكس الترتيب ✓")

    def action_reconnect(self):
        raw = self.txt_in.get("1.0", "end-1c")
        if not raw.strip():
            return
        connected = reconnect_letters(raw)
        self.set_output(connected, "تم تشبيك الحروف المقطعة بنجاح ✓")

    def action_wrap_html(self):
        raw = self.txt_in.get("1.0", "end-1c")
        if not raw.strip():
            return
        html_code = wrap_html_rtl(raw)
        self.set_output(html_code, "تم إنشاء بطاقة HTML RTL جاهزة للاستخدام ✓")

    def paste_input(self):
        try:
            clip = self.clipboard_get()
            self.txt_in.delete("1.0", "end")
            self.txt_in.insert("1.0", clip)
            self.action_fix_bidi()
            self.show_toast("تم اللصق من الحافظة وتصحيح النص تلقائياً ✓")
        except Exception:
            messagebox.showinfo("تنبيه", "الحافظة فارغة أو لا تحتوي على نص.", parent=self)

    def copy_output(self):
        out = self.txt_out.get("1.0", "end-1c")
        if out:
            self.clipboard_clear()
            self.clipboard_append(out)
            self.show_toast("تم نسخ النص المصحح إلى الحافظة ✓")

    def clear_all(self):
        self.txt_in.delete("1.0", "end")
        self.txt_out.delete("1.0", "end")
        self.char_lbl["text"] = "0 حرف"
        self.show_toast("تم مسح المحتوى")

    def toggle_clip_monitor(self):
        if self.clip_var.get():
            self.auto_clip_active = True
            self.show_toast("⚡ تم تفعيل المراقبة التلقائية للحافظة")
            if not self.clip_thread or not self.clip_thread.is_alive():
                self.clip_thread = threading.Thread(target=self._clip_monitor_worker, daemon=True)
                self.clip_thread.start()
        else:
            self.auto_clip_active = False
            self.show_toast("تم إيقاف مراقبة الحافظة")

    def _clip_monitor_worker(self):
        """خيط لمراقبة الحافظة وتصحيح أي نصوص عربية يتم نسخها تلقائياً."""
        while self.auto_clip_active:
            try:
                clip = self.clipboard_get()
                if clip and clip != self.last_clip_text and is_arabic_text(clip):
                    self.last_clip_text = clip
                    # تطبيق التصحيح
                    fixed = fix_antigravity_bidi(clip)
                    if fixed != clip:
                        # تحديث الحافظة بالنسخة المصححة
                        self.after(0, lambda f=fixed: self._update_clip_from_worker(f))
            except Exception:
                pass
            time.sleep(0.7)

    def _update_clip_from_worker(self, fixed_text):
        try:
            self.clipboard_clear()
            self.clipboard_append(fixed_text)
            self.last_clip_text = fixed_text
            self.txt_in.delete("1.0", "end")
            self.txt_in.insert("1.0", fixed_text)
            self.txt_out.delete("1.0", "end")
            self.txt_out.insert("1.0", fixed_text)
            self.show_toast("⚡ تم تصحيح النص المنسوخ تلقائياً في الحافظة ✓")
        except Exception:
            pass


def main():
    app = ArabicBidiFixerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
