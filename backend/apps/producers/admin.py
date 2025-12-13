from django.contrib import admin
from .models import ProducerProfile, ProducerPhoto


class ProducerPhotoInline(admin.TabularInline):
    model = ProducerPhoto
    extra = 1


@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'address', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'address', 'user__email')
    inlines = [ProducerPhotoInline]


@admin.register(ProducerPhoto)
class ProducerPhotoAdmin(admin.ModelAdmin):
    list_display = ('producer', 'image_file', 'created_at')
    list_filter = ('created_at',)

