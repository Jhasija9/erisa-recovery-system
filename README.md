
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

## Testing

### Setup Admin User
```bash
python manage.py setup_auth
```

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
