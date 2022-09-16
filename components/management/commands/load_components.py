import json

from pathlib import Path

from pydantic import ValidationError
from django.core.management.base import BaseCommand, CommandError

from blueprintapi.oscal.component import Model as ComponentModel
from components.models import Component


class Command(BaseCommand):
    help = (
        "Ingest component data into the Component table. "
        "Currently assumes a single component definition defined against a single catalog"
    )

    def add_arguments(self, parser):
        parser.add_argument("--load-test-data", type=bool, default=True)

    def handle(self, *args, **options):
        if options["load_test_data"]:
            self._load_test_data()

    def _load_component(self, json_path: Path):
        """Ingest a component from a valid OSCAL JSON file."""
        try:
            component = ComponentModel.from_json(json_path)
        except ValidationError as exc:
            raise CommandError(f"Could not load, {json_path.name} due to invalid data: {exc}") from exc

        # Assume only one item in the "components" list for now
        component_def = component.component_definition.components[0]

        _, created = Component.objects.get_or_create(
            title=component_def.title,
            description=component_def.description,
            type=component_def.type,
            controls=component_def.control_ids,
            component_json=json.loads(component.json(by_alias=True, exclude_none=True)),
            status=Component.Status.PUBLIC,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Component, {component_def.title} was successfully created."))
        else:
            self.style.WARNING(f"Component, {component_def.title} already exists. Skipping creation.")

    # noinspection PyMethodMayBeStatic
    def _load_test_data(self):
        """Load test component data included in the repo."""
        data_dir = Path(__file__).parents[2] / "data"

        for component_def in data_dir.glob("*json"):
            self._load_component(component_def)
