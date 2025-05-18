from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from PIL import Image
import os

# Create your models here.

def validate_image_size(image):
    """Validate that the image is not larger than 2MB"""
    file_size = image.size
    limit_mb = 2
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Image size cannot exceed {limit_mb}MB")

def validate_image_type(image):
    """Validate that the file is an accepted image type"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Only JPEG, PNG, and WebP files are supported")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(
        upload_to='profile_photos',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_type]
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Crop the image to 1:1 aspect ratio if a photo exists
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height != img.width:
                # Crop to square
                min_dimension = min(img.width, img.height)
                left = (img.width - min_dimension) / 2
                top = (img.height - min_dimension) / 2
                right = (img.width + min_dimension) / 2
                bottom = (img.height + min_dimension) / 2
                
                img = img.crop((left, top, right, bottom))
                img.save(self.photo.path)
