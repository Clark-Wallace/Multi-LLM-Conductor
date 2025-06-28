# ServiceConnect - Social Media Platform for Service Members

A secure, verified social media platform designed specifically for military service members to connect, share experiences, and support each other.

## Features

### Core Features
- **Military Verification**: Secure verification system for active duty, reserve, and veteran status
- **Unit/Base Groups**: Automatic grouping by unit, base, and service branch
- **Secure Messaging**: End-to-end encrypted messaging between verified members
- **Support Resources**: Access to mental health, career transition, and family support resources
- **Privacy Controls**: Granular control over what information is shared

### Social Features
- **Posts & Feed**: Share updates, photos, and experiences
- **Groups**: Join or create groups based on units, bases, interests, or support topics
- **Connections**: Build your network with fellow service members
- **Events**: Organize and join unit events, meetups, and support groups

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT with military verification
- **Real-time**: WebSockets

### Frontend
- **Framework**: Next.js 14 with React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API Client**: Axios with React Query

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd service-connect
```

2. Copy environment variables:
```bash
cp backend/.env.example backend/.env
```

3. Start the application:
```bash
docker-compose up
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Make sure PostgreSQL is running
# Update .env with your database credentials
alembic upgrade head
```

4. Run the backend:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

## Project Structure

```
service-connect/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   ├── alembic/          # Database migrations
│   ├── tests/            # Test files
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API services
│   ├── styles/           # Global styles
│   └── package.json
├── infrastructure/       # Deployment configs
└── docker-compose.yml
```

## Security Features

- **Military Verification**: Integration points for DD-214, CAC card, or other military ID verification
- **End-to-End Encryption**: Secure messaging between members
- **Privacy Controls**: Users control visibility of deployment status, unit info, and location
- **Data Protection**: GDPR-compliant data handling and storage

## Roadmap

- [ ] CAC card authentication integration
- [ ] Mobile applications (iOS/Android)
- [ ] Video chat for support groups
- [ ] AI-powered resource recommendations
- [ ] Integration with VA services
- [ ] Deployment tracking and notifications

## Contributing

This project is designed to serve the military community. We welcome contributions from service members and developers who understand the unique needs of military personnel.

## License

[License details to be determined]

## Support

For support, please contact [support email] or visit our help center.