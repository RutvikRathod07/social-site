import io
import requests
from django.core.management.base import BaseCommand
from faker import Faker
from blogapp.models import Post,CustomUser
from django.utils import timezone
from PIL import Image


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("========start==========")
        fake = Faker()

        for i in range(11):
            # Post.objects.get(id=i).delete()

            title = fake.name()
            # desc = fake.sentence()
            desc = ""
            for _ in range(3):
                desc += fake.sentence() + " "

            # Download a random image from the internet
            response = requests.get(f'https://picsum.photos/id/{i+50}/300/300')
            img_bytes = response.content

            # Load the image bytes into a PIL Image object
            img = Image.open(io.BytesIO(img_bytes))

            publish_date = timezone.make_aware(fake.date_time_between(start_date='-1y', end_date='now'), timezone.utc)
            postby =CustomUser.objects.get(pk=1)
            post = Post(title=title, desc=desc, publish_date=publish_date, postby=postby)

            # Create a BytesIO object to save the image to
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            # Save the image to the Post object
            img_name = f'{title}.jpg'
            post.img.save(img_name, img_io, save=True)
            post.save()
