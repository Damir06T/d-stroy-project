from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone

from django.db.models.signals import post_save

from django.dispatch import receiver



class UserProfile(models.Model):

    """

    Расширение стандартной модели User для хранения персональных настроек:

    темы и языка (Требование).

    """

    THEME_CHOICES = (

        ('light', 'Светлая'),

        ('dark', 'Тёмная'),

    )

   

    LANGUAGE_CHOICES = (

        ('ru', 'Русский'),

        ('en', 'English'),

        ('kk', 'Қазақша'),

    )



    user = models.OneToOneField(User, on_delete=models.CASCADE)

   

    theme = models.CharField(

        max_length=5,

        choices=THEME_CHOICES,

        default='light',

        verbose_name='Цветовая тема'

    )

   

    language = models.CharField(

        max_length=2,

        choices=LANGUAGE_CHOICES,

        default='ru',

        verbose_name='Язык интерфейса'

    )



    def __str__(self):

        return f'Профиль {self.user.username}'



class LoginHistory(models.Model):

    """

    Модель для системы "Последних входов" (дата, время, IP-адрес) (Требование).

    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(default=timezone.now)

    ip_address = models.GenericIPAddressField(null=True, blank=True)



    class Meta:

        verbose_name_plural = "Login History"

        ordering = ['-timestamp']



    def __str__(self):

        return f'Вход {self.user.username} в {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'



# --- Сигналы для автоматизации ---



@receiver(post_save, sender=User)

def create_user_profile(sender, instance, created, **kwargs):

    """Создает UserProfile, когда создается новый User."""

    if created:

        UserProfile.objects.create(user=instance)

    try:

        instance.userprofile.save()

    except UserProfile.DoesNotExist:

        UserProfile.objects.create(user=instance)



@receiver(post_save, sender=LoginHistory)

def limit_login_history(sender, instance, **kwargs):

    """Ограничивает историю входов до 5 записей (Требование)."""

    history = LoginHistory.objects.filter(user=instance.user)

    if history.count() > 5:

        # Удаляем самые старые записи (начиная с 6-й)

        oldest_entries = history[5:]

        LoginHistory.objects.filter(pk__in=oldest_entries.values_list('pk', flat=True)).delete()