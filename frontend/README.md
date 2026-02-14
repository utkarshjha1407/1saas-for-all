# CareOps - Unified Operations Platform

A comprehensive operations platform for service-based businesses built with React, TypeScript, and Vite.

## Features

- 📅 Booking Management
- 💬 Unified Inbox (Email & SMS)
- 📋 Dynamic Forms System
- 📦 Inventory Tracking
- 📊 Real-time Dashboard
- 👥 Staff Management
- 🤖 Automated Workflows

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Components**: Radix UI + shadcn/ui
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see Backend/README.md)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Update .env with your backend API URL
# VITE_API_URL=http://localhost:8000/api/v1
```

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run linter
npm run lint
```

The app will be available at http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   ├── services/       # API service layer
│   └── types/          # TypeScript type definitions
├── public/             # Static assets
└── index.html          # Entry HTML file
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Run ESLint

## Backend Integration

This frontend connects to the CareOps FastAPI backend. Make sure the backend is running before starting the frontend.

Backend API Documentation: http://localhost:8000/api/v1/docs

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linter
4. Submit a pull request

## License

Proprietary - CareOps Hackathon Project
