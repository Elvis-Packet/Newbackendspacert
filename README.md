# Spacer API - Backend Service

## Overview


Spacer API is the backend service for the Spacer space rental platform. Built with Flask and PostgreSQL, this API provides a comprehensive set of endpoints to manage spaces, bookings, users, payments, and testimonials. The service includes authentication, authorization, data validation, and image storage capabilities.

## 🛠️ Technologies

## Backend Architecture

The backend is built using Flask and follows a modular structure with clearly separated components:

- **Models:** Define the database schema and relationships using SQLAlchemy ORM. Key models include User, Space, Booking, Payment, and Testimonial.
- **Routes:** Handle API endpoints grouped by functionality such as authentication, spaces, bookings, users, payments, and testimonials.
- **Utils:** Contain helper functions for authentication, image upload, email sending, validation, and payment processing.
- **Migrations:** Manage database schema changes using Alembic.

## Features

- User authentication and authorization with JWT (JSON Web Tokens) for secure access control.
- Role-based access control with three roles: admin, owner, and client, each with different permissions.
- CRUD operations for managing spaces, bookings, users, payments, and testimonials.
- Pagination and filtering support for listing spaces, including filtering by availability status (`available` or `unavailable`).
- Image upload support for spaces using Cloudinary, including automatic image resizing and optimization.
- API documentation available through Swagger UI for easy exploration and testing of endpoints.
- CORS configured to allow secure integration with the frontend application.
- Logging and error handling implemented for better debugging and monitoring.

## User Model and Roles

Users have roles that determine their access level within the application:

- **Admin:** Full access to all resources and management capabilities.
- **Owner:** Can manage their own spaces and bookings.
- **Client:** Can browse spaces and make bookings.

Passwords are securely stored using bcrypt hashing. User attributes include email, first and last names, phone, bio, avatar URL, and verification status.

## Image Upload

Images for spaces are uploaded to Cloudinary, a cloud-based image management service. The backend automatically resizes images to a maximum of 800x800 pixels while maintaining aspect ratio, optimizes quality, and stores them securely. This ensures efficient storage and fast delivery of images.


- **Flask** - Web framework
- **SQLAlchemy** - ORM for database interactions
- **PostgreSQL** - Relational database
- **Flask-Migrate** - Database migrations
- **Flask-JWT-Extended** - JWT authentication
- **Cloudinary** - Cloud storage for images
- **Flask-CORS** - Cross-origin resource sharing
- **Marshmallow** - Data serialization/deserialization
- **Gunicorn** - WSGI HTTP Server for production

## 📋 Features

### Authentication & Authorization
- Secure user registration and login
- JWT token-based authentication
- Token refresh mechanism
- Role-based access control (user, admin)
- Password hashing with bcrypt

### Space Management
- Create, read, update, delete (CRUD) operations for spaces
- Filtering by availability, location, and other parameters
- Pagination for space listings
- Image upload and management
- Search capabilities
- `/api/auth` - Authentication endpoints (register, login, token refresh, user profile)
- `/api/spaces` - Manage spaces (list, create, update, delete)
- `/api/bookings` - Manage bookings
- `/api/users` - User management
- `/api/payments` - Payment processing
- `/api/testimonials` - User testimonials

## API Documentation

The API is documented using Swagger UI, which provides an interactive interface to explore and test all available endpoints. This documentation is accessible when the backend is running.

## Configuration

The application requires several environment variables for configuration:

- `DATABASE_URL`: Database connection string.
- `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`: Secret keys for JWT token generation and validation.
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: Credentials for Cloudinary image upload.
- `CORS_ORIGINS`: Allowed origins for CORS to enable frontend integration.

## Database

The backend uses a relational database managed via SQLAlchemy ORM. Key models include:

- **User:** Stores user information and roles.
- **Space:** Represents rentable spaces with details and images.
- **Booking:** Records bookings made by users for spaces.
- **Payment:** Handles payment transactions.
- **Testimonial:** Stores user testimonials and reviews.

Database migrations are managed using Alembic to handle schema changes safely.

### Booking System
- Create and manage bookings
- Availability checking
- Booking status workflow (pending, confirmed, cancelled, completed)
- Admin approval process

### User Management
- User profile CRUD operations
- Role management
- Password reset functionality

### Payment Processing
- Payment status tracking
- Payment method storage
- Receipt generation

### Testimonials
- Create and retrieve user testimonials
- Rating system

### General Features
- Comprehensive error handling
- Input validation
- Logging
- API documentation with Swagger

## 📂 Project Structure

```
Newbackendspacert/
├── app/                    # Application package
│   ├── models/             # Database models
│   │   ├── user.py         # User model
│   │   ├── space.py        # Space model
│   │   ├── booking.py      # Booking model
│   │   ├── payment.py      # Payment model
│   │   └── testimonial.py  # Testimonial model
│   ├── routes/             # API routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── spaces.py       # Space routes
│   │   ├── bookings.py     # Booking routes
│   │   ├── users.py        # User routes
│   │   ├── payments.py     # Payment routes
│   │   └── testimonials.py # Testimonial routes
│   ├── schemas/            # Marshmallow schemas for serialization
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── migrations/             # Database migrations
├── config.py               # Application configuration
├── app.py                  # Application factory
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── seed_spaces.py          # Seed script for test data
└── create_admin.py         # Script to create admin user
```

## 🚀 Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Cloudinary account (for image storage)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Newbackendspacert
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
1. Install dependencies:
pip install -r requirements.txt



3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/spacer
   JWT_SECRET_KEY=your_jwt_secret_key
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   FLASK_ENV=development
   ```

5. **Set up the database**
   ```bash
   flask db upgrade
   ```

6. **Create an admin user** (optional)
   ```bash
   python create_admin.py
   ```

7. **Seed the database with test data** (optional)
   ```bash
   python seed_spaces.py
   ```

8. **Run the application**
   ```bash
   flask run
   # or 
   python run.py
   ```
3. Run database migrations:
flask db upgrade



4. Start the Flask application:
flask run



## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user
- `POST /api/auth/refresh` - Refresh an access token
- `POST /api/auth/logout` - Logout a user

### Spaces
- `GET /api/spaces` - Get all spaces (with pagination and filtering)
- `GET /api/spaces/:id` - Get a specific space
- `POST /api/spaces` - Create a new space (admin only)
- `PUT /api/spaces/:id` - Update a space (admin only)
- `DELETE /api/spaces/:id` - Delete a space (admin only)
- `POST /api/spaces/:id/images` - Upload an image for a space

### Bookings
- `GET /api/bookings` - Get user's bookings or all bookings (admin)
- `GET /api/bookings/:id` - Get a specific booking
- `POST /api/bookings` - Create a new booking
- `PUT /api/bookings/:id/approve` - Approve a booking (admin only)
- `PUT /api/bookings/:id/cancel` - Cancel a booking
- `GET /api/bookings/check-availability` - Check space availability

### Users
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/:id` - Get a specific user
- `PUT /api/users/:id` - Update a user
- `DELETE /api/users/:id` - Delete a user (admin only)

### Payments
- `GET /api/payments` - Get user's payments
- `POST /api/payments` - Create a new payment
- `GET /api/payments/:id` - Get a specific payment
- `GET /api/payments/:id/receipt` - Get a payment receipt

### Testimonials
- `GET /api/testimonials` - Get all testimonials
- `POST /api/testimonials` - Create a new testimonial
- `GET /api/testimonials/:id` - Get a specific testimonial
- `PUT /api/testimonials/:id` - Update a testimonial (owner only)
- `DELETE /api/testimonials/:id` - Delete a testimonial (owner or admin)

## 🔄 Database Schema

- **Users** - Stores user information (id, email, password, role, etc.)
- **Spaces** - Stores space information (id, name, description, price, status, etc.)
- **Bookings** - Stores booking information (id, user_id, space_id, start_time, end_time, status, etc.)
- **Payments** - Stores payment information (id, booking_id, amount, status, etc.)
- **Testimonials** - Stores user testimonials (id, user_id, content, rating, etc.)
- **Images** - Stores space images (id, space_id, image_url, etc.)

## 🧪 Testing

1. **Postman Collection**
   - A Postman collection (`Peerspace_Spaces.postman_collection.json`) is included for API testing.
   - Import the collection into Postman to test the API endpoints.

2. **Manual Testing**
   - Test all endpoints with valid and invalid data.
   - Verify authentication and authorization rules.
   - Test error handling and input validation.

## 🛡️ Security Considerations

- JWT tokens are used for authentication.
- Passwords are hashed using bcrypt before storage.
- Input validation is implemented to prevent injection attacks.
- Role-based access control is implemented for protected resources.
- CORS is configured to allow requests only from the frontend origin.

## 🚧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify that PostgreSQL is running.
   - Check that the `DATABASE_URL` environment variable is correctly set.
   - Verify database user permissions.

2. **Authentication Issues**
   - Check that the JWT secret key is properly set.
   - Verify that tokens have not expired.

3. **Image Upload Problems**
   - Verify Cloudinary credentials.
   - Check file size and format restrictions.

## 🔍 Logging

- Application logs are written to the console and can be redirected to a file.
- In production, logs should be collected and monitored.

## 🚀 Deployment

1. **Prepare for Production**
   - Set `FLASK_ENV=production` in the environment variables.
   - Configure a production-ready database.
   - Set up a reverse proxy (e.g., Nginx).

2. **Gunicorn Configuration**
   - Use Gunicorn to serve the application in production.
   - Example command: `gunicorn -w 4 -b 0.0.0.0:5000 run:app`

3. **Database Migrations**
   - Always run migrations when deploying updates: `flask db upgrade`

## 📞 Contact

For questions or support, please contact the development team at backend-support@spacer.com.
  # **Simon====Dev >>>>>>>** >>> https://github.com/simon036
  ## **Elvis---packet>>>>>>>**>>>> https://github.com/Elvis-Packet

## 📄 License

This project is licensed under the Moringa License. 
## Contact
