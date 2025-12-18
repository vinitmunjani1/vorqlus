"""
Utility functions for the chatbot application.
"""

# Category keywords mapping for automatic role categorization
CATEGORIES = {
    "Health & Fitness": ["diet", "fitness", "health", "nutrition", "exercise", "sleep", "wellness", 
                         "workout", "meal", "recipe", "meal prep", "health tracker", "fitness tracker",
                         "fitness goal", "sleep tracker", "sleep coach", "sleep therapy", "sleep habit"],
    "Finance": ["financial", "tax", "investment", "budget", "debt", "money", "finance", "saving", 
                "spending", "personal finance", "household budget", "debt management", "debt repayment",
                "debt consolidation", "coupon", "smart shopping"],
    "Travel": ["travel", "holiday", "trip", "vacation", "packing", "destination", "travel guide",
               "travel safety", "travel budgeting"],
    "Productivity": ["productivity", "time management", "task", "schedule", "organization", "efficiency",
                     "personal assistant", "virtual personal assistant", "productivity assistant",
                     "home organization"],
    "Lifestyle": ["fashion", "shopping", "home", "decor", "style", "personal shopper", "interior",
                  "fashion stylist", "virtual fashion", "home decor", "home improvement", 
                  "home cleaning", "gift finder"],
    "Career": ["career", "job", "resume", "interview", "business", "sales", "professional",
               "career coach", "job search", "job interview", "resume builder", "business strategy",
               "sales coach", "public relations"],
    "Education": ["study", "learning", "language", "college", "school", "education", "homework",
                  "study buddy", "college advisor", "parent-teacher", "memory", "memory training",
                  "memory improvement"],
    "Relationships": ["relationship", "dating", "social", "etiquette", "compatibility", "love",
                      "relationship advisor", "relationship compatibility", "social etiquette",
                      "ai love matchmaker", "conflict resolution"],
    "Personal Development": ["life coach", "confidence", "growth", "mindfulness", "meditation",
                             "self-care", "mental health", "mental wellness", "personal growth",
                             "confidence coach", "mindfulness", "meditation guide", "stress management",
                             "self-care advisor", "spiritual guidance"],
    "Creative": ["writing", "speech", "content", "social media", "public speaking", "speech writing",
                 "speech therapist", "voice coach", "public speaking coach", "social media manager"],
    "Parenting & Family": ["parenting", "parent", "children", "child"],
    "Events & Planning": ["event", "wedding", "party", "event planner", "wedding planner", "event budgeting"],
    "Other": []  # Default category for roles that don't match any keywords
}


def categorize_role(role_name, short_description="", long_description=""):
    """
    Automatically categorize an AI role based on keywords in its name and descriptions.
    
    Args:
        role_name (str): The name of the AI role
        short_description (str): Short description of the role
        long_description (str): Long description of the role
        
    Returns:
        str: The category name the role belongs to
    """
    # Combine all text for keyword matching (case-insensitive)
    search_text = f"{role_name} {short_description} {long_description}".lower()
    
    # Check each category for matching keywords
    # Priority order matters - check more specific categories first
    for category, keywords in CATEGORIES.items():
        if category == "Other":
            continue  # Skip "Other" - it's the default
        
        for keyword in keywords:
            if keyword.lower() in search_text:
                return category
    
    # If no match found, return "Other"
    return "Other"


def get_all_categories():
    """
    Get a list of all categories (excluding "Other").
    
    Returns:
        list: List of category names
    """
    return [cat for cat in CATEGORIES.keys() if cat != "Other"]


# Icon mapping for AI roles - maps role names to Bootstrap Icons
ROLE_ICONS = {
    # Health & Fitness
    "Diet Planner AI": "bi-egg-fried",
    "Fitness Coach AI": "bi-activity",
    "Health Tracker AI": "bi-heart-pulse",
    "Fitness Tracker AI": "bi-speedometer2",
    "Fitness Goal Tracker AI": "bi-trophy",
    "Sleep Coach AI": "bi-moon-stars",
    "Sleep Tracker AI": "bi-moon",
    "Sleep Therapy AI": "bi-cloud-moon",
    "Sleep Habit Tracker AI": "bi-clock-history",
    "Exercise Routine AI": "bi-barbell",
    "Meal Prep Assistant AI": "bi-basket",
    "Meal Planner AI": "bi-calendar-check",
    "Recipe Assistant AI": "bi-book",
    "Nutritionist AI": "bi-apple",
    "Healthy Habit Coach AI": "bi-heart",
    "Health Motivation AI": "bi-lightning-charge",
    "Cooking Tutor AI": "bi-egg",
    
    # Finance
    "Financial Advisor AI": "bi-cash-stack",
    "Tax Assistant AI": "bi-receipt",
    "Investment Advisor AI": "bi-graph-up-arrow",
    "Debt Management AI": "bi-credit-card",
    "Debt Repayment AI": "bi-wallet2",
    "Debt Consolidation AI": "bi-wallet",
    "Personal Finance Tracker AI": "bi-piggy-bank",
    "Household Budgeting AI": "bi-calculator",
    "AI Budgeting Assistant": "bi-cash-coin",
    "Coupon Finder AI": "bi-tag",
    "Smart Shopping Assistant AI": "bi-cart-check",
    
    # Travel
    "Travel Guide AI": "bi-geo-alt",
    "Holiday Planner AI": "bi-airplane",
    "Travel Packing Assistant AI": "bi-suitcase",
    "Travel Safety AI": "bi-shield-check",
    "Travel Budgeting AI": "bi-map",
    
    # Productivity
    "Time Management Assistant AI": "bi-clock",
    "Productivity Coach AI": "bi-rocket-takeoff",
    "Productivity Assistant AI": "bi-check2-square",
    "Personal Assistant AI": "bi-calendar-event",
    "Virtual Personal Assistant AI": "bi-person-badge",
    "Home Organization AI": "bi-folder-symlink",
    
    # Lifestyle
    "Fashion Stylist AI": "bi-bag",
    "Virtual Fashion Consultant AI": "bi-handbag",
    "Virtual Personal Stylist AI": "bi-star",
    "Personal Shopper AI": "bi-cart",
    "Home Decor Advisor AI": "bi-house-door",
    "Interior Designer AI": "bi-house-heart",
    "Home Improvement AI": "bi-tools",
    "Home Cleaning Assistant AI": "bi-broom",
    "Gift Finder AI": "bi-gift",
    
    # Career
    "Career Coach AI": "bi-briefcase",
    "Job Search Assistant AI": "bi-search",
    "Resume Builder AI": "bi-file-earmark-text",
    "Job Interview Coach AI": "bi-people",
    "Business Strategy Advisor AI": "bi-diagram-3",
    "Sales Coach AI": "bi-graph-up",
    "Public Relations Advisor AI": "bi-megaphone",
    "Customer Support AI": "bi-headset",
    "Customer Feedback AI": "bi-chat-left-text",
    
    # Education
    "Study Buddy AI": "bi-book-half",
    "Language Learning AI": "bi-translate",
    "College Advisor AI": "bi-mortarboard",
    "Parent-Teacher AI": "bi-backpack",
    "Memory Improvement AI": "bi-brain",
    "Memory Training AI": "bi-lightbulb",
    
    # Relationships
    "Relationship Advisor AI": "bi-heart-fill",
    "Relationship Compatibility AI": "bi-hearts",
    "Social Etiquette Advisor AI": "bi-person-check",
    "AI Love Matchmaker": "bi-arrow-through-heart",
    "Conflict Resolution AI": "bi-handshake",
    
    # Personal Development
    "Life Coach AI": "bi-compass",
    "Confidence Coach AI": "bi-star-fill",
    "Personal Growth AI": "bi-flower1",
    "Mindfulness AI": "bi-flower2",
    "Meditation Guide AI": "bi-circle",
    "Stress Management AI": "bi-cloud-rain",
    "Self-Care Advisor AI": "bi-spa",
    "Mental Health Assistant AI": "bi-emoji-smile",
    "Mental Wellness AI": "bi-sun",
    "Spiritual Guidance AI": "bi-stars",
    
    # Creative
    "Public Speaking Coach AI": "bi-mic",
    "Speech Writing AI": "bi-pencil-square",
    "Speech Therapist AI": "bi-chat-dots",
    "Voice Coach AI": "bi-soundwave",
    "Social Media Manager AI": "bi-instagram",
    
    # Parenting & Family
    "Parenting Advisor AI": "bi-people-fill",
    "Pet Care Advisor AI": "bi-heart-pulse-fill",
    
    # Events & Planning
    "Event Planner AI": "bi-calendar-event",
    "Wedding Planner AI": "bi-heart",
    "Event Budgeting AI": "bi-calculator",
    
    # Other
    "Legal Advisor AI": "bi-scale",
    "Real Estate Advisor AI": "bi-building",
    "Gardening Assistant AI": "bi-flower3",
    "Personalized News AI": "bi-newspaper",
    "Crisis Management AI": "bi-exclamation-triangle",
    "Personal Security AI": "bi-shield-lock",
    "Hobby Exploration AI": "bi-palette",
    "Food Waste Reduction AI": "bi-recycle",
    "Sustainability Advisor AI": "bi-tree",
    "Grocery List Assistant AI": "bi-list-check",
}


def get_role_icon(role_name):
    """
    Get the appropriate Bootstrap Icon class for an AI role.
    
    Args:
        role_name (str): The name of the AI role
        
    Returns:
        str: Bootstrap Icon class name (e.g., "bi-heart-pulse")
    """
    # Direct match first
    if role_name in ROLE_ICONS:
        return ROLE_ICONS[role_name]
    
    # Fallback: try partial matching for similar roles
    role_lower = role_name.lower()
    
    # Health & Fitness icons
    if "diet" in role_lower or "meal" in role_lower or "nutrition" in role_lower:
        return "bi-apple"
    if "fitness" in role_lower or "exercise" in role_lower or "workout" in role_lower:
        return "bi-activity"
    if "sleep" in role_lower:
        return "bi-moon-stars"
    if "health" in role_lower:
        return "bi-heart-pulse"
    
    # Finance icons
    if "financial" in role_lower or "finance" in role_lower or "budget" in role_lower:
        return "bi-cash-stack"
    if "tax" in role_lower:
        return "bi-receipt"
    if "investment" in role_lower:
        return "bi-graph-up-arrow"
    if "debt" in role_lower:
        return "bi-credit-card"
    if "coupon" in role_lower or "shopping" in role_lower:
        return "bi-tag"
    
    # Travel icons
    if "travel" in role_lower or "holiday" in role_lower or "trip" in role_lower:
        return "bi-airplane"
    if "packing" in role_lower:
        return "bi-suitcase"
    
    # Productivity icons
    if "productivity" in role_lower or "time management" in role_lower:
        return "bi-clock"
    if "assistant" in role_lower and "personal" in role_lower:
        return "bi-person-badge"
    if "organization" in role_lower:
        return "bi-folder-symlink"
    
    # Lifestyle icons
    if "fashion" in role_lower or "stylist" in role_lower:
        return "bi-bag"
    if "home" in role_lower or "decor" in role_lower or "interior" in role_lower:
        return "bi-house-door"
    if "shopping" in role_lower or "shopper" in role_lower:
        return "bi-cart"
    if "gift" in role_lower:
        return "bi-gift"
    
    # Career icons
    if "career" in role_lower or "job" in role_lower:
        return "bi-briefcase"
    if "resume" in role_lower:
        return "bi-file-earmark-text"
    if "interview" in role_lower:
        return "bi-people"
    if "business" in role_lower:
        return "bi-diagram-3"
    if "sales" in role_lower:
        return "bi-graph-up"
    
    # Education icons
    if "study" in role_lower or "learning" in role_lower or "education" in role_lower:
        return "bi-book-half"
    if "language" in role_lower:
        return "bi-translate"
    if "college" in role_lower or "school" in role_lower:
        return "bi-mortarboard"
    if "memory" in role_lower:
        return "bi-brain"
    
    # Relationships icons
    if "relationship" in role_lower or "dating" in role_lower or "love" in role_lower:
        return "bi-heart-fill"
    if "social" in role_lower or "etiquette" in role_lower:
        return "bi-person-check"
    
    # Personal Development icons
    if "life coach" in role_lower or "coach" in role_lower:
        return "bi-compass"
    if "confidence" in role_lower:
        return "bi-star-fill"
    if "mindfulness" in role_lower or "meditation" in role_lower:
        return "bi-circle"
    if "stress" in role_lower:
        return "bi-cloud-rain"
    if "mental" in role_lower:
        return "bi-emoji-smile"
    
    # Creative icons
    if "speech" in role_lower or "speaking" in role_lower or "voice" in role_lower:
        return "bi-mic"
    if "writing" in role_lower:
        return "bi-pencil-square"
    if "social media" in role_lower:
        return "bi-instagram"
    
    # Parenting icons
    if "parent" in role_lower:
        return "bi-people-fill"
    if "pet" in role_lower:
        return "bi-heart-pulse-fill"
    
    # Events icons
    if "event" in role_lower or "wedding" in role_lower:
        return "bi-calendar-event"
    
    # Default icon
    return "bi-robot"

