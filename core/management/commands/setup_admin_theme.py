from django.core.management.base import BaseCommand
from admin_interface.models import Theme

class Command(BaseCommand):
    help = 'Set up the admin interface theme'

    def handle(self, *args, **options):
        # Get or create the default theme
        theme, created = Theme.objects.get_or_create(
            name='Guide App Theme',
            defaults={
                'active': True,
                'title': 'Guide App Administration',
                'title_visible': True,
                'env_name': 'Guide App',
                'env_visible_in_header': True,
                'env_color': '#667eea',
                'list_filter_dropdown': True,
                'recent_actions_visible': True,
                'related_modal_active': True,
                'related_modal_background_opacity': 0.3,
                'related_modal_rounded_corners': True,
                'related_modal_close_button_visible': True,
                'language_chooser_active': False,
                'list_filter_sticky': True,
                'foldable_apps': True,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created Guide App admin theme'
                )
            )
        else:
            # Update existing theme
            theme.active = True
            theme.title = 'Guide App Administration'
            theme.env_name = 'Guide App'
            theme.env_color = '#667eea'
            theme.list_filter_dropdown = True
            theme.recent_actions_visible = True
            theme.related_modal_active = True
            theme.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully updated Guide App admin theme'
                )
            )
