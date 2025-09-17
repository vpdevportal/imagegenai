# ImageGenAI - AI-Powered Image Generation Platform

A modern monorepo application built with **FastAPI** (Python backend) and **Next.js** (TypeScript frontend), orchestrated with **Turborepo** for optimal development experience.

## 🚀 Features

- **AI Image Generation**: Generate stunning images from text prompts
- **Modern Tech Stack**: FastAPI + Next.js + TypeScript + Tailwind CSS
- **Monorepo Architecture**: Organized with Turborepo for efficient development
- **Docker Support**: Full containerization for development and production
- **Real-time Updates**: WebSocket support for live image generation status
- **Responsive Design**: Beautiful, mobile-first UI/UX
- **Type Safety**: End-to-end TypeScript support

## 📁 Project Structure

```
imagegenai/
├── apps/
│   ├── backend/          # FastAPI Python backend
│   │   ├── app/          # Application modules
│   │   ├── main.py       # FastAPI application entry point
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/         # Next.js TypeScript frontend
│       ├── src/
│       │   ├── app/      # Next.js 13+ app directory
│       │   ├── components/
│       │   └── lib/
│       ├── package.json
│       └── Dockerfile
├── packages/
│   └── shared/           # Shared types and utilities
├── docker-compose.yml    # Full stack deployment
├── docker-compose.dev.yml # Development services only
├── turbo.json           # Turborepo configuration
└── package.json         # Root package configuration
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11** - Latest Python version
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and task queue
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Heroicons** - Beautiful SVG icons

### DevOps & Tools
- **Turborepo** - Monorepo build system
- **Docker** - Containerization
- **ESLint & Prettier** - Code quality and formatting
- **Jest** - Testing framework

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose (optional)

### Option 1: Local Development (Recommended)

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd imagegenai
   npm install
   ```

2. **Start development servers:**
   ```bash
   # Easy one-command start (recommended)
   npm run start-dev
   
   # Or using the shell script directly
   ./start-dev.sh
   
   # Or start individually:
   npm run backend:dev  # Backend on http://localhost:8000
   npm run frontend:dev # Frontend on http://localhost:3000
   ```

### Option 2: Docker Development

1. **Start development services (PostgreSQL + Redis):**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Run applications locally:**
   ```bash
   npm run dev
   ```

### Option 3: Docker Development

```bash
# Start development environment with Docker (single container with hot reloading)
docker-compose up -d

# Or use the convenient script
./docker-scripts.sh dev

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

**Access Points:**
- Frontend: http://localhost:5001
- Backend API: http://localhost:6001
- API Documentation: http://localhost:6001/api/docs

For detailed Docker instructions, see [DOCKER-SINGLE.md](DOCKER-SINGLE.md).

## 📝 Available Scripts

### Root Level Commands
```bash
npm run dev              # Start both apps in development mode
npm run build           # Build all applications
npm run lint            # Lint all code
npm run test            # Run all tests
npm run clean           # Clean all build artifacts
npm run format          # Format code with Prettier

# Individual app commands
npm run backend:dev     # Start only backend
npm run frontend:dev    # Start only frontend
npm run backend:build   # Build only backend
npm run frontend:build  # Build only frontend
```

### Backend Commands
```bash
cd apps/backend

# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000

# Code quality
black .                 # Format Python code
flake8 .               # Lint Python code
pytest                 # Run tests
```

### Frontend Commands
```bash
cd apps/frontend

npm run dev            # Start development server
npm run build          # Build for production
npm run start          # Start production server
npm run lint           # Lint code
npm run test           # Run tests
```

## 🌐 API Endpoints

### Backend API (http://localhost:8000)

- `GET /api/health` - Health check
- `GET /api/` - Root endpoint
- `POST /api/generate` - Generate image from prompt
- `GET /api/images` - List generated images
- `GET /api/docs` - Interactive API documentation (Swagger)

## 🔧 Configuration

### Environment Variables

Create `.env` files in the respective app directories:

**Backend (`apps/backend/.env`):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/imagegenai
REDIS_URL=redis://localhost:6379
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:3000
SECRET_KEY=your_secret_key_here
```

**Frontend (`apps/frontend/.env.local`):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Backend tests
cd apps/backend && pytest

# Frontend tests
cd apps/frontend && npm run test
```

## 📦 Production Deployment

### Docker Production
```bash
# Build and start production stack
docker-compose -f docker-compose.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Manual Deployment

1. **Build applications:**
   ```bash
   npm run build
   ```

2. **Set up production environment:**
   - Configure production database
   - Set environment variables
   - Set up reverse proxy (nginx)
   - Configure SSL certificates

## 🤝 Development Workflow

1. **Feature Development:**
   - Create feature branch
   - Make changes in respective app
   - Test locally with `npm run dev`
   - Run tests and linting
   - Create pull request

2. **Code Quality:**
   - Follow TypeScript best practices
   - Use Prettier for formatting
   - Write tests for new features
   - Document API changes

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Backend: Change port in `apps/backend/main.py`
   - Frontend: Change port with `-p 3001` flag

2. **Database connection issues:**
   - Ensure PostgreSQL is running
   - Check connection string in environment variables

3. **CORS errors:**
   - Verify `FRONTEND_URL` in backend environment
   - Check CORS middleware configuration

### Getting Help

- Check the [Issues](../../issues) section
- Review application logs
- Ensure all dependencies are installed
- Verify environment configuration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Vercel for Next.js and Turborepo
- The open-source community for amazing tools and libraries

---

**Happy coding! 🎨✨**
