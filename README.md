# DispatchAI - AI Agent Service Booking Platform

An intelligent, autonomous AI Agent system that handles customer service bookings through natural voice conversations. Built with Agentic AI principles, DispatchAI features a voice-based AI agent that autonomously manages the entire booking process from initial contact to confirmation.

## What is DispatchAI?

DispatchAI is an **Agentic AI system** that deploys voice-activated AI agents to handle customer phone calls for service-based businesses. The AI agent operates autonomously to:

- **Answer incoming calls** and engage customers in natural conversation
- **Understand customer needs** through LLM-powered reasoning
- **Recommend appropriate services** based on context and availability
- **Collect booking information** through conversational dialogue
- **Make decisions** about conversation flow (continue, clarify, or conclude)
- **Maintain context** across the entire conversation session
- **Generate summaries** of customer interactions and booking details

### Agentic AI Features

✅ **Autonomous Operation** - Agent independently manages entire conversation lifecycle
✅ **Contextual Memory** - Redis-backed session management maintains conversation history
✅ **Goal-Oriented Behavior** - Guides customers toward successful service bookings
✅ **Reasoning & Understanding** - LLM-powered natural language comprehension
✅ **Dynamic Decision Making** - Determines next actions based on conversation context
✅ **Multi-turn Conversations** - Handles complex back-and-forth dialogue

## Architecture

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────┐
│                     Customer Phone Call                      │
│                         (Twilio)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              NestJS Backend (Agent Orchestration)            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CallProcessorService - Agent Core Loop              │   │
│  │  • Conversation state management                     │   │
│  │  • Context loading (services, company info)          │   │
│  │  • Decision making (gather/hangup)                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │  SessionHelper - Agent Memory (Redis)                 │  │
│  │  • Conversation history                               │  │
│  │  • Business context (company, services)               │  │
│  │  • Session state                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         Python AI Service (LLM Reasoning Engine)             │
│  • Conversation processing (/ai/conversation)                │
│  • Intent understanding & response generation                │
│  • Summary generation (/ai/summary)                          │
│  • Powered by LangChain + OpenAI                             │
└──────────────────────────────────────────────────────────────┘
```

### Agent Workflow

```
1. Call Received → Initialize Agent Session
2. Load Context → Fetch company info, available services
3. Welcome Customer → AI introduces business and services
4. Conversation Loop:
   ├─ Listen → Capture customer speech (Twilio)
   ├─ Understand → LLM processes intent
   ├─ Decide → Determine next action
   └─ Respond → AI generates natural reply
5. Booking Complete → Generate summary
6. End Call → Persist data to MongoDB
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent Orchestration** | NestJS + TypeScript | Conversation flow control, state management |
| **AI Reasoning** | Python FastAPI + LangChain + OpenAI | Natural language understanding & generation |
| **Agent Memory** | Redis | Short-term session storage, conversation context |
| **Persistent Storage** | MongoDB + Mongoose | Call logs, transcripts, bookings, user data |
| **Voice Interface** | Twilio Voice API | Phone system integration, speech-to-text |
| **Admin Dashboard** | Next.js 15 + Material-UI + Redux | Business management interface |
| **Payment** | Stripe | Subscription billing |

## Project Structure

```
dispatch-ai/
├── backend/                    # NestJS API & Agent Backend
│   ├── src/modules/
│   │   ├── telephony/         # AI Agent core implementation
│   │   │   ├── services/
│   │   │   │   ├── call-processor.service.ts      # Agent orchestration
│   │   │   │   ├── ai-integration.service.ts      # LLM interface
│   │   │   │   └── call-data-persistence.service.ts
│   │   │   ├── helpers/
│   │   │   │   ├── session.helper.ts              # Agent memory management
│   │   │   │   └── welcome-message.helper.ts
│   │   │   └── repositories/
│   │   │       └── session.repository.ts          # Redis operations
│   │   ├── service-booking/   # Booking management
│   │   ├── calllog/           # Call records
│   │   ├── transcript/        # Conversation transcripts
│   │   ├── company/           # Business entities
│   │   ├── auth/              # Authentication
│   │   └── subscription/      # Billing
│   └── ai/                    # Python AI Service (FastAPI)
│       ├── app/
│       │   ├── api/
│       │   │   ├── call.py            # /ai/conversation endpoint
│       │   │   └── summary.py         # /ai/summary endpoint
│       │   └── main.py
│       └── pyproject.toml
│
└── frontend/                   # Next.js Admin Dashboard
    └── src/
        ├── app/               # Next.js App Router
        ├── features/          # Feature modules
        └── components/        # Shared components
```

## Getting Started

### Prerequisites

- **Node.js** v16+
- **Python** 3.11+
- **pnpm** (package manager)
- **Docker & Docker Compose**
- **MongoDB**
- **Redis**
- **uv** (Python package manager)

### Quick Start with Docker

```bash
# Clone the repository
git clone <your-repo-url>
cd dispatch-ai

# Start all services
cd backend
docker compose up -d --build

# View logs
docker compose logs -f api
docker compose logs -f dispatchai-ai
```

Services will be available at:
- Backend API: `http://localhost:4000`
- API Documentation: `http://localhost:4000/api/docs`
- AI Service: `http://localhost:8000`
- AI Service Docs: `http://localhost:8000/docs`

### Local Development

#### Backend (NestJS)

```bash
cd backend
pnpm install
pnpm dev                    # Development server with hot reload
pnpm build                  # Production build
pnpm test                   # Run tests
pnpm lint                   # Format and lint code
```

#### AI Service (Python)

```bash
cd backend/ai

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and run
uv sync
uv run fastapi dev app/main.py
```

#### Frontend (Next.js)

```bash
cd frontend
pnpm install
pnpm dev                    # Development server at http://localhost:3000
pnpm build                  # Production build
```

## Key Features

### For Business Owners

- **24/7 Automated Phone Answering** - AI agent never misses a call
- **Intelligent Booking Management** - Calendar integration and scheduling
- **Multi-location Support** - Manage services across different branches
- **Subscription Plans** - Tiered pricing via Stripe
- **Analytics Dashboard** - Call logs, transcripts, and performance metrics
- **Custom Greetings** - Personalize your AI agent's introduction

### For Developers

- **Modular Architecture** - Clean separation of concerns
- **TypeScript Path Aliases** - Import with `@/` prefix
- **Comprehensive API Docs** - Swagger/OpenAPI documentation
- **Session Management** - Redis-backed conversation state
- **Event-Driven Design** - Webhook-based Twilio integration
- **Type Safety** - Full TypeScript coverage with strict mode

## API Endpoints

### Agent Endpoints (Backend)

- `POST /api/telephony/voice` - Incoming call handler (Twilio webhook)
- `POST /api/telephony/gather` - Speech processing (Twilio webhook)
- `POST /api/telephony/status` - Call status updates (Twilio webhook)

### AI Service Endpoints

- `POST /api/ai/conversation` - LLM conversation processing
- `POST /api/ai/summary` - Generate call summaries
- `GET /api/ai/health` - Health check

### Business API

- `POST /api/service-booking` - Create booking
- `GET /api/service-booking` - List bookings
- `GET /api/calllog` - Call history
- `GET /api/transcript/:id` - Conversation transcript

## Testing

```bash
cd backend

# Run all tests
pnpm test

# Run specific test suites
pnpm test:unit              # Unit tests
pnpm test:integration       # Integration tests
pnpm test:e2e               # End-to-end tests

# Type checking
pnpm type-check
```

## Environment Configuration

Create `.env` files in backend and frontend directories with required variables:

**Backend `.env`:**
```env
MONGODB_URI=mongodb://localhost:27017/dispatchai
REDIS_URL=redis://localhost:6379
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
PUBLIC_URL=https://your-domain.com/api
OPENAI_API_KEY=your_openai_key
STRIPE_SECRET_KEY=your_stripe_key
```

## Deployment

### UAT Environment

```bash
cd backend
docker compose -f docker-compose.uat.yml up -d --build
```

### Production

Ensure all environment variables are properly configured and deploy using your preferred platform (AWS, GCP, Azure, etc.).

## Use Cases

DispatchAI is ideal for service-based businesses that rely on phone bookings:

- 🏠 Home Services (plumbing, HVAC, cleaning)
- 🔧 Repair Services (appliance, auto, electronics)
- 💅 Beauty & Wellness (salons, spas, massage)
- 🏥 Healthcare (clinics, dental, therapy)
- 📚 Professional Services (tutoring, consulting)
- 🚗 Automotive Services (detailing, maintenance)

## Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [Frontend README](./frontend/README.md) - Frontend development guide
- [CLAUDE.md](./CLAUDE.md) - AI assistant development guide
- API Docs: `http://localhost:4000/api/docs`

## Contributing

This is a private project. For questions or contributions, please contact the development team.

## License

Proprietary - All rights reserved
