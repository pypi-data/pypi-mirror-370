# Installation Guide

This guide explains how to set up and run **Fremko** using [UV](https://docs.astral.sh/uv/getting-started/installation/).

---

## 1. Install UV

Follow the official installation instructions:  
👉 [UV Installation Docs](https://docs.astral.sh/uv/getting-started/installation/)

---

## 2. Create a Project Directory

```bash
cd Desktop
mkdir fremko
cd fremko
````

---

## 3. Create a Virtual Environment

```bash
uv venv --python 3.13
```

---

## 4. Activate the Virtual Environment

* **Windows (PowerShell or CMD):**

  ```powershell
  .venv\Scripts\activate
  ```

* **Linux / macOS (bash/zsh):**

  ```bash
  source .venv/bin/activate
  ```

---

## 5. Install Fremko

```bash
uv pip install -U fremko
```

---

## 6. Run Fremko

```bash
fremko web
```

---

✅ You’re ready to use **Fremko**!
