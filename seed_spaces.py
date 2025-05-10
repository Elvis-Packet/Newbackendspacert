from app import db, create_app
from app.models.user import User
from app.models.space import Space, SpaceImage
from app.models.booking import Booking
from app.models.review import Review
from faker import Faker
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

app = create_app()
fake = Faker()

REAL_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "https://images.unsplash.com/photo-1494526585095-c41746248156",
    "https://images.unsplash.com/photo-1520880867055-1e30d1cb001c",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d",
    "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
    "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5",
]

def seed_users(num_users=5):
    users = []
    # Create an admin user first
    admin = User(
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        phone=fake.phone_number(),
        bio='System administrator',
        avatar_url='https://i.pravatar.cc/150?img=1'
    )
    users.append(admin)
    db.session.add(admin)

    # Create regular users
    for _ in range(num_users - 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = User(
            email=fake.email(),
            password_hash=generate_password_hash('password123'),
            first_name=first_name,
            last_name=last_name,
            phone=fake.phone_number(),
            bio=fake.text(max_nb_chars=200),
            avatar_url=f"https://i.pravatar.cc/150?img={random.randint(2, 70)}"
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    return users

def create_space_with_images(name, description, price, address, city, capacity, owner_id):
    space = Space(
        name=name,
        description=description,
        price_per_hour=price,
        address=address,
        city=city,
        capacity=capacity,
        owner_id=owner_id,
        is_available=True,
    )
    db.session.add(space)
    db.session.flush()  # To get space.id before commit

    num_images = random.randint(1, 3)
    chosen_images = random.sample(REAL_IMAGE_URLS, num_images)
    for i, url in enumerate(chosen_images):
        image = SpaceImage(
            space_id=space.id,
            image_url=url + "?auto=format&fit=crop&w=800&q=80",
            is_primary=(i == 0)
        )
        db.session.add(image)
    return space

def seed_spaces(users, num_spaces=10):
    spaces = []
    for _ in range(num_spaces):
        space = Space(
            name=fake.company() + " " + fake.bs().title(),
            description=fake.paragraph(nb_sentences=3),
            price_per_hour=round(random.uniform(20, 200), 2),
            address=fake.address(),
            city=fake.city(),
            capacity=random.randint(5, 50),
            owner_id=random.choice(users).id,
            is_available=True
        )
        spaces.append(space)
        db.session.add(space)
        
        # Add images for each space
        num_images = random.randint(1, 3)
        for i in range(num_images):
            image = SpaceImage(
                space=space,
                image_url=f"https://picsum.photos/800/600?random={random.randint(1,1000)}",
                is_primary=(i == 0)
            )
            db.session.add(image)
    
    db.session.commit()
    return spaces

def seed_bookings(users, spaces, num_bookings=20):
    bookings = []
    purposes = [
        'Business Meeting', 
        'Workshop', 
        'Conference', 
        'Training Session', 
        'Photo Shoot',
        'Team Building',
        'Private Event',
        'Presentation',
        'Interview',
        'Seminar'
    ]
    
    for _ in range(num_bookings):
        start_time = datetime.now() + timedelta(days=random.randint(-30, 30))
        booking = Booking(
            user_id=random.choice(users).id,
            space_id=random.choice(spaces).id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=random.randint(1, 8)),
            total_price=random.uniform(50, 500),
            status=random.choice(['pending', 'confirmed', 'completed', 'cancelled']),
            purpose=random.choice(purposes),  # Add purpose here
            payment_status='pending'  # Add payment_status if required
        )
        bookings.append(booking)
        db.session.add(booking)
    db.session.commit()
    return bookings

def seed_reviews(users, spaces, num_reviews=15):
    reviews = []
    for _ in range(num_reviews):
        review = Review(
            user_id=random.choice(users).id,
            space_id=random.choice(spaces).id,
            rating=random.randint(1, 5),
            comment=fake.paragraph(),
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        reviews.append(review)
        db.session.add(review)
    db.session.commit()
    return reviews

def seed_all():
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            print("Clearing existing data...")
            # Delete in proper order to respect foreign key constraints
            db.session.query(Review).delete()
            db.session.query(Booking).delete()
            db.session.query(SpaceImage).delete()
            db.session.query(Space).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            print("Seeding users...")
            users = seed_users()
            
            print("Seeding spaces...")
            spaces = seed_spaces(users)
            
            print("Seeding bookings...")
            bookings = seed_bookings(users, spaces)
            
            print("Seeding reviews...")
            reviews = seed_reviews(users, spaces)
            
            print("Seeding completed successfully!")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == "__main__":
    seed_all()
