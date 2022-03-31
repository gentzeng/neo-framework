from typing import Type
from django import forms

from .models import (
    NewsfeedBase,
    CaseStudy,
)


class NewsfeedBaseCreationForm(forms.ModelForm):
    class Meta:
        model: Type[NewsfeedBase] = NewsfeedBase
        fields = "__all__"

    # def clean_like_probability(self):
    #     like_probability = self.cleaned_data.get("like_probability")
    #     if like_probability < 0.0:
    #         raise forms.ValidationError(
    #             f"like_probability ({like_probability}%) is below 0%!"
    #         )

    #     if like_probability > 100.0:
    #         raise forms.ValidationError(
    #             f"like_probability ({like_probability}%) is over 100%!"
    #         )

    #     return like_probability

    def clean_newsfeed_size(self):
        newsfeed_size = self.cleaned_data.get("newsfeed_size")
        if newsfeed_size < 1:
            raise forms.ValidationError(
                f"newsfeed_size ({newsfeed_size}) has to be at least 1!"
            )

        return newsfeed_size

    def clean(self):
        cleaned_data = super().clean()
        newsfeed_size = cleaned_data.get("newsfeed_size")
        post_position_info = cleaned_data.get("post_position_info")

        if post_position_info is not None:
            if newsfeed_size < len(post_position_info):
                raise forms.ValidationError(
                    (
                        f"To many fixed post positions!"
                        f"[newsfeed_size = {newsfeed_size}, "
                        f"fixed position count = {len(post_position_info)}]"
                    )
                )


class CaseStudyForm(forms.ModelForm):
    class Meta:
        model: Type[CaseStudy] = CaseStudy
        fields = "__all__"
