from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from catalogs.models import Catalog


class Command(BaseCommand):
    help = "Ingest catalog data into the Catalog and Control tables."

    def add_arguments(self, parser):
        parser.add_argument("--catalog-file", type=str)
        parser.add_argument("--impact-level", type=str, default=None)
        parser.add_argument("--name", type=str)
        parser.add_argument("--source", type=str, default=None)
        parser.add_argument("--catalog-version", type=str, default=None)

    def handle(self, *args, **options):
        input_file = Path(options["catalog_file"])

        try:
            with open(input_file, mode="rb") as catalog:
                file = File(catalog)
                name = input_name if (input_name := options["name"]) else input_file.name
                create_kwargs = {"file_name": file, "name": name}

                for arg in ("source", "catalog_version", "impact_level"):
                    if value := options[arg]:
                        create_kwargs[arg if arg != "catalog_version" else "version"] = value

                Catalog.objects.create(**create_kwargs)

        except IntegrityError as exc:
            raise CommandError(f"Error in creating new catalog: {exc}") from exc
        except (IOError, FileNotFoundError) as exc:
            raise CommandError(f"Error loading catalog file: {exc}") from exc

        self.stdout.write(self.style.SUCCESS('Successfully ingested catalog "%s"' % name))
