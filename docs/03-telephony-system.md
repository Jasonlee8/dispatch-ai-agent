# Telephony System PRD

## Overview

The Telephony System handles all voice communication between customers and the AI agent, integrating Twilio's voice platform with DispatchAI's backend to enable seamless phone-based interactions.

## Objectives

**Primary Goals:**
1. Provide reliable phone number provisioning
2. Handle high-quality voice-to-text and text-to-voice conversion
3. Maintain <1 second latency for real-time conversation
4. Support 99.9% uptime for voice services
5. Enable call recording and transcription

## System Components

### 🟢 Implemented Components

#### 1. Phone Number Management

**Capability:** Provision and manage business phone numbers

**Features:**
- Purchase Twilio phone numbers
- Assign numbers to businesses
- Configure number settings
- Number porting support (future)

**Technical Implementation:**
```typescript
// Twilio number configuration
{
  phoneNumber: "+1234567890",
  voiceUrl: "https://api.dispatchai.com/api/telephony/voice",
  voiceMethod: "POST",
  statusCallback: "https://api.dispatchai.com/api/telephony/status",
  statusCallbackMethod: "POST"
}
```

#### 2. Incoming Call Handling

**Call Flow:**

```
1. Customer Dials Business Number
   ↓
2. Twilio Receives Call
   ↓
3. POST /api/telephony/voice (Initial webhook)
   ├─ Load business context
   ├─ Initialize AI agent session
   ├─ Generate welcome message
   └─ Return TwiML response
   ↓
4. Twilio Speaks Welcome
   ↓
5. Twilio Gathers Customer Speech
   ↓
6. POST /api/telephony/gather (Each customer input)
   ├─ Convert speech to text
   ├─ Process with AI agent
   ├─ Generate response
   └─ Return TwiML
   ↓
7. Repeat steps 5-6 until conversation complete
   ↓
8. POST /api/telephony/status (Call ends)
   ├─ Generate summary
   ├─ Save transcript
   └─ Create call log
```

**Webhook Endpoints:**

**Voice (Initial):**
```typescript
POST /api/telephony/voice
Request: {
  CallSid: "CAxxxx",
  From: "+1234567890",
  To: "+0987654321",
  CallStatus: "ringing"
}
Response: TwiML XML
```

**Gather (Each turn):**
```typescript
POST /api/telephony/gather
Request: {
  CallSid: "CAxxxx",
  SpeechResult: "I need to fix my AC",
  Confidence: 0.95
}
Response: TwiML XML
```

**Status (Updates):**
```typescript
POST /api/telephony/status
Request: {
  CallSid: "CAxxxx",
  CallStatus: "completed",
  CallDuration: "120"
}
```

#### 3. Speech Recognition (Speech-to-Text)

**Provider:** Twilio (Google Cloud Speech API)

**Configuration:**
- Language: English (US) default
- Speech timeout: 3 seconds
- Enhanced model: True
- Profanity filter: False
- Speech model: "phone_call"

**Quality Settings:**
```xml
<Gather
  input="speech"
  timeout="3"
  speechTimeout="auto"
  language="en-US"
  enhanced="true"
  speechModel="phone_call"
/>
```

**Accuracy:**
- Target: >90% word accuracy
- Monitoring: Confidence scores logged
- Improvement: Acoustic model training (future)

#### 4. Text-to-Speech (Voice Synthesis)

**Provider:** Twilio (Amazon Polly)

**Voice Options:**
- Default: "Polly.Joanna" (female, US English)
- Alternative: "Polly.Matthew" (male, US English)
- Language: en-US

**Configuration:**
```xml
<Say voice="Polly.Joanna" language="en-US">
  Thank you for calling ABC Plumbing...
</Say>
```

**Quality Settings:**
- Natural speaking rate
- Appropriate pauses for punctuation
- Clear pronunciation
- Professional tone

#### 5. Call Recording

**Status:** 🟢 Implemented

**Features:**
- Automatic call recording
- Secure storage (Twilio/S3)
- Recording URL in call log
- Playback in admin dashboard

**Configuration:**
```xml
<Record
  action="https://api.dispatchai.com/api/telephony/recording"
  timeout="10"
  transcribe="false"
/>
```

**Storage:**
- Retention: 90 days default
- Encryption: At rest and in transit
- Access: Business owner only
- Deletion: On request or auto-purge

#### 6. Call Status Tracking

**Status Types:**
- `queued` - Call initiated
- `ringing` - Phone ringing
- `in-progress` - Call active
- `completed` - Call ended normally
- `busy` - Line busy
- `failed` - Call failed
- `no-answer` - No answer

**Status Handling:**
```typescript
const statusHandlers = {
  'completed': handleCompletedStatus,    // Save data, generate summary
  'busy': handleFinalStatus,             // Log and cleanup
  'failed': handleFinalStatus,           // Log error, cleanup
  'no-answer': handleFinalStatus,        // Log and cleanup
  'queued': handleNonFinalStatus,        // Just log
  'ringing': handleNonFinalStatus,       // Just log
  'in-progress': handleNonFinalStatus,   // Just log
};
```

### 🟡 In Progress

#### Multi-number Support

**Status:** 🟡 Development

**Capability:** Support multiple phone numbers per business

**Use Cases:**
- Different numbers for different locations
- Separate marketing campaign numbers
- Dedicated VIP customer line

**Implementation:**
```typescript
interface PhoneNumber {
  id: string;
  number: string;
  location?: string;
  label?: string;
  isActive: boolean;
  forwardTo?: string;  // Optional human fallback
}
```

### 🔵 Planned Features

#### Call Forwarding

**Target:** Q2 2024

**Capability:** Forward calls to human agent when needed

**Use Cases:**
- AI unable to handle request
- Customer requests human
- VIP customers
- Complex issues

**Configuration:**
```typescript
interface CallForwardingRule {
  condition: 'ai_escalation' | 'customer_request' | 'vip' | 'time_based';
  destination: string;  // Phone number or SIP address
  priority: number;
  enabled: boolean;
}
```

#### Voicemail Handling

**Target:** Q2 2024

**Capability:** Leave voicemail when customer doesn't answer

**Features:**
- Outbound call campaigns
- Custom voicemail messages
- Transcription of received voicemails

#### SMS Integration

**Target:** Q1 2024

**Capability:** Send SMS follow-ups and confirmations

**Use Cases:**
- Booking confirmations
- Reminder notifications
- Follow-up links
- Customer feedback requests

**Example:**
```
SMS after booking:
"Your appointment with ABC Plumbing is confirmed for
tomorrow at 2:00 PM. Reply CANCEL to cancel or RESCHEDULE
to change time."
```

#### International Calling

**Target:** Q3 2024

**Capability:** Support numbers in multiple countries

**Initial Markets:**
- 🟢 US (implemented)
- 🔵 Canada
- 🔵 UK
- 🔵 Australia

## TwiML Response Generation

### Response Structure

**Basic Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Joanna">
    Hello, thank you for calling ABC Plumbing.
  </Say>
  <Gather input="speech" action="/api/telephony/gather" timeout="3">
    <Say>How can I help you today?</Say>
  </Gather>
</Response>
```

**Response with Recording:**
```xml
<Response>
  <Say>Let me help you with that.</Say>
  <Record action="/api/telephony/recording" maxLength="60"/>
  <Say>Thank you, goodbye!</Say>
  <Hangup/>
</Response>
```

**Hangup Response:**
```xml
<Response>
  <Say>Thank you for calling. Goodbye!</Say>
  <Hangup/>
</Response>
```

### Helper Functions

**Location:** `backend/src/modules/telephony/utils/twilio-response.util.ts`

```typescript
export function buildSayResponse(options: {
  text: string;
  next: NextAction;
  sid: string;
  publicUrl: string;
}): string {
  const { text, next, sid, publicUrl } = options;

  if (next === NextAction.HANGUP) {
    return `
      <Response>
        <Say voice="Polly.Joanna">${escapeXml(text)}</Say>
        <Hangup/>
      </Response>
    `;
  }

  return `
    <Response>
      <Gather
        input="speech"
        action="${publicUrl}/telephony/gather"
        method="POST"
        timeout="3"
        speechTimeout="auto"
      >
        <Say voice="Polly.Joanna">${escapeXml(text)}</Say>
      </Gather>
    </Response>
  `;
}
```

## Call Quality & Performance

### Quality Metrics

| Metric | Target | Monitoring |
|--------|--------|------------|
| Speech Recognition Accuracy | >90% | Confidence scores |
| Call Latency (total) | <1s | Response time tracking |
| AI Response Time | <2s | Service timing |
| Voice Quality (MOS) | >4.0 | Twilio metrics |
| Call Completion Rate | >95% | Status tracking |

### Performance Optimization

**Latency Reduction:**
1. **Concurrent Processing**
   - Parallel AI service calls
   - Async database operations
   - Connection pooling

2. **Caching**
   - Business context cached in Redis
   - Frequently used responses cached
   - Session state optimized

3. **Response Streaming**
   - Return TwiML immediately
   - Stream AI responses as generated (future)

**Network Optimization:**
- CDN for static assets
- Regional Twilio numbers
- Optimized API routing

### Error Handling

**Twilio Errors:**
```typescript
try {
  const response = await generateAIResponse(message);
  return buildTwiML(response);
} catch (error) {
  logger.error('AI service failed', { error });
  // Fallback response
  return buildTwiML({
    text: SYSTEM_RESPONSES.FALLBACK,
    action: NextAction.HANGUP
  });
}
```

**Network Failures:**
- Retry logic (max 3 attempts)
- Exponential backoff
- Circuit breaker pattern

**Timeout Handling:**
- 5 second timeout for AI service
- 10 second total call processing timeout
- Graceful degradation with fallback

## Security & Compliance

### Call Security

**Encryption:**
- TLS 1.2+ for webhooks
- SRTP for media streams
- Encrypted storage for recordings

**Authentication:**
- Twilio webhook signature validation
- API key authentication
- IP whitelist for webhooks

**Validation:**
```typescript
import { validateRequest } from 'twilio';

function validateTwilioRequest(req: Request): boolean {
  const signature = req.headers['x-twilio-signature'];
  const url = `${PUBLIC_URL}${req.path}`;
  const params = req.body;

  return validateRequest(
    TWILIO_AUTH_TOKEN,
    signature,
    url,
    params
  );
}
```

### TCPA Compliance

**Requirements:**
- Do Not Call list checking (planned)
- Recording consent notification
- Opt-out mechanism
- Call time restrictions (8am-9pm local)

**Implementation:**
```typescript
// Call time validation
function isValidCallTime(timezone: string): boolean {
  const localTime = moment().tz(timezone);
  const hour = localTime.hour();
  return hour >= 8 && hour < 21;  // 8am to 9pm
}
```

### Data Privacy

**PII Handling:**
- Minimal data collection
- Encryption at rest
- Access logging
- Retention policies

**Customer Rights:**
- Request call recording
- Request data deletion
- Opt-out of recording
- Access to transcripts

## Monitoring & Alerts

### Real-time Monitoring

**Metrics Tracked:**
- Active calls count
- Call success/failure rate
- Average call duration
- Speech recognition confidence
- AI response latency
- System errors

**Dashboard:**
- Real-time call status
- Error rate graphs
- Performance metrics
- Alert history

### Alerting

**Critical Alerts:**
- Twilio service down
- High error rate (>1%)
- AI service unavailable
- Database connection lost

**Warning Alerts:**
- High call volume
- Low speech confidence (<80%)
- Slow AI responses (>3s)
- Increased call duration

**Alert Channels:**
- Email to on-call engineer
- Slack notifications
- PagerDuty integration (future)

## Testing Strategy

### Pre-production Testing

**Unit Tests:**
- TwiML generation
- Webhook validation
- Status handling

**Integration Tests:**
- End-to-end call simulation
- Twilio webhook handling
- Error scenarios

**Load Testing:**
- Concurrent call handling
- Peak volume simulation
- Stress testing

### Production Testing

**Synthetic Monitoring:**
- Automated test calls every hour
- Voice quality validation
- End-to-end flow verification

**A/B Testing:**
- Different voice options
- Speech timeout values
- TwiML configurations

## Cost Management

### Twilio Pricing

**Phone Numbers:**
- $1/month per number

**Voice Usage:**
- Inbound: $0.0085/minute
- Outbound: $0.013/minute (future)
- Recording: $0.0025/minute

**Estimated Costs:**

| Monthly Calls | Duration | Cost |
|--------------|----------|------|
| 100 calls | 3 min avg | $2.55 |
| 500 calls | 3 min avg | $12.75 |
| 1000 calls | 3 min avg | $25.50 |

**Cost Optimization:**
- Reduce average handle time
- Optimize speech timeouts
- Efficient call routing
- Compression for recordings

## Future Enhancements

### Q1 2024
- ✅ SMS notifications
- ✅ Multi-language support
- Call analytics dashboard
- Enhanced reporting

### Q2 2024
- Call forwarding to humans
- Voicemail handling
- Conference calling
- Call queuing

### Q3 2024
- Advanced IVR menus
- Call center features
- Supervisor monitoring
- Quality scoring

### Q4 2024
- Video calling support
- Screen sharing (for visual services)
- Multi-channel (voice + SMS + chat)
- AI voice cloning (custom voices)

## Appendix

### Related Documents
- [AI Agent System](./02-ai-agent-system.md)
- [Technical Architecture](./07-technical-architecture.md)
- [API Specification](./api-specification.md)

### External References
- [Twilio Voice Documentation](https://www.twilio.com/docs/voice)
- [TwiML Reference](https://www.twilio.com/docs/voice/twiml)
- [Twilio Best Practices](https://www.twilio.com/docs/voice/best-practices)

### Glossary
- **TwiML** - Twilio Markup Language for call control
- **SIP** - Session Initiation Protocol
- **SRTP** - Secure Real-time Transport Protocol
- **MOS** - Mean Opinion Score (voice quality metric)
- **TCPA** - Telephone Consumer Protection Act
- **DNC** - Do Not Call list
