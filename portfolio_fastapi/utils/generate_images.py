from PIL import Image, ImageDraw, ImageFont
import os

def create_social_icon(text, color, size=(24, 24)):
    """Create a simple social media icon with text."""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    draw.ellipse([0, 0, size[0]-1, size[1]-1], fill=color)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text in white
    draw.text((x, y), text, fill='white', font=font)
    return img

def create_project_image(text, size=(400, 200)):
    """Create a placeholder project image."""
    img = Image.new('RGB', size, '#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline='#ddd')
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='#333', font=font)
    return img

def main():
    # Create static/images directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    os.makedirs(static_dir, exist_ok=True)
    
    # Generate social media icons
    social_icons = {
        'github.png': ('GH', '#333333'),
        'linkedin.png': ('LI', '#0077B5'),
        'twitter.png': ('T', '#1DA1F2')
    }
    
    for filename, (text, color) in social_icons.items():
        img = create_social_icon(text, color)
        img.save(os.path.join(static_dir, filename))
    
    # Generate project images
    project_images = {
        'project1.jpg': 'LLM Project',
        'project2.jpg': 'RAG System',
        'project3.jpg': 'Time Series'
    }
    
    for filename, text in project_images.items():
        img = create_project_image(text)
        img.save(os.path.join(static_dir, filename))
    
    # Generate profile and certification images
    profile_img = create_project_image('Profile Picture', (200, 200))
    profile_img.save(os.path.join(static_dir, 'profile.jpg'))
    
    for i in range(1, 4):
        cert_img = create_project_image(f'Certification {i}', (100, 100))
        cert_img.save(os.path.join(static_dir, f'cert{i}.png'))

if __name__ == '__main__':
    main() 