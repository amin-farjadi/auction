# Generated by Django 3.0.3 on 2020-10-16 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_comment_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='listing',
            new_name='listings',
        ),
        migrations.AlterField(
            model_name='category',
            name='category',
            field=models.CharField(choices=[('Electronics', 'Electronics'), ('Toys', 'Toys'), ('Fashion', 'Fashion')], max_length=50),
        ),
    ]
