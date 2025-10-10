# AI Agent System PRD

## Overview

The AI Agent System is the core intelligence of DispatchAI, responsible for understanding customer needs, conducting natural conversations, and autonomously completing service bookings over the phone.

## Objectives

**Primary Goals:**
1. Handle 95%+ of customer calls without human intervention
2. Maintain >40% booking conversion rate
3. Provide human-like conversation experience
4. Complete average call in <3 minutes
5. Achieve >4.5/5 customer satisfaction rating

**Success Criteria:**
- First call resolution >90%
- AI accuracy >95% (correct intent understanding)
- Call abandonment rate <5%
- Escalation to human <5% of calls

## Agent Capabilities

### 🟢 Core Capabilities (Implemented)

#### 1. Natural Language Understanding

**Capability:** Understand customer intent from natural speech

**Features:**
- Multi-turn conversation handling
- Context retention across conversation
- Intent classification (booking, inquiry, complaint)
- Entity extraction (service type, date, time, contact info)
- Handles varied phrasings and colloquialisms

**Examples:**
```
Customer: "I need someone to fix my AC, it's not cooling"
Agent Understanding:
  - Intent: Service Request
  - Service Category: HVAC
  - Problem: AC not cooling
  - Urgency: Immediate (implied)

Customer: "Can you guys do it tomorrow afternoon?"
Agent Understanding:
  - Intent: Availability Check
  - Date: Tomorrow (relative)
  - Time: Afternoon (2pm-6pm range)
```

#### 2. Conversation Management

**Capability:** Autonomously guide conversation toward booking completion

**Conversation Flow:**
```
1. Welcome & Greeting
   ├─ Introduce business
   ├─ List available services
   └─ Ask how to help

2. Intent Understanding
   ├─ Identify service needed
   ├─ Understand customer requirements
   └─ Ask clarifying questions

3. Information Collection
   ├─ Gather customer details (name, contact)
   ├─ Determine preferred date/time
   ├─ Collect service-specific info
   └─ Note special requests

4. Availability Check
   ├─ Check scheduling system
   ├─ Offer available time slots
   └─ Handle conflicts/reschedule

5. Booking Confirmation
   ├─ Repeat booking details
   ├─ Confirm customer agreement
   ├─ Create booking record
   └─ Provide confirmation

6. Closing
   ├─ Thank customer
   ├─ Provide next steps
   └─ End call
```

**Decision Points:**
- When to ask clarifying questions
- When to offer alternatives
- When conversation is complete
- When to escalate to human (future)

#### 3. Service Knowledge

**Capability:** Maintain comprehensive knowledge of business offerings

**Knowledge Base Includes:**
- Service catalog (name, description, pricing)
- Service duration estimates
- Service requirements (e.g., "need to access attic")
- Service limitations (e.g., "only residential")
- Company policies (cancellation, payment, etc.)

**Dynamic Loading:**
```typescript
// Agent loads on call initiation
{
  company: {
    name: "ABC Plumbing",
    greeting: "Thank you for calling ABC Plumbing...",
  },
  services: [
    {
      id: "srv_123",
      name: "Drain Cleaning",
      price: "$150",
      duration: "60 minutes",
      description: "Professional drain cleaning..."
    },
    // ... more services
  ]
}
```

#### 4. Contextual Memory

**Capability:** Remember conversation history and context

**Short-term Memory (Active Call):**
- All customer messages
- All agent responses
- Extracted information (name, service, date, etc.)
- Conversation state (intent, stage)
- Business context (services, availability)

**Memory Structure:**
```typescript
interface CallSession {
  callSid: string;
  history: Array<{
    speaker: 'customer' | 'AI';
    message: string;
    timestamp: string;
  }>;
  extractedInfo: {
    customerName?: string;
    customerPhone?: string;
    serviceRequested?: string;
    preferredDate?: string;
    preferredTime?: string;
    notes?: string;
  };
  company: CompanyInfo;
  services: ServiceInfo[];
}
```

**Long-term Memory (Post-Call):**
- Call logs in MongoDB
- Transcripts for training
- Customer preferences (future)
- Common questions/issues (future)

#### 5. Decision Making

**Capability:** Make autonomous decisions about conversation flow

**Decision Types:**

**A. Continue vs. End Call**
```typescript
{
  message: "Great! Your appointment is confirmed for tomorrow at 2pm.",
  shouldHangup: true  // Agent decides conversation is complete
}
```

**B. Information Gathering Strategy**
- Ask one question at a time vs. multiple
- Direct questions vs. open-ended
- Prioritize critical info vs. optional

**C. Handling Uncertainty**
- Request clarification
- Offer alternatives
- Suggest next best action

**D. Error Recovery**
- Rephrase question if not understood
- Provide examples
- Simplify language

### 🟡 Enhanced Capabilities (In Progress)

#### Multi-language Support

**Status:** 🟡 Spanish in development

**Capabilities:**
- Auto-detect customer language
- Respond in customer's language
- Switch languages mid-conversation
- Maintain context across languages

**Supported Languages (Roadmap):**
- 🟢 English (US)
- 🟡 Spanish (Q1 2024)
- 🔵 Mandarin Chinese (Q2 2024)
- 🔵 French (Q3 2024)

#### Sentiment Analysis

**Status:** 🟡 In development

**Capabilities:**
- Detect customer emotion (happy, frustrated, angry, confused)
- Adapt tone based on sentiment
- Escalate if customer is very upset
- Track satisfaction trends

**Use Cases:**
```
Customer: "This is the third time I'm calling about this!"
Sentiment: Frustrated/Angry
Agent Response: Apologetic, empathetic, offer immediate solution

Customer: "You guys are the best, so helpful!"
Sentiment: Happy/Satisfied
Agent Response: Warm, appreciative, reinforce positive experience
```

### 🔵 Future Capabilities (Planned)

#### Intelligent Upselling

**Target:** Q2 2024

**Capabilities:**
- Recommend related services
- Bundle offerings
- Seasonal promotions
- Loyalty rewards

**Example:**
```
Customer books drain cleaning
Agent suggests: "While our technician is there, would you like us to
                inspect your water heater? We're offering a free
                inspection this month."
```

#### Proactive Follow-up

**Target:** Q3 2024

**Capabilities:**
- Call customers for appointment reminders
- Follow up on completed services
- Request reviews
- Offer maintenance plans

#### Voice Customization

**Target:** Q2 2024

**Options:**
- Male/female voice
- Accent selection
- Speech rate
- Tone (professional, friendly, casual)

#### Emotional Intelligence

**Target:** Q3 2024

**Capabilities:**
- Recognize vocal emotions (not just words)
- Mirror customer energy level
- Build rapport through conversation style
- Detect and respond to sarcasm

## Agent Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Customer Call                         │
│                   (Voice Input)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                Twilio (Speech-to-Text)                   │
│                  Converts to Text                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           CallProcessorService (Orchestrator)            │
│                                                          │
│  1. Load Session & Context (Redis)                      │
│  2. Append Customer Message                             │
│  3. Call AI Service for Response                        │
│  4. Decide Next Action                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AI Service (LLM Reasoning)                  │
│                                                          │
│  Input:                                                  │
│  - Customer message                                     │
│  - Conversation history                                 │
│  - Business context (services, etc.)                    │
│                                                          │
│  Process:                                               │
│  - Understand intent                                    │
│  - Extract information                                  │
│  - Generate natural response                            │
│  - Decide if conversation complete                      │
│                                                          │
│  Output:                                                │
│  - Response text                                        │
│  - shouldHangup flag                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Twilio (Text-to-Speech)                    │
│             Converts to Voice + TwiML                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                Customer Hears Response                   │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. CallProcessorService
**Role:** Agent orchestration and conversation flow control

**Responsibilities:**
- Initialize agent session on call start
- Load business context (company, services)
- Manage conversation loop
- Call AI service for reasoning
- Control call flow (continue/end)
- Handle errors and fallbacks

**Location:** `backend/src/modules/telephony/services/call-processor.service.ts`

#### 2. SessionHelper
**Role:** Agent memory management

**Responsibilities:**
- Create/retrieve conversation sessions
- Store conversation history
- Maintain business context
- Manage session lifecycle
- Clean up after call completion

**Storage:** Redis (short-term, active calls)

**Location:** `backend/src/modules/telephony/helpers/session.helper.ts`

#### 3. AiIntegrationService
**Role:** Interface to LLM reasoning engine

**Responsibilities:**
- Call Python AI service
- Handle timeouts and retries
- Parse AI responses
- Manage fallback responses

**Location:** `backend/src/modules/telephony/services/ai-integration.service.ts`

#### 4. AI Service (Python)
**Role:** LLM-powered reasoning and response generation

**Responsibilities:**
- Process conversation context
- Understand customer intent
- Generate natural language responses
- Make conversation decisions
- Extract structured information

**Technology:** FastAPI + LangChain + OpenAI GPT-4

**Location:** `backend/ai/app/`

#### 5. CallDataPersistenceService
**Role:** Post-call data handling

**Responsibilities:**
- Generate AI summary
- Create call log record
- Save transcript
- Extract analytics data
- Clean up Redis session

**Location:** `backend/src/modules/telephony/services/call-data-persistence.service.ts`

## AI Training & Improvement

### Training Data Sources

**Current:**
- Real customer calls (with permission)
- Simulated conversations
- Common service industry scenarios

**Future:**
- Customer feedback on call quality
- Booking success/failure analysis
- A/B testing different responses
- Human agent conversations (for comparison)

### Continuous Improvement Loop

```
1. Collect Data
   ├─ Call recordings
   ├─ Transcripts
   ├─ Customer satisfaction ratings
   └─ Booking outcomes

2. Analyze Performance
   ├─ Identify misunderstandings
   ├─ Find conversation dead-ends
   ├─ Measure conversion rates
   └─ Track common complaints

3. Improve Model
   ├─ Add training examples
   ├─ Refine prompts
   ├─ Update conversation flows
   └─ Add new capabilities

4. Test & Validate
   ├─ A/B testing
   ├─ Shadow mode (compare to human)
   ├─ Beta customer feedback
   └─ Quality assurance review

5. Deploy & Monitor
   ├─ Gradual rollout
   ├─ Real-time monitoring
   ├─ Performance tracking
   └─ Incident response
```

### Quality Metrics

| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| Intent Accuracy | >95% | 🟡 TBD | Manual review of sample calls |
| Booking Conversion | >40% | 🟡 TBD | Bookings ÷ Eligible calls |
| Customer Satisfaction | >4.5/5 | 🟡 TBD | Post-call survey |
| Average Handle Time | <3 min | 🟡 TBD | Call duration tracking |
| First Call Resolution | >90% | 🟡 TBD | Follow-up call rate |

## Error Handling & Fallbacks

### Fallback Hierarchy

**Level 1: Rephrasing**
```
Customer: [unclear speech]
Agent: "I'm sorry, I didn't quite catch that. Could you repeat?"
```

**Level 2: Simplification**
```
Customer: [complex multi-part question]
Agent: "Let me help you step by step. First, which service do you need?"
```

**Level 3: Alternatives**
```
Customer: [asking for unavailable time]
Agent: "I don't have that slot available. I can offer Tuesday at 2pm or
        Wednesday at 10am. Which works better?"
```

**Level 4: Generic Fallback**
```
Agent: "I apologize, I'm having trouble understanding. Let me help you
        book an appointment. What type of service do you need?"
```

**Level 5: Human Escalation (Future)**
```
Agent: "I'd like to connect you with one of our team members who can
        better assist you. Please hold for a moment."
```

### AI Service Failure Handling

**Scenario:** AI service is down or times out

**Response:**
```typescript
try {
  const response = await aiService.getReply(callSid, message);
} catch (error) {
  // Fallback response
  return SYSTEM_RESPONSES.FALLBACK;
  // "I apologize, I'm experiencing technical difficulties.
  //  Please try calling back in a few minutes."
}
```

**Monitoring:** Alert on-call engineer if failure rate >1%

## Privacy & Compliance

### Data Handling

**Call Recordings:**
- Stored securely in Twilio/cloud storage
- Encrypted at rest and in transit
- Retention policy: 90 days default
- Customer can request deletion

**Transcripts:**
- Stored in MongoDB
- Personal information redacted for analytics
- Access limited to business owner

**Customer Data:**
- Minimal collection (name, phone, service request)
- Not shared with third parties
- Compliant with TCPA regulations

### Consent

**Recording Notice:**
"This call may be recorded for quality and training purposes."

**Data Usage:**
- Explicit consent for call recording
- Opt-out option available
- Privacy policy disclosure

## Testing Strategy

### Pre-launch Testing

**Unit Tests:**
- Intent classification accuracy
- Entity extraction precision
- Response generation quality

**Integration Tests:**
- End-to-end call flows
- Twilio integration
- Database operations

**User Acceptance Testing:**
- Beta customers test real calls
- Feedback collection
- Issue identification

### Ongoing Testing

**A/B Testing:**
- Test different conversation flows
- Compare greeting variations
- Optimize booking conversion

**Shadow Mode:**
- Run AI alongside human agents
- Compare responses
- Identify improvement areas

**Quality Assurance:**
- Random call sampling (10%)
- Manual review by QA team
- Score against quality rubric

## Success Stories (Template)

### Home Services Example

**Before DispatchAI:**
- Missed 40% of calls (busy, after hours)
- Average booking time: 8 minutes per call
- Staff cost: $15/hour × 20 hours/week = $300/week

**After DispatchAI:**
- Answer rate: 100%
- Average booking time: 2.5 minutes
- Cost: $199/month
- **ROI:** Save $900/month, capture +40% more leads

### Beauty Salon Example

**Before DispatchAI:**
- 30% of calls during service appointments (interrupted)
- Inconsistent customer information collection
- Double bookings due to manual errors

**After DispatchAI:**
- 100% call coverage without interruptions
- Complete, accurate customer data
- Zero double bookings
- **Result:** 25% increase in appointments booked

## Appendix

### Related Documents
- [Product Overview](./01-product-overview.md)
- [Telephony System](./03-telephony-system.md)
- [Technical Architecture](./07-technical-architecture.md)

### Glossary
- **Intent:** What the customer wants to accomplish
- **Entity:** Specific information (date, service name, etc.)
- **Session:** Conversation state during active call
- **Context:** All relevant information for understanding current message
- **Fallback:** Default response when AI is uncertain
- **LLM:** Large Language Model (GPT-4, etc.)
