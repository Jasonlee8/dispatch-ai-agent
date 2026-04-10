# DispatchAI — Agentic AI Voice System

DispatchAI is an **agentic AI system** that handles real-time customer phone calls, performs reasoning, guides conversations, extracts structured booking data, and persists results through a production-style backend architecture.

---

## 🔥 What Makes This Project Different

This is not a simple chatbot.

DispatchAI is designed as a **full AI system**, combining:

- real-time voice interaction
- multi-turn reasoning
- session memory
- system orchestration
- structured data extraction

---

## 🧠 Core Capabilities

- 📞 **Voice Interaction** — Handles live phone calls via Twilio
- 🧠 **LLM Reasoning** — Understands intent and generates responses
- 🔁 **Multi-turn Dialogue** — Maintains context across conversation
- 🧩 **Decision Making** — Controls conversation flow dynamically
- 🗂 **Booking Extraction** — Converts conversation → structured data
- 🧠 **Session Memory** — Redis-backed state management
- 📊 **Persistence Layer** — MongoDB stores calls, logs, and results

---

## 🏗 System Architecture

Customer Call (Twilio)
↓
NestJS Backend (Orchestration)
↓
Session Memory (Redis)
↓
FastAPI AI Service (LLM Reasoning)
↓
Booking Extraction
↓
MongoDB Persistence
↓
Summary Generation


## 🎯 Example AI Interaction


AI Agent:
"Sure, I can help you with that. May I have your name?"

Customer: "John"

AI Agent:
"Thanks John. Could you provide your phone number?"

Customer: "0400000000"

AI Agent:
"Got it. What service do you need? Like House Cleaning, Garden Maintenance or Plumbing?"

Customer: "Garden Maintenance"

AI Agent:
"Great. What date would you like to book?"

Customer: "15th April, 2:00pm"

AI Agent:
"Lastly, may I have your address?"

Customer: "123 Main Street"

AI Agent:
"Thank you. Let me confirm your booking:

Name: John  
Phone: 0400000000  
Service: Garden Maintenance
Date: 15th April, 2:00pm  
Address: 123 Main Street  

Is this correct?"

Customer: "Yes"

AI Agent:
"Perfect. Your booking has been confirmed. Thank you!"

→ Booking extracted:
- name: John
- phone: 0400000000
- service: Garden Maintenance
- date: 15th April, 2:00pm
- address: 123 Main Street

## 🧠 System Design Highlights

- Agent loop instead of request-response model
- Separation of orchestration (NestJS) and reasoning (FastAPI)
- Redis for short-term memory, MongoDB for persistence
- Designed for real-world constraints (voice latency, async flow)






