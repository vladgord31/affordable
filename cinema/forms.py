from typing import Literal
from django import forms

from main.models import Comments, Movie, Reviews, Seat

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields: tuple[Literal['text']] = ('text',)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ('title', 'text', 'rating',)


class SeatSelectionForm(forms.Form):
    movie = forms.ModelChoiceField(queryset=Movie.objects.all(), label="Фільм")
    seats = forms.ModelMultipleChoiceField(
        queryset=Seat.objects.filter(status="free"),
        widget=forms.CheckboxSelectMultiple,
        label="Місця",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "movie" in self.fields:
            self.fields["seats"].queryset = Seat.objects.filter(
                movie_session=self.fields["movie"].queryset.first(), status="free"
            )

    def clean(self):
        cleaned_data = super().clean()
        movie = cleaned_data.get("movie")
        seats = cleaned_data.get("seats")

        if movie and seats:
            for seat in seats:
                if seat.movie_session != movie or seat.status != "free":
                    raise forms.ValidationError(
                        "Обрані місця недоступні для цього фільму або вже зайняті."
                    )

        return cleaned_data
