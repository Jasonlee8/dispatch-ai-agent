# Backend — DispatchAI

This backend implements the **agent orchestration layer** of DispatchAI, an AI system for handling real-time phone-based service bookings.

It manages voice interactions, session memory, AI reasoning, and structured data persistence.

---

## 🧠 System Role

The backend is responsible for:

- handling Twilio voice webhooks
- managing conversation sessions (Redis)
- orchestrating the agent decision loop
- calling the AI service for reasoning
- extracting structured booking data
- persisting results to MongoDB

---

## 🏗 Architecture

Customer Call (Twilio)
↓
NestJS Telephony Controller
↓
CallProcessorService (Agent Loop)
↓
Session Memory (Redis)
↓
FastAPI AI Service (LLM Reasoning)
↓
Booking Extraction
↓
MongoDB Persistence


---

## 🔁 Agent Flow

listen → understand → decide → respond → repeat


### Flow Breakdown

1. **Call Start**
   - Twilio triggers `/api/telephony/voice`
   - Session initialized in Redis

2. **Conversation Loop**
   - Customer speech → Twilio STT
   - Input sent to AI service (`/ai/conversation`)
   - AI returns response + next action
   - System decides whether to continue or end

3. **Call Completion**
   - Twilio triggers `/api/telephony/status`
   - System:
     - generates summary
     - stores transcript
     - saves booking data
     - clears session

---

## 🧩 Key Components

### CallProcessorService
- core agent loop
- controls conversation flow
- handles decision making

### SessionHelper (Redis)
- stores conversation history
- maintains session state
- enables multi-turn memory

### AiIntegrationService
- communicates with FastAPI AI service
- handles LLM responses and summaries

### CallDataPersistenceService
- saves call logs
- stores transcripts
- persists structured booking data

---

## 📡 Key Endpoints

### Telephony (Twilio)

- `POST /api/telephony/voice`
- `POST /api/telephony/gather`
- `POST /api/telephony/status`

### AI Integration

- `POST /api/ai/conversation`
- `POST /api/ai/summary`

---

## ⚙️ Tech Stack

- NestJS (orchestration layer)
- Redis (session memory)
- MongoDB (persistence)
- FastAPI (AI reasoning)
- Twilio (voice interface)

---

## 🚀 Run Locally

### Start services

```bash
docker compose up -d

-- Start backend
pnpm install
pnpm dev


--Start AI service
cd ai
uv sync
uv run fastapi dev app/main.py