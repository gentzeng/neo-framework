from django.core.management import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from utils_newsfeed.csv_upload import load_csv

User = get_user_model()

user = User.objects.get(pk=2)


class Command(BaseCommand):
    help = "Loads posts and authors from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("user", type=str)
        parser.add_argument("file_path", type=str)
        parser.add_argument("newsfeed_base_id", type=int)

    def handle(self, *args, **options):
        start_time = timezone.now()

        file_path = options["file_path"]
        newsfeed_base_id = options["newsfeed_base_id"]
        load_csv(user=user, file_path=file_path, newsfeed_base_id=newsfeed_base_id)

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Loading CSV took: "
                    f"{(end_time-start_time).total_seconds()} seconds "
                    f"for newsfeed_base {newsfeed_base_id}."
                )
            )
        )
