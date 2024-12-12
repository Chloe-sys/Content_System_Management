import os
import django

# Setup Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()

from content_system.models import Post

# Delete all records from the Post model (use with caution)
deleted_count, _ = Post.objects.all().delete()

# Output the number of deleted records
print(f"Successfully deleted {deleted_count} records from the database.")
