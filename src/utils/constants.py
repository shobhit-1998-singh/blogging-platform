
# ── Interests / Blog Tags
# Used in: UserProfileAction, BlogCreateAction, FeedAction

ALLOWED_INTERESTS = [
    "tech",
    "science",
    "backend",
    "frontend",
    "system-design",
    "dsa",
    "ai-ml",
    "devops",
    "database",
    "mobile",
    "cybersecurity",
    "open-source",
    "career",
    "productivity",
    "programming",
    "cloud",
]

# Interest constraints 
MIN_INTERESTS = 1
MAX_INTERESTS = 5  

# Blog tag constraints 
MAX_BLOG_TAGS = 4 

# Image constraints
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
]
MAX_IMAGE_SIZE_MB = 10   
MAX_BLOG_IMAGES = 3 

# Social link prefixes 

SOCIAL_LINK_PREFIXES = {
    "github": "https://github.com/",
    "linkedin": "https://www.linkedin.com/in/",
    "leetcode": "https://leetcode.com/",
    "x": "https://x.com/",
}

# Cloudinary folder structure 
CLOUDINARY_PROFILE_FOLDER = "blogging_platform/profiles"
CLOUDINARY_BLOG_FOLDER = "blogging_platform/blogs"