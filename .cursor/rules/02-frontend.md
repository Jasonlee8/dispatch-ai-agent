# Frontend (Next.js/React) Specific Rules

Rules specific to the Next.js frontend in `/frontend/src/`.

## Component Structure (MANDATORY)

### File Size Limits

- **Components**: Max 400 lines
- **Pages**: Max 300 lines
- **Hooks**: Max 150 lines
- **Utils**: Max 200 lines

**If exceeded, refactor by:**
- Extracting sub-components
- Creating custom hooks
- Moving logic to services
- Splitting into multiple files

### Component Organization

```typescript
// ✅ GOOD - Well-organized component
import { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';

import { useQuery } from '@tanstack/react-query';

import { fetchCallLogs } from '@/services/calllog.service';

import type { CallLog } from '@/types/calllog';

interface CallLogListProps {
  userId?: string;
}

export default function CallLogList({ userId }: CallLogListProps) {
  // Hooks first
  const [filter, setFilter] = useState<string>('');
  const { data, isLoading, error } = useQuery({
    queryKey: ['callLogs', userId],
    queryFn: () => fetchCallLogs(userId)
  });

  // Event handlers
  const handleFilterChange = (value: string) => {
    setFilter(value);
  };

  // Early returns
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  // Render
  return (
    <Box>
      {/* JSX */}
    </Box>
  );
}
```

## State Management Rules

### Use the RIGHT Tool for the RIGHT State

**Redux Toolkit** - Global application state
```typescript
// ✅ GOOD - Auth state in Redux
// redux/slices/authSlice.ts
import { createSlice } from '@reduxjs/toolkit';

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, token: null },
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
    },
  },
});

// Component
const user = useSelector((state: RootState) => state.auth.user);
```

**TanStack Query (React Query)** - Server state (API data)
```typescript
// ✅ GOOD - API data with TanStack Query
import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchBookings, createBooking } from '@/services/booking.service';

function BookingList() {
  // Fetching
  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: fetchBookings,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Mutation
  const mutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
    },
  });

  return <div>{/* ... */}</div>;
}
```

**useState** - Local component state (UI-only)
```typescript
// ✅ GOOD - UI state with useState
function SearchBar() {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  return <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />;
}
```

### NEVER Duplicate Server State in Redux

```typescript
// ❌ BAD - Server state in Redux
const callLogs = useSelector(state => state.callLogs.list);

// ✅ GOOD - Server state in TanStack Query
const { data: callLogs } = useQuery({
  queryKey: ['callLogs'],
  queryFn: fetchCallLogs
});
```

## API Integration (MANDATORY)

### ALWAYS Use Service Layer

```typescript
// ✅ GOOD - Service file
// services/booking.service.ts
import api from './api';

export const fetchBookings = async (userId?: string): Promise<Booking[]> => {
  const params = userId ? { userId } : {};
  const response = await api.get<Booking[]>('/service-booking', { params });
  return response.data;
};

export const createBooking = async (data: CreateBookingDto): Promise<Booking> => {
  const response = await api.post<Booking>('/service-booking', data);
  return response.data;
};

// Component
import { fetchBookings } from '@/services/booking.service';

const { data } = useQuery({
  queryKey: ['bookings'],
  queryFn: fetchBookings
});
```

```typescript
// ❌ BAD - Direct API call in component
function BookingList() {
  const [bookings, setBookings] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:4000/api/service-booking')
      .then(res => setBookings(res.data));
  }, []);
}
```

### Configure Axios Instance

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api',
  timeout: 10000,
});

// Request interceptor - Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Form Handling (MANDATORY)

### Use React Hook Form + Zod

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// ✅ GOOD - Schema-based validation
const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email'),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number'),
  serviceId: z.string().min(1, 'Service is required'),
});

type FormData = z.infer<typeof schema>;

function BookingForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    await createBooking(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        Submit
      </button>
    </form>
  );
}
```

## Client vs Server Components

### Use Server Components by Default

```typescript
// ✅ GOOD - Server component (default)
// app/admin/call-log/page.tsx
import { fetchCallLogs } from '@/services/calllog.service';

export default async function CallLogPage() {
  const logs = await fetchCallLogs();

  return (
    <div>
      <h1>Call Logs</h1>
      <CallLogList logs={logs} />
    </div>
  );
}
```

### Use 'use client' ONLY When Necessary

```typescript
// ✅ GOOD - Client component (needs state)
'use client';

import { useState } from 'react';

export default function SearchBar() {
  const [search, setSearch] = useState('');

  return <input value={search} onChange={e => setSearch(e.target.value)} />;
}
```

**Use 'use client' when you need:**
- State (`useState`, `useReducer`)
- Effects (`useEffect`)
- Event handlers (`onClick`, etc.)
- Browser APIs (`localStorage`, `window`, etc.)
- Context (`useContext`)
- React Query hooks

## TypeScript in React

### Define Prop Types

```typescript
// ✅ GOOD - Explicit prop types
interface CallLogItemProps {
  callLog: CallLog;
  onView: (id: string) => void;
  showDetails?: boolean;
}

export default function CallLogItem({
  callLog,
  onView,
  showDetails = false,
}: CallLogItemProps) {
  return <div>{/* ... */}</div>;
}

// ❌ BAD - No prop types
export default function CallLogItem({ callLog, onView, showDetails }) {
  return <div>{/* ... */}</div>;
}
```

### Use Type Inference

```typescript
// ✅ GOOD - Let TypeScript infer
const [count, setCount] = useState(0); // Inferred as number
const [user, setUser] = useState<User | null>(null); // Explicit when needed

// ❌ BAD - Unnecessary typing
const [count, setCount] = useState<number>(0);
```

## Component Patterns

### Extract Complex Logic to Custom Hooks

```typescript
// ✅ GOOD - Custom hook
// hooks/useCallLogs.ts
import { useQuery } from '@tanstack/react-query';
import { fetchCallLogs } from '@/services/calllog.service';

export function useCallLogs(userId?: string) {
  return useQuery({
    queryKey: ['callLogs', userId],
    queryFn: () => fetchCallLogs(userId),
    staleTime: 5 * 60 * 1000,
  });
}

// Component
function CallLogPage() {
  const { data, isLoading, error } = useCallLogs();
  // ...
}
```

### Component Composition

```typescript
// ✅ GOOD - Small, focused components
function CallLogList({ logs }: { logs: CallLog[] }) {
  return (
    <div>
      {logs.map(log => (
        <CallLogItem key={log.id} log={log} />
      ))}
    </div>
  );
}

function CallLogItem({ log }: { log: CallLog }) {
  return (
    <Card>
      <CallLogHeader log={log} />
      <CallLogDetails log={log} />
      <CallLogActions log={log} />
    </Card>
  );
}

// ❌ BAD - Monolithic component
function CallLogList({ logs }: { logs: CallLog[] }) {
  return (
    <div>
      {logs.map(log => (
        <Card>
          <div>{/* 200 lines of JSX */}</div>
        </Card>
      ))}
    </div>
  );
}
```

## Styling (Material-UI)

### Use Theme Consistently

```typescript
// ✅ GOOD - Using theme
import { Box, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

function MyComponent() {
  const theme = useTheme();

  return (
    <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
      <Typography variant="h5" color="primary">
        Title
      </Typography>
    </Box>
  );
}

// ❌ BAD - Hardcoded colors
<Box sx={{ p: 2, bgcolor: '#ffffff' }}>
  <Typography sx={{ color: '#1976d2' }}>Title</Typography>
</Box>
```

### Use sx Prop for Styling

```typescript
// ✅ GOOD - sx prop
<Box
  sx={{
    display: 'flex',
    gap: 2,
    p: 3,
    borderRadius: 1,
    bgcolor: 'background.paper',
  }}
>
  {/* ... */}
</Box>

// ❌ BAD - Inline styles
<div style={{ display: 'flex', gap: '16px', padding: '24px' }}>
  {/* ... */}
</div>
```

## Performance Optimization

### Memoization

```typescript
import { useMemo, useCallback } from 'react';

// ✅ GOOD - Memoize expensive calculations
function DataTable({ data }: { data: Item[] }) {
  const sortedData = useMemo(() => {
    return data.sort((a, b) => a.timestamp - b.timestamp);
  }, [data]);

  const handleRowClick = useCallback((id: string) => {
    console.log('Row clicked:', id);
  }, []);

  return <Table data={sortedData} onRowClick={handleRowClick} />;
}
```

### React.memo for Pure Components

```typescript
import { memo } from 'react';

// ✅ GOOD - Memo for expensive renders
const CallLogItem = memo(function CallLogItem({ log }: { log: CallLog }) {
  return <div>{/* Complex rendering */}</div>;
});
```

## Error Handling

### Error Boundaries

```typescript
// components/ErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

### Query Error Handling

```typescript
// ✅ GOOD - Handle errors
function CallLogList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['callLogs'],
    queryFn: fetchCallLogs,
  });

  if (isLoading) return <CircularProgress />;
  if (error) {
    return (
      <Alert severity="error">
        Failed to load call logs: {error.message}
      </Alert>
    );
  }

  return <div>{/* Render data */}</div>;
}
```

## Environment Variables

### Use NEXT_PUBLIC_ Prefix

```typescript
// ✅ GOOD - Public env var
const API_URL = process.env.NEXT_PUBLIC_API_URL;

// ❌ BAD - Not accessible in client
const API_URL = process.env.API_URL; // undefined in browser
```

### Type Environment Variables

```typescript
// env.d.ts
declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string;
    NEXT_PUBLIC_STRIPE_KEY: string;
    NEXT_PUBLIC_GOOGLE_CLIENT_ID: string;
  }
}
```

## Accessibility

### Use Semantic HTML

```typescript
// ✅ GOOD - Semantic HTML
<nav>
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>

<main>
  <h1>Call Logs</h1>
  <article>{/* Call log content */}</article>
</main>

// ❌ BAD - Div soup
<div className="nav">
  <div className="nav-item">Dashboard</div>
</div>
```

### Add ARIA Labels

```typescript
// ✅ GOOD - ARIA labels
<Button
  aria-label="Delete call log"
  onClick={handleDelete}
>
  <DeleteIcon />
</Button>

<TextField
  label="Search"
  aria-describedby="search-helper-text"
/>
```

## Code Review Checklist (Frontend)

- [ ] Components < 400 lines
- [ ] Server state uses TanStack Query (not Redux)
- [ ] Global state uses Redux Toolkit
- [ ] All API calls go through service layer
- [ ] Forms use React Hook Form + Zod
- [ ] Prop types defined for all components
- [ ] 'use client' only when necessary
- [ ] No inline styles (use sx prop)
- [ ] Theme values used (not hardcoded colors)
- [ ] Error states handled
- [ ] Loading states handled
- [ ] Environment variables use NEXT_PUBLIC_ prefix
- [ ] No `console.log` in production code
- [ ] Accessible (semantic HTML, ARIA labels)
- [ ] Memoization for expensive operations
