# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Nom de la catégorie')),
                ('icon', models.CharField(help_text="Nom de l'icône (ex: carrot, apple, wheat, etc.)", max_length=100, verbose_name='Icône')),
                ('display_name', models.CharField(max_length=100, verbose_name="Nom d'affichage")),
                ('order', models.IntegerField(default=0, verbose_name='Ordre d\'affichage')),
            ],
            options={
                'verbose_name': 'Catégorie de produit',
                'verbose_name_plural': 'Catégories de produits',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ProductPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_file', models.ImageField(upload_to='products/', verbose_name='Photo')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='products.product', db_index=True)),
            ],
            options={
                'verbose_name': 'Photo de produit',
                'verbose_name_plural': 'Photos de produits',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.productcategory', verbose_name='Catégorie', db_index=True),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'created_at'], name='products_pr_category_created_idx'),
        ),
    ]


