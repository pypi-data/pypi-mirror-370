## Fremko

Android device control framework with LLM-powered agents, a WebSocket control plane, and a FastAPI web UI. Run the server on your computer, connect your phone, and automate interactions (tap, swipe, input, launch apps), stream the screen, and drive goals with your preferred LLM.

## Features

- Control Android devices over WebSocket via an on-device accessibility service (Fremko Portal)
- Built-in CLI to run a control server or a combined web UI + HTTP API
- FastAPI endpoints and a minimal web dashboard for live preview and actions
- Pluggable LLM backends (OpenAI, Anthropic, Google GenAI, DeepSeek, Ollama) via `llama-index`

## Prerequisites

- Python 3.10+
- `adb` available in your `PATH`. (Optional)
- An Android device with Developer Options + USB debugging enabled. (Optional)
- Fremko Portal app (see link below) 

## Installation

You have a few options for installing **fremko**:

### Option 1: Recommended (using `uv`)
See [UV_INSTALLATION.md](UV_INSTALLATION.md)

---

### Option 2: Easy (from PyPI)
```bash
pip install fremko
```

---

### Option 3: Development (from source)

```bash
# Requires Python 3.10+
git clone https://github.com/johnmalek312/fremko.git
cd fremko
pip install -e .   # or: uv pip install -e .   # if you are using uv
```

## Quickstart

1) Prepare your Android device
- Enable Developer Options and USB debugging.
- Install and set up the Fremko Portal app: `https://www.github.com/johnmalek312/fremko-portal`
- From your computer, you can also try:
```bash
fremko setup   # installs the APK (if needed) and opens Accessibility settings to enable the Portal
fremko enable  # grants accessibility permission to the Fremko Portal app
fremko ping    # verifies the Portal is installed + reachable
```

2) Start the server on your computer
```bash
fremko web
```
Then open `http://localhost:8080` to view the dashboard.

3) Connect the phone to the server
- In the Fremko Portal app on the phone, set the server URL to `ws://<your-computer-ip>:10001`
- Once connected, the device appears under Clients in the web UI

## CLI

```bash
# Run WebSocket server only
fremko server [--provider GoogleGenAI] [--model models/gemini-2.5-flash] [--ws-port 10001]

# Run server + web UI/HTTP API (recommended)
fremko web [--ws-port 10001] [--http-port 8080] [--host 0.0.0.0]

# ADB helpers
fremko devices
fremko connect <ip:port>
fremko disconnect <ip:port>

# Device readiness
fremko enable                  # gives accessibility permission to the Fremko Portal app on your device
fremko setup [-d SERIAL]       # installs the APK (if needed) and enables the Portal accessibility service
fremko ping  [-d SERIAL]       # verifies the Portal is installed + reachable
```

Common options: `--provider`, `--model`, `--temperature`, `--steps`, `--base_url`, `--api_base`, `--reasoning`, `--reflection`, `--tracing`, `--debug`.

## Web UI and HTTP API

When you run `fremko web`, a FastAPI app serves the dashboard and a simple API:

- `GET /api/clients` — list connected clients
- `GET /api/clients/{id}` — client details
- `POST /api/clients/{id}/goal` — start an agent goal
- `GET /api/clients/{id}/screenshot` — latest screenshot
- `GET /api/clients/{id}/state` — accessibility tree + phone state
- `POST /api/clients/{id}/tap` — tap at coordinates
- `POST /api/clients/{id}/swipe` — straight-line swipe
- `POST /api/clients/{id}/gesture_path` — arbitrary path gesture
- `POST /api/clients/{id}/input` — input text
- `POST /api/clients/{id}/key` — press Android keycode
- `POST /api/clients/{id}/start_app` — start an app
- `POST /api/clients/{id}/stream/{start|update|stop}` — control device-to-server video stream
- `GET /ws/preview/{id}` — WebSocket with JPEG frames for browser preview

Preview streaming is backed by H.264 decoding on the server and JPEG frames to the browser.

## Configuration (LLMs)

LLM selection and configuration are handled through `llama-index` integrations. Set relevant environment variables for your provider:

- Google GenAI: `GOOGLE_API_KEY`
- OpenAI / compatible: `OPENAI_API_KEY`, optional `OPENAI_BASE_URL`
- Anthropic: `ANTHROPIC_API_KEY`
- DeepSeek: `DEEPSEEK_API_KEY`
- Ollama: ensure the local Ollama service is running and configure base URL if needed

Defaults: provider `GoogleGenAI`, model `models/gemini-2.5-flash`.

## Troubleshooting

- No clients in UI: ensure the phone Portal is connected to `ws://<host>:10001` and the server is reachable from the device’s network.
- Accessibility errors: open Accessibility settings on the phone and enable the Fremko Portal service.
- Screenshots/stream not working: check that screen-capture permissions are granted in the Portal, then re-enable if needed.
- ADB device not found: verify `adb devices`, USB debugging, authorization prompts, and cables/drivers.

## License

MIT