"""
Populate multimedia content database with real images and content
Run this script to add multimedia content to lessons
"""

from database import db

def populate_multimedia_content():
    """Add multimedia content to specific lessons"""
    
    # Phishing lesson multimedia (Course 1, Module 2, Lesson 1)
    db.add_multimedia_content(
        'image',
        'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&h=400&fit=crop',
        'Real phishing email example with red flags highlighted',
        1, 2, 1
    )
    
    # Password security lesson multimedia (Course 1, Module 1, Lesson 3)
    db.add_multimedia_content(
        'image',
        'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=600&h=300&fit=crop',
        'Password security visualization showing weak vs strong passwords',
        1, 1, 3
    )
    
    # Network security lesson multimedia (Course 2, Module 1, Lesson 1)
    db.add_multimedia_content(
        'image',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&h=400&fit=crop',
        'Network infrastructure and connectivity visualization',
        2, 1, 1
    )
    
    # Social engineering lesson multimedia (Course 1, Module 2, Lesson 2)
    db.add_multimedia_content(
        'image',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&h=400&fit=crop',
        'Social engineering attack visualization',
        1, 2, 2
    )
    
    # Add educational videos
    db.add_multimedia_content(
        'video',
        'https://www.youtube.com/watch?v=Z7Wl2FW2TcA',
        'What is Phishing? - Cybersecurity Explained',
        1, 2, 1
    )
    
    db.add_multimedia_content(
        'video',
        'https://www.youtube.com/watch?v=3NjQ9b3pgIg',
        'Password Security and Best Practices',
        1, 1, 3
    )
    
    print("✅ Multimedia content populated successfully!")
    print("📊 Added content to:")
    print("  • Phishing lessons with real email examples")
    print("  • Password security with strength visualizations")
    print("  • Network security with infrastructure diagrams")
    print("  • Social engineering with attack examples")
    print("  • Educational videos for key topics")

if __name__ == "__main__":
    populate_multimedia_content()