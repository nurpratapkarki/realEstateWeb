#!/usr/bin/env python3
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import (
    PropertyType,
    Property,
    PropertyImage,
    Agent,
    Organization,
    PropertyInquiry,
    PropertyVisit,
    SavedProperty,
    Service,
    HeroSlide,
    JourneyStep,
    AboutUs,
    PropertyAlert,
    Team,
)
from faker import Faker
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

fake = Faker()
User = get_user_model()

# Helper to create a fake image


def get_fake_image(name="test.jpg"):
    file = BytesIO()
    image = Image.new(
        "RGB",
        (100, 100),
        color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    )
    image.save(file, "JPEG")
    file.seek(0)
    return ContentFile(file.read(), name)


class Command(BaseCommand):
    help = "Generate fake data for the real estate project."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Generating fake data..."))

        # 1. Property Types
        property_types = []
        for _ in range(5):
            pt = PropertyType.objects.create(
                name=fake.unique.word().title(),
                description=fake.sentence(),
                is_active=True,
            )
            property_types.append(pt)

        # 2. Organizations
        orgs = []
        for _ in range(2):
            org = Organization.objects.create(
                name=fake.company(),
                description=fake.text(),
                phone=fake.numerify(text="+1##########"),
                email=fake.company_email(),
                address=fake.address(),
                whatsapp=fake.numerify(text="+1##########"),
                facebook=fake.url(),
                instagram=fake.url(),
                linkedin=fake.url(),
                twitter=fake.url(),
            )
            orgs.append(org)

        # 3. Users (customers and agents)
        users = []
        agents = []
        for i in range(10):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.numerify(text="+1##########"),
            )
            users.append(user)
            # Make some users agents
            if i < 3:
                agent = Agent.objects.create(
                    user=user,
                    experience_years=random.randint(1, 10),
                    license_number=fake.unique.bothify(text="LIC####"),
                    is_active=True,
                )
                # Assign specializations
                agent.specializations.set(
                    random.sample(property_types, k=random.randint(1, 3))
                )
                agents.append(agent)

        # 4. Properties
        properties = []
        for _ in range(20):
            prop = Property.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                property_type=random.choice(property_types),
                price=round(random.uniform(50000, 1000000), 2),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 4),
                area=round(random.uniform(500, 5000), 2),
                location=fake.city(),
                address=fake.address(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                is_featured=random.choice([True, False]),
                is_active=True,
            )
            properties.append(prop)
            # Add images
            for j in range(random.randint(1, 4)):
                PropertyImage.objects.create(
                    property=prop,
                    image=get_fake_image(f"property_{prop.id}_{j}.jpg"),
                    is_primary=(j == 0),
                    order=j,
                )

        # 5. Services
        for _ in range(5):
            Service.objects.create(
                title=fake.sentence(nb_words=3),
                description=fake.text(),
                icon=fake.word(),
                is_active=True,
                order=random.randint(1, 10),
            )

        # 6. Hero Slides
        for _ in range(3):
            HeroSlide.objects.create(
                title=fake.sentence(nb_words=3),
                subtitle=fake.sentence(),
                image=get_fake_image("hero.jpg"),
                link_url=fake.url(),
                is_active=True,
                order=random.randint(1, 5),
            )

        # 7. Journey Steps
        for _ in range(4):
            JourneyStep.objects.create(
                title=fake.sentence(nb_words=2),
                description=fake.text(),
                icon=fake.word(),
                order=random.randint(1, 10),
                is_active=True,
            )

        # 8. About Us
        AboutUs.objects.create(
            title="About Us",
            content=fake.text(),
            vision=fake.text(),
            mission=fake.text(),
            image1=get_fake_image("about1.jpg"),
            image2=get_fake_image("about2.jpg"),
            is_active=True,
        )

        # 9. Team Members
        for _ in range(6):
            Team.objects.create(
                name=fake.name(),
                bio=fake.text(max_nb_chars=200),
                position=fake.job(),
                email=fake.email(),
                image=get_fake_image("team_member.jpg"),
            )

        # 10. Property Inquiries
        for _ in range(10):
            PropertyInquiry.objects.create(
                customer=random.choice(users),
                property=random.choice(properties),
                agent=random.choice(agents) if agents else None,
                message=fake.sentence(),
                status=random.choice(["pending", "responded", "closed"]),
            )

        # 11. Property Visits
        for _ in range(10):
            PropertyVisit.objects.create(
                customer=random.choice(users),
                property=random.choice(properties),
                agent=random.choice(agents) if agents else None,
                scheduled_date=fake.date_this_year(),
                scheduled_time=fake.time(),
                status=random.choice(["scheduled", "completed", "cancelled"]),
                notes=fake.sentence(),
            )

        # 12. Saved Properties
        for _ in range(15):
            try:
                SavedProperty.objects.create(
                    customer=random.choice(users), property=random.choice(properties)
                )
            except:
                pass  # Ignore duplicates

        # 13. Property Alerts
        for _ in range(8):
            PropertyAlert.objects.create(
                customer=random.choice(users),
                property_type=random.choice(property_types),
                min_price=round(random.uniform(50000, 200000), 2),
                max_price=round(random.uniform(200000, 1000000), 2),
                location=fake.city(),
                min_bedrooms=random.randint(1, 3),
                max_bedrooms=random.randint(3, 5),
                is_active=True,
            )

        self.stdout.write(self.style.SUCCESS("Fake data generation complete."))


def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
