from app import create_app, db
from app.models.user import User

app = create_app()
app.app_context().push()

def create_admin_user(email, password, first_name, last_name):
    if User.query.filter_by(email=email).first():
        print(f"User with email {email} already exists.")
        return

    admin_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='admin'
    )
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin user {email} created successfully.")

if __name__ == "__main__":
    # Replace these values with the desired admin user details
    email = "admin@example.com"
    password = "AdminPassword123!"
    first_name = "Admin"
    last_name = "User"

    create_admin_user(email, password, first_name, last_name)
