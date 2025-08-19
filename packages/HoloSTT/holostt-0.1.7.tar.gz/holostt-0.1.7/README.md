
---

# HoloSTT

## Overview

**HoloSTT** is a modern, thread-safe speech recognition and input manager for Python applications.
It unifies active speech, ambient listening, and keyboard input into a single, production-ready interface for any AI-driven project.

**Highlights:**

* **Multi-modal input:** Seamlessly combine voice (active/ambient) and keyboard input.
* **No vendor lock-in:** Works with any skill set, AI stack, or backend logic.
* **Advanced audio handling:** Adaptive noise management, energy thresholds, platform-aware volume support.
* **Thread-safe singleton:** Designed for multi-threaded and interactive desktop, assistant, and automation apps.
* **Real-time text processing:** Built-in cleaning, comparison, and input filtering utilities.

---

## Why HoloSTT?

Typical speech recognition modules often come with limitations:

* Limited to just microphone input, or just keyboard.
* Lack of fallback modes, or forced use of a single speech engine.
* Not suitable for multi-threaded apps, or lacking input state management.

**HoloSTT** solves these problems by:

* Offering both **active (“push-to-talk”)** and **ambient (always-on)** listening, with instant keyboard fallback.
* Providing a **centralized, extensible interface** for all input and recognition events.
* Supporting robust error handling, state tracking, and dynamic configuration—ready for modern AI workflows.

---

## Key Features

* **Flexible Audio Capture:**
  Toggle between active/ambient listening or switch to keyboard input instantly.

* **Dynamic Noise and Volume Handling:**
  Automatically adapts to background noise and adjusts thresholds for clear, accurate recognition.

* **Centralized State & Properties:**
  Track commands, input modes, timeouts, and all key settings in one place.

* **Customizable Input Processing:**
  Clean and filter input text, apply replacements, compare similarity, and trigger actions.

* **Robust Error Handling:**
  Handles microphone, audio, and network exceptions gracefully.

* **Production-Ready:**
  Built for real-world, scalable AI systems.

---

## How It Works

1. **Call the HoloSTT manager** in your application.
2. **Select input mode:** active voice, ambient voice, or keyboard.
3. **Process and clean recognized text** automatically.
4. **Use output directly** for commands, automations, or AI skills.

---

## FAQ

**Q: Does HoloSTT require a specific folder or class naming?**
A: No. Organize your project and input logic as you see fit.

**Q: Can I use my own text cleaning or filtering?**
A: Yes. HoloSTT exposes all processing utilities and is easy to extend.

**Q: Is it production-ready and thread-safe?**
A: Yes. The singleton implementation ensures safe multi-threaded operation.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil