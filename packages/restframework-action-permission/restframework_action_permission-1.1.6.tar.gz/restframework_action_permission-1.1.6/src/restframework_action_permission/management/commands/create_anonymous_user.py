from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create anonymous user in defined user model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keys",
            nargs="+",
        )
        parser.add_argument(
            "--values",
            nargs="+",
        )

    def handle(self, *args, **options):
        keys = options["keys"]
        values = options["values"]

        if len(keys) != len(values):
            raise CommandError("keys and values should be in same length")

        row = {key: value for key, value in zip(options["keys"], options["values"])}
        model = get_user_model()
        model.objects.create(id=1, **row)
