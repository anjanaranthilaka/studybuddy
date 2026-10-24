import sys
import ollama


def main():
    print("Testing connection to local Ollama server...")
    try:
        models_response = ollama.list()
        # In newer ollama-python versions, models is a list of objects or dicts
        model_names = [
            m.model if hasattr(m, 'model') else m.get('name', str(m))
            for m in models_response.get('models', [])
        ]

        print("\n[SUCCESS] Connected to Ollama server.")
        print("Available local models:")
        for name in model_names:
            print(f"  - {name}")

        target_model = "qwen2.5:3b"
        matches = [m for m in model_names if target_model in m]
        if matches:
            print(f"\n[CONFIRMED] Target model '{target_model}' is available and ready for tool calling.")
        else:
            print(f"\n[WARNING] '{target_model}' was not found in local models. Did you run 'ollama pull qwen2.5:3b'?")

    except Exception as e:
        print(f"\n[ERROR] Could not connect to Ollama: {e}")
        print("Make sure Ollama is running in your Windows taskbar.")
        sys.exit(1)


if __name__ == "__main__":
    main()