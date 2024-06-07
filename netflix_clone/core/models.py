import uuid

from django.db import models
from django.conf import settings

class Movie(models.Model):
    GENRE_CHOICE = [
        ("action", "Action"),
        ("comedy", "Comedy"),
        ("drama", "Drama"),
        ("horror", "Horror"),
        ("war", "War"),
        ("documentary", "Documentary"),
        ("animation", "Animation"),
        ("Biography", "Biography"),
        ("science_fiction", "Science_fiction"),
        ("fantasy", "Fantasy"),
    ]

    uu_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    relase_date = models.DateField()
    genre = models.CharField(max_length=255, choices=GENRE_CHOICE)
    length = models.PositiveIntegerField()
    image_card = models.ImageField(upload_to='movie_images/card/')
    image_cover = models.ImageField(upload_to='movie_images/cover/')
    video = models.FileField(upload_to="movie_videos/")
    movie_views = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class MovieList(models.Model):
    """Relation many to many, created new table relation between user and movie."""

    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return f"Favorite for {self.owner_user} and {self.movie}"
