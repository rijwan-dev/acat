def analyze_document(text):
    flags = []

    suspicious_words = ["Photoshop", "Fake", "Counterfeit", "Sample"]
    for w in suspicious_words:
        if w.lower() in text.lower():
            flags.append(f"Detected suspicious term: {w}")

    if len(text) < 50:
        flags.append("Document too short to be authentic.")

    return {
        "valid": len(flags) == 0,
        "flags": flags
    }
