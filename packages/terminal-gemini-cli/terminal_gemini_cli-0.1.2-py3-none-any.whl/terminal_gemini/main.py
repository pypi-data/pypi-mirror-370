def main():
    import sys
    prompt = " ".join(sys.argv[1:]) or "Hello from Gemini CLI!"
    print(f"[Gemini] {prompt}")
