# pylint: disable=import-error
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Movie, MovieList


@login_required(login_url="login")
def index(request):
    """Function display index page."""
    movies = Movie.objects.all()
    # top 5
    movies_top_five = Movie.objects.all()[:5]
    featured_movies = movies[len(movies) - 1]
    # genres
    genres = Movie.GENRE_CHOICE
    # genres = Movie.objects.values("genre").distinct().order_by("genre")
    context = {
        "movies": movies,
        "movies_top_five": movies_top_five,
        "featured_movies": featured_movies,
        "genres": genres,
    }
    return render(request, "index.html", context)


@login_required(login_url="login")
def movie(request, pk):
    """Function display movie page."""
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id=movie_uuid)
    context = {
        "movie_details": movie_details,
    }
    return render(request, "movie.html", context)


@login_required(login_url="login")
def search(request):
    """Search elements"""
    if request.method == "POST":
        search_text = request.POST["search_text"]
        movies = Movie.objects.filter(title__icontains=search_text)
        context = {"movies": movies, "search_text": search_text}
        return render(request, "search.html", context)
    elif request.htmx:
        search_text = request.POST["search_text"]
        movies = Movie.objects.filter(title__icontains=search_text)
        context = {"movies": movies, "search_text": search_text}
        return render(request, "search.html", context)
    else:
        return redirect("/")


@login_required(login_url="login")
def genre(request, genre):
    """Function display movie page."""
    movie_genre = genre
    movies = Movie.objects.filter(genre=movie_genre)
    context = {
        "movies": movies,
        "movies_genre": movie_genre,
    }
    return render(request, "genre.html", context)


@login_required(login_url="login")
def favorite(request):
    """Function display my favorite list Movies."""
    movie_list = MovieList.objects.filter(owner_user=request.user)

    user_movie_list = []

    for m in movie_list:
        user_movie_list.append(m.movie)

    if not movie_list:
        # Maneja el caso en que no hay objetos MovieList
        context = {
            "message": "No hay películas favoritas.",
        }
    else:
        user_movie_list = [m.movie for m in movie_list]
        context = {
            "movies": user_movie_list,
        }
    return render(request, "favorite.html", context)


def check_in_list(request):
    movie_id = request.GET.get("movie_id")

    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    match = re.search(uuid_pattern, movie_id)
    movie_id = match.group() if match else None

    # Comprueba si el video ya está en la lista de favoritos del usuario
    is_in_list = False
    if movie_id:
        try:
            movie = Movie.objects.get(uu_id=movie_id)
            is_in_list = MovieList.objects.filter(
                owner_user=request.user, movie=movie
            ).exists()
        except Movie.DoesNotExist:
            pass
    print("is_in_list: %s" % is_in_list)
    return JsonResponse({"is_in_list": is_in_list})


@login_required(login_url="login")
def add_remove_favorite(request):
    """Function add movie to my favorite list."""
    if request.method == "POST":
        movie_url_id = request.POST["movie_id"]

        # patter for uu_id
        # example: http://127.0.0.1:8000/movie/5487165e-6e7d-4606-a4b9-9476bb38adbb

        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        match = re.search(uuid_pattern, movie_url_id)
        movie_id = match.group() if match else None

        # check if movie is already in the list
        movie = get_object_or_404(Movie, uu_id=movie_id)

        # get movie or add movie to list
        movie_list, created = MovieList.objects.get_or_create(
            owner_user=request.user, movie=movie
        )

        if created:
            response_data = {"status": "success", "message": "Video added to favorites"}
        elif MovieList.objects.filter(owner_user=request.user, movie=movie).exists():
            movie_list = MovieList.objects.get(owner_user=request.user, movie=movie)
            movie_list.delete()
            response_data = {
                "status": "warning",
                "message": "Removed video from favorites",
            }
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=400
        )
    return JsonResponse(response_data)


def login(request):
    """Function login user to the system."""
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        remember = request.POST.get("remember", False)

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if remember:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 días
            else:
                request.session.set_expiry(0)  # Expira cuando se cierra el navegador

            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def signup(request):
    """Function register user to the system."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeat-password']
        if password == repeat_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # log user in the system and redirect
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    return render(request, 'signup.html')


@login_required(login_url="login")
def logout(request):
    """Function logout user from the system."""
    auth.logout(request)
    return redirect("login")
