import unicodedata
import re

def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text))
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text

def test_security_normalization():
    test_cases = [
        ("Normal Name", "normal-name"),
        ("Maestría en Química", "maestria-en-quimica"),
        ("Dangerous / <script> alert(1) </script>", "dangerous-script-alert-1-script"),
        ("../../../etc/passwd", "etc-passwd"),
        ("   Spaces   and --- Hyphens ---   ", "spaces-and-hyphens"),
        ("Emoji 🚀 and Symbols @#$%", "emoji-and-symbols"),
        ("Injection'; DROP TABLE users; --", "injection-drop-table-users"),
    ]
    
    for input_text, expected in test_cases:
        result = slugify(input_text)
        print(f"Input: '{input_text}' -> Result: '{result}'")
        # Regex to check only [a-z0-9-]
        assert re.match(r'^[a-z0-9-]*$', result), f"SECURITY VIOLATION: '{result}' contains illegal characters"
        print("  Status: OK")

if __name__ == "__main__":
    test_security_normalization()
    print("\nALL SECURITY TESTS PASSED: Slugs are restricted to [a-z0-9-]")
