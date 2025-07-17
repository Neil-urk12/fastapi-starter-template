# FastAPI Starter Template with JWT-Based Authentication

A modern FastAPI application featuring user authentication, role-based access control, and item management functionality for example CRUD operations.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **User Management** - User registration, login, and profile management
- 🛡️ **Role-Based Access Control** - Multi-role user system (admin, user)
- 📦 **Item Management** - CRUD operations for items
- 🔒 **Password Security** - Bcrypt password hashing
- 🗄️ **SQLite Database** - Lightweight database with SQLAlchemy ORM
- 📝 **API Documentation** - Auto-generated OpenAPI/Swagger docs
- ⚡ **Async Support** - Asynchronous request handling

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database
- **JWT** - JSON Web Tokens for authentication
- **Bcrypt** - Password hashing
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server

## Project Structure

```
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── init_db.py          # Database initialization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── item.py             # Item SQLAlchemy model
│   │   ├── token.py            # Token Pydantic models
│   │   └── user.py             # User & Role SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py             # Authentication endpoints
│   │   └── item.py             # Item CRUD endpoints
│   ├── schemas/
│   │   ├── item.py             # Item Pydantic schemas
│   │   └── user.py             # User Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py     # Authentication logic
│       └── user_service.py     # User management logic
├── config.py                   # Application configuration
├── database.py                 # Database setup
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-auth-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your_secret_key_here
   SQLALCHEMY_DATABASE_URL=sqlite:///./app.db
   ```

## Usage

### Running the Application

```bash
uvicorn main:app --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### API Endpoints

#### Authentication
- `POST /api/token` - Login and get access token
- `POST /api/users` - Register new user
- `GET /api/users/me` - Get current user profile
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users?username=<username>` - Get user by username
- `GET /api/users/email?email=<email>` - Get user by email
- `GET /api/protected` - Protected route example

#### Items
- `POST /api/items` - Create new item
- `GET /api/items` - Get all items
- `GET /api/items/{item_id}` - Get item by ID
- `PATCH /api/items/{item_id}` - Update item

### Authentication Flow

1. **Register a new user**
   ```bash
   curl -X POST "http://localhost:8000/api/users" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "johndoe",
          "firstname": "John",
          "lastname": "Doe",
          "email": "john@example.com",
          "password": "secretpassword"
        }'
   ```

2. **Login to get access token**
   ```bash
   curl -X POST "http://localhost:8000/api/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=johndoe&password=secretpassword"
   ```

3. **Use token for protected routes**
   ```bash
   curl -X GET "http://localhost:8000/api/users/me" \
        -H "Authorization: Bearer <your_access_token>"
   ```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `firstname` - User's first name
- `lastname` - User's last name
- `email` - Unique email address
- `hashed_password` - Bcrypt hashed password
- `is_active` - Account status
- `created_at` - Account creation timestamp

### Roles Table
- `id` - Primary key
- `name` - Role name (e.g., "user", "admin")
- `created_at` - Role creation timestamp

### Items Table
- `id` - Primary key
- `name` - Item name
- `available` - Availability status

### User-Roles Relationship
Many-to-many relationship allowing users to have multiple roles.

## Configuration

The application uses environment variables for configuration:

- `SECRET_KEY` - JWT secret key (required)
- `SQLALCHEMY_DATABASE_URL` - Database connection string (required)

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Role-Based Access**: Users can have multiple roles for fine-grained permissions
- **Input Validation**: Pydantic models ensure data integrity
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection attacks

## Development

### Database Initialization

The application automatically:
- Creates database tables on startup
- Initializes default roles ("user", "admin")
- Sets up proper relationships and indexes

### Adding New Features

1. **Models**: Add new SQLAlchemy models in `app/models/`
2. **Schemas**: Create Pydantic schemas in `app/schemas/`
3. **Routes**: Implement API endpoints in `app/routes/`
4. **Services**: Add business logic in `app/services/`

### Testing

The application includes a test database (`test`) for development and testing purposes.

## API Documentation

Once the application is running, visit:
- http://localhost:8000/docs for Swagger UI
- http://localhost:8000/redoc for ReDoc

These provide interactive API documentation where you can test endpoints directly.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.