import hashlib

import streamlit as st
import google.generativeai as genai


# ==================================================
# Medicare Compass
# Bilingual Output Layer
#
# 規則：
# - English：不需要額外產生雙語版本
# - 非 English：按下 Bilingual 後才呼叫 AI
# - 使用者語言在上，English 在下
# - AI 只做翻譯 / 雙語重排，不重新分析 Medicare
# - 結果存 Session State，避免每次 rerun 都重新呼叫 AI
# ==================================================


SUPPORTED_LANGUAGES = {
    "繁體中文": "Traditional Chinese",
    "簡體中文": "Simplified Chinese",
    "Español": "Spanish",
    "한국어": "Korean",
}


PREFERRED_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]


# ==================================================
# Basic helpers
# ==================================================

def is_english(current_lang):
    return current_lang == "English"


def supports_bilingual(current_lang):
    """
    English 不需要雙語版本。
    其他目前支援的語言才顯示 Bilingual 功能。
    """
    return current_lang in SUPPORTED_LANGUAGES


# ==================================================
# Cache
# ==================================================

def _content_hash(source_text, current_lang):
    """
    用內容 + 語言產生 hash。

    如果 Summary 內容改變，
    舊的雙語結果就不會被錯誤重用。
    """
    raw = f"{current_lang}\n{source_text or ''}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def get_cached_bilingual(
    cache_name,
    source_text,
    current_lang,
):
    """
    找出目前內容是否已經有產生過雙語版本。
    """

    cache_root = st.session_state.get(
        "_bilingual_cache",
        {}
    )

    cache_item = cache_root.get(cache_name)

    if not cache_item:
        return None

    current_hash = _content_hash(
        source_text,
        current_lang,
    )

    if cache_item.get("hash") != current_hash:
        return None

    return cache_item.get("content")


def _save_bilingual_cache(
    cache_name,
    source_text,
    current_lang,
    bilingual_content,
):
    """
    將 AI 完成的雙語版本存入 Session State。
    """

    if "_bilingual_cache" not in st.session_state:
        st.session_state["_bilingual_cache"] = {}

    st.session_state["_bilingual_cache"][cache_name] = {
        "hash": _content_hash(
            source_text,
            current_lang,
        ),
        "language": current_lang,
        "content": bilingual_content,
    }


def clear_bilingual_cache(cache_name=None):
    """
    Reset conversation 時可以呼叫。

    cache_name=None：
        全部清掉

    cache_name="summary"：
        只清 Summary
    """

    if cache_name is None:
        st.session_state.pop(
            "_bilingual_cache",
            None,
        )
        return

    cache_root = st.session_state.get(
        "_bilingual_cache",
        {}
    )

    cache_root.pop(
        cache_name,
        None,
    )


# ==================================================
# Gemini model selection
# ==================================================

def _get_available_models():
    """
    沿用目前 Medicare Compass ai_engine 的模型 fallback 邏輯。
    """

    valid_models = []

    try:
        available_models = {}

        for model in genai.list_models():

            if (
                "generateContent"
                in model.supported_generation_methods
            ):
                model_id = model.name.replace(
                    "models/",
                    "",
                )

                available_models[model_id] = model.name

        valid_models = [
            available_models[model_id]
            for model_id in PREFERRED_MODELS
            if model_id in available_models
        ]

    except Exception:
        pass

    if not valid_models:
        valid_models = [
            f"models/{model_id}"
            for model_id in PREFERRED_MODELS
        ]

    return valid_models


# ==================================================
# AI prompt
# ==================================================

def _build_translation_prompt(
    source_text,
    current_lang,
):
    """
    這裡非常重要：
    AI 只能翻譯，不可以重新做 Medicare 分析。
    """

    language_name = SUPPORTED_LANGUAGES.get(
        current_lang,
        current_lang,
    )

    return f"""
You are the bilingual document translator for Medicare Compass.

YOUR ONLY TASK:
Convert the provided Medicare Compass output into a bilingual document
for both the user and an English-speaking U.S. Medicare professional.

SOURCE LANGUAGE:
{language_name}

TARGET FORMAT:
{language_name} first
English immediately below it

CRITICAL RULES:

1. TRANSLATION ONLY.
Do NOT perform a new Medicare analysis.
Do NOT add recommendations.
Do NOT remove recommendations.
Do NOT change eligibility conclusions.
Do NOT introduce new facts.

2. Preserve the meaning of the original content exactly.

3. Every meaningful heading, sentence, bullet point, label, or recommendation
must be followed immediately by its English equivalent.

4. Keep the original-language content first and the English translation second.

5. Preserve Markdown structure whenever possible:
- headings
- bullet points
- bold text
- numbered lists
- links

6. Preserve all of the following exactly:
- dates
- ZIP Codes
- dollar amounts
- URLs
- Medicare plan names
- Part A
- Part B
- Part C
- Part D
- Original Medicare
- Medicare Advantage
- Medigap
- IEP
- SEP
- SHIP
- SSA
- CMS

7. Do not translate official program names into misleading substitutes.
You may explain them in the target language, but preserve the official English term.

8. Do NOT output commentary such as:
"Here is the translation"
"Bilingual version"
"Translation:"
or any explanation about your work.

9. Do NOT output JSON.

10. Do NOT wrap the result in a Markdown code block.

11. The result must be suitable for:
- on-screen preview
- TXT download
- printing / PDF
- showing directly to a SHIP counselor

SOURCE DOCUMENT:

--- START SOURCE ---

{source_text}

--- END SOURCE ---
""".strip()


# ==================================================
# Generate bilingual document
# ==================================================

def generate_bilingual_version(
    source_text,
    current_lang,
    cache_name,
):
    """
    產生雙語版本並存進 Session State。

    回傳：
        bilingual Markdown string

    如果 English：
        直接回原文，不呼叫 AI。
    """

    source_text = str(
        source_text or ""
    ).strip()

    if not source_text:
        raise ValueError(
            "Source content is empty."
        )

    # English 不需要另外翻譯
    if is_english(current_lang):
        return source_text

    if not supports_bilingual(current_lang):
        raise ValueError(
            f"Unsupported bilingual language: {current_lang}"
        )

    # --------------------------------------------------
    # 先找 Cache
    # --------------------------------------------------

    cached = get_cached_bilingual(
        cache_name,
        source_text,
        current_lang,
    )

    if cached:
        return cached

    # --------------------------------------------------
    # 準備 AI Prompt
    # --------------------------------------------------

    prompt = _build_translation_prompt(
        source_text,
        current_lang,
    )

    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
    )

    last_exception = None

    # --------------------------------------------------
    # 模型 fallback
    # --------------------------------------------------

    for model_name in _get_available_models():

        try:

            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
            )

            response = model.generate_content(
                prompt
            )

            result = str(
                response.text or ""
            ).strip()

            # --------------------------------------------------
            # 防止模型偶爾包 ```markdown
            # --------------------------------------------------

            if result.startswith("```markdown"):
                result = result[len("```markdown"):].strip()

            elif result.startswith("```"):
                result = result[3:].strip()

            if result.endswith("```"):
                result = result[:-3].strip()

            if not result:
                raise ValueError(
                    "Gemini returned empty bilingual content."
                )

            # --------------------------------------------------
            # 存 Cache
            # --------------------------------------------------

            _save_bilingual_cache(
                cache_name,
                source_text,
                current_lang,
                result,
            )

            return result

        except Exception as exc:
            last_exception = exc
            continue

    # --------------------------------------------------
    # 所有模型都失敗
    # --------------------------------------------------

    raise RuntimeError(
        "Unable to generate the bilingual version."
    ) from last_exception


# ==================================================
# 以下保留原本 formatter
# 避免 main_ai.py 若已 import 這些函式時發生錯誤
# ==================================================

def bilingual_text(
    current_lang,
    english_text,
    localized_text=None,
):
    english_text = str(
        english_text or ""
    ).strip()

    localized_text = str(
        localized_text or ""
    ).strip()

    if is_english(current_lang):
        return english_text

    if not localized_text:
        return english_text

    if localized_text == english_text:
        return english_text

    return (
        f"{localized_text}\n\n"
        f"{english_text}"
    )


def bilingual_inline(
    current_lang,
    english_text,
    localized_text=None,
):
    english_text = str(
        english_text or ""
    ).strip()

    localized_text = str(
        localized_text or ""
    ).strip()

    if is_english(current_lang):
        return english_text

    if not localized_text:
        return english_text

    if localized_text == english_text:
        return english_text

    return (
        f"{localized_text}  \n"
        f"{english_text}"
    )


def bilingual_heading(
    current_lang,
    english_heading,
    localized_heading=None,
    level=4,
):
    english_heading = str(
        english_heading or ""
    ).strip()

    localized_heading = str(
        localized_heading or ""
    ).strip()

    level = max(
        1,
        min(int(level), 6),
    )

    prefix = "#" * level

    if is_english(current_lang):
        return f"{prefix} {english_heading}"

    if not localized_heading:
        return f"{prefix} {english_heading}"

    if localized_heading == english_heading:
        return f"{prefix} {english_heading}"

    return (
        f"{prefix} {localized_heading}\n"
        f"{prefix} {english_heading}"
    )


def bilingual_bullet(
    current_lang,
    english_text,
    localized_text=None,
):
    english_text = str(
        english_text or ""
    ).strip()

    localized_text = str(
        localized_text or ""
    ).strip()

    if is_english(current_lang):
        return f"- {english_text}"

    if not localized_text:
        return f"- {english_text}"

    if localized_text == english_text:
        return f"- {english_text}"

    return (
        f"- {localized_text}\n"
        f"  {english_text}"
    )