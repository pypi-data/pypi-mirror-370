"""
Generate funny random project names
"""

import random

ADJECTIVES = [
    "Bouncy", "Jazzy", "Sneaky", "Bubbly", "Quirky", "Zesty", "Fluffy", "Giggly",
    "Wobbly", "Sparkly", "Dizzy", "Sassy", "Cheeky", "Groovy", "Funky", "Zippy",
    "Jolly", "Peppy", "Silly", "Wacky", "Happy", "Wiggly", "Perky", "Goofy",
    "Bouncing", "Dancing", "Jumping", "Flying", "Spinning", "Rolling", "Sliding",
    "Cosmic", "Mystic", "Electric", "Neon", "Turbo", "Mega", "Ultra", "Super"
]

NOUNS = [
    "Penguin", "Unicorn", "Dragon", "Phoenix", "Llama", "Sloth", "Octopus", "Narwhal",
    "Platypus", "Koala", "Panda", "Otter", "Hedgehog", "Flamingo", "Peacock", "Dolphin",
    "Wizard", "Ninja", "Pirate", "Robot", "Alien", "Ghost", "Vampire", "Zombie",
    "Taco", "Pizza", "Donut", "Cookie", "Cupcake", "Waffle", "Burrito", "Sushi",
    "Rocket", "Comet", "Galaxy", "Nebula", "Asteroid", "Meteor", "Starship", "Satellite"
]

def generate_funny_project_name() -> str:
    """Generate a random funny project name"""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    number = random.randint(100, 999)
    return f"{adjective}-{noun}-{number}"

def generate_multiple_names(count: int = 5) -> list:
    """Generate multiple unique funny project names"""
    names = set()
    while len(names) < count:
        names.add(generate_funny_project_name())
    return list(names)
