# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DispatchAI is an **Agentic AI system** for autonomous voice-based service bookings. The system deploys AI agents that independently handle customer phone calls, understand needs, make decisions, and complete bookings without human intervention.

**Three-Tier Architecture:**
1. **Backend (NestJS)** - Agent orchestration layer, manages conversation flow and state
2. **Frontend (Next.js)** - Admin dashboard for monitoring and configuring AI agents
3. **AI Service (FastAPI/Python)** - LLM reasoning engine for natural language understanding

## Core Development Principles

**ALWAYS follow SOLID, DRY, and KISS principles (see `.cursorrules` for details):**

- **SOLID**: Single responsibility, dependency injection, interface segregation
- **DRY**: Extract reusable logic into helpers/services, use constants
- **KISS**: Simple, readable code over clever solutions

**Critical Rules:**
- Use `@/` path aliases for all imports (never relative paths like `../../`)
- Use `winstonLogger` for logging (never `console.log`)
- Use `async/await` (never `.then()` chains)
- Avoid `any` type - use proper TypeScript types
- Keep controllers thin - business logic belongs in services
- Use dependency injection via constructor

## Development Commands

### Backend (NestJS)

```bash
cd backend
pnpm install
pnpm dev                    # Development server with watch mode
pnpm build                  # Production build
pnpm start                  # Run production build
pnpm test                   # Run all tests
pnpm test path/to/test.ts   # Run specific test file
pnpm test:unit              # Unit tests only
pnpm test:integration       # Integration tests only
pnpm test:e2e               # End-to-end tests only
pnpm type-check             # TypeScript type checking
pnpm lint                   # Format and lint all code
pnpm seed                   # Run database seeds
```

**Docker Development:**
```bash
cd backend
docker compose down
docker compose up -d --build    # Build and start containers
docker compose logs -f api      # View API logs
docker compose logs -f dispatchai-ai  # View AI service logs
```

**Docker UAT:**
```bash
cd backend
docker compose -f docker-compose.uat.yml up -d --build
```

### Frontend (Next.js)

```bash
cd frontend
pnpm install
pnpm dev          # Development server at http://localhost:3000
pnpm build        # Production build
pnpm start        # Run production build
pnpm lint         # Lint and fix
pnpm type-check   # TypeScript type checking
```

### AI Service (Python/FastAPI)

```bash
cd backend/ai
uv sync                      # Install dependencies
uv run fastapi dev app/main.py   # Development server at http://localhost:8000
```

API docs available at `http://localhost:8000/docs`

## AI Agent System Architecture

### How the Agent Works

The AI agent operates autonomously through a **perception → reasoning → action** loop:

**1. Call Initialization** (`POST /api/telephony/voice`)
- Twilio webhook triggers `CallProcessorService.handleVoice()`
- Agent creates session in Redis via `SessionHelper.ensureSession()`
- Loads business context (company info, available services)
- Generates personalized welcome message
- Returns TwiML to start conversation

**2. Conversation Loop** (`POST /api/telephony/gather`)
- Customer speaks → Twilio converts to text → webhook to backend
- `CallProcessorService.handleGather()` processes input:
  - Appends customer message to conversation history
  - Calls `AiIntegrationService.getAIReply()` → hits Python AI service
  - AI service (LLM) analyzes conversation, generates response
  - AI returns `{ message, shouldHangup }` decision
- Agent decides next action:
  - `NextAction.GATHER` - Continue conversation
  - `NextAction.HANGUP` - End call
- Appends AI message to history
- Returns TwiML with AI's response

**3. Call Completion** (`POST /api/telephony/status`)
- Twilio sends final status (completed, busy, failed, etc.)
- `CallProcessorService.handleStatus()` triggers finalization
- `CallDataPersistenceService.processCallCompletion()`:
  - Generates AI summary via `/ai/summary` endpoint
  - Creates call log record in MongoDB
  - Saves conversation transcript
  - Cleans up Redis session

### Agent Memory System

**Short-term Memory (Redis)**
- Session structure stored in Redis during active call
- Managed via `SessionHelper` (never access Redis directly)
- Contains:
  - Conversation history (all customer/AI messages)
  - Company context (name, greeting, services)
  - Call metadata (callSid, timestamps)

**Long-term Memory (MongoDB)**
- Persisted after call completion
- Call logs, transcripts, summaries
- Used for analytics and agent improvement

### Key Agent Components

**`CallProcessorService`** (`backend/src/modules/telephony/services/call-processor.service.ts`)
- **Core orchestrator** for agent behavior
- Methods:
  - `handleVoice()` - Initialize agent session
  - `handleGather()` - Process customer input, get AI response, decide next action
  - `handleStatus()` - Handle call lifecycle events
- Uses handler map pattern for status processing

**`SessionHelper`** (`backend/src/modules/telephony/helpers/session.helper.ts`)
- **Agent memory manager**
- Methods:
  - `ensureSession()` - Create/retrieve session
  - `appendUserMessage()` / `appendAiMessage()` - Maintain conversation history
  - `fillCompanyServices()` - Load business context into agent memory
  - `fillCompany()` - Load company info

**`AiIntegrationService`** (`backend/src/modules/telephony/services/ai-integration.service.ts`)
- **Interface to LLM reasoning engine**
- Methods:
  - `getAIReply(callSid, message)` - Get conversational response from AI
  - `generateAISummary(callSid, session)` - Create call summary
- Includes timeout, retry logic, error handling

**`CallDataPersistenceService`** (`backend/src/modules/telephony/services/call-data-persistence.service.ts`)
- **Data persistence handler**
- Creates call logs, saves transcripts, stores summaries
- Only called after call completion

**`SessionRepository`** (`backend/src/modules/telephony/repositories/session.repository.ts`)
- **Redis data access layer**
- Encapsulates all Redis operations
- Provides clean interface for session CRUD

## Backend Architecture

### Module Organization

NestJS modular architecture with domain-driven design. Each feature is a module in `backend/src/modules/`:

**Core Modules:**
- `auth/` - JWT authentication, Google OAuth
- `user/` - User management
- `company/` - Company/organization management
- `onboarding/` - User onboarding flows

**Service Management:**
- `service/` - Service definitions (what AI agent can book)
- `service-booking/` - Booking management and scheduling
- `service-form-field/` - Dynamic form fields for services
- `service-location-mapping/` - Service-location relationships
- `location/` - Location/branch management
- `availability/` - Service availability scheduling

**Telephony & AI Agent:**
- `telephony/` - **AI Agent core implementation**
  - `services/` - Agent orchestration, AI integration, data persistence
  - `helpers/` - Session management, data transformation, validation
  - `repositories/` - Redis session storage
  - `types/` - Session data structures
  - `telephony.controller.ts` - Twilio webhook endpoints
- `calllog/` - Call record management
- `transcript/` - Call transcripts
- `transcript-chunk/` - Transcript segment storage

**Billing:**
- `subscription/` - Subscription management
- `plan/` - Subscription plan definitions
- `stripe/` - Stripe payment integration

**Supporting:**
- `database/` - MongoDB connection
- `health/` - Health check endpoints
- `setting/` - Application settings
- `blog/` - Blog content management

### Path Aliases

**CRITICAL:** Always use `@/` prefix for imports:

```typescript
// ✅ CORRECT
import { UserService } from '@/modules/user/user.service';
import { winstonLogger } from '@/logger/winston.logger';

// ❌ WRONG - Never use relative paths
import { UserService } from '../../user/user.service';
```

### Module Structure Convention

Each NestJS module follows this pattern:
```
feature/
├── feature.module.ts          # Module definition with imports/exports
├── feature.controller.ts      # HTTP endpoints (thin, delegates to service)
├── feature.service.ts         # Business logic
├── schema/
│   └── feature.schema.ts      # Mongoose schema
├── dto/
│   ├── create-feature.dto.ts  # Input validation for create
│   └── update-feature.dto.ts  # Input validation for update
├── helpers/                   # Utility functions
├── repositories/              # Data access layer (if needed)
└── types/                     # TypeScript interfaces
```

### Service Layer Patterns

**Controllers (Thin):**
- Handle HTTP request/response only
- Delegate all logic to services
- Use DTOs for validation

```typescript
@Controller('service')
export class ServiceController {
  constructor(private readonly service: ServiceService) {}

  @Get()
  async findAll() {
    return this.service.findAll(); // ✅ Delegate to service
  }
}
```

**Services (Business Logic):**
- Contain all business logic
- Use dependency injection
- Return domain objects, not HTTP responses

```typescript
@Injectable()
export class ServiceService {
  constructor(
    @InjectModel(Service.name) private model: Model<ServiceDocument>,
    private readonly validationHelper: ValidationHelper,
  ) {}

  async findAll(): Promise<Service[]> {
    return this.model.find().exec();
  }
}
```

**Helpers (Utilities):**
- Focused single-purpose utilities
- Often static methods
- No dependencies on other services

```typescript
export class DataTransformerHelper {
  static buildCustomerMessageForAI(message: string) {
    return {
      speaker: 'customer',
      message,
      startedAt: new Date().toISOString()
    };
  }
}
```

**Repositories (Data Access):**
- Encapsulate database/Redis operations
- Provide clean interface to services
- Abstract storage implementation

### AI Agent Integration Patterns

**Session Management Pattern:**
```typescript
// ✅ ALWAYS use SessionHelper
await this.sessionHelper.ensureSession(callSid);
await this.sessionHelper.appendUserMessage(callSid, message);

// ❌ NEVER access Redis directly
await this.redis.set(callSid, JSON.stringify(data));
```

**AI Integration Pattern:**
```typescript
// ✅ ALWAYS use AiIntegrationService with fallback
try {
  const reply = await this.aiIntegration.getAIReply(callSid, message);
  return reply.message;
} catch (error) {
  winstonLogger.error('AI service failed', { error });
  return SYSTEM_RESPONSES.fallback;  // Always have fallback
}
```

**Agent Decision Pattern:**
```typescript
// ✅ Let AI control flow via shouldHangup
if (aiReplyData.shouldHangup === true) {
  return await this.speakAndLog(callSid, reply, NextAction.HANGUP);
}
return this.speakAndLog(callSid, reply, NextAction.GATHER);
```

**Data Persistence Pattern:**
```typescript
// ✅ Only persist after call completion
async handleStatus(statusData: VoiceStatusBody) {
  if (statusData.CallStatus === 'completed') {
    await this.dataPersistence.processCallCompletion(callSid, statusData);
  }
}
```

## Frontend Architecture

**Structure:** Next.js 15 App Router with feature-based organization

- `src/app/` - Next.js app router pages and layouts
  - `admin/` - Admin dashboard pages
  - `auth/` - Authentication pages
  - `onboarding/` - Onboarding flow
  - `(public)/` - Public-facing pages

- `src/features/` - Feature modules (auth, calendar, calllog, company, etc.)
- `src/components/` - Shared React components
- `src/redux/` & `src/store/` - Redux Toolkit state management
- `src/services/` - API client services
- `src/types/` - TypeScript type definitions
- `src/lib/` - Utility libraries
- `src/theme/` - Material-UI theme configuration

### State Management Strategy

**Use the right tool for the right state:**

- **Redux Toolkit** - Global state (auth, user preferences, theme)
- **TanStack Query** - Server state (API data, caching)
- **useState** - Local UI state (modals, forms)

```typescript
// ✅ CORRECT - Server state with TanStack Query
const { data, isLoading } = useQuery({
  queryKey: ['callLogs'],
  queryFn: fetchCallLogs  // From service file
});

// ❌ WRONG - Don't duplicate server state in Redux
const callLogs = useSelector(state => state.callLogs.list);
```

### API Integration Pattern

**Always use service layer:**

```typescript
// ✅ CORRECT - Service file
// src/services/calllog.service.ts
import api from './api';

export const fetchCallLogs = async () => {
  const response = await api.get('/calllog');
  return response.data;
};

// Component
import { fetchCallLogs } from '@/services/calllog.service';
const { data } = useQuery({ queryKey: ['callLogs'], queryFn: fetchCallLogs });

// ❌ WRONG - Direct API call in component
useEffect(() => {
  axios.get('http://localhost:4000/api/calllog').then(setData);
}, []);
```

## AI Service Architecture (Python/FastAPI)

**Framework:** FastAPI with async/await

**Endpoints:**
- `POST /api/ai/conversation` - LLM conversation processing (main agent reasoning)
- `POST /api/ai/reply` - Simple response generation
- `POST /api/ai/summary` - Call summarization (post-call)
- `GET /api/ai/health` - Health check

**Structure:**
```
backend/ai/
├── app/
│   ├── api/              # FastAPI routers
│   │   ├── call.py       # Conversation endpoint
│   │   ├── summary.py    # Summary endpoint
│   │   └── health.py
│   ├── infrastructure/   # Redis, external services
│   ├── config.py         # Environment config
│   └── main.py           # FastAPI app
└── pyproject.toml        # Dependencies (uv)
```

**Integration Point:**
- NestJS backend calls AI service via HTTP
- In Docker: `http://dispatchai-ai:8000`
- Local dev: `http://localhost:8000`

## Key Integration Points

### 1. Telephony Call Flow
```
Customer Call
    ↓
Twilio (Speech-to-Text)
    ↓
POST /api/telephony/voice (Initial)
    ↓
CallProcessorService.handleVoice()
    ↓
SessionHelper (Create session, load context)
    ↓
Return TwiML (Welcome message)
    ↓
POST /api/telephony/gather (Each input)
    ↓
CallProcessorService.handleGather()
    ↓
AiIntegrationService.getAIReply()
    ↓
POST /api/ai/conversation (Python AI Service)
    ↓
LLM reasoning, decision making
    ↓
Return { message, shouldHangup }
    ↓
Return TwiML (AI response + gather/hangup)
    ↓
POST /api/telephony/status (On completion)
    ↓
CallDataPersistenceService.processCallCompletion()
    ↓
POST /api/ai/summary (Generate summary)
    ↓
Save to MongoDB, cleanup Redis
```

### 2. Service Booking Flow
- Frontend → `POST /api/service-booking`
- Validates against `service-form-field` definitions
- Maps to location via `service-location-mapping`
- Checks `availability` for scheduling
- Creates booking record

### 3. Authentication Flow
- JWT tokens for session management
- Google OAuth2 integration
- CSRF protection via `CSRFGuard`
- Token validation in guards

## Common Development Patterns

### Adding a New Backend Module

1. Create module directory:
```bash
mkdir -p backend/src/modules/your-feature
mkdir backend/src/modules/your-feature/schema
mkdir backend/src/modules/your-feature/dto
```

2. Create module files:
```typescript
// your-feature.module.ts
@Module({
  imports: [
    MongooseModule.forFeature([{ name: YourFeature.name, schema: YourFeatureSchema }])
  ],
  controllers: [YourFeatureController],
  providers: [YourFeatureService],
  exports: [YourFeatureService]  // If needed by other modules
})
export class YourFeatureModule {}
```

3. Register in `app.module.ts`:
```typescript
import { YourFeatureModule } from '@/modules/your-feature/your-feature.module';

@Module({
  imports: [
    // ... existing modules
    YourFeatureModule,
  ],
})
export class AppModule {}
```

### Error Handling Pattern

```typescript
import { NotFoundException } from '@nestjs/common';
import { winstonLogger } from '@/logger/winston.logger';

async findById(id: string) {
  const entity = await this.model.findById(id);
  if (!entity) {
    winstonLogger.warn(`Entity not found: ${id}`);
    throw new NotFoundException(`Entity with ID ${id} not found`);
  }
  return entity;
}
```

### Testing Pattern

```typescript
describe('CallProcessorService', () => {
  let service: CallProcessorService;
  let sessionHelper: SessionHelper;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        CallProcessorService,
        { provide: SessionHelper, useValue: mockSessionHelper },
      ],
    }).compile();

    service = module.get<CallProcessorService>(CallProcessorService);
  });

  describe('handleVoice', () => {
    it('should initialize session and load company context', async () => {
      // Arrange
      const voiceData = { CallSid: 'test-sid', To: '+1234567890' };

      // Act
      const result = await service.handleVoice(voiceData);

      // Assert
      expect(sessionHelper.ensureSession).toHaveBeenCalledWith('test-sid');
      expect(result).toContain('welcome');
    });
  });
});
```

## API Documentation

- **Backend Swagger:** `http://localhost:4000/api/docs`
- **AI Service Docs:** `http://localhost:8000/docs`

## Health Checks

```bash
# Backend health
curl http://localhost:4000/api/health

# Database health
curl http://localhost:4000/api/health/db

# AI service health
curl http://localhost:8000/api/ai/health
```

## Database

- **Type:** MongoDB with Mongoose ODM
- **Schemas:** Located in each module's `schema/` directory
- **Seeds:** Run `pnpm seed` in backend to populate test data
- **Indexes:** Add indexes for frequently queried fields

## Docker Services

Docker Compose setup includes:
- `dispatchai-api` - NestJS backend (port 4000)
- `dispatchai-ai` - Python AI service (port 8000)
- `mongo` - MongoDB database
- `redis` - Redis for session storage

Services communicate via Docker network using service names as hostnames.

## Environment Configuration

Backend uses `@nestjs/config` with `.env` files:

```env
# Required variables
MONGODB_URI=mongodb://localhost:27017/dispatchai
REDIS_URL=redis://localhost:6379
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
AI_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_jwt_secret
STRIPE_SECRET_KEY=your_stripe_key
```

## Critical Anti-Patterns to Avoid

❌ **NEVER:**
- Use `any` type (use proper TypeScript types)
- Use relative imports (always use `@/` aliases)
- Use `console.log` (use `winstonLogger`)
- Access Redis directly (use `SessionHelper`)
- Put business logic in controllers (use services)
- Access database from controllers (use services)
- Ignore error handling
- Forget AI fallback responses

✅ **ALWAYS:**
- Use dependency injection
- Follow SOLID principles
- Keep functions small (< 20 lines)
- Write self-documenting code
- Handle all errors gracefully
- Log important events with `winstonLogger`
- Use `async/await` (never `.then()`)
- Validate inputs with DTOs

## Quick Reference

**Logging:**
```typescript
import { winstonLogger } from '@/logger/winston.logger';
winstonLogger.log('Info message');
winstonLogger.warn('Warning message');
winstonLogger.error('Error message', { context });
```

**DTOs:**
```typescript
import { IsString, IsNotEmpty } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  name: string;
}
```

**Async Operations:**
```typescript
// ✅ Concurrent operations
const [users, services] = await Promise.all([
  this.userService.findAll(),
  this.serviceService.findAll()
]);

// ✅ Sequential when needed
await this.sessionHelper.ensureSession(callSid);
await this.sessionHelper.appendUserMessage(callSid, message);
```

For detailed coding standards, see `.cursorrules` file.
