import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from config.health import integrity_checks


class Command(BaseCommand):
    help = 'Exporte les contrôles d’intégrité en JSON (lecture seule).'

    def add_arguments(self, parser):
        parser.add_argument('--output', help='Chemin du fichier JSON; sinon sortie standard.')

    def handle(self, *args, **options):
        checks = integrity_checks()
        content = json.dumps({'generated_at': timezone.now(), 'total': sum(c['count'] for c in checks), 'checks': checks}, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)
        if options['output']:
            path = Path(options['output'])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content+'\n', encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f'Rapport exporté : {path}'))
        else:
            self.stdout.write(content)
