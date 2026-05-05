import cloudinary
import cloudinary.uploader

from config import Config
from src.utils.constants import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE_MB, CLOUDINARY_PROFILE_FOLDER, CLOUDINARY_BLOG_FOLDER

# Configure Cloudinary once at module level 
cloudinary.config(
    cloud_name = Config.CLOUDINARY_CLOUD_NAME,
    api_key    = Config.CLOUDINARY_API_KEY,
    api_secret = Config.CLOUDINARY_API_SECRET,
    secure     = True    # always use https — never http
)


# URL builder 

def build_image_url(public_id, transformation=""):
    base = (
        f"https://res.cloudinary.com/"
        f"{Config.CLOUDINARY_CLOUD_NAME}/image/upload"
    )

    if transformation:
        return f"{base}/{transformation}/{public_id}"

    return f"{base}/{public_id}"


# Internal validator 

def _validate_image(file):
    if not file:
        return False, "No image file provided."

    # MIME type check
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return False, (
            "Invalid file type. "
            "Please upload a JPEG, PNG, WEBP, or GIF image."
        )

    # File size check 
    file.seek(0, 2)
    file_size_mb = file.tell() / (1024 * 1024)
    file.seek(0)

    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return False, (
            f"Image size {file_size_mb:.1f}MB exceeds the "
            f"{MAX_IMAGE_SIZE_MB}MB limit."
        )

    return True, None


# Profile image 

def upload_profile_image(file, user_id):
    is_valid, error = _validate_image(file)
    if not is_valid:
        return False, error

    try:
        result = cloudinary.uploader.upload(
            file,
            folder        = CLOUDINARY_PROFILE_FOLDER,
            public_id     = f"user_{user_id}",
            overwrite     = True,
            resource_type = "image",
        )

        return True, result["public_id"]

    except cloudinary.exceptions.Error as e:
        print(f"[CLOUDINARY ERROR - PROFILE] {str(e)}")
        return False, "Image upload failed. Please try again."

    except Exception as e:
        print(f"[CLOUDINARY ERROR - UNKNOWN] {str(e)}")
        return False, "Unexpected error during upload. Please try again."


# Blog image 

def upload_blog_image(file, user_id, image_index):
    import time

    is_valid, error = _validate_image(file)
    if not is_valid:
        return False, error

    try:
        public_id = f"blog_{user_id}_{int(time.time())}_{image_index}"

        result = cloudinary.uploader.upload(
            file,
            folder        = CLOUDINARY_BLOG_FOLDER,
            public_id     = public_id,
            overwrite     = False,
            resource_type = "image",
        )

        return True, result["public_id"]

    except cloudinary.exceptions.Error as e:
        print(f"[CLOUDINARY ERROR - BLOG] {str(e)}")
        return False, "Blog image upload failed. Please try again."

    except Exception as e:
        print(f"[CLOUDINARY ERROR - UNKNOWN] {str(e)}")
        return False, "Unexpected error during upload. Please try again."


# Delete image 

def delete_image(public_id):
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"

    except Exception as e:
        print(f"[CLOUDINARY ERROR - DELETE] {public_id}: {str(e)}")
        return False