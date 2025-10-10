# General Project Rules

These rules apply to all code in the DispatchAI project.

## Core Principles

### SOLID Principles (Mandatory)

**Single Responsibility Principle**
- Each file should have ONE clear purpose
- Each class/function should do ONE thing well
- If you need to use "and" to describe what a file/function does, it's doing too much

**Open/Closed Principle**
- Use interfaces and abstract classes for extensibility
- Prefer composition over inheritance
- Use dependency injection

**Liskov Substitution Principle**
- Ensure derived classes are substitutable for their base classes
- Maintain consistent method signatures

**Interface Segregation Principle**
- Create focused, client-specific interfaces
- Don't force implementations of unused methods

**Dependency Inversion Principle**
- Depend on abstractions, not concrete implementations
- Use dependency injection (constructor injection preferred)

### DRY (Don't Repeat Yourself)

**Extract Repeated Logic**
- If code appears 3+ times, extract it into a reusable function/helper
- Use constants for repeated values
- Create utility functions for common operations

**Examples:**
```typescript
// ❌ BAD - Repeated logic
function processUserA() {
  const timestamp = new Date().toISOString();
  logger.log(`Processing at ${timestamp}`);
  // ...
}

function processUserB() {
  const timestamp = new Date().toISOString();
  logger.log(`Processing at ${timestamp}`);
  // ...
}

// ✅ GOOD - Extracted helper
function logProcessing(action: string) {
  const timestamp = new Date().toISOString();
  logger.log(`${action} at ${timestamp}`);
}

function processUserA() {
  logProcessing('Processing User A');
  // ...
}
```

### KISS (Keep It Simple, Stupid)

- Prefer simple, explicit code over clever, complex code
- If it takes more than 30 seconds to understand what code does, refactor it
- Break complex logic into smaller, named functions

## File Size Limits

### **CRITICAL: Maximum File Size = 1000 lines**

**Automatic Refactoring Required:**
- If ANY file exceeds 1000 lines, you MUST refactor it before making changes
- Split large files by:
  - Extracting helpers into separate files
  - Breaking down services into smaller services
  - Separating concerns (types, utils, business logic)
  - Creating sub-modules

**How to Refactor Large Files:**
```
// Original: user.service.ts (1500 lines)
user/
├── user.service.ts (300 lines - main service)
├── helpers/
│   ├── user-validation.helper.ts (150 lines)
│   ├── user-transformation.helper.ts (200 lines)
│   └── user-email.helper.ts (150 lines)
├── utils/
│   └── user-utils.ts (100 lines)
└── types/
    └── user-types.ts (80 lines)
```

**Before making ANY changes to a large file:**
1. Check line count: `wc -l filename`
2. If > 1000 lines, create refactoring plan
3. Extract logical sections into separate files
4. Update imports
5. Run tests to ensure nothing broke
6. THEN make your intended changes

## Naming Conventions

### TypeScript/JavaScript

**Classes:** `PascalCase`
```typescript
class CallProcessorService {}
class UserRepository {}
```

**Functions/Methods:** `camelCase`
```typescript
function handleVoice() {}
async findUserById(id: string) {}
```

**Variables:** `camelCase`
```typescript
const callSid = 'CS123';
let isProcessing = false;
```

**Constants:** `UPPER_SNAKE_CASE` (MANDATORY)
```typescript
// ✅ CORRECT
const MAX_RETRY_ATTEMPTS = 3;
const API_BASE_URL = 'https://api.example.com';
const SYSTEM_RESPONSES = {
  ERROR: 'An error occurred',
  FALLBACK: 'Please try again'
};

// ❌ WRONG - Constants must be uppercase
const maxRetryAttempts = 3;
const apiBaseUrl = 'https://api.example.com';
```

**Private Properties:** Prefix with `_` or use TypeScript `private`
```typescript
class Service {
  private _cache: Map<string, any>;
  private readonly config: Config;
}
```

**Boolean Variables:** Use `is`, `has`, `should` prefix
```typescript
const isValid = true;
const hasPermission = false;
const shouldRetry = true;
```

**Files:** `kebab-case`
```
call-processor.service.ts
user-validation.helper.ts
session-repository.ts
```

**Interfaces/Types:** `PascalCase` (NO `I` prefix)
```typescript
// ✅ CORRECT
interface User {}
type CallStatus = 'active' | 'completed';

// ❌ WRONG - Don't use I prefix
interface IUser {}
```

### Python

**Classes:** `PascalCase`
```python
class AiService:
    pass
```

**Functions/Variables:** `snake_case`
```python
def process_conversation():
    user_message = "Hello"
```

**Constants:** `UPPER_SNAKE_CASE`
```python
MAX_TOKENS = 2000
API_TIMEOUT = 30
```

## Protected Files and Folders

### **NEVER Modify These Directories:**

```
❌ FORBIDDEN - These are build artifacts or generated files
/backend/dist/
/frontend/.next/
/frontend/out/
/backend/node_modules/
/frontend/node_modules/
/backend/ai/.venv/
/backend/ai/__pycache__/
```

**If you attempt to modify files in these directories, STOP and:**
1. Identify the source file instead
2. Make changes to the source
3. Run the build command
4. Let the build process regenerate these files

**Example:**
```typescript
// ❌ WRONG - Editing compiled file
// backend/dist/modules/user/user.service.js

// ✅ CORRECT - Edit source file
// backend/src/modules/user/user.service.ts
// Then run: pnpm build
```

### **NEVER Commit These Files:**

```
.env
.env.local
.env.production
*.log
*.pid
.DS_Store
*.swp
*.swo
```

## Code Quality Standards

### Maximum Function Length

**Functions > 50 lines should be refactored**

```typescript
// ❌ BAD - Too long, does too many things
async function processUserData(user: User) {
  // 80 lines of code...
}

// ✅ GOOD - Broken down
async function processUserData(user: User) {
  const validated = await validateUser(user);
  const transformed = transformUserData(validated);
  const enriched = await enrichWithExternalData(transformed);
  return await saveUser(enriched);
}

async function validateUser(user: User) { /* ... */ }
function transformUserData(user: ValidatedUser) { /* ... */ }
async function enrichWithExternalData(user: TransformedUser) { /* ... */ }
async function saveUser(user: EnrichedUser) { /* ... */ }
```

### Maximum Function Parameters

**Functions > 3 parameters should use an options object**

```typescript
// ❌ BAD - Too many parameters
function createBooking(
  userId: string,
  serviceId: string,
  locationId: string,
  date: Date,
  notes: string,
  status: string
) {}

// ✅ GOOD - Use options object
interface CreateBookingOptions {
  userId: string;
  serviceId: string;
  locationId: string;
  date: Date;
  notes?: string;
  status?: BookingStatus;
}

function createBooking(options: CreateBookingOptions) {}
```

### Avoid Deep Nesting

**Maximum nesting depth: 3 levels**

```typescript
// ❌ BAD - Too deeply nested
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      if (user.subscription) {
        if (user.subscription.isValid) {
          // Do something
        }
      }
    }
  }
}

// ✅ GOOD - Early returns
if (!user) return;
if (!user.isActive) return;
if (!user.hasPermission) return;
if (!user.subscription?.isValid) return;

// Do something
```

## TypeScript Strict Mode

**MANDATORY: No `any` type**

```typescript
// ❌ FORBIDDEN
function processData(data: any) {}
const result: any = await fetch();

// ✅ REQUIRED - Use proper types
function processData(data: UserData) {}
const result: FetchResult = await fetch();

// ✅ If type is truly unknown, use 'unknown'
function processData(data: unknown) {
  if (isUserData(data)) {
    // Type guard
    // Now data is UserData
  }
}
```

**Type Guards for Unknown Types:**
```typescript
function isUserData(data: unknown): data is UserData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  );
}
```

## Import Organization

**Mandatory Order:**

1. External dependencies
2. Internal absolute imports (`@/`)
3. Relative imports
4. Type-only imports

**One blank line between groups:**

```typescript
// ✅ CORRECT
import { Injectable } from '@nestjs/common';
import { Model } from 'mongoose';

import { UserService } from '@/modules/user/user.service';
import { winstonLogger } from '@/logger/winston.logger';

import { helperFunction } from './helpers/helper';

import type { User } from '@/modules/user/schema/user.schema';
import type { CallStatus } from './types';
```

## Comments

### When to Comment

**DO comment:**
- Complex business logic
- Non-obvious decisions
- "Why" something was done a certain way
- Workarounds for bugs/limitations
- Algorithm explanations

**DON'T comment:**
- Obvious code
- What the code does (code should be self-documenting)
- Commented-out code (delete it, use git history)

```typescript
// ❌ BAD - States the obvious
// Set user name to "John"
user.name = 'John';

// ❌ BAD - Commented-out code
// function oldImplementation() {
//   // ...
// }

// ✅ GOOD - Explains why
// We use a 5-second timeout here because Twilio's webhook
// can take up to 4 seconds to respond during peak hours
const TWILIO_TIMEOUT = 5000;

// ✅ GOOD - Explains complex logic
// Binary search requires sorted array. We sort by timestamp
// because call logs are typically accessed in chronological order
const sortedLogs = callLogs.sort((a, b) => a.timestamp - b.timestamp);
```

### JSDoc for Public APIs

```typescript
/**
 * Processes an incoming voice call and initializes the AI agent session.
 *
 * @param voiceData - Twilio webhook payload containing call metadata
 * @returns TwiML XML response to control call flow
 * @throws {NotFoundException} When user with given phone number doesn't exist
 *
 * @example
 * ```typescript
 * const twiml = await handleVoice({
 *   CallSid: 'CA123',
 *   To: '+1234567890'
 * });
 * ```
 */
async handleVoice(voiceData: VoiceGatherBody): Promise<string> {
  // Implementation
}
```

## Error Handling

**ALL async functions MUST have error handling**

```typescript
// ❌ BAD - No error handling
async function getUser(id: string) {
  const user = await this.userModel.findById(id);
  return user;
}

// ✅ GOOD - Proper error handling
async function getUser(id: string) {
  try {
    const user = await this.userModel.findById(id);
    if (!user) {
      winstonLogger.warn(`User not found: ${id}`);
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  } catch (error) {
    winstonLogger.error(`Failed to fetch user ${id}`, {
      error: (error as Error).message,
      stack: (error as Error).stack
    });
    throw error;
  }
}
```

## Logging

**MANDATORY: Use `winstonLogger`, NEVER `console.log`**

```typescript
// ❌ FORBIDDEN
console.log('User created');
console.error('Error occurred');

// ✅ REQUIRED
import { winstonLogger } from '@/logger/winston.logger';

winstonLogger.log('User created', { userId: user.id });
winstonLogger.warn('Retry attempt', { attempt: 2, maxAttempts: 3 });
winstonLogger.error('Operation failed', {
  error: error.message,
  stack: error.stack
});
```

**Log Levels:**
- `log()` - General information
- `warn()` - Warning conditions
- `error()` - Error conditions

**Always include context:**
```typescript
// ❌ BAD - No context
winstonLogger.error('Failed');

// ✅ GOOD - With context
winstonLogger.error('Failed to process call', {
  callSid: 'CA123',
  error: error.message,
  timestamp: new Date().toISOString()
});
```

## Git Commit Messages

**Use Conventional Commits format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring (no functionality change)
- `docs` - Documentation changes
- `style` - Code style changes (formatting, semicolons, etc.)
- `test` - Adding or updating tests
- `chore` - Maintenance tasks (dependencies, build, etc.)
- `perf` - Performance improvements

**Examples:**
```
feat(telephony): add call recording support

Implement recording functionality for AI agent calls:
- Add recording toggle in TwiML response
- Store recording URL in call log
- Add API endpoint to retrieve recordings

Closes #123

---

fix(auth): resolve JWT token expiration issue

JWT tokens were expiring after 1 hour instead of 24 hours
due to incorrect time unit calculation.

---

refactor(session): extract Redis operations to repository

Move all Redis operations from SessionHelper to SessionRepository
to follow repository pattern and improve testability.
```

## Code Review Checklist

Before submitting code, verify:

- [ ] No file exceeds 1000 lines
- [ ] All constants are `UPPER_SNAKE_CASE`
- [ ] No modifications to `dist/`, `.next/`, or `node_modules/`
- [ ] No `any` types
- [ ] No `console.log` statements
- [ ] Imports are properly organized
- [ ] Functions are < 50 lines
- [ ] Functions have < 4 parameters (use objects)
- [ ] Nesting depth < 3 levels
- [ ] All async functions have error handling
- [ ] Meaningful variable names (no `x`, `data`, `temp`)
- [ ] Comments explain "why", not "what"
- [ ] Tests written/updated
- [ ] No sensitive data (API keys, passwords, etc.)
- [ ] Follows SOLID, DRY, KISS principles
