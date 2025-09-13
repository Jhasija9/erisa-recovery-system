# ERISA Recovery Claims Management System

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A modern, enterprise-grade claims management platform built with Django**

[Live Demo](#) • [Documentation](#) • [Report Bug](#) • [Request Feature](#)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Admin Setup](#admin-setup)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **ERISA Recovery Claims Management System** is a comprehensive, modern web application designed to streamline insurance claims processing, analysis, and recovery operations. Built with Django and featuring a responsive, intuitive interface, it empowers healthcare organizations to efficiently manage denied claims and maximize revenue recovery.

### Key Objectives
- **Maximize Revenue Recovery** - Turn denied claims into payable revenue
- **Streamline Operations** - Reduce manual processing time by 70%
- **Enhance Visibility** - Real-time analytics and comprehensive reporting
- **Improve Accuracy** - Automated validation and error detection

---

## Features

### Core Features
- **Advanced Dashboard** - Real-time KPIs, charts, and analytics
- **Smart Search & Filter** - Multi-criteria search with instant results
- **Claims Management** - Full CRUD operations with HTMX integration
- **Flagging System** - Flag claims for review with custom reasons
- **Note Management** - Add contextual notes and annotations
- **Data Upload** - Drag-and-drop CSV/JSON file processing
- **User Management** - Role-based access control (Admin/User)

### Advanced Features
- **Analytics Dashboard** - Claims by month, payment ratios, CPT analysis
- **Modern UI/UX** - Responsive design with Tailwind CSS
- **Real-time Updates** - HTMX-powered dynamic content
- **Secure Authentication** - Email/Username login with validation
- **Smart Filtering** - Status, insurer, date range filtering

---

## Tech Stack

### Backend
- **Python 3.12** - Core programming language
- **Django 4.2.7** - Web framework
- **SQLite/PostgreSQL** - Database
- **Django Extensions** - Enhanced functionality

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **HTMX** - Dynamic HTML without JavaScript
- **Alpine.js** - Lightweight JavaScript framework
- **Chart.js** - Data visualization

### Development Tools
- **Black** - Code formatting
- **Flake8** - Linting
- **Pre-commit** - Git hooks
- **Django Testing** - Unit testing

---

## Quick Start

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/erisa-recovery-system.git
cd erisa-recovery-system
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Setup admin user
python manage.py setup_auth
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Main App**: http://127.0.0.1:8000/
- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Data Upload**: http://127.0.0.1:8000/upload/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 7. Load Data (Admin Only)
1. **Login as Admin** - Use the admin credentials from setup_auth command
2. **Navigate to Data Upload** - Go to the "Data Ingest" page
3. **Upload Files** - Use the drag-and-drop interface to upload CSV/JSON files
4. **Select Format** - Choose between JSON or CSV format
5. **Process Data** - Click "Upload Data" to process and load the claims

---

## Screenshots

### Claims Dashboard
![Claims Dashboard](screenshots/claims-dashboard.png)
*Modern, responsive claims listing with advanced filtering*

### Analytics Dashboard
![Analytics Dashboard](screenshots/analytics-dashboard.png)
*Comprehensive analytics with interactive charts*

### Data Upload
![Data Upload](screenshots/data-upload.png)
*Drag-and-drop file upload with real-time validation*

---

## Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Tailwind +   │◄──►│   (Django)      │◄──►│   (SQLite/      │
│   HTMX +        │    │                 │    │   PostgreSQL)   │
│   Alpine.js)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure
```
erisa_recovery_project/
├── erisa_recovery/          # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI configuration
├── claims/                 # Main application
│   ├── models.py             # Data models
│   ├── views.py              # View functions
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin configuration
│   ├── forms.py              # Form definitions
│   ├── management/        # Management commands
│   ├── templates/         # HTML templates
│   └── static/            # Static files
├── static/                # Global static files
├── data/                  # Sample data files
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
└── README.md                # This file
```

---

## API Documentation

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/claims/login/` | Login page |
| `POST` | `/claims/login/` | Authenticate user |
| `GET` | `/claims/register/` | Registration page |
| `POST` | `/claims/register/` | Create new user |
| `GET` | `/claims/logout/` | Logout user |
| `GET` | `/claims/not-authorized/` | Not authorized page |

### Claims Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home redirect to claims list |
| `GET` | `/claims/` | Claims list view |
| `GET` | `/claims/dashboard/` | Admin dashboard |
| `GET` | `/claims/claim/<id>/` | Claim detail view |
| `POST` | `/claims/claim/<id>/flag/` | Add flag to claim |
| `POST` | `/claims/claim/<id>/note/` | Add note to claim |
| `POST` | `/claims/claim/<id>/resolve-flag/` | Resolve flag |

### Data Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/claims/upload/` | Data upload page (Admin only) |
| `POST` | `/claims/upload/` | Process uploaded data (Admin only) |

### Admin & OAuth
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/` | Django admin panel |
| `GET` | `/accounts/google/login/` | Google OAuth login |
| `GET` | `/accounts/google/login/callback/` | Google OAuth callback |

---

## Usage

### For Regular Users
1. **View Claims** - Browse all claims in the main table
2. **Search/Filter** - Use the search bar and filters to find specific claims
3. **View Details** - Click on any claim row to see detailed information
4. **Flag Claims** - Use the "Flag for Review" button to mark claims needing attention
5. **Add Notes** - Use the "Add Note" button to add annotations and comments

### For Admin Users
1. **Data Upload** - Access the "Data Ingest" page to upload new claims data
2. **Dashboard Analytics** - View comprehensive statistics and analytics
3. **System Administration** - Access Django admin panel for advanced management

---

## Admin Setup

### Setup Admin User
```bash
python manage.py setup_auth
```

**What this command does:**
- Creates admin user with full permissions
- Sets up admin profile
- Clears any existing test data
- Enables access to dashboard and data upload features
- **Run this command and you will get the admin login details**

---

## Deployment

### Vercel Deployment (Recommended)

1. **Prepare for Deployment**
```bash
# Install production dependencies
pip install gunicorn whitenoise psycopg2-binary

# Collect static files
python manage.py collectstatic
```

2. **Deploy to Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Environment Variables
Set these in your Vercel dashboard:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.vercel.app
DATABASE_URL=your-postgresql-url
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
SITE_ID=1
```

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Django Community** - For the amazing web framework
- **Tailwind CSS** - For the utility-first CSS framework
- **HTMX** - For dynamic HTML without JavaScript
- **Chart.js** - For beautiful data visualization

---

<div align="center">

**Built with love for the ERISA Recovery Dev Challenge**

[Back to Top](#erisa-recovery-claims-management-system)

</div>
