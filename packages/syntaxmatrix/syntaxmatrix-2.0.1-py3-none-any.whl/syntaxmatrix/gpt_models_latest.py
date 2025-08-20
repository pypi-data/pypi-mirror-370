# --- Helper: robustly extract text from Responses API objects ---
def extract_output_text(resp) -> str:
    # Fast path
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text.strip()
    # Fallback: parse .output for message->content blocks
    text_parts = []
    output = getattr(resp, "output", None) or []
    for item in output:
        if getattr(item, "type", "") != "message":
            continue
        for block in getattr(item, "content", []) or []:
            btype = getattr(block, "type", "")
            if btype in ("output_text", "text"):
                t = (getattr(block, "text", "") or "").strip()
                if t:
                    text_parts.append(t)
    return "\n".join(text_parts).strip()


def set_args(model, instructions, input, previous_id=None, store=False, reasoning_effort="minimal", verbosity="low"):

    base_params = {
            "model": model,
            "instructions": instructions,
            "input": input,
            "previous_response_id": previous_id,
            "store": store,
            "truncation": "auto",
    }
    if model == "gpt-5-chat-latest":
        args = base_params
    else:
        args = {**base_params,
                "reasoning": {"effort": reasoning_effort},
                "text": {"verbosity": verbosity}
            }
    return args