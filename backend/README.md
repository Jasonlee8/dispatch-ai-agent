# DispatchAI Backend

NestJS-based backend API for DispatchAI, featuring an autonomous AI agent system for voice-based service bookings. The backend orchestrates AI-powered phone conversations, manages agent memory through Redis sessions, and integrates with a Python-based LLM reasoning engine.

## Architecture Overview

The backend serves as the **Agent Orchestration Layer**, coordinating between:
- **Twilio Voice API** - Voice interface for customer calls
- **AI Reasoning Service** (Python/FastAPI) - LLM-powered conversation processing
- **Redis** - Agent short-term memory (session state)
- **MongoDB** - Persistent storage (call logs, bookings, user data)

## Project Structure

```
backend/
├── src/
│   ├── modules/
│   │   ├── telephony/            # 🤖 AI Agent Core Implementation
│   │   │   ├── services/
│   │   │   │   ├── call-processor.service.ts        # Agent orchestration & decision making
│   │   │   │   ├── ai-integration.service.ts        # LLM API interface
│   │   │   │   └── call-data-persistence.service.ts # Data persistence after calls
│   │   │   ├── helpers/
│   │   │   │   ├── session.helper.ts                # Agent memory management
│   │   │   │   ├── welcome-message.helper.ts        # Greeting generation
│   │   │   │   ├── data-transformer.helper.ts       # Data format conversion
│   │   │   │   └── validation.helper.ts
│   │   │   ├── repositories/
│   │   │   │   └── session.repository.ts            # Redis session operations
│   │   │   ├── types/
│   │   │   │   └── redis-session.ts                 # Session data structures
│   │   │   ├── telephony.controller.ts              # Twilio webhook endpoints
│   │   │   ├── telephony.service.ts
│   │   │   └── telephony.module.ts
│   │   │
│   │   ├── service-booking/      # Booking management
│   │   ├── service/              # Service definitions
│   │   ├── service-form-field/   # Dynamic form fields
│   │   ├── service-location-mapping/ # Service-location relationships
│   │   ├── location/             # Location/branch management
│   │   ├── availability/         # Scheduling and availability
│   │   │
│   │   ├── calllog/              # Call records
│   │   ├── transcript/           # Conversation transcripts
│   │   ├── transcript-chunk/     # Transcript segments
│   │   │
│   │   ├── auth/                 # Authentication (JWT, Google OAuth)
│   │   ├── user/                 # User management
│   │   ├── company/              # Company/organization management
│   │   ├── onboarding/           # User onboarding flows
│   │   │
│   │   ├── subscription/         # Subscription management
│   │   ├── plan/                 # Subscription plans
│   │   ├── stripe/               # Stripe payment integration
│   │   │
│   │   ├── setting/              # Application settings
│   │   ├── blog/                 # Blog content management
│   │   ├── database/             # MongoDB connection
│   │   └── health/               # Health check endpoints
│   │
│   ├── lib/
│   │   ├── ai/                   # AI service HTTP client
│   │   ├── redis/                # Redis client configuration
│   │   └── twilio/               # Twilio client configuration
│   │
│   ├── common/
│   │   ├── interfaces/           # Shared TypeScript interfaces
│   │   ├── constants/            # System constants
│   │   └── guards/               # Authentication & security guards
│   │
│   ├── logger/                   # Winston logging configuration
│   └── main.ts                   # Application entry point
│
├── ai/                           # 🧠 Python AI Service (FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   ├── call.py           # POST /ai/conversation - LLM conversation
│   │   │   ├── summary.py        # POST /ai/summary - Call summarization
│   │   │   ├── chat.py           # POST /ai/chat - Chat endpoint
│   │   │   └── health.py         # GET /ai/health - Health check
│   │   ├── infrastructure/
│   │   │   └── redis_client.py   # Redis client for AI service
│   │   ├── config.py             # Environment configuration
│   │   └── main.py               # FastAPI application
│   ├── pyproject.toml            # Python dependencies (uv)
│   ├── Dockerfile                # AI service container
│   └── Dockerfile.uat            # UAT environment container
│
├── scripts/
│   └── seeds/                    # Database seed scripts
├── test/                         # Test files (unit, integration, e2e)
├── docker-compose.yml            # Development Docker setup
├── docker-compose.uat.yml        # UAT environment setup
├── Dockerfile                    # NestJS API container
├── nest-cli.json                 # NestJS CLI configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies and scripts
```

## Prerequisites

- **Node.js** v16+
- **pnpm** (package manager)
- **Docker** and **Docker Compose**
- **MongoDB** (local or Docker)
- **Redis** (local or Docker)
- **Python** 3.11+ (for AI module)
- **uv** (Python package manager)

## Getting Started

### Option 1: Docker Development (Recommended)

```bash
# Stop any running containers
docker compose down

# Build and start all services (NestJS API, AI service, MongoDB, Redis)
docker compose up -d --build

# View API logs
docker compose logs -f api

# View AI service logs
docker compose logs -f dispatchai-ai
```

**Services:**
- NestJS API: `http://localhost:4000`
- Swagger API Docs: `http://localhost:4000/api/docs`
- AI Service: `http://localhost:8000` (internal)
- AI Service Docs: `http://localhost:8000/docs`

### Option 2: Local Development

#### 1. Install Dependencies

```bash
pnpm install
```

#### 2. Start MongoDB and Redis

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
docker run -d -p 6379:6379 --name redis redis:latest

# Or use local installations
```

#### 3. Run NestJS Backend

```bash
pnpm dev          # Development server with hot reload
pnpm build        # Production build
pnpm start        # Run production build
```

#### 4. Run AI Service (Python)

In a separate terminal:

```bash
cd ai

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run FastAPI development server
uv run fastapi dev app/main.py
```

The AI service will be available at `http://localhost:8000`

### Docker UAT Environment

```bash
docker compose -f docker-compose.uat.yml up -d --build
```

## Development Commands

### Build & Run

```bash
pnpm dev                    # Development server with watch mode
pnpm build                  # Production build
pnpm start                  # Run production build
```

### Testing

```bash
pnpm test                   # Run all tests
pnpm test:unit              # Unit tests only
pnpm test:integration       # Integration tests only
pnpm test:e2e               # End-to-end tests only
pnpm test:ci                # CI pipeline tests (unit + integration)
pnpm test:watch             # Watch mode for tests

# Run specific test file
pnpm test path/to/test_file.ts
```

### Code Quality

```bash
pnpm type-check             # TypeScript type checking
pnpm type-check:test        # Type check test files
pnpm lint                   # Format and lint all code
pnpm lint:src               # Lint source files only
pnpm lint:test              # Lint test files only
```

### Database

```bash
pnpm seed                   # Run database seed scripts
```

## Configuration

### TypeScript Path Aliases

This project uses path aliases with the `@/` prefix for cleaner imports:

```typescript
// ❌ Avoid relative paths
import { SomeService } from '../../some/path/some.service';

// ✅ Use path aliases
import { SomeService } from '@/modules/some/some.service';
```

Configured in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
MONGODB_URI=mongodb://localhost:27017/dispatchai

# Redis
REDIS_URL=redis://localhost:6379

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# AI Service
AI_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key

# Application
PUBLIC_URL=https://your-domain.com/api
NODE_ENV=development
PORT=4000

# Authentication
JWT_SECRET=your_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret
```

## AI Agent System

### How the AI Agent Works

1. **Call Received** (`POST /api/telephony/voice`)
   - Twilio webhook triggers `CallProcessorService.handleVoice()`
   - Agent initializes session in Redis via `SessionHelper.ensureSession()`
   - Loads company info, available services into agent memory
   - Generates welcome message and starts conversation

2. **Conversation Loop** (`POST /api/telephony/gather`)
   - Customer speaks → Twilio sends speech-to-text
   - `CallProcessorService.handleGather()` processes input
   - Appends customer message to conversation history
   - Calls AI service `/ai/conversation` for LLM response
   - AI decides: continue (`NextAction.GATHER`) or end (`NextAction.HANGUP`)
   - Agent responds via TwiML

3. **Call Completion** (`POST /api/telephony/status`)
   - Twilio sends status update (completed, busy, failed, etc.)
   - `CallProcessorService.handleStatus()` triggers finalization
   - `CallDataPersistenceService` processes call data:
     - Generates AI summary via `/ai/summary`
     - Creates call log record
     - Saves transcript
     - Cleans up Redis session

### Key Services

#### `CallProcessorService` - Agent Core Loop
The main orchestrator for AI agent behavior:
- `handleVoice()` - Initialize agent session
- `handleGather()` - Process customer input and generate responses
- `handleStatus()` - Handle call lifecycle events

#### `SessionHelper` - Agent Memory
Manages conversation state in Redis:
- `ensureSession()` - Create/retrieve session
- `appendUserMessage()` / `appendAiMessage()` - Maintain conversation history
- `fillCompanyServices()` - Load business context

#### `AiIntegrationService` - LLM Interface
Communicates with the Python AI service:
- `getAIReply()` - Get conversational response from LLM
- `generateAISummary()` - Create call summary after completion

#### `CallDataPersistenceService` - Data Persistence
Handles post-call data storage:
- Creates call logs
- Saves transcripts
- Stores AI-generated summaries

## API Documentation

### Swagger/OpenAPI

Access interactive API documentation at:
```
http://localhost:4000/api/docs
```

### Health Checks

**Basic Health Check:**
```bash
curl http://localhost:4000/api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-03-03T14:15:00.000Z",
  "service": "dispatchAI API",
  "environment": "development"
}
```

**Database Health Check:**
```bash
curl http://localhost:4000/api/health/db
```

Response:
```json
{
  "status": "ok",
  "database": "MongoDB",
  "connected": true,
  "timestamp": "2025-03-03T14:15:00.000Z"
}
```

### Key Endpoints

#### Telephony (AI Agent)
- `POST /api/telephony/voice` - Initial call handler (Twilio webhook)
- `POST /api/telephony/gather` - Speech input handler (Twilio webhook)
- `POST /api/telephony/status` - Call status updates (Twilio webhook)

#### Service Booking
- `POST /api/service-booking` - Create booking
- `GET /api/service-booking` - List bookings
- `GET /api/service-booking/:id` - Get booking details
- `PATCH /api/service-booking/:id` - Update booking
- `DELETE /api/service-booking/:id` - Delete booking

#### Call Management
- `GET /api/calllog` - List call logs
- `GET /api/calllog/:id` - Get call details
- `GET /api/transcript/:id` - Get conversation transcript

#### Authentication
- `POST /api/auth/login` - User login (JWT)
- `POST /api/auth/register` - User registration
- `GET /api/auth/google` - Google OAuth login

## AI Module (Python FastAPI)

### Local Development

```bash
cd ai

# Install dependencies
uv sync

# Run development server
uv run fastapi dev app/main.py

# The service will be available at:
# http://localhost:8000
# API docs: http://localhost:8000/docs
```

### AI Endpoints

- `POST /api/ai/conversation` - LLM-powered conversation processing
  - Input: `{ callSid, customerMessage }`
  - Output: `{ aiResponse, shouldHangup? }`

- `POST /api/ai/summary` - Generate call summaries
  - Input: `{ callSid, conversation, serviceInfo }`
  - Output: `{ summary, keyPoints }`

- `POST /api/ai/reply` - Simple reply endpoint
- `POST /api/ai/chat` - Chat endpoint
- `GET /api/ai/health` - Health check

### Integration Points

The NestJS backend communicates with the AI service:
- **Conversation processing**: `telephony/services/ai-integration.service.ts:17` → `POST /ai/conversation`
- **Call summarization**: `telephony/services/ai-integration.service.ts:39` → `POST /ai/summary`

In Docker, the AI service runs as `dispatchai-ai` and is accessible at `http://dispatchai-ai:8000`

### Dependencies (pyproject.toml)

- **FastAPI** - Web framework
- **LangChain OpenAI** - LLM integration (planned)
- **Redis** - Session storage
- **Pydantic** - Data validation
- **Ruff** - Python linting and formatting

## Adding New Modules

### 1. Create Module Structure

```bash
mkdir -p src/modules/your-feature
touch src/modules/your-feature/your-feature.module.ts
touch src/modules/your-feature/your-feature.controller.ts
touch src/modules/your-feature/your-feature.service.ts
mkdir src/modules/your-feature/schema
mkdir src/modules/your-feature/dto
```

### 2. Implement Module Files

**Module Definition** (`your-feature.module.ts`):
```typescript
import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { YourFeature, YourFeatureSchema } from './schema/your-feature.schema';
import { YourFeatureController } from './your-feature.controller';
import { YourFeatureService } from './your-feature.service';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: YourFeature.name, schema: YourFeatureSchema }
    ])
  ],
  controllers: [YourFeatureController],
  providers: [YourFeatureService],
  exports: [YourFeatureService]
})
export class YourFeatureModule {}
```

**Controller** (`your-feature.controller.ts`):
```typescript
import { Controller, Get, Post, Body } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { YourFeatureService } from './your-feature.service';

@ApiTags('your-feature')
@Controller('your-feature')
export class YourFeatureController {
  constructor(private readonly service: YourFeatureService) {}

  @Get()
  async findAll() {
    return this.service.findAll();
  }

  @Post()
  async create(@Body() dto: CreateYourFeatureDto) {
    return this.service.create(dto);
  }
}
```

**Service** (`your-feature.service.ts`):
```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { YourFeature, YourFeatureDocument } from './schema/your-feature.schema';

@Injectable()
export class YourFeatureService {
  constructor(
    @InjectModel(YourFeature.name)
    private readonly model: Model<YourFeatureDocument>
  ) {}

  async findAll(): Promise<YourFeature[]> {
    return this.model.find().exec();
  }

  async create(dto: CreateYourFeatureDto): Promise<YourFeature> {
    const entity = new this.model(dto);
    return entity.save();
  }
}
```

### 3. Register in AppModule

Edit `src/modules/app.module.ts`:
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

## Troubleshooting

### Common Issues

**1. Module Not Found Errors**
- Check import paths (use `@/` prefix for absolute imports)
- Verify module is properly exported and imported
- Run `pnpm install` to ensure dependencies are installed

**2. Endpoints Not Accessible**
- Check NestJS logs for "Mapped {route}" messages
- Verify controller is included in module's `controllers` array
- Ensure module is imported in `app.module.ts`

**3. Docker Issues**
- If changes aren't reflecting: `docker compose up --build -d`
- Check logs: `docker compose logs -f api`
- Restart containers: `docker compose restart`

**4. Redis Connection Issues**
- Verify Redis is running: `docker ps | grep redis`
- Check `REDIS_URL` in `.env`
- Test connection: `redis-cli ping`

**5. MongoDB Connection Issues**
- Verify MongoDB is running: `docker ps | grep mongo`
- Check `MONGODB_URI` in `.env`
- View logs: `docker compose logs mongo`

**6. AI Service Communication Errors**
- Ensure AI service is running: `docker compose logs dispatchai-ai`
- Check `AI_SERVICE_URL` environment variable
- Verify FastAPI is accessible: `curl http://localhost:8000/api/ai/health`

### Debug Mode

Enable detailed logging:
```bash
# In .env
NODE_ENV=development
LOG_LEVEL=debug
```

## Testing Strategy

### Unit Tests
Test individual services and utilities in isolation:
```bash
pnpm test:unit
```

Located in `test/unit/`

### Integration Tests
Test module interactions and database operations:
```bash
pnpm test:integration
```

Located in `test/integration/`

### E2E Tests
Test complete user flows through the API:
```bash
pnpm test:e2e
```

Located in `test/e2e/`

### Writing Tests

Example test file:
```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { YourFeatureService } from './your-feature.service';

describe('YourFeatureService', () => {
  let service: YourFeatureService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [YourFeatureService],
    }).compile();

    service = module.get<YourFeatureService>(YourFeatureService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
```

## Deployment

### Production Build

```bash
pnpm build
pnpm start
```

### Docker Production

```bash
docker build -t dispatchai-backend .
docker run -p 4000:4000 --env-file .env dispatchai-backend
```

### UAT Environment

```bash
docker compose -f docker-compose.uat.yml up -d --build
```

## License

Proprietary - All rights reserved
