from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import User


class Command(BaseCommand):
    help = 'Деактивирует пользователей, которые не были онлайн более 365 дней'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Количество дней неактивности (по умолчанию 365)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать пользователей без фактической деактивации'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)

        inactive_users = User.objects.filter(
            last_seen__lt=cutoff_date,
            is_active=True,
            is_staff=False
        )

        count = inactive_users.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Режим проверки: найдено {count} неактивных пользователей'
                )
            )
            for user in inactive_users[:10]:
                self.stdout.write(
                    f'  - {user.email} (последнее посещение: {user.last_seen})'
                )
            if count > 10:
                self.stdout.write(f'  ... и еще {count - 10} пользователей')
        else:
            inactive_users.update(is_active=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Деактивировано {count} пользователей'
                )
            )
