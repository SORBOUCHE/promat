# -*- coding: utf-8 -*-
"""برومات - prompt matcher: finds the best prompt for any request from prompts.chat library."""
import json
import re
import sys
import time
from pathlib import Path

import prompts_core as pc

BASE = Path(__file__).parent
CSV_PATH = BASE / "prompts.csv"
OUT_DIR = BASE / "generated_prompts"


def load_prompts():
    """تحميل متجر البرومات موحداً مع التطبيق."""
    store = pc.load_store()
    return store.get("prompts", [])


def create_prompt(best, request):
    profile = re.sub(r"^\W+|\W+$", "", re.sub(r"\s{2,}", " ", request))
    return {
        "act": best["act"],
        "prompt": best["prompt"],
        "for_devs": best.get("for_devs", False),
        "instantiated": (
            "أنت الآن بصدد العمل بالدور التالي وهو الأنسب لطلبك:\n"
            f"{best['act']}\n\n{best['prompt']}\n\n"
            f"وهذا هو الطلب الذي تريد تنفيذه باستخدام هذا الدور: {profile}"
        ),
    }


def save_generated(result, request):
    OUT_DIR.mkdir(exist_ok=True)
    fname = OUT_DIR / f"prompt_{int(time.time())}.txt"
    content = (
        f"الدور: {result['act']}\n"
        f"{'-' * 60}\n"
        f"{result['prompt']}\n"
        f"{'-' * 60}\n"
        f"البرومبت المنشأ الكامل المتعلق بطلبك:\n"
        f"{result['instantiated']}\n\n"
        f"الطلب الأصلي: {request}\n"
    )
    fname.write_text(content, encoding="utf-8-sig")
    return fname


def run(request, as_json=False):
    prompts = load_prompts()
    results = pc.search_prompts(prompts, request)[:5]

    if as_json:
        payload = []
        for _, p in results:
            r = create_prompt(p, request)
            payload.append({"act": r["act"], "prompt": r["prompt"], "for_devs": r["for_devs"]})
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not results or results[0][0] == 0:
        print("لم أجد برومبت مناسباً لهذا الطلب. جرّب كلمات أخرى.")
        return

    top_score, best = results[0]
    result = create_prompt(best, request)
    print("=" * 60)
    print(f"أفضل برومبت يوافق طلبك: {result['act']}")
    print("=" * 60)
    print(result["instantiated"])
    print("=" * 60)
    fname = save_generated(result, request)
    print(f"الحفظ في: {fname}")
    print("")
    print("بدائل:")
    for score, p in results[1:]:
        if score == 0:
            break
        print(f"  - {p['act']}")


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    if as_json:
        args.remove("--json")
    request = " ".join(args).strip()

    if request:
        run(request, as_json)
        return

    print("مكتبة البرومبتات (prompts.chat) — أدخل طلبك، وسيُختار أفضل برومبت ويُنشئ لك.")
    try:
        while True:
            request = input("\nاكتب طلبك (أو exit للخروج): ").strip()
            if not request or request.lower() in ("exit", "quit", "q"):
                break
            run(request)
    except (EOFError, KeyboardInterrupt):
        print("")


if __name__ == "__main__":
    main()
