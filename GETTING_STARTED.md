# Getting Started with CareOps

Welcome! This guide will help you get CareOps up and running in under 10 minutes.

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Python 3.9 or higher** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18 or higher** - [Download here](https://nodejs.org/)
3. **Docker Desktop** (for Redis) - [Download here](https://www.docker.com/products/docker-desktop/)
4. **Supabase Account** (free) - [Sign up here](https://supabase.com/)

## 🚀 Step-by-Step Setup

### Step 1: Clone or Download the Project

If you haven't already, get the project files on your computer.

### Step 2: Set Up Supabase Database

1. Go to [supabase.com](https://supabase.com/) and sign in
2. Click "New Project"
3. Fill in:
   - Name: `careops`
   - Database Password: (create a strong password)
   - Region: (choose closest to you)
4. Wait for project to be created (~2 minutes)
5. Once ready, go to **Settings** → **API**
6. Copy these values (you'll need them):
   - `Project URL` (looks like: https://xxxxx.supabase.co)
   - `anon public` key (long string starting with "eyJ...")
7. Go to **SQL Editor**
8. Click "New Query"
9. Open `Backend/supabase_schema.sql` from the project
10. Copy all the SQL code and paste it into the query editor
11. Click "Run" to create all tables

### Step 3: Configure Backend

1. Open a terminal/command prompt
2. Navigate to the Backend folder:
   ```bash
   cd Backend
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate it:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Create `.env` file by copying the example:
   ```bash
   # Windows
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

7. Open `.env` in a text editor and fill in:
   ```env
   SUPABASE_URL=your_project_url_from_step2
   SUPABASE_KEY=your_anon_key_from_step2
   SECRET_KEY=generate_this_in_next_step
   CORS_ORIGINS=http://localhost:8080
   ```

8. Generate a SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copy the output and paste it as your SECRET_KEY in `.env`

### Step 4: Start Redis

1. Open Docker Desktop (make sure it's running)
2. In your terminal, run:
   ```bash
   docker run -d -p 6379:6379 --name careops-redis redis:alpine
   ```
3. You should see a long container ID - that means it worked!

### Step 5: Start Backend

1. Make sure you're still in the Backend folder with venv activated
2. Run:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. You should see:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```
4. Open http://localhost:8000/docs in your browser
5. You should see the API documentation - backend is working! ✅

### Step 6: Configure Frontend

1. Open a NEW terminal (keep backend running)
2. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Create `.env` file:
   ```bash
   # Windows
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

5. Open `.env` and verify it has:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Step 7: Start Frontend

1. In the frontend terminal, run:
   ```bash
   npm run dev
   ```
2. You should see:
   ```
   VITE ready in XXX ms
   ➜  Local:   http://localhost:8080/
   ```
3. Open http://localhost:8080 in your browser
4. You should see the CareOps landing page! ✅

## 🎉 You're Ready!

### Create Your First Account

1. Click "Get Started" on the landing page
2. Fill in the registration form:
   - Full Name: Your name
   - Email: Your email
   - Password: At least 6 characters
   - Workspace Name: Your business name
3. Click "Create Account"
4. You'll be automatically logged in and redirected to the dashboard!

### Explore the Features

Now you can:
- ✅ View the dashboard with stats
- ✅ Navigate to Bookings page
- ✅ Check out the Inbox
- ✅ Manage Contacts
- ✅ Create Forms
- ✅ Track Inventory
- ✅ Configure Settings

## 🔄 Starting the App Later

After the initial setup, you only need to:

### Option 1: Use the Startup Script (Windows)
```bash
# From project root
start-dev.bat
```
This will start Redis, Backend, and Frontend automatically!

### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd Backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Make sure Docker Desktop is running for Redis
```

## 📚 Next Steps

- Read the [README.md](./README.md) for detailed documentation
- Check [API_DOCUMENTATION.md](./Backend/API_DOCUMENTATION.md) for API reference
- See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for current features
- Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) if you encounter issues

## ❓ Common First-Time Issues

### "Module not found" in Backend
```bash
# Make sure venv is activated (you should see (venv) in terminal)
# Then reinstall:
pip install -r requirements.txt
```

### "Cannot find module" in Frontend
```bash
# Delete node_modules and reinstall:
rmdir /s node_modules  # Windows
rm -rf node_modules    # Mac/Linux
npm install
```

### Can't connect to backend
- Make sure backend is running (check terminal)
- Verify it's on port 8000
- Check `.env` files are configured correctly

### Login not working
- Make sure you ran the SQL schema in Supabase
- Check backend terminal for errors
- Verify Supabase credentials in `.env`

## 🆘 Need Help?

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Look at backend terminal for error messages
3. Check browser console (F12) for frontend errors
4. Verify all environment variables are set correctly

## 🎯 Quick Test Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:8080
- [ ] Can see API docs at http://localhost:8000/docs
- [ ] Can see landing page at http://localhost:8080
- [ ] Can register a new account
- [ ] Can login successfully
- [ ] Can see dashboard with data
- [ ] Can navigate between pages

If all checkboxes are ✅, you're all set! Welcome to CareOps! 🎉
