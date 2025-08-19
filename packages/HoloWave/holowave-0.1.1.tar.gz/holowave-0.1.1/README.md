﻿
---

# HoloWave

## Overview

**HoloWave** is a modern, thread-safe audio playback manager for Python applications.
It provides robust, low-latency sound signaling, channel management, and cross-platform fallbacks for automation, agent systems, and productivity tools.

**Highlights:**

* **Low-latency sound playback:** Instantly play any supported audio file with minimal delay.
* **Thread-safe singleton:** Designed for multi-threaded, interactive, or automated applications.
* **Custom sound mapping:** Associate sounds with keys or events for rapid notification and feedback.
* **Automatic cross-platform fallback:** Produces a system beep if audio hardware or files are unavailable.
* **Flexible channel management:** Control mixer channels, output routing, and concurrency with ease.

---

## Why HoloWave?

Standard sound modules are often limited to blocking playback, lack robust error handling, or require boilerplate for channel management.

**HoloWave** solves these problems by:

* Providing a **centralized, extensible interface** for all sound playback.
* Robust error handling and fallback signaling on any OS.
* Supporting channel-based playback for overlapping or grouped sounds.
* Ensuring safe operation in multi-threaded or interactive environments.

---

## Key Features

* **Simple Sound Playback:**
  Play any loaded audio file by key, with non-blocking channel control.

* **Cross-Platform Support:**
  Uses `pygame` for playback, with built-in system beep fallback.

* **Custom Sound Mapping:**
  Map sound files to any integer or string keys for quick event-driven playback.

* **Thread-Safe Singleton:**
  Safe to use across threads or in long-running service applications.

* **Robust Error Handling:**
  Handles missing files, mixer errors, and hardware issues gracefully.

---

## How It Works

1. **Instantiate HoloWave** in your Python application.
2. **Map sounds to keys or events** in your app logic.
3. **Trigger playback** by calling `getSound(key)` from any thread or event handler.
4. **Automatically falls back** to system beep if playback fails.

---

## FAQ

**Q: Does HoloWave require a specific folder or class naming?**
A: No. Organize your project and sound files as you see fit.

**Q: Can I use HoloWave for overlapping or concurrent sounds?**
A: Yes. Channel management allows for multiple simultaneous sounds.

**Q: Is HoloWave thread-safe and production-ready?**
A: Yes. The singleton implementation and locking ensure safe use in all environments.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgments

Project by:
- Tristan McBride Sr.
- Sybil