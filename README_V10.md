# ARGO v10 - Enterprise PMO Platform

![Version](https://img.shields.io/badge/version-10.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![React](https://img.shields.io/badge/react-19.2.0-61dafb)
![FastAPI](https://img.shields.io/badge/fastapi-0.115+-009688)

**Professional-grade Project Management Office platform with AI-powered RAG capabilities.**

## 🚀 Features

### Core Capabilities
- ✅ **Real-time Chat** - WebSocket-powered AI assistant with RAG
- ✅ **Document Management** - Upload, index, and search project documents
- ✅ **Analytics Dashboard** - Real-time cost tracking and usage metrics
- ✅ **RAG Engine** - HyDE + Semantic Reranking + Library integration
- ✅ **Professional UI** - Modern React with shadcn/ui components
- ✅ **REST + WebSocket API** - Full-featured FastAPI backend

### Technical Stack

**Backend:**
- FastAPI (REST + WebSocket)
- Python 3.11+
- RAG Engine (HyDE, Reranking, Semantic Cache)
- SQLite Database
- LangChain + OpenAI

**Frontend:**
- React 19.2.0
- TypeScript 5.6+
- Vite 7
- TanStack Query
- shadcn/ui + Tailwind CSS v4
- Recharts for analytics

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- OpenAI API key

## 🛠️ Installation

### Quick Start (Recommended)

```bash
# Clone or navigate to the project
cd ARGO-v9

# Start both backend and frontend
./start_all.sh
```

The application will be available at:
- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

#### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or vim, or any text editor

# Start the backend
python main.py
```

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend_ui

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start the frontend
npm run dev:client
```

## ⚙️ Configuration

### Backend (.env)

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
HOST=0.0.0.0
PORT=8000
DATABASE_PATH=./data/argo.db
TEMP_DIR=./temp
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📖 Usage

### 1. Access the Application

Open your browser to http://localhost:5000

### 2. Upload Documents

- Click **"Upload Files"** button or drag & drop
- Supported formats: PDF, DOCX, XLSX, TXT, MD, CSV
- Max file size: 50MB
- Files are automatically indexed with RAG

### 3. Chat with AI Assistant

- Navigate to **"Chat"** tab
- Ask questions about your documents
- View sources and confidence scores
- Real-time responses via WebSocket

### 4. View Analytics

- Navigate to **"Analytics"** tab
- Monitor API usage and costs
- Track token consumption
- View project distributions

## 🏗️ Architecture

```
ARGO-v9/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend configuration
│
├── frontend_ui/               # React Frontend
│   ├── client/
│   │   └── src/
│   │       ├── components/    # React components
│   │       ├── lib/          # API client & utilities
│   │       └── pages/        # Page components
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend configuration
│
├── ARGO_v9.0_CLEAN/          # Core ARGO components
│   ├── core/                 # RAG Engine, Model Router
│   ├── tools/                # Extractors, Analyzers
│   └── config/               # Configuration files
│
└── start_all.sh              # Startup script
```

## 🔌 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - System status

### Project
- `GET /api/project` - Get current project

### Chat
- `POST /api/chat` - Send chat message (REST)
- `WS /ws/chat` - Real-time chat (WebSocket)

### Documents
- `GET /api/documents` - List all documents
- `POST /api/documents/upload` - Upload document

### Analytics
- `GET /api/analytics` - Get analytics data

**Full API documentation**: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend_ui
npm run test
```

## 🔒 Security Features

- ✅ CORS configuration
- ✅ File type validation
- ✅ File size limits
- ✅ Input sanitization
- ✅ Error handling with proper HTTP codes
- ✅ Environment variable isolation

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

### Frontend won't start
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Or use a different port
PORT=3000 npm run dev:client
```

### WebSocket connection fails
- Ensure backend is running
- Check console for connection errors
- Verify `VITE_WS_URL` in frontend/.env

### No chat responses
- Verify `OPENAI_API_KEY` is set in backend/.env
- Check backend logs for errors
- Ensure you have OpenAI API credits

## 📊 Performance

- **Chat Response Time**: ~2-5 seconds (with RAG)
- **Document Upload**: Processes ~100 chunks/second
- **WebSocket Latency**: <100ms
- **Concurrent Users**: Tested up to 50 simultaneous connections

## 🛣️ Roadmap

- [ ] Multi-project support
- [ ] User authentication & authorization
- [ ] Advanced analytics with export
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)
- [ ] Docker containerization
- [ ] Kubernetes deployment

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For issues, questions, or feature requests:
- Create an issue in the repository
- Contact: support@argo-platform.com

## 📚 Additional Documentation

- [ARGO_v9.0 Documentation](./ARGO_v9.0_CLEAN/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](./DELIVERY_COMPLETE.md)

---

**Built with ❤️ by the ARGO Team**

*Version 10.0.0 - Professional Enterprise Grade PMO Platform*
