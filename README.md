# <p align="center">🤖 Jarvis — Personal AI Assistant</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-beta-orange.svg" alt="status" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="python" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="license" />
  <img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="build" />
  <img src="https://img.shields.io/badge/author-Ashutosh%20Barthwal-blueviolet.svg" alt="author" />
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/000/0000000/hero-banner-placeholder.png" alt="Jarvis banner" width="900" />
</p>

---

## 🔭 Project Overview

**Jarvis** is a desktop AI assistant that accepts voice and text commands to automate tasks, fetch information, run programs, and respond conversationally using LLMs.  
Designed for personal productivity, quick automation, and learning — lightweight and configurable.

---

## ✨ Highlights

- 🎤 **Voice + Text** interaction
- 🧠 **LLM-powered responses** (OpenAI, Groq, or other providers)
- ⚙️ **Command execution**: launch apps, run scripts, open URLs
- 🗂️ **Configurable memory/context** for richer conversations
- 🔒 **Secure**: secrets stored in `.env` (and never pushed)

---

## 📸 Demo

> Replace the placeholders below with your actual GIFs/screenshots inside the repo (`assets/demo.gif`, `assets/screenshot1.png`).

<p align="center">
  <img src="assets/demo.gif" alt="Jarvis demo" width="720" />
</p>

---

## 🧭 Table of Contents

- [Quick Start](#rocket-quick-start)
- [Installation](#wrench-installation)
- [Configuration](#gear-configuration)
- [Usage](#play-button-usage)
- [Commands & Examples](#keyboard-commands--examples)
- [Architecture & Files](#file-cabinet-architecture--files)
- [Development Tips](#construction-worker-development-tips)
- [Contributing](#handshake-contributing)
- [License](#scroll-license)

---

## 🚀 Quick Start

```bash
# clone
git clone https://github.com/codePutar/share_jarvis.git
cd share_jarvis

# create venv (recommended)
python -m venv venv
# windows
venv\Scripts\activate
# mac/linux
source venv/bin/activate

# install deps
pip install -r requirements.txt

# create .env from example
cp .env.example .env
# edit .env to add your API keys (do NOT commit .env)

# run
python main.py
