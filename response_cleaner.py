import re

def clean_response(text: str) -> str:
    """第一層：正則表達式過濾已知的系統標籤與 Prompt 殘留"""
    if not text:
        return ""
    
    # 確保把各種可能的思考與草稿標籤都過濾掉
    patterns = [
        r"<(think|thought)>.*?</\1>",
        r"User Profile:.*?\n",
        r"Key Constraint Checklist:.*?\n",
        r"Personal Medicare Timeline:.*?\n",
        r"Persona/Role:.*?\n",
        r"\(Self-Correction\):.*?\n",
        r"Final Content Plan:.*?\n",
        r"Comparison Table:.*?\n",
        r"Key decision making question:.*?\n",
        r"^\s*[\*\-]?\s*Directly print.*$",
        r"^\s*[\*\-]?\s*Markdown bullets\?.*$",
        r"^\s*[\*\-]?\s*Final Polish\..*$",
        r"^\s*[\*\-]?\s*Self-Correction:.*$",
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
    return cleaned.strip()

def sanitize_ai_output(raw_text, target_lang="English"):
    """第二層安全網 (Task 1.2)：利用特徵錨點進行強制截斷與逐行清洗"""
    if not raw_text:
        return ""

    # 擴增錨點清單，包含問候語與常見的 Markdown 大標題
    content_anchors = [
        "### ", "Hello", "Hi!", "Welcome", "Here is", "To give you", 
        "您好", "你好", "為您整理", "系统已为您", "¡Hola", "Aquí tiene",
        "안녕하세요", "여기", "Path 1:", "Path 2:", "Option 1:"
    ]

    # 尋找「最早出現」的錨點，將錨點前面的預熱廢話全部丟棄
    first_anchor_idx = -1
    for anchor in content_anchors:
        idx = raw_text.find(anchor)
        if idx != -1:
            if first_anchor_idx == -1 or idx < first_anchor_idx:
                first_anchor_idx = idx
                
    if first_anchor_idx != -1:
        raw_text = raw_text[first_anchor_idx:]

    # 逐行檢查，濾掉不需要的殘留指令
    lines = raw_text.split("\n")
    clean_lines = []
    bad_keywords = [
        "*Review against rules:*", "*Final Polish:*", "*Correction on",
        "*Final Content Construction:*", "*Ready.*", "*One more check:*",
        "*Constraint Check:*", "*Final check on rules:*", "User's goal:",
        "Constraint:", "Instruction:", "Concise bullet points?", "No drafts"
    ]

    for line in lines:
        stripped = line.strip()
        if any(bad.lower() in stripped.lower() for bad in bad_keywords):
            continue
        clean_lines.append(line)

    final_text = "\n".join(clean_lines).strip()
    
    # 🚨 Task 1.3: 絕對不回傳髒掉的 raw_text，如果 final_text 為空，回傳 "" 讓前端去拿 Fallback
    return final_text if final_text else ""