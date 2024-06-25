from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, redirect, render, get_object_or_404
from cinema.utils import q_search
from main.models import Category, Comments, Genre, Movie, MovieShots, Seat
from django.views.generic.base import View
from cinema.forms import CommentForm, ReviewForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import q_search

class MovieCatalogView(View):
    def get(self, request):
        genres = Genre.objects.all()
        categories = Category.objects.all()
        movies = Movie.objects.all()

        genre_slug = request.GET.get('genre')
        category_slug = request.GET.get('category')
        query = request.GET.get('q')

        if category_slug:
            movies = Movie.objects.filter(category__slug=category_slug)
            movies = get_list_or_404(movies)
        elif query:
            movies = q_search(query)

        if genre_slug:
            movies = movies.filter(genres__slug=genre_slug)

        paginator = Paginator(movies, 1)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'movies': page_obj,
            'genres': genres,
            'categories': categories,
            'genre_slug': genre_slug,
        }
        return render(request, 'cinema/catalog.html', context)

class MovieDetailView(View):
    def get(self, request, movie_slug):
        movie = get_object_or_404(Movie, slug=movie_slug)
        movies = Movie.objects.exclude(slug=movie_slug)
        comments = movie.comments.all()
        reviews = movie.reviews.all()
        review_form = ReviewForm()
        movieshots = MovieShots.objects.filter(movie=movie)
        context = {
            "movie": movie,
            "movies": movies,
            "comments": comments,
            "reviews": reviews,
            "review_form": review_form,
            "movieshots": movieshots,
        }
        return render(request, "cinema/movie.html", context)

class AddComment(LoginRequiredMixin, View):
    def post(self, request, movie_slug):
        form = CommentForm(request.POST)
        movie = get_object_or_404(Movie, slug=movie_slug)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.user = request.user
            comment.save()
        return redirect("cinema:movie", movie_slug=movie_slug)

class AddReview(LoginRequiredMixin, View):
    def post(self, request, movie_slug):
        form = ReviewForm(request.POST)
        movie = get_object_or_404(Movie, slug=movie_slug)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user 
            review.save()
        return redirect("cinema:movie", movie_slug=movie_slug)


class TicketView(LoginRequiredMixin, View):
    def get(self, request, movie_slug):
        movie = get_object_or_404(Movie, slug=movie_slug)
        seats = movie.seat.all()
        context = {
            "movie": movie,
            "seats": seats,
        }
        return render(request, "cinema/tickets.html", context)


class ReservationView(LoginRequiredMixin, View):
    def post(self, request, movie_slug):
        selected_seat_ids = request.POST.getlist("seat_ids[]")
        session_id = request.POST.get("session_id")

        movie = get_object_or_404(Movie, slug=movie_slug)
        selected_seats = Seat.objects.filter(id__in=selected_seat_ids)

        # Mark selected seats as reserved
        for seat in selected_seats:
            seat.status = "reserved"
            seat.save()

        # Perform any additional logic (e.g., create a payment record, send notifications, etc.)

        return redirect("cinema:movie_tickets", movie_slug=movie.slug)
