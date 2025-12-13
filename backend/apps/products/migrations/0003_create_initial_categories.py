# Generated manually
from django.db import migrations


def create_initial_categories(apps, schema_editor):
    ProductCategory = apps.get_model('products', 'ProductCategory')
    
    categories = [
        {'name': 'legumes', 'icon': 'carrot', 'display_name': 'Légumes', 'order': 1},
        {'name': 'fruits', 'icon': 'apple', 'display_name': 'Fruits', 'order': 2},
        {'name': 'cereales', 'icon': 'wheat', 'display_name': 'Céréales', 'order': 3},
        {'name': 'pain', 'icon': 'bread', 'display_name': 'Pain', 'order': 4},
        {'name': 'miel', 'icon': 'honey', 'display_name': 'Miel', 'order': 5},
        {'name': 'viande', 'icon': 'meat', 'display_name': 'Viande', 'order': 6},
        {'name': 'biere', 'icon': 'beer', 'display_name': 'Bière', 'order': 7},
        {'name': 'autre', 'icon': 'package', 'display_name': 'Autre', 'order': 99},
    ]
    
    for cat_data in categories:
        ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'icon': cat_data['icon'],
                'display_name': cat_data['display_name'],
                'order': cat_data['order']
            }
        )


def reverse_create_categories(apps, schema_editor):
    ProductCategory = apps.get_model('products', 'ProductCategory')
    ProductCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_add_category_and_photos'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, reverse_create_categories),
    ]


