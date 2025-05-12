# Spacer API Backend

This is the backend API for the Spacer application, which manages space bookings.

## Features

- User authentication and authorization with JWT
- CRUD operations for spaces, bookings, users, payments, and testimonials
- Pagination and filtering support for listing spaces
- Image upload support for spaces using Cloudinary
- Role-based access control for admin and owners
- API documentation with Swagger UI
- CORS configured for frontend integration

## API Endpoints

- `/api/auth` - Authentication endpoints (login, register, token refresh)
- `/api/spaces` - Manage spaces (list, create, update, delete)
- `/api/bookings` - Manage bookings
- `/api/users` - User management
- `/api/payments` - Payment processing
- `/api/testimonials` - User testimonials

## Configuration

- Database connection configured via `DATABASE_URL` environment variable
- JWT secret keys configured via environment variables
- Cloudinary credentials for image uploads
- CORS configured to allow requests from the frontend URL

## Running the Application

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set environment variables for configuration (e.g., database URL, JWT keys, Cloudinary keys).

3. Run database migrations:
   ```
   flask db upgrade
   ```

4. Start the Flask application:
   ```
   flask run
   ```

## Testing

- Test API endpoints using tools like Postman or Curl.
- Verify frontend integration by running the frontend app and ensuring data fetching works correctly.

## Notes

- The backend API expects the frontend to call endpoints with the `/api` prefix.
- The `status` query parameter in `/api/spaces` supports values `available` and `unavailable` to filter spaces by availability.
- Logging and error handling are implemented for better debugging.

## Contact

For any issues or questions, please contact the development team.
