# DispatchAI Frontend

Next.js 15 admin dashboard for DispatchAI - manage your AI agent service booking platform. This modern React-based application provides business owners with complete control over their autonomous AI phone agents, services, bookings, and analytics.

## Overview

The frontend is a comprehensive management interface for the DispatchAI AI Agent system, featuring:

- 📞 **Call Management** - View AI agent conversation logs, transcripts, and call analytics
- 📅 **Booking Dashboard** - Manage service bookings captured by the AI agent
- 🤖 **Agent Configuration** - Customize AI agent greetings, services, and behavior
- 📊 **Analytics & Insights** - Monitor AI agent performance and customer interactions
- 🏢 **Multi-location Support** - Manage services across different branches
- ⚙️ **Settings & Customization** - Configure company profile, availability, and preferences
- 💳 **Subscription Management** - Handle billing and plan upgrades via Stripe

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: Material-UI (MUI) v6
- **State Management**: Redux Toolkit + redux-persist
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **Calendar**: react-big-calendar
- **Styling**: Emotion (CSS-in-JS)
- **Charts**: MUI X Charts
- **Code Quality**: ESLint, Prettier, Husky (Git hooks)

## Project Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── (public)/              # Public routes (landing, pricing)
│   │   ├── admin/                 # Admin dashboard routes
│   │   │   ├── calendar/          # Booking calendar view
│   │   │   ├── call-log/          # AI agent call history
│   │   │   ├── company/           # Company management
│   │   │   ├── onboarding/        # Initial setup wizard
│   │   │   ├── overview/          # Dashboard home
│   │   │   ├── service/           # Service management
│   │   │   ├── settings/          # Account settings
│   │   │   ├── subscription/      # Billing & plans
│   │   │   └── transcript/        # Conversation transcripts
│   │   ├── auth/                  # Authentication pages
│   │   ├── onboarding/            # User onboarding flow
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Landing page
│   │   └── StoreProvider.tsx      # Redux provider wrapper
│   │
│   ├── features/                   # Feature-based modules
│   │   ├── auth/                  # Authentication components & logic
│   │   ├── calendar/              # Calendar components
│   │   ├── callog/                # Call log components
│   │   ├── company/               # Company management
│   │   ├── onboarding/            # Onboarding wizard
│   │   ├── overview/              # Dashboard widgets
│   │   ├── public/                # Public-facing components
│   │   ├── service/               # Service configuration
│   │   ├── service-management/    # Advanced service tools
│   │   ├── settings/              # Settings panels
│   │   ├── subscription/          # Subscription UI
│   │   ├── transcript/            # Transcript viewer
│   │   └── transcript-chunk/      # Transcript segments
│   │
│   ├── components/                 # Shared UI components
│   │   ├── layout/                # Layout components (Header, Sidebar, etc.)
│   │   ├── common/                # Reusable components (Button, Card, etc.)
│   │   └── forms/                 # Form components
│   │
│   ├── redux/                      # Redux state management
│   │   ├── slices/                # Redux Toolkit slices
│   │   └── store.ts               # Store configuration
│   │
│   ├── services/                   # API client services
│   │   ├── api.ts                 # Axios instance & interceptors
│   │   ├── auth.service.ts        # Authentication API
│   │   ├── booking.service.ts     # Booking API
│   │   ├── calllog.service.ts     # Call log API
│   │   └── ...                    # Other service clients
│   │
│   ├── types/                      # TypeScript type definitions
│   │   ├── api/                   # API response types
│   │   ├── models/                # Domain models
│   │   └── common.ts              # Shared types
│   │
│   ├── lib/                        # Utility libraries
│   │   ├── utils.ts               # Helper functions
│   │   └── constants.ts           # App constants
│   │
│   ├── theme/                      # MUI theme configuration
│   │   ├── theme.ts               # Theme definition
│   │   └── palette.ts             # Color palette
│   │
│   ├── utils/                      # Utility functions
│   └── constants/                  # Application constants
│
├── public/                         # Static assets
├── .husky/                         # Git hooks
├── next.config.js                  # Next.js configuration
├── tsconfig.json                   # TypeScript configuration
├── package.json                    # Dependencies and scripts
└── .eslintrc.json                  # ESLint configuration
```

## Getting Started

### Prerequisites

- **Node.js** v20+
- **pnpm** (recommended package manager)

### Installation

```bash
# Install pnpm globally if not already installed
npm install -g pnpm

# Install dependencies
pnpm install
```

### Development

```bash
# Start development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

The app will auto-reload when you edit files in `src/`.

### Build for Production

```bash
# Create optimized production build
pnpm build

# Run production server
pnpm start
```

### Code Quality

```bash
# Run linter with auto-fix
pnpm lint

# Type checking
pnpm type-check

# Run tests (when available)
pnpm test
```

## Key Features

### 1. Call Management & AI Agent Monitoring

**Call Log** (`/admin/call-log`)
- View all AI agent phone conversations
- Filter by date, status, duration
- Quick access to transcripts and summaries

**Transcript Viewer** (`/admin/transcript/:id`)
- Full conversation playback
- AI-generated summaries and key points
- Customer sentiment analysis
- Booking details extracted by AI

### 2. Booking Dashboard

**Calendar View** (`/admin/calendar`)
- Visual booking calendar powered by `react-big-calendar`
- Drag-and-drop rescheduling
- Multi-view support (day, week, month)
- Availability management

**Booking Management**
- View bookings captured by AI agent
- Edit booking details
- Update booking status
- Customer information management

### 3. Service Configuration

**Service Management** (`/admin/service`)
- Define services that AI agent can book
- Set pricing, duration, and descriptions
- Configure dynamic form fields for each service
- AI agent uses this data during conversations

**Service-Location Mapping**
- Assign services to specific locations
- Manage multi-branch operations
- Location-specific pricing and availability

### 4. AI Agent Customization

**Company Settings** (`/admin/company`)
- Business name (used in AI greetings)
- Custom greeting message for AI agent
- Contact information
- Branding configuration

**Availability Settings**
- Define business hours
- Set AI agent operating schedule
- Manage holidays and exceptions

### 5. Analytics & Insights

**Dashboard** (`/admin/overview`)
- Call volume metrics
- Booking conversion rates
- AI agent performance stats
- Revenue tracking
- Customer interaction trends

### 6. Subscription & Billing

**Subscription Management** (`/admin/subscription`)
- View current plan
- Upgrade/downgrade subscriptions
- Billing history
- Stripe integration for payments

## State Management

### Redux Toolkit

The app uses Redux Toolkit for global state management:

```typescript
// Example: Using Redux state in a component
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store/store';
import { setUser } from '@/redux/slices/authSlice';

function MyComponent() {
  const user = useSelector((state: RootState) => state.auth.user);
  const dispatch = useDispatch();

  // Dispatch actions
  dispatch(setUser(userData));
}
```

### Redux Persist

State is automatically persisted to localStorage:
- User authentication state
- User preferences
- Theme settings

### TanStack Query (React Query)

Used for server state management and caching:

```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchBookings } from '@/services/booking.service';

function BookingList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['bookings'],
    queryFn: fetchBookings,
  });
}
```

## API Integration

### API Client Setup

The app uses Axios for HTTP requests with interceptors:

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api',
});

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Service Layer

API calls are organized into service files:

```typescript
// src/services/calllog.service.ts
import api from './api';

export const fetchCallLogs = async () => {
  const response = await api.get('/calllog');
  return response.data;
};

export const fetchCallDetails = async (id: string) => {
  const response = await api.get(`/calllog/${id}`);
  return response.data;
};
```

## Forms & Validation

### React Hook Form + Zod

Forms use React Hook Form with Zod schema validation:

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}
    </form>
  );
}
```

## Styling & Theming

### Material-UI Theme

Customize the theme in `src/theme/theme.ts`:

```typescript
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});
```

### Using MUI Components

```typescript
import { Button, Card, Typography } from '@mui/material';

function MyComponent() {
  return (
    <Card>
      <Typography variant="h5">Title</Typography>
      <Button variant="contained" color="primary">
        Click Me
      </Button>
    </Card>
  );
}
```

## Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:4000/api

# Authentication
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key

# Environment
NEXT_PUBLIC_ENV=development
```

## Git Hooks (Husky)

Pre-commit hooks automatically run linting and formatting:

```json
// .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx lint-staged
```

**lint-staged** configuration in `package.json`:
```json
{
  "lint-staged": {
    "*.{js,ts,tsx}": [
      "prettier --write --end-of-line lf",
      "eslint --fix"
    ]
  }
}
```

## Deployment

### Vercel (Recommended)

The easiest way to deploy Next.js:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

Build and run with Docker:

```bash
# Build image
docker build -t dispatchai-frontend .

# Run container
docker run -p 3000:3000 dispatchai-frontend
```

### Environment Variables for Production

Ensure all `NEXT_PUBLIC_*` variables are set in your deployment platform.

## Common Patterns

### Protected Routes

```typescript
// Example: Protected admin route
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector } from 'react-redux';

export default function AdminLayout({ children }) {
  const router = useRouter();
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, router]);

  return <>{children}</>;
}
```

### Loading States

```typescript
import { CircularProgress, Box } from '@mui/material';

function MyComponent() {
  const { data, isLoading } = useQuery(['data'], fetchData);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return <div>{/* Render data */}</div>;
}
```

### Error Handling

```typescript
import { Alert } from '@mui/material';

function MyComponent() {
  const { data, error } = useQuery(['data'], fetchData);

  if (error) {
    return <Alert severity="error">Failed to load data</Alert>;
  }

  return <div>{/* Render data */}</div>;
}
```

## Troubleshooting

### Common Issues

**1. Module Not Found**
- Clear `.next` cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && pnpm install`

**2. API Connection Issues**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check that backend is running on the specified port
- Check browser console for CORS errors

**3. Build Failures**
- Run type checking: `pnpm type-check`
- Fix any TypeScript errors
- Check for missing environment variables

**4. Hydration Errors**
- Ensure server and client render the same content
- Check for browser-only code running on server
- Use `'use client'` directive for client-only components

**5. State Not Persisting**
- Check redux-persist configuration
- Clear localStorage if state schema changed
- Verify `PersistGate` is wrapping the app

## Learn More

### Next.js Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Learn Next.js](https://nextjs.org/learn)

### Material-UI Resources
- [MUI Documentation](https://mui.com/material-ui/getting-started/)
- [MUI Components](https://mui.com/material-ui/all-components/)
- [MUI Theming](https://mui.com/material-ui/customization/theming/)

### Redux Resources
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Redux Persist](https://github.com/rt2zz/redux-persist)

### React Query Resources
- [TanStack Query](https://tanstack.com/query/latest)

## Contributing

This is a private project. For questions or contributions, please contact the development team.

## License

Proprietary - All rights reserved
