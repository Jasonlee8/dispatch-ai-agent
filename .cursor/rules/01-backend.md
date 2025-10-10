# Backend (NestJS) Specific Rules

Rules specific to the NestJS backend in `/backend/src/`.

## Module Structure (MANDATORY)

### File Organization

Every module MUST follow this structure:

```
feature/
├── feature.module.ts          # Module definition
├── feature.controller.ts      # HTTP endpoints (THIN - max 200 lines)
├── feature.service.ts         # Business logic (max 500 lines)
├── schema/
│   └── feature.schema.ts      # Mongoose schema
├── dto/
│   ├── create-feature.dto.ts  # Create validation
│   └── update-feature.dto.ts  # Update validation
├── helpers/                   # Pure utility functions
│   └── feature-helper.ts      # (max 300 lines each)
├── repositories/              # Data access layer
│   └── feature.repository.ts  # (max 400 lines)
└── types/                     # TypeScript interfaces
    └── feature-types.ts       # (max 200 lines)
```

**If any file exceeds its max line limit, refactor immediately.**

### Controller Rules

**Controllers MUST be thin (< 200 lines)**

```typescript
// ✅ GOOD - Thin controller
@Controller('service')
@ApiTags('service')
export class ServiceController {
  constructor(private readonly service: ServiceService) {}

  @Get()
  @ApiOperation({ summary: 'Get all services' })
  async findAll(@Query('userId') userId?: string) {
    return this.service.findAll(userId);
  }

  @Post()
  @ApiOperation({ summary: 'Create a service' })
  async create(@Body() dto: CreateServiceDto) {
    return this.service.create(dto);
  }
}

// ❌ BAD - Business logic in controller
@Controller('service')
export class ServiceController {
  @Post()
  async create(@Body() dto: CreateServiceDto) {
    // Don't do validation here
    if (!dto.name) throw new BadRequestException();

    // Don't do business logic here
    const service = new this.model(dto);
    await service.save();

    // Don't do transformations here
    return { id: service._id, ...service };
  }
}
```

**Controller Responsibilities (ONLY):**
1. Receive HTTP request
2. Validate request (using DTOs)
3. Call service method
4. Return HTTP response

**Controllers MUST NOT:**
- Contain business logic
- Access database directly
- Transform data
- Handle errors beyond throwing NestJS exceptions

### Service Rules

**Services contain ALL business logic**

```typescript
// ✅ GOOD - Business logic in service
@Injectable()
export class ServiceService {
  constructor(
    @InjectModel(Service.name) private model: Model<ServiceDocument>,
    private readonly validationHelper: ValidationHelper,
    private readonly emailService: EmailService,
  ) {}

  async create(dto: CreateServiceDto): Promise<Service> {
    // Validation
    await this.validationHelper.validateServiceData(dto);

    // Business logic
    const service = new this.model(dto);
    await service.save();

    // Side effects
    await this.emailService.sendServiceCreatedEmail(service);

    return service;
  }

  async findAll(userId?: string): Promise<Service[]> {
    const filter = userId ? { userId: { $eq: userId } } : {};
    return this.model.find(filter).exec();
  }
}
```

**Service MUST:**
- Be marked with `@Injectable()`
- Use constructor injection for dependencies
- Return domain objects (not HTTP responses)
- Handle business logic and orchestration
- Be testable (mockable dependencies)

**Service MUST NOT:**
- Know about HTTP (no Request, Response objects)
- Access database directly (use repositories)
- Return HTTP status codes

### Repository Pattern (For Complex Data Access)

**Use repositories to encapsulate data access:**

```typescript
// ✅ GOOD - Repository pattern
@Injectable()
export class SessionRepository {
  constructor(
    @Inject('REDIS_CLIENT') private readonly redis: Redis
  ) {}

  async create(callSid: string): Promise<CallSkeleton> {
    const session: CallSkeleton = {
      callSid,
      history: [],
      company: null,
      services: [],
    };
    await this.redis.set(callSid, JSON.stringify(session), 'EX', 3600);
    return session;
  }

  async load(callSid: string): Promise<CallSkeleton | null> {
    const data = await this.redis.get(callSid);
    return data ? JSON.parse(data) : null;
  }

  async delete(callSid: string): Promise<void> {
    await this.redis.del(callSid);
  }
}

// Service uses repository
@Injectable()
export class SessionHelper {
  constructor(private readonly repository: SessionRepository) {}

  async ensureSession(callSid: string): Promise<CallSkeleton> {
    let session = await this.repository.load(callSid);
    if (!session) {
      session = await this.repository.create(callSid);
    }
    return session;
  }
}
```

**When to use Repository Pattern:**
- Complex queries
- Multiple data sources (Redis, MongoDB, external APIs)
- Need for query optimization
- Data access needs testing in isolation

## Path Aliases (MANDATORY)

**ALWAYS use `@/` prefix, NEVER relative paths**

```typescript
// ✅ REQUIRED
import { UserService } from '@/modules/user/user.service';
import { winstonLogger } from '@/logger/winston.logger';
import { SYSTEM_RESPONSES } from '@/common/constants/system-responses.constant';

// ❌ FORBIDDEN - Will cause auto-fix
import { UserService } from '../../user/user.service';
import { winstonLogger } from '../../../logger/winston.logger';
```

**If you see a relative import, fix it immediately.**

## DTOs and Validation

### Create Separate DTOs for Different Operations

```typescript
// ✅ GOOD - Separate DTOs
// dto/create-service.dto.ts
export class CreateServiceDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty()
  @IsNumber()
  @IsPositive()
  price: number;
}

// dto/update-service.dto.ts
export class UpdateServiceDto {
  @ApiProperty({ required: false })
  @IsString()
  @IsOptional()
  name?: string;

  @ApiProperty({ required: false })
  @IsNumber()
  @IsPositive()
  @IsOptional()
  price?: number;
}
```

### Validation Rules

**ALL DTOs MUST have validation decorators:**

```typescript
import { IsString, IsNotEmpty, IsOptional, IsNumber, IsEmail, IsEnum } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateBookingDto {
  @ApiProperty({ description: 'User ID' })
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ApiProperty({ description: 'Service ID' })
  @IsString()
  @IsNotEmpty()
  serviceId: string;

  @ApiProperty({ description: 'Booking time' })
  @IsNotEmpty()
  bookingTime: Date;

  @ApiProperty({ description: 'Customer email', required: false })
  @IsEmail()
  @IsOptional()
  customerEmail?: string;

  @ApiProperty({ description: 'Booking status', enum: ['pending', 'confirmed', 'cancelled'] })
  @IsEnum(['pending', 'confirmed', 'cancelled'])
  status: string;
}
```

**Common Validators:**
- `@IsString()` - Must be string
- `@IsNumber()` - Must be number
- `@IsEmail()` - Must be valid email
- `@IsEnum([])` - Must be one of enum values
- `@IsNotEmpty()` - Cannot be empty
- `@IsOptional()` - Can be undefined
- `@IsPositive()` - Must be > 0
- `@Min()` / `@Max()` - Range validation
- `@Length(min, max)` - String length

### Swagger Documentation

**ALL DTOs MUST have `@ApiProperty()`:**

```typescript
export class CreateUserDto {
  @ApiProperty({
    description: 'User email address',
    example: 'user@example.com',
  })
  @IsEmail()
  email: string;

  @ApiProperty({
    description: 'User full name',
    example: 'John Doe',
    minLength: 2,
    maxLength: 100,
  })
  @IsString()
  @Length(2, 100)
  name: string;

  @ApiProperty({
    description: 'User role',
    enum: ['admin', 'user', 'guest'],
    default: 'user',
  })
  @IsEnum(['admin', 'user', 'guest'])
  role: string;
}
```

## Error Handling

### Use NestJS Built-in Exceptions

```typescript
import {
  NotFoundException,
  BadRequestException,
  UnauthorizedException,
  ForbiddenException,
  ConflictException,
  InternalServerException,
} from '@nestjs/common';

// ✅ GOOD
async findById(id: string) {
  const entity = await this.model.findById(id);
  if (!entity) {
    throw new NotFoundException(`Entity with ID ${id} not found`);
  }
  return entity;
}

async create(dto: CreateDto) {
  const existing = await this.model.findOne({ name: dto.name });
  if (existing) {
    throw new ConflictException(`Entity with name ${dto.name} already exists`);
  }
  return this.model.create(dto);
}
```

### Always Log Errors

```typescript
import { winstonLogger } from '@/logger/winston.logger';

async processCall(callSid: string) {
  try {
    const result = await this.aiService.process(callSid);
    return result;
  } catch (error) {
    winstonLogger.error('Failed to process call', {
      callSid,
      error: (error as Error).message,
      stack: (error as Error).stack,
    });
    throw new InternalServerException('Call processing failed');
  }
}
```

## Async/Await (MANDATORY)

**ALWAYS use async/await, NEVER use `.then()`**

```typescript
// ✅ GOOD
async function getUser(id: string) {
  const user = await this.userModel.findById(id);
  const services = await this.serviceModel.find({ userId: id });
  return { user, services };
}

// ✅ GOOD - Concurrent operations
async function getData(id: string) {
  const [user, services, bookings] = await Promise.all([
    this.userModel.findById(id),
    this.serviceModel.find({ userId: id }),
    this.bookingModel.find({ userId: id }),
  ]);
  return { user, services, bookings };
}

// ❌ BAD - Don't use .then()
function getUser(id: string) {
  return this.userModel.findById(id).then(user => {
    return this.serviceModel.find({ userId: user.id }).then(services => {
      return { user, services };
    });
  });
}
```

## Database Operations

### Use Mongoose Properly

```typescript
// ✅ GOOD - Efficient query
async findActiveUsers() {
  return this.userModel
    .find({ isActive: true })
    .select('name email')  // Project only needed fields
    .lean()                // Return plain objects (faster)
    .exec();
}

// ✅ GOOD - With population
async findUserWithServices(id: string) {
  return this.userModel
    .findById(id)
    .populate('services')
    .exec();
}

// ❌ BAD - Fetching all data when not needed
async findActiveUsers() {
  const allUsers = await this.userModel.find().exec();
  return allUsers.filter(u => u.isActive);
}
```

### Add Indexes for Performance

```typescript
// schema/user.schema.ts
@Schema({ timestamps: true })
export class User {
  @Prop({ required: true, unique: true, index: true })
  email: string;

  @Prop({ required: true, index: true })
  twilioPhoneNumber: string;

  @Prop({ default: true, index: true })
  isActive: boolean;
}

// Compound index for common queries
UserSchema.index({ company: 1, isActive: 1 });
```

## Dependency Injection

**ALWAYS use constructor injection:**

```typescript
// ✅ GOOD
@Injectable()
export class CallProcessorService {
  constructor(
    private readonly sessionHelper: SessionHelper,
    private readonly userService: UserService,
    private readonly aiIntegration: AiIntegrationService,
  ) {}
}

// ❌ BAD - Don't create instances manually
@Injectable()
export class CallProcessorService {
  private sessionHelper: SessionHelper;

  constructor() {
    this.sessionHelper = new SessionHelper(); // DON'T DO THIS
  }
}
```

### Export Services That Are Used by Other Modules

```typescript
// user.module.ts
@Module({
  imports: [
    MongooseModule.forFeature([{ name: User.name, schema: UserSchema }])
  ],
  controllers: [UserController],
  providers: [UserService],
  exports: [UserService],  // ✅ Export so other modules can use it
})
export class UserModule {}

// company.module.ts
@Module({
  imports: [UserModule],  // Import UserModule to use UserService
  controllers: [CompanyController],
  providers: [CompanyService],
})
export class CompanyModule {}
```

## Environment Variables

### Use @nestjs/config

```typescript
// ✅ GOOD - Type-safe config
import { ConfigService } from '@nestjs/config';

@Injectable()
export class TwilioService {
  private readonly accountSid: string;
  private readonly authToken: string;

  constructor(private configService: ConfigService) {
    this.accountSid = this.configService.get<string>('TWILIO_ACCOUNT_SID');
    this.authToken = this.configService.get<string>('TWILIO_AUTH_TOKEN');
  }
}

// ❌ BAD - Direct process.env access
@Injectable()
export class TwilioService {
  private readonly accountSid = process.env.TWILIO_ACCOUNT_SID;
}
```

## Testing

### Unit Tests for Services

```typescript
// user.service.spec.ts
describe('UserService', () => {
  let service: UserService;
  let model: Model<UserDocument>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UserService,
        {
          provide: getModelToken(User.name),
          useValue: {
            find: jest.fn(),
            findById: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<UserService>(UserService);
    model = module.get<Model<UserDocument>>(getModelToken(User.name));
  });

  describe('findAll', () => {
    it('should return all users', async () => {
      // Arrange
      const mockUsers = [{ name: 'John' }, { name: 'Jane' }];
      jest.spyOn(model, 'find').mockReturnValue({
        exec: jest.fn().mockResolvedValue(mockUsers),
      } as any);

      // Act
      const result = await service.findAll();

      // Assert
      expect(result).toEqual(mockUsers);
      expect(model.find).toHaveBeenCalled();
    });
  });
});
```

## AI Agent Specific Rules

### Session Management

**NEVER access Redis directly - ALWAYS use SessionHelper:**

```typescript
// ✅ GOOD
await this.sessionHelper.ensureSession(callSid);
await this.sessionHelper.appendUserMessage(callSid, message);

// ❌ BAD
await this.redis.set(callSid, JSON.stringify(data));
```

### AI Integration

**ALWAYS have fallback responses:**

```typescript
// ✅ GOOD
try {
  const reply = await this.aiIntegration.getAIReply(callSid, message);
  return reply.message;
} catch (error) {
  winstonLogger.error('AI service failed', { callSid, error });
  return SYSTEM_RESPONSES.FALLBACK;
}

// ❌ BAD - No fallback
const reply = await this.aiIntegration.getAIReply(callSid, message);
return reply.message;
```

### TwiML Responses

**Use helper utilities:**

```typescript
// ✅ GOOD
return buildSayResponse({
  text: welcomeMessage,
  next: NextAction.GATHER,
  sid: callSid,
  publicUrl: PUBLIC_URL,
});

// ❌ BAD - Manual XML construction
return `<Response><Say>${welcomeMessage}</Say><Gather>...</Gather></Response>`;
```

## Code Review Checklist (Backend)

- [ ] Controllers are thin (< 200 lines)
- [ ] Business logic is in services, not controllers
- [ ] All imports use `@/` prefix
- [ ] All DTOs have validation decorators
- [ ] All DTOs have `@ApiProperty()` decorators
- [ ] All constants are `UPPER_SNAKE_CASE`
- [ ] No `console.log` - using `winstonLogger`
- [ ] All async functions use `async/await`
- [ ] All async functions have error handling
- [ ] No `any` types
- [ ] Repository pattern for complex data access
- [ ] Indexes added for frequently queried fields
- [ ] Tests written/updated
- [ ] No direct Redis access (use SessionHelper)
- [ ] AI integration has fallback responses
