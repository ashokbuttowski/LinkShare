# LinkShare - Personal Link Collection App

LinkShare is a full-stack web application that allows users to save and organize their favorite links with automatic metadata extraction.

## Features

- User authentication (registration/login) with JWT tokens
- Save links with automatic title, description, and image extraction  
- View saved links in a beautiful card-based layout
- Delete saved links
- Responsive design with Tailwind CSS

## Tech Stack

- **Frontend**: React 19, Tailwind CSS, Axios
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **Authentication**: JWT tokens with bcrypt password hashing

## Quick Start (Current Cloud Environment)

The app is currently running and accessible at:
- Frontend: https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com
- Backend API: https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com/api

## Local Development with Docker Compose

If you want to run this locally using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd linkshare

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:10001
# Backend API: http://localhost:10002/api
```

### Environment Configuration

The application uses different environment configurations:

- **Cloud Environment**: Uses managed URLs and services
- **Docker Compose**: Uses localhost URLs with specific ports

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user  
- `GET /api/auth/me` - Get current user info

### Links
- `GET /api/links` - Get user's saved links
- `POST /api/links` - Save a new link
- `DELETE /api/links/{link_id}` - Delete a link
- `POST /api/links/extract-metadata` - Extract metadata from URL

### Health
- `GET /api/health` - Health check endpoint

## Troubleshooting

If you encounter "User authentication failed" errors:

1. **Docker Compose Issues**: Ensure all services are running:
   ```bash
   docker-compose ps
   ```

2. **Backend Connectivity**: Test the backend health endpoint:
   ```bash
   curl http://localhost:10002/api/health
   ```

3. **MongoDB Connection**: Ensure MongoDB is accessible:
   ```bash
   docker-compose logs mongodb
   ```

4. **Check Logs**: View service logs for errors:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Development  
```bash
cd frontend
yarn install
yarn start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
