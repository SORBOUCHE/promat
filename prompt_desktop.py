# -*- coding: utf-8 -*-
"""
برومات — تطبيق سطح المكتب الاحترافي للبحث، الشرح، الترجمة، والتعديل على البرومات
Promat Desktop Application
"""

import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import prompts_core as pc

BASE = Path(__file__).parent
APP_BG = "#0f172a"          # Slate 900
APP_BG2 = "#1e293b"         # Slate 800
APP_BG_HOVER = "#334155"    # Slate 700
ACCENT = "#4f46e5"          # Indigo 600
ACCENT_HOVER = "#4338ca"    # Indigo 700
EMERALD = "#10b981"         # Emerald 500
PURPLE = "#8b5cf6"          # Purple 500
AMBER = "#f59e0b"           # Amber 500
LIGHT_BG = "#f8fafc"        # Slate 50
CARD_BG = "#ffffff"
TEXT_MAIN = "#0f172a"
TEXT_MUTED = "#64748b"
BORDER_COLOR = "#e2e8f0"


class EnhanceDialog(tk.Toplevel):
    """نافذة التحسين الذكي للبرومبت وتكييفه لمختلف نماذج الذكاء الاصطناعي."""

    def __init__(self, master, prompt_item, on_save_as_new=None):
        super().__init__(master)
        self.prompt_item = prompt_item
        self.on_save_as_new = on_save_as_new
        self.title("✨ التحسين الذكي وهندسة البرومبت")
        self.geometry("880x680")
        self.minsize(760, 520)
        self.configure(bg=LIGHT_BG)
        self.transient(master)
        self.grab_set()
        self.result_text = ""

        # رأس النافذة
        head = tk.Frame(self, bg=APP_BG, height=54)
        head.pack(fill="x")
        tk.Label(head, text="✨ التحسين الذكي وتكييف النموذج", bg=APP_BG, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="right", padx=16, pady=12)
        tk.Label(head, text=prompt_item.get("act", ""), bg=APP_BG, fg="#94a3b8",
                 font=("Segoe UI", 10)).pack(side="right", padx=6)

        # شريط التحكم والخيارات
        cfg = tk.Frame(self, bg="white", padx=14, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        cfg.pack(fill="x", padx=12, pady=(12, 6))

        # اختيار النموذج
        m_frame = tk.Frame(cfg, bg="white")
        m_frame.pack(side="right", padx=8)
        tk.Label(m_frame, text="النموذج المستهدف:", bg="white", fg=TEXT_MAIN,
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=6)
        self.model_box = ttk.Combobox(m_frame, values=list(pc.MODELS.keys()), state="readonly", width=22)
        self.model_box.current(0)
        self.model_box.pack(side="right")
        self.model_box.bind("<<ComboboxSelected>>", lambda e: self.generate())

        # لغة القالب
        l_frame = tk.Frame(cfg, bg="white")
        l_frame.pack(side="right", padx=12)
        tk.Label(l_frame, text="لغة التوجيه:", bg="white", fg=TEXT_MAIN,
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=6)
        self.lang_var = tk.StringVar(value="ar")
        rb_ar = tk.Radiobutton(l_frame, text="عربي", variable=self.lang_var, value="ar",
                               bg="white", command=self.generate)
        rb_ar.pack(side="right")
        rb_en = tk.Radiobutton(l_frame, text="English", variable=self.lang_var, value="en",
                               bg="white", command=self.generate)
        rb_en.pack(side="right", padx=4)

        # أزرار الإجراءات في الرأس
        tk.Button(cfg, text="⟳ إعادة توليد", bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2",
                  command=self.generate).pack(side="left", padx=4)

        # صندوق النص المخرج
        text_card = tk.Frame(self, bg="white", highlightbackground=BORDER_COLOR, highlightthickness=1)
        text_card.pack(fill="both", expand=True, padx=12, pady=6)

        self.out = tk.Text(text_card, wrap="word", font=("Consolas", 10), bg="#f8fafc",
                           relief="flat", padx=14, pady=12)
        self.out.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(text_card, orient="vertical", command=self.out.yview)
        self.out.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # الشريط السفلي
        foot = tk.Frame(self, bg=LIGHT_BG, padx=12, pady=10)
        foot.pack(fill="x")

        tk.Button(foot, text="📋 نسخ إلى الحافظة", bg=EMERALD, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=16, pady=5, cursor="hand2",
                  command=self.copy_result).pack(side="right", padx=6)

        tk.Button(foot, text="💾 حفظ كبرومبت جديد بالمكتبة", bg=PURPLE, fg="white", relief="flat",
                  font=("Segoe UI", 10), padx=14, pady=5, cursor="hand2",
                  command=self.save_as_new).pack(side="right", padx=6)

        tk.Button(foot, text="📁 تصدير لملف نصي...", bg=APP_BG2, fg="white", relief="flat",
                  font=("Segoe UI", 10), padx=14, pady=5, cursor="hand2",
                  command=self.save_file).pack(side="left", padx=6)

        self.status_lbl = tk.Label(foot, text="", bg=LIGHT_BG, fg=EMERALD, font=("Segoe UI", 9, "bold"))
        self.status_lbl.pack(side="left", padx=10)

        self.generate()

    def generate(self):
        m_key = pc.MODELS.get(self.model_box.get(), "generic")
        lang = self.lang_var.get()
        self.result_text = pc.build_enhanced_prompt(self.prompt_item, m_key, lang)
        self.out.delete("1.0", "end")
        self.out.insert("1.0", self.result_text)
        self.status_lbl["text"] = "تم توليد البرومبت المحسّن بنجاح ✓"
        self.after(2500, lambda: self.status_lbl.config(text=""))

    def copy_result(self):
        txt = self.out.get("1.0", "end").strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.status_lbl["text"] = "تم النسخ إلى الحافظة ✓"
            self.after(2500, lambda: self.status_lbl.config(text=""))

    def save_as_new(self):
        txt = self.out.get("1.0", "end").strip()
        if not txt:
            return
        new_act = f"{self.prompt_item.get('act', '')} (Enhanced)"
        if self.on_save_as_new:
            self.on_save_as_new(new_act, txt, self.prompt_item.get("category", "أخرى"))
            messagebox.showinfo("تم الحفظ", f"تمت إضافة البرومبت المحسّن إلى مكتبتك:\n{new_act}", parent=self)
            self.destroy()

    def save_file(self):
        txt = self.out.get("1.0", "end").strip()
        if not txt:
            return
        default_name = f"enhanced_{int(time.time())}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md")], parent=self)
        if path:
            Path(path).write_text(txt, encoding="utf-8-sig")
            messagebox.showinfo("تم الحفظ", "تم تصدير الملف بنجاح ✓", parent=self)


class NewPromptDialog(tk.Toplevel):
    """نافذة إنشاء برومبت جديد وإضافته إلى المكتبة."""

    def __init__(self, master, on_create):
        super().__init__(master)
        self.on_create = on_create
        self.title("➕ إضافة برومبت جديد إلى المكتبة")
        self.geometry("640x560")
        self.minsize(560, 480)
        self.configure(bg=LIGHT_BG)
        self.transient(master)
        self.grab_set()

        head = tk.Frame(self, bg=APP_BG, height=50)
        head.pack(fill="x")
        tk.Label(head, text="➕ إضافة برومبت جديد", bg=APP_BG, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="right", padx=16, pady=12)

        form = tk.Frame(self, bg="white", padx=18, pady=16, highlightbackground=BORDER_COLOR, highlightthickness=1)
        form.pack(fill="both", expand=True, padx=14, pady=14)

        # اسم الدور
        tk.Label(form, text="اسم الدور أو التخصص (Act):", bg="white", fg=TEXT_MAIN,
                 font=("Segoe UI", 10, "bold")).pack(anchor="e", pady=(4, 2))
        self.act_entry = ttk.Entry(form, font=("Segoe UI", 10))
        self.act_entry.pack(fill="x", ipady=4, pady=(0, 10))

        # التصنيف والنوع
        row2 = tk.Frame(form, bg="white")
        row2.pack(fill="x", pady=(0, 10))

        tk.Label(row2, text="التصنيف:", bg="white", fg=TEXT_MAIN,
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=(4, 6))
        cat_names = [name for name, _ in pc.CATEGORIES if name != "أخرى"] + ["أخرى"]
        self.cat_box = ttk.Combobox(row2, values=cat_names, state="readonly", width=18)
        self.cat_box.current(0)
        self.cat_box.pack(side="right", padx=(0, 14))

        self.devs_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="مخصص للمبرمجين", variable=self.devs_var).pack(side="right")

        # نص البرومبت
        tk.Label(form, text="نص البرومبت (Prompt Instructions):", bg="white", fg=TEXT_MAIN,
                 font=("Segoe UI", 10, "bold")).pack(anchor="e", pady=(4, 2))
        self.prompt_text = tk.Text(form, wrap="word", font=("Consolas", 10), bg="#f8fafc",
                                   relief="flat", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.prompt_text.pack(fill="both", expand=True, pady=(0, 12))

        # أزرار الإجراء
        btns = tk.Frame(form, bg="white")
        btns.pack(fill="x")
        tk.Button(btns, text="إلغاء", relief="flat", bg="#e2e8f0", fg=TEXT_MAIN,
                  font=("Segoe UI", 10), padx=16, pady=5, cursor="hand2",
                  command=self.destroy).pack(side="left")
        tk.Button(btns, text="💾 حفظ البرومبت", bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=20, pady=5, cursor="hand2",
                  command=self.save).pack(side="right")

    def save(self):
        act = self.act_entry.get().strip()
        prompt = self.prompt_text.get("1.0", "end").strip()
        category = self.cat_box.get()
        for_devs = self.devs_var.get()

        if not act or not prompt:
            messagebox.showwarning("بيانات ناقصة", "يرجى كتابة اسم الدور ونص البرومبت أولاً.", parent=self)
            return

        self.on_create(act, prompt, category, for_devs)
        messagebox.showinfo("تمت الإضافة", "تمت إضافة البرومبت بنجاح إلى مكتبتك ✓", parent=self)
        self.destroy()


class App(tk.Tk):
    """النافذة الرئيسية لتطبيق برومات."""

    def __init__(self):
        super().__init__()
        self.title("برومات — المكتبة الذكية للبرومبتات")
        self.geometry("1280x780")
        self.minsize(1020, 620)
        self.configure(bg=LIGHT_BG)

        # تحميل البيانات
        self.store = pc.load_store()
        self.view_mode = "all"
        self.cat_filter = None
        self.query = ""
        self.devs_only = tk.BooleanVar(value=False)
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="جاهز")
        self.current_prompt = None
        self.is_translated_view = False
        self.original_cache_text = ""
        self._search_timer = None

        self.setup_styles()
        self.build_ui()
        self.refresh_list()
        self.setup_shortcuts()

        # فحص صامت للتحديثات في خيط خلفي دون إزعاج
        self.after(1500, self.check_updates_quietly)

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=LIGHT_BG, font=("Segoe UI", 10))
        style.configure("TFrame", background=LIGHT_BG)
        style.configure("TLabel", background=LIGHT_BG, foreground=TEXT_MAIN)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=32, background="white",
                        fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0",
                        foreground=TEXT_MAIN, relief="flat", padding=(6, 8))
        style.map("Treeview", background=[("selected", "#e0e7ff")],
                  foreground=[("selected", "#312e81")])
        style.configure("TNotebook", background=CARD_BG, tabposition="n")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 6))

    def setup_shortcuts(self):
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Control-n>", lambda e: self.open_new_dialog())
        self.bind("<Control-c>", self.handle_copy_shortcut)
        self.bind("<Delete>", lambda e: self.delete_current_prompt())

    def handle_copy_shortcut(self, event):
        # نسخ فقط إذا لم يكن التركيز في مربع إدخال
        focus = self.focus_get()
        if not isinstance(focus, (tk.Entry, ttk.Entry, tk.Text)):
            self.copy_current_prompt()

    def build_ui(self):
        # 1. الشريط العلوي (Top Header Bar)
        top_bar = tk.Frame(self, bg=CARD_BG, height=64, padx=16, pady=10,
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_bar.pack(fill="x", side="top")

        # شعار وعنوان البرنامج في اليمين
        logo_frame = tk.Frame(top_bar, bg=CARD_BG)
        logo_frame.pack(side="right", padx=(12, 4))
        tk.Label(logo_frame, text="◆ بـرومـات", bg=CARD_BG, fg=ACCENT,
                 font=("Segoe UI", 15, "bold")).pack(side="right")
        tk.Label(logo_frame, text="المكتبة الذكية", bg=CARD_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(side="right", padx=6)

        # شريط البحث الذكي
        search_frame = tk.Frame(top_bar, bg=CARD_BG)
        search_frame.pack(side="right", fill="x", expand=True, padx=20)

        tk.Label(search_frame, text="🔍", bg=CARD_BG, font=("Segoe UI", 11)).pack(side="right", padx=4)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        self.search_entry.pack(side="right", fill="x", expand=True, ipady=4)
        self.search_var.trace_add("write", self.on_search_typing)

        tk.Button(search_frame, text="✕ مسح", relief="flat", bg="#f1f5f9", fg=TEXT_MUTED,
                  font=("Segoe UI", 9), padx=8, pady=4, cursor="hand2",
                  command=self.clear_search).pack(side="right", padx=4)

        ttk.Checkbutton(top_bar, text="للمبرمجين فقط", variable=self.devs_only,
                        command=self.refresh_list).pack(side="right", padx=8)

        # أزرار الإجراءات العلوية
        tk.Button(top_bar, text="➕ برومبت جديد", bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=5, cursor="hand2",
                  command=self.open_new_dialog).pack(side="left", padx=4)

        tk.Button(top_bar, text="⟳ تحديث المكتبة", bg="#f1f5f9", fg=TEXT_MAIN, relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=12, pady=5, cursor="hand2",
                  command=self.manual_update).pack(side="left", padx=4)

        # 2. شريط الحالة السفلي (Status Bar)
        status_bar = tk.Frame(self, bg=CARD_BG, height=30, padx=14, pady=4,
                              highlightbackground=BORDER_COLOR, highlightthickness=1)
        status_bar.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(status_bar, textvariable=self.status_var, bg=CARD_BG,
                                   fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.status_lbl.pack(side="right")

        self.pb = ttk.Progressbar(status_bar, mode="indeterminate", length=140)

        self.count_lbl = tk.Label(status_bar, text="", bg=CARD_BG, fg=TEXT_MAIN,
                                  font=("Segoe UI", 9, "bold"))
        self.count_lbl.pack(side="left")

        # 3. القائمة الجانبية للتنقل والتصنيفات (Right Sidebar)
        self.sidebar = tk.Frame(self, bg=APP_BG, width=240)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="الأقسام والتنقل", bg=APP_BG, fg="#94a3b8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="e", padx=14, pady=(16, 6))

        nav_items = [
            ("الكل", "all", "📚"),
            ("المفضلة", "favorites", "★"),
            ("برومات جديدة", "new", "🆕"),
            ("المعدلة محلياً", "edited", "✏️"),
            ("أحدث الإضافات", "recent", "🕘"),
        ]
        self.nav_buttons = {}
        for label, mode, icon in nav_items:
            b = tk.Button(self.sidebar, text=f"{icon}  {label}", anchor="e",
                          bg=APP_BG, fg="#cbd5e1", activebackground=APP_BG2,
                          activeforeground="white", relief="flat", bd=0,
                          font=("Segoe UI", 10), padx=14, pady=6, cursor="hand2",
                          command=lambda m=mode: self.set_view(m))
            b.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[mode] = b

        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=12, pady=10)

        tk.Label(self.sidebar, text="التصنيف حسب النوع", bg=APP_BG, fg="#94a3b8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="e", padx=14, pady=(4, 6))

        self.cat_buttons_frame = tk.Frame(self.sidebar, bg=APP_BG)
        self.cat_buttons_frame.pack(fill="x", padx=4)
        self.cat_buttons = {}

        self.cat_all_button = tk.Button(self.cat_buttons_frame, text="◆ كل التصنيفات",
                                        anchor="e", bg=APP_BG, fg="#7dd3fc",
                                        activebackground=APP_BG2, activeforeground="white",
                                        relief="flat", bd=0, font=("Segoe UI", 9, "bold"),
                                        padx=12, pady=4, cursor="hand2",
                                        command=self.clear_cat)
        self.cat_all_button.pack(fill="x", padx=6, pady=1)

        self.build_cat_buttons()

        # 4. المنطقة الرئيسية المقسمة إلى جدول البرومات واللوحة الجانبية (PanedWindow)
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        # اللوحة الجانبية التفصيلية (Side Detail & Action Panel) - في اليسار
        self.side_detail = tk.Frame(main_paned, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
        main_paned.add(self.side_detail, weight=4)

        # جدول استعراض البرومات (Center Table Pane)
        table_frame = tk.Frame(main_paned, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
        main_paned.add(table_frame, weight=3)

        self.build_table(table_frame)
        self.build_side_panel(self.side_detail)

    def build_table(self, parent):
        cols = ("#", "act", "cat", "flag")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("#", text="#")
        self.tree.heading("act", text="الدور / اسم البرومبت")
        self.tree.heading("cat", text="التصنيف")
        self.tree.heading("flag", text="الحالة")

        self.tree.column("#", width=42, anchor="center", stretch=False)
        self.tree.column("act", width=360, anchor="w")
        self.tree.column("cat", width=120, anchor="center", stretch=False)
        self.tree.column("flag", width=110, anchor="center", stretch=False)

        self.tree.tag_configure("new", background="#fef9c3")        # أصفر فاتح للجديد
        self.tree.tag_configure("odd", background="#f8fafc")        # صفوف متبادلة
        self.tree.tag_configure("fav", foreground="#db2777")        # وردي للمفضلة
        self.tree.tag_configure("edited", foreground="#2563eb")     # أزرق للمعدل

        self.tree.bind("<<TreeviewSelect>>", self.on_select_prompt)
        self.tree.bind("<Double-1>", lambda e: self.toggle_fav())

        sb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="left", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def build_side_panel(self, parent):
        """بناء اللوحة الجانبية التفاعلية المشتملة على الشرح بالعربية، الترجمة، التعديل والتحسين."""
        # رأس اللوحة
        self.detail_header = tk.Frame(parent, bg=APP_BG2, padx=14, pady=10)
        self.detail_header.pack(fill="x")

        self.prompt_title_lbl = tk.Label(self.detail_header, text="اختر برومبت من القائمة لاستعراضه",
                                         bg=APP_BG2, fg="white", font=("Segoe UI", 12, "bold"))
        self.prompt_title_lbl.pack(side="right")

        self.prompt_badge_lbl = tk.Label(self.detail_header, text="", bg=APP_BG2, fg="#38bdf8",
                                         font=("Segoe UI", 9))
        self.prompt_badge_lbl.pack(side="left")

        # شريط أدوات الإجراءات السريعة (Action Toolbar)
        act_bar = tk.Frame(parent, bg="white", padx=10, pady=8, highlightbackground=BORDER_COLOR, highlightthickness=1)
        act_bar.pack(fill="x")

        # زر الحفظ المباشر
        self.save_edit_btn = tk.Button(act_bar, text="💾 حفظ التعديل", bg=EMERALD, fg="white", relief="flat",
                                       font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2",
                                       command=self.save_current_edit)
        self.save_edit_btn.pack(side="right", padx=3)

        # زر الترجمة للعربية
        self.translate_btn = tk.Button(act_bar, text="🌐 ترجمة للعربية", bg="#0284c7", fg="white", relief="flat",
                                       font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2",
                                       command=self.toggle_translate)
        self.translate_btn.pack(side="right", padx=3)

        # زر التحسين بالذكاء الاصطناعي
        self.enhance_btn = tk.Button(act_bar, text="✨ تحسين بالذكاء", bg=PURPLE, fg="white", relief="flat",
                                     font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2",
                                     command=self.open_enhance_dialog)
        self.enhance_btn.pack(side="right", padx=3)

        # زر النسخ
        tk.Button(act_bar, text="📋 نسخ", bg="#f1f5f9", fg=TEXT_MAIN, relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2",
                  command=self.copy_current_prompt).pack(side="right", padx=3)

        # زر المفضلة
        self.fav_btn = tk.Button(act_bar, text="★ مفضلة", bg="#f1f5f9", fg=TEXT_MAIN, relief="flat",
                                 font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2",
                                 command=self.toggle_fav)
        self.fav_btn.pack(side="right", padx=3)

        # زر الحذف
        tk.Button(act_bar, text="🗑️ حذف", bg="#fee2e2", fg="#dc2626", relief="flat",
                  font=("Segoe UI", 9), padx=8, pady=4, cursor="hand2",
                  command=self.delete_current_prompt).pack(side="left", padx=3)

        # تبويبات اللوحة (Tabs Notebook)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=6)

        # تبويب 1: نص البرومبت (محرر تفاعلي مباشر)
        self.tab_prompt = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_prompt, text=" 📄 نص البرومبت (قابل للتعديل) ")

        self.prompt_text_widget = tk.Text(self.tab_prompt, wrap="word", font=("Consolas", 10),
                                          bg="#f8fafc", fg=TEXT_MAIN, relief="flat", padx=12, pady=10)
        self.prompt_text_widget.pack(side="left", fill="both", expand=True)
        sb_p = ttk.Scrollbar(self.tab_prompt, orient="vertical", command=self.prompt_text_widget.yview)
        self.prompt_text_widget.configure(yscrollcommand=sb_p.set)
        sb_p.pack(side="right", fill="y")

        # تبويب 2: شرح البرومبت بالعربية
        self.tab_explain = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_explain, text=" 💡 شرح البرومبت بالعربية ")

        # شريط علوي مصغر للشرح
        exp_top = tk.Frame(self.tab_explain, bg="white", padx=10, pady=6)
        exp_top.pack(fill="x")
        tk.Label(exp_top, text="💡 توصيف دقيق للمهمة باللغة العربية", bg="white", fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=6)
        tk.Button(exp_top, text="⟳ تحديث الشرح الدقيق", bg="#f1f5f9", fg=TEXT_MAIN, relief="flat",
                  font=("Segoe UI", 8), padx=8, pady=2, cursor="hand2",
                  command=self.refresh_deep_explanation).pack(side="left")

        exp_body = tk.Frame(self.tab_explain, bg="white")
        exp_body.pack(fill="both", expand=True)

        self.explain_text_widget = tk.Text(exp_body, wrap="word", font=("Segoe UI", 10),
                                           bg="#f8fafc", fg=TEXT_MAIN, relief="flat", padx=14, pady=12, state="disabled")
        self.explain_text_widget.pack(side="left", fill="both", expand=True)
        sb_e = ttk.Scrollbar(exp_body, orient="vertical", command=self.explain_text_widget.yview)
        self.explain_text_widget.configure(yscrollcommand=sb_e.set)
        sb_e.pack(side="right", fill="y")

        # تبويب 3: تعبئة المتغيرات التفاعلية ${...}
        self.tab_vars = tk.Frame(self.notebook, bg="white", padx=12, pady=10)
        self.notebook.add(self.tab_vars, text=" 🧩 المتغيرات التفاعلية ")

        self.vars_scroll_frame = tk.Frame(self.tab_vars, bg="white")
        self.vars_scroll_frame.pack(fill="both", expand=True)
        self.vars_entries = {}

    def build_cat_buttons(self):
        # تفريغ الأزرار السابقة لمنع التكرار نهائياً
        for w in self.cat_buttons_frame.winfo_children():
            if w != self.cat_all_button:
                w.destroy()
        self.cat_buttons.clear()

        counts = {}
        for p in self.store.get("prompts", []):
            c = p.get("category", "أخرى")
            counts[c] = counts.get(c, 0) + 1

        for name, _ in pc.CATEGORIES:
            n = counts.get(name, 0)
            b = tk.Button(self.cat_buttons_frame,
                          text=f"  {name}   ({n})", anchor="e",
                          bg=APP_BG, fg="#cbd5e1", activebackground=APP_BG2,
                          activeforeground="white", relief="flat", bd=0,
                          font=("Segoe UI", 9), padx=12, pady=3, cursor="hand2",
                          command=lambda nm=name: self.set_cat(nm))
            b.pack(fill="x", padx=6, pady=1)
            self.cat_buttons[name] = b

    def set_view(self, mode):
        self.view_mode = mode
        self.cat_filter = None
        self.highlight_nav()
        self.refresh_list()

    def set_cat(self, name):
        self.view_mode = "category"
        self.cat_filter = name
        self.highlight_nav()
        self.refresh_list()

    def clear_cat(self):
        self.cat_filter = None
        self.view_mode = "all"
        self.highlight_nav()
        self.refresh_list()

    def highlight_nav(self):
        for m, b in self.nav_buttons.items():
            active = (m == self.view_mode)
            b["bg"] = APP_BG2 if active else APP_BG
            b["fg"] = "white" if active else "#cbd5e1"
        for name, b in self.cat_buttons.items():
            active = (self.view_mode == "category" and self.cat_filter == name)
            b["fg"] = "#7dd3fc" if active else "#94a3b8"
        self.cat_all_button["fg"] = "#7dd3fc" if self.cat_filter is None else "#94a3b8"

    def on_search_typing(self, *args):
        # تفعيل البحث المباشر مع تأخير بسيط (Debounce) لمنع الثقل أثناء الكتابة السريعة
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(250, self.execute_live_search)

    def execute_live_search(self):
        self.query = self.search_var.get().strip()
        self.refresh_list()

    def clear_search(self):
        self.search_var.set("")
        self.query = ""
        self.refresh_list()

    def get_filtered_prompts(self):
        ps = self.store.get("prompts", [])
        favs = set(self.store.get("favorites", []))

        # 1. تصفية القوائم الجانبية
        if self.view_mode == "favorites":
            ps = [p for p in ps if p.get("key") in favs]
        elif self.view_mode == "new":
            ps = [p for p in ps if p.get("new")]
        elif self.view_mode == "edited":
            ps = [p for p in ps if p.get("user_edited")]
        elif self.view_mode == "recent":
            ps = sorted(ps, key=lambda p: p.get("added", 0), reverse=True)[:150]
        elif self.view_mode == "category" and self.cat_filter:
            ps = [p for p in ps if p.get("category") == self.cat_filter]

        # 2. تطبيق البحث ومراعاة خيار المبرمجين
        return pc.search_prompts(ps, self.query, devs_only=self.devs_only.get(), category_filter=None)

    def refresh_list(self):
        scored_items = self.get_filtered_prompts()
        self.tree.delete(*self.tree.get_children())
        favs = set(self.store.get("favorites", []))

        for i, (score, p) in enumerate(scored_items, 1):
            tags = []
            flag = []
            if p.get("new"):
                tags.append("new")
                flag.append("🆕 جديد")
            if p.get("key") in favs:
                tags.append("fav")
                flag.append("★ مفضلة")
            if p.get("user_edited"):
                tags.append("edited")
                flag.append("✏️ معدل")
            if i % 2 == 0 and not p.get("new"):
                tags.append("odd")
            if score and i <= 3:
                flag.append("🎯 أفضل مطابقة")

            self.tree.insert("", "end", iid=p["key"],
                             values=(i, p.get("act", ""), p.get("category", "أخرى"), " • ".join(flag)),
                             tags=tags)

        # تحديث عداد النتائج
        names = {
            "all": "كل البرومات", "favorites": "المفضلة", "new": "الجديد",
            "edited": "المعدلة محلياً", "recent": "آخر الإضافات",
            "category": self.cat_filter or "",
        }
        view_title = names.get(self.view_mode, self.cat_filter or "")
        search_suffix = f" (بحث: {self.query})" if self.query else ""
        self.count_lbl["text"] = f"{view_title}{search_suffix}: {len(scored_items)} برومبت"

        # إعادة تحديد البرومبت الحالي إن كان معروضاً
        if self.current_prompt and self.current_prompt.get("key") in self.tree.get_children():
            self.tree.selection_set(self.current_prompt["key"])

    def on_select_prompt(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        key = sel[0]
        for p in self.store.get("prompts", []):
            if p.get("key") == key:
                self.load_prompt_details(p)
                break

    def load_prompt_details(self, p):
        self.current_prompt = p
        self.is_translated_view = False
        self.original_cache_text = p.get("prompt", "")

        # تحديث الرأس
        self.prompt_title_lbl["text"] = p.get("act", "")
        badges = [f"📂 {p.get('category', 'أخرى')}"]
        favs = set(self.store.get("favorites", []))
        if p.get("key") in favs:
            badges.append("★ مفضلة")
            self.fav_btn["text"] = "★ إزالة المفضلة"
            self.fav_btn["bg"] = "#fef3c7"
        else:
            self.fav_btn["text"] = "☆ أضف للمفضلة"
            self.fav_btn["bg"] = "#f1f5f9"
        if p.get("for_devs"):
            badges.append("💻 للمبرمجين")
        self.prompt_badge_lbl["text"] = "   |   ".join(badges)
        self.translate_btn["text"] = "🌐 ترجمة للعربية"

        # تحميل نص البرومبت في المحرر
        self.prompt_text_widget.delete("1.0", "end")
        self.prompt_text_widget.insert("1.0", self.original_cache_text)

        # تحميل الشرح الذكي بالعربية مع التوصيف الدقيق المباشر
        cached_hl = pc._HEADLINE_CACHE.get(p.get("key"))
        explanation = pc.explain_prompt_arabic(p, headline=cached_hl)
        self.explain_text_widget.config(state="normal")
        self.explain_text_widget.delete("1.0", "end")
        self.explain_text_widget.insert("1.0", explanation)
        self.explain_text_widget.config(state="disabled")

        if cached_hl:
            short_hl = (cached_hl[:45] + "...") if len(cached_hl) > 45 else cached_hl
            self.prompt_badge_lbl["text"] = f"{p.get('category', 'أخرى')}  •  {short_hl}"
        else:
            self.async_load_deep_explanation(p)

        # تحميل المتغيرات التفاعلية
        self.render_variables_tab(p.get("prompt", ""))

        # إزالة وسم "جديد" تلقائياً عند فتحه
        if p.get("new"):
            p["new"] = False
            pc.save_store_async(self.store)

    def async_load_deep_explanation(self, p, force=False):
        """توليد التوصيف الدقيق في خيط خلفي لمنع تجميد الواجهة."""
        key = p.get("key")
        if not key:
            return
        if force and key in pc._HEADLINE_CACHE:
            del pc._HEADLINE_CACHE[key]

        def _worker():
            hl = pc.generate_precise_headline(p)

            def _apply():
                if self.current_prompt and self.current_prompt.get("key") == key:
                    short_hl = (hl[:45] + "...") if len(hl) > 45 else hl
                    self.prompt_badge_lbl["text"] = f"{p.get('category', 'أخرى')}  •  {short_hl}"
                    updated_exp = pc.explain_prompt_arabic(p, headline=hl)
                    self.explain_text_widget.config(state="normal")
                    self.explain_text_widget.delete("1.0", "end")
                    self.explain_text_widget.insert("1.0", updated_exp)
                    self.explain_text_widget.config(state="disabled")

            self.after(0, _apply)

        threading.Thread(target=_worker, daemon=True).start()

    def refresh_deep_explanation(self):
        if self.current_prompt:
            self.show_status("جاري إعادة توليد الشرح عالي الدقة...", busy=True)
            self.async_load_deep_explanation(self.current_prompt, force=True)
            self.after(1500, lambda: self.show_status("جاهز", False))

    def render_variables_tab(self, prompt_text):
        for w in self.vars_scroll_frame.winfo_children():
            w.destroy()
        self.vars_entries.clear()

        variables = pc.extract_variables(prompt_text)
        if not variables:
            tk.Label(self.vars_scroll_frame, text="لا يحتوي هذا البرومبت على متغيرات تفاعلية ${...}.",
                     bg="white", fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(pady=20)
            return

        tk.Label(self.vars_scroll_frame,
                 text="تم اكتشاف متغيرات تفاعلية في هذا البرومبت. املأ القيم أدناه ثم اضغط تطبيق:",
                 bg="white", fg=TEXT_MAIN, font=("Segoe UI", 9, "bold")).pack(anchor="e", pady=(4, 10))

        for v in variables:
            row = tk.Frame(self.vars_scroll_frame, bg="white", pady=4)
            row.pack(fill="x")
            tk.Label(row, text=f"{v['name']}:", bg="white", fg=TEXT_MAIN,
                     font=("Segoe UI", 9, "bold"), width=18, anchor="e").pack(side="right", padx=6)
            ent = ttk.Entry(row, font=("Segoe UI", 10))
            if v["default"]:
                ent.insert(0, v["default"])
            ent.pack(side="right", fill="x", expand=True, padx=4)
            self.vars_entries[v["raw"]] = ent

        tk.Button(self.vars_scroll_frame, text="✓ تطبيق المتغيرات على نص البرومبت",
                  bg=ACCENT, fg="white", relief="flat", font=("Segoe UI", 9, "bold"),
                  padx=14, pady=5, cursor="hand2", command=self.apply_variables).pack(pady=12)

    def apply_variables(self):
        if not self.current_prompt:
            return
        vals = {raw: ent.get().strip() for raw, ent in self.vars_entries.items()}
        current_txt = self.prompt_text_widget.get("1.0", "end").strip()
        new_txt = pc.substitute_variables(current_txt, vals)
        self.prompt_text_widget.delete("1.0", "end")
        self.prompt_text_widget.insert("1.0", new_txt)
        self.notebook.select(self.tab_prompt)
        self.show_status("تم تطبيق قيم المتغيرات على نص البرومبت ✓")

    def save_current_edit(self):
        """حفظ التعديلات التي أجراها المستخدم على البرومبت المفتوح."""
        if not self.current_prompt:
            messagebox.showinfo("تنبيه", "اختر برومبت من القائمة أولاً.", parent=self)
            return
        new_text = self.prompt_text_widget.get("1.0", "end").strip()
        if not new_text:
            messagebox.showwarning("خطأ", "لا يمكن حفظ برومبت بنص فارغ.", parent=self)
            return

        self.current_prompt["prompt"] = new_text
        self.current_prompt["user_edited"] = True
        self.original_cache_text = new_text
        pc.tokenize_prompt(self.current_prompt)
        pc.save_store_async(self.store)

        # تحديث الشرح والمتغيرات
        self.explain_text_widget.config(state="normal")
        self.explain_text_widget.delete("1.0", "end")
        self.explain_text_widget.insert("1.0", pc.explain_prompt_arabic(self.current_prompt))
        self.explain_text_widget.config(state="disabled")
        self.render_variables_tab(new_text)

        self.refresh_list()
        self.show_status("تم حفظ تعديل البرومبت بنجاح ✓")

    def toggle_translate(self):
        """التبديل بين الترجمة العربية والنص الأصلي."""
        if not self.current_prompt:
            return

        if self.is_translated_view:
            # العودة للنص الأصلي
            self.prompt_text_widget.delete("1.0", "end")
            self.prompt_text_widget.insert("1.0", self.original_cache_text)
            self.translate_btn["text"] = "🌐 ترجمة للعربية"
            self.is_translated_view = False
            self.show_status("تمت العودة إلى النص الأصلي")
            return

        # بدء الترجمة في خيط خلفي لمنع تجمد الشاشة
        text_to_translate = self.prompt_text_widget.get("1.0", "end").strip()
        self.show_status("جاري الترجمة الفورية إلى العربية...", busy=True)
        self.translate_btn["state"] = "disabled"

        def _worker():
            translated = pc.translate_to_arabic(text_to_translate)

            def _done():
                self.prompt_text_widget.delete("1.0", "end")
                self.prompt_text_widget.insert("1.0", translated)
                self.translate_btn["text"] = "🌐 عرض النص الأصلي"
                self.translate_btn["state"] = "normal"
                self.is_translated_view = True
                self.show_status("تمت الترجمة إلى العربية بنجاح ✓", busy=False)

            self.after(0, _done)

        threading.Thread(target=_worker, daemon=True).start()

    def toggle_fav(self):
        if not self.current_prompt:
            return
        key = self.current_prompt.get("key")
        favs = self.store.setdefault("favorites", [])
        if key in favs:
            favs.remove(key)
            self.fav_btn["text"] = "☆ أضف للمفضلة"
            self.fav_btn["bg"] = "#f1f5f9"
            self.show_status("تمت الإزالة من المفضلة")
        else:
            favs.append(key)
            self.fav_btn["text"] = "★ إزالة المفضلة"
            self.fav_btn["bg"] = "#fef3c7"
            self.show_status("تمت الإضافة إلى المفضلة ★")

        pc.save_store_async(self.store)
        self.refresh_list()

    def copy_current_prompt(self):
        txt = self.prompt_text_widget.get("1.0", "end").strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.show_status("تم نسخ نص البرومبت إلى الحافظة ✓")

    def delete_current_prompt(self):
        if not self.current_prompt:
            return
        act = self.current_prompt.get("act", "")
        confirm = messagebox.askyesno(
            "تأكيد الحذف",
            f"هل أنت متأكد من رغبتك في حذف هذا البرومبت؟\n\nالدور: {act}",
            parent=self
        )
        if confirm:
            pc.delete_prompt(self.store, self.current_prompt.get("key"))
            self.current_prompt = None
            self.prompt_title_lbl["text"] = "اختر برومبت من القائمة لاستعراضه"
            self.prompt_badge_lbl["text"] = ""
            self.prompt_text_widget.delete("1.0", "end")
            self.explain_text_widget.config(state="normal")
            self.explain_text_widget.delete("1.0", "end")
            self.explain_text_widget.config(state="disabled")
            self.build_cat_buttons()
            self.refresh_list()
            self.show_status(f"تم حذف البرومبت ({act}) بنجاح ✓")

    def open_new_dialog(self):
        def _on_create(act, prompt, category, for_devs):
            new_item = pc.add_new_prompt(self.store, act, prompt, category, for_devs)
            self.build_cat_buttons()
            self.view_mode = "all"
            self.refresh_list()
            self.load_prompt_details(new_item)

        NewPromptDialog(self, _on_create)

    def open_enhance_dialog(self):
        if not self.current_prompt:
            messagebox.showinfo("اختر برومبت", "اختر برومبت من القائمة أولاً لتطويره وتحسينه.", parent=self)
            return

        def _on_save_new(act, prompt, category):
            new_item = pc.add_new_prompt(self.store, act, prompt, category, self.current_prompt.get("for_devs", False))
            self.build_cat_buttons()
            self.refresh_list()
            self.load_prompt_details(new_item)

        EnhanceDialog(self, self.current_prompt, _on_save_new)

    def show_status(self, text, busy=False):
        def _apply():
            self.status_var.set(text)
            if busy:
                self.pb.pack(side="right", padx=8)
                self.pb.start(10)
            else:
                self.pb.stop()
                self.pb.pack_forget()

        self.after(0, _apply)

    def manual_update(self):
        self.show_status("جاري فحص وتحديث البرومات من GitHub...", busy=True)
        threading.Thread(target=self._update_worker, args=(False,), daemon=True).start()

    def check_updates_quietly(self):
        threading.Thread(target=self._update_worker, args=(True,), daemon=True).start()

    def _update_worker(self, quiet: bool):
        incoming = None
        for url in pc.RAW_URLS:
            try:
                req = pc.urllib.request.Request(url, headers={"User-Agent": "promat/2.0"})
                with pc.urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                if len(data) > 1000:
                    pc.TMP_PATH.write_bytes(data)
                    incoming = pc.load_csv_rows(pc.TMP_PATH)
                    break
            except Exception:
                continue

        if incoming is None:
            if not quiet:
                self.show_status("⚠️ تعذر الاتصال بـ GitHub - يتم العمل بالنسخة المحلية")
            return

        try:
            existing = {p["key"] for p in self.store.get("prompts", [])}
            added = []
            for r in incoming:
                k = pc.key_of(r["act"], r["prompt"])
                if k not in existing:
                    r["key"] = k
                    r["new"] = True
                    r["added"] = int(time.time())
                    r["builtin"] = False
                    added.append(pc.prepare_row(r))

            def _apply():
                if added:
                    self.store["prompts"].extend(added)
                    pc.save_store_async(self.store)
                    self.build_cat_buttons()
                    self.refresh_list()
                    self.show_status(f"✓ تم إضافة {len(added)} برومبت جديد إلى المكتبة")
                else:
                    self.show_status(f"✓ المكتبة محدّثة بالكامل ({len(self.store['prompts'])} برومبت)")

            self.after(0, _apply)
        finally:
            try:
                pc.TMP_PATH.unlink()
            except OSError:
                pass


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
