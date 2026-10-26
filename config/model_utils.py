from django.db import models


class Horodatage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        if kwargs.get('update_fields'):
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'updated_at'}
        return super().save(*args, **kwargs)
