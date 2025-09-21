# 🚀 PM Interview Bot - Local Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software
- **Python 3.8+** (Download from [python.org](https://python.org))
- **Node.js 16+** (Download from [nodejs.org](https://nodejs.org))
- **PostgreSQL 12+** (Download from [postgresql.org](https://postgresql.org))
- **Git** (Download from [git-scm.com](https://git-scm.com))

### Optional (for enhanced AI features)
- **Pinecone Account** (for vector storage)
- **Weaviate Instance** (alternative vector storage)

## 📋 Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd pm-interview-bot
```

### 2. Database Setup

#### Install PostgreSQL
1. Download and install PostgreSQL from [postgresql.org](https://postgresql.org)
2. During installation, remember the password you set for the `postgres` user

#### Create Database and User
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# In PostgreSQL shell, run:
CREATE DATABASE pm_interview_db;
CREATE USER pm_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pm_interview_db TO pm_user;

# Connect to the new database
\c pm_interview_db;

# Grant schema privileges
GRANT ALL ON SCHEMA public TO pm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pm_user;

# Enable UUID extension (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Exit PostgreSQL
\q
```

### 3. Backend Setup

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

#### Configure .env File
```bash
# Database Configuration
DATABASE_URL=postgresql://pm_user:your_secure_password@localhost/pm_interview_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# AI Configuration (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Vector Database Configuration (Optional)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
WEAVIATE_URL=http://localhost:8080

# Social Login Configuration (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Get Required API Keys

##### OpenAI API Key (Required for AI features)
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

##### Pinecone API Key (Optional - for enhanced question storage)
1. Go to [Pinecone](https://pinecone.io)
2. Sign up for a free account
3. Create a new project
4. Get your API key from the dashboard
5. Copy to your `.env` file

#### Run Database Migrations
```bash
# The app will automatically create tables on first run
python run.py
```

### 4. Frontend Setup

#### Open New Terminal and Navigate to Frontend
```bash
# Open new terminal window/tab
cd frontend  # or root directory if React is in root
```

#### Install Dependencies
```bash
npm install
```

#### Start Development Server
```bash
npm run dev
```

### 5. Start the Application

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

#### Terminal 2 - Frontend
```bash
npm run dev
```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api (see API endpoints below)

## 🧪 Testing the Setup

### 1. Test Backend API
```bash
# Test health endpoint
curl http://localhost:5000/api/companies

# Should return list of companies
```

### 2. Test Frontend
1. Open http://localhost:5173 in your browser
2. You should see the login/signup page
3. Try creating an account or logging in

### 3. Test AI Features
1. Set up OpenAI API key in `.env`
2. Create an account and complete onboarding
3. Try generating questions with job description
4. Complete an interview to test AI evaluation

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check if PostgreSQL is running
sudo service postgresql status  # Linux
brew services list | grep postgresql  # macOS
# Windows: Check Services in Task Manager

# Test database connection
psql -U pm_user -d pm_interview_db -h localhost
```

#### Python Dependencies Error
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies one by one if bulk install fails
pip install flask flask-sqlalchemy flask-cors flask-jwt-extended
pip install psycopg2-binary python-dotenv requests werkzeug
pip install openai numpy scikit-learn scipy pydantic
```

#### Node.js Dependencies Error
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### OpenAI API Error
1. Verify your API key is correct
2. Check your OpenAI account has credits
3. Ensure you're using the correct model names

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Environment-Specific Setup

#### Windows Additional Steps
```bash
# Install Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Use Windows Subsystem for Linux (WSL) for better compatibility
wsl --install
```

#### macOS Additional Steps
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL via Homebrew
brew install postgresql
brew services start postgresql
```

#### Linux Additional Steps
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install python3-pip postgresql postgresql-server
```

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Set secure values for production
FLASK_ENV=production
JWT_SECRET_KEY=super-secure-production-key-min-32-chars
DATABASE_URL=postgresql://user:pass@prod-db:5432/pm_interview_db
```

### Docker Deployment (Optional)
```bash
# Build and run with Docker
docker-compose up --build
```

## 📊 Monitoring and Logs

### Backend Logs
```bash
# View real-time logs
tail -f backend/app.log

# Check for errors
grep ERROR backend/app.log
```

### Database Monitoring
```bash
# Connect to database and check tables
psql -U pm_user -d pm_interview_db
\dt  # List all tables
\d users  # Describe users table
```

## 🔐 Security Considerations

### For Development
- Use strong passwords for database
- Keep API keys secure and never commit them
- Use HTTPS in production

### For Production
- Use environment variables for all secrets
- Set up proper firewall rules
- Enable SSL/TLS certificates
- Regular security updates

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure all environment variables are set properly
4. Check the logs for specific error messages

## 🎉 Success!

If everything is set up correctly, you should be able to:

✅ Access the frontend at http://localhost:5173  
✅ Register/login to create an account  
✅ Complete the onboarding process  
✅ Select companies and upload job descriptions  
✅ Take AI-powered interviews  
✅ View detailed results and analytics  

Happy coding! 🚀