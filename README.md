# 🤖 Agentic GTM System (AI Sales Follow-up Automation)

## 🧠 Overview
This project simulates a real-world **Go-To-Market (GTM) follow-up automation system** using Python.  
It reads CRM data from a CSV file and automatically decides whether to follow up with leads through **WhatsApp** or **Voice calls (TTS)**.

The system uses **offline voice synthesis** (`pyttsx3`) to generate realistic audio follow-ups without requiring internet or API keys.

---

## ⚙️ Features
- Reads lead data from a CRM CSV file
- Automatically decides if a follow-up is due (last contact > 3 days)
- Chooses the right channel (WhatsApp or Voice)
- Simulates message sending or generates a voice call audio
- Logs all outcomes to a CSV file for reporting

---

## 📂 Folder Structure
