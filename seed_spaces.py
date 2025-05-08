from app import db, create_app
from app.models.space import Space, SpaceImage
from faker import Faker
import random

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

def seed_spaces():
    with app.app_context():
        # Clear existing spaces and images
        SpaceImage.query.delete()
        Space.query.delete()

        # For owner_id, use 1 as default or create a dummy owner if needed
        owner_id = 1

        featured_spaces = []
        for _ in range(5):
            name = fake.company() + " " + fake.bs().title()
            description = fake.paragraph(nb_sentences=3)
            price = round(random.uniform(50, 200), 2)
            address = fake.address()
            city = fake.city()
            capacity = random.randint(5, 50)
            featured_spaces.append(create_space_with_images(name, description, price, address, city, capacity, owner_id))

        available_spaces = []
        for _ in range(5):
            name = fake.catch_phrase()
            description = fake.paragraph(nb_sentences=2)
            price = round(random.uniform(20, 100), 2)
            address = fake.address()
            city = fake.city()
            capacity = random.randint(1, 20)
            available_spaces.append(create_space_with_images(name, description, price, address, city, capacity, owner_id))

        db.session.commit()
        print("Seeded featured and available spaces with images successfully.")

if __name__ == "__main__":
    seed_spaces()
