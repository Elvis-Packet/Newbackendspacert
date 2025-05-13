# Spacer API Backend

This is the backend API for the Spacer application, which manages space bookings.

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

## API Endpoints

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

## Running the Application

1. Install dependencies:
pip install -r requirements.txt



2. Set environment variables for configuration (e.g., database URL, JWT keys, Cloudinary keys).

3. Run database migrations:
flask db upgrade



4. Start the Flask application:
flask run



## Testing

- Test API endpoints using tools like Postman or Curl.
- Verify frontend integration by running the frontend app and ensuring data fetching works correctly.

## Notes

- The backend API expects the frontend to call endpoints with the `/api` prefix.
- The `status` query parameter in `/api/spaces` supports values `available` and `unavailable` to filter spaces by availability.
- Logging and error handling are implemented for better debugging.

## Contact