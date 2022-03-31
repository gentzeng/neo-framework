from django.contrib import admin

# Register your models here.
from .models import (
    CaseStudy,
    CaseStudyRound,
    NewsfeedBase,
    NewsfeedScrapingSetting,
    NewsfeedDisplayingSetting,
    AuthorSource,
    Author,
    AuthorAgent,
    # Post,
    PostManual,
    ScrapedPost,
    PostUrl,
    PostStatistic,
    Result,
)


class CaseStudyColumns(admin.ModelAdmin):
    list_display = ["id", "user", "name", "time_created"]


class CaseStudyRoundColumns(admin.ModelAdmin):
    list_display = ["id", "user", "case_study_id", "name", "time_created"]


class NewsfeedBaseColumns(admin.ModelAdmin):
    list_display = ["id", "user", "case_study_round_id", "name", "time_created"]


class AuthorSourceColumns(admin.ModelAdmin):
    list_display = ["id", "name"]


class AuthorColumns(admin.ModelAdmin):
    list_display = ["id", "name"]


class AuthorAgentColumns(admin.ModelAdmin):
    list_display = ["id", "name"]
    list_display = ["id", "author_source", "author", "name", "username", "verified"]


class PostManualColumns(admin.ModelAdmin):
    list_display = ["id", "user", "author_agent", "time_created"]


class PostUrlColumns(admin.ModelAdmin):
    list_display = ["id", "post_manual", "scraped_post", "url"]


class ScrapedPostColumns(admin.ModelAdmin):
    list_display = ["id", "user", "author_agent", "time_created"]


admin.site.register(CaseStudy, CaseStudyColumns)
admin.site.register(CaseStudyRound, CaseStudyRoundColumns)
admin.site.register(NewsfeedBase, NewsfeedBaseColumns)
admin.site.register(NewsfeedScrapingSetting)
admin.site.register(NewsfeedDisplayingSetting)
admin.site.register(AuthorSource, AuthorSourceColumns)
admin.site.register(Author, AuthorColumns)
admin.site.register(AuthorAgent, AuthorAgentColumns)
admin.site.register(ScrapedPost, ScrapedPostColumns)
admin.site.register(PostManual, PostManualColumns)
admin.site.register(PostUrl, PostUrlColumns)
admin.site.register(PostStatistic)
admin.site.register(Result)
