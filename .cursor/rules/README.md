# DispatchAI Coding Rules

This directory contains detailed coding rules for the DispatchAI project, organized by domain.

## Rule Files

### 00-general.md
**Applies to:** All code in the project

Core principles and standards that apply universally:
- SOLID, DRY, KISS principles with examples
- **File size limit: 1000 lines** (auto-refactor required)
- Naming conventions (PascalCase, camelCase, UPPER_SNAKE_CASE)
- **Protected files**: Never modify `dist/`, `.next/`, `node_modules/`
- **Constants MUST be UPPER_SNAKE_CASE**
- Code quality standards (max function length, parameters, nesting)
- TypeScript strict mode (no `any` types)
- Import organization
- Comment guidelines
- Error handling patterns
- **Logging: Use `winstonLogger`, NEVER `console.log`**
- Git commit message format
- Code review checklist

### 01-backend.md
**Applies to:** `/backend/src/` (NestJS/TypeScript)

Backend-specific rules:
- Module structure (controllers < 200 lines, services < 500 lines)
- Controller must be thin (delegate to services)
- Service layer patterns (business logic only)
- Repository pattern (for complex data access)
- **Path aliases: ALWAYS use `@/` prefix**
- DTOs and validation (class-validator)
- Swagger documentation (`@ApiProperty()`)
- Error handling (NestJS exceptions)
- Async/await (NEVER `.then()`)
- Mongoose best practices
- Dependency injection
- Environment variables (`@nestjs/config`)
- Testing patterns
- AI Agent specific rules (SessionHelper, fallbacks)

### 02-frontend.md
**Applies to:** `/frontend/src/` (Next.js/React)

Frontend-specific rules:
- Component size limits (max 400 lines)
- State management strategy:
  - **Redux Toolkit** → Global state (auth, preferences)
  - **TanStack Query** → Server state (API data)
  - **useState** → Local UI state
- **API calls MUST use service layer**
- Form handling (React Hook Form + Zod)
- Client vs Server Components (`'use client'` only when needed)
- TypeScript in React (prop types)
- Custom hooks for complex logic
- Component composition
- Material-UI theming
- Performance (memoization, React.memo)
- Error boundaries
- Environment variables (`NEXT_PUBLIC_` prefix)
- Accessibility (semantic HTML, ARIA)

### 03-ai-service.md
**Applies to:** `/backend/ai/` (Python/FastAPI)

AI Service-specific rules:
- File organization (routers < 400 lines, services < 500 lines)
- Python naming conventions:
  - **Constants: UPPER_SNAKE_CASE**
  - **Functions/variables: snake_case**
  - **Classes: PascalCase**
- **Type hints MANDATORY** (all functions)
- Pydantic models for validation
- Async/await for I/O operations
- Error handling (FastAPI HTTPException)
- Logging (Python logging module, not print)
- FastAPI best practices (routers, dependencies)
- Docstrings (Google-style)
- Pydantic Settings for environment variables
- Testing with pytest
- Connection pooling
- Security (input validation, error sanitization)

## Quick Reference

### File Size Limits
| Type | Max Lines |
|------|-----------|
| Any file | 1000 |
| Backend Controller | 200 |
| Backend Service | 500 |
| Backend Repository | 400 |
| Frontend Component | 400 |
| Frontend Page | 300 |
| Frontend Hook | 150 |
| Python Router | 400 |
| Python Service | 500 |

**If exceeded → REFACTOR immediately before making changes**

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `CallProcessorService` |
| Functions/Methods | camelCase (TS), snake_case (Py) | `handleVoice()`, `process_call()` |
| Variables | camelCase (TS), snake_case (Py) | `callSid`, `call_sid` |
| **Constants** | **UPPER_SNAKE_CASE** | `MAX_RETRY_ATTEMPTS` |
| Files | kebab-case | `call-processor.service.ts` |
| Booleans | is/has/should prefix | `isValid`, `hasPermission` |

### Critical Rules

#### ❌ NEVER
- Exceed 1000 lines in any file
- Use `any` type in TypeScript
- Use `console.log` or `print` (use proper logging)
- Use relative imports (use `@/` in backend/frontend)
- Modify `dist/`, `.next/`, `node_modules/`
- Put business logic in controllers
- Duplicate server state in Redux
- Use lowercase constants
- Access Redis directly (use SessionHelper)
- Forget AI fallback responses
- Commit `.env` files or secrets

#### ✅ ALWAYS
- Follow SOLID, DRY, KISS principles
- Use UPPER_SNAKE_CASE for constants
- Use dependency injection
- Handle all errors gracefully
- Write type-safe code
- Use proper logging (winstonLogger in TS, logging in Python)
- Validate all inputs
- Write tests
- Use service layer for API calls (frontend)
- Have AI fallback responses (backend)
- Use async/await (never .then())

## Usage

These rules are automatically read by:
- **Cursor AI** - Uses `.cursor/rules/` directory
- **GitHub Copilot** - Can be referenced
- **Claude Code** - References via `.cursorrules` and CLAUDE.md

### For Developers

1. Read `00-general.md` first (applies to all code)
2. Read domain-specific rules for your work:
   - Backend work → `01-backend.md`
   - Frontend work → `02-frontend.md`
   - AI service work → `03-ai-service.md`
3. Use checklists at the end of each file before committing

### For AI Coding Tools

The root `.cursorrules` file provides a comprehensive overview and links to these detailed rules. AI tools should:
1. Follow principles in `.cursorrules`
2. Reference specific domain rules from this directory
3. Enforce file size limits automatically
4. Suggest refactoring when rules are violated

## Enforcement

**File Size Violations:**
If a file exceeds 1000 lines:
1. Stop current work
2. Create refactoring plan
3. Extract logical sections into separate files
4. Update imports
5. Run tests
6. Then proceed with intended changes

**Constant Naming Violations:**
If a constant is not UPPER_SNAKE_CASE:
1. Rename immediately
2. Update all references
3. Ensure no regressions

**Protected File Violations:**
If attempting to modify `dist/`, `.next/`, etc.:
1. Stop immediately
2. Find source file
3. Modify source instead
4. Rebuild

## Updating Rules

When updating rules:
1. Update appropriate domain file
2. Update root `.cursorrules` if needed
3. Update `CLAUDE.md` if it affects architecture
4. Communicate changes to team
5. Run linters to catch violations

## Questions?

See main project documentation:
- [CLAUDE.md](../CLAUDE.md) - Architecture and patterns
- [.cursorrules](../.cursorrules) - Main coding rules
- [README.md](../README.md) - Project overview
