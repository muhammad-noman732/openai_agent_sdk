from dataclasses import dataclass
from typing import ClassVar

@dataclass
class American:
    """
    A dataclass to represent an American person.
    Demonstrates:
    - Class variables (shared by all Americans)
    - Instance variables (unique per person)
    - Instance methods (work with self)
    - Class methods (work with class-level data)
    """

    # ---------------- CLASS VARIABLES ----------------
    # ClassVar tells dataclass: "this is NOT an instance field"
    # These belong to the CLASS, shared across all instances
    national_language: ClassVar[str] = "English"
    national_food: ClassVar[str] = "Hamburger"

    # ---------------- INSTANCE VARIABLES ----------------
    # These belong to each INSTANCE (person), unique for each
    name: str
    age: int
    weight: float

    # ---------------- INSTANCE METHOD ----------------
    # Instance methods always take 'self' (the current object).
    # Use 'self' to access instance variables.
    def get_user_detail(self):
        return f"{self.name} is {self.age} years old and weighs {self.weight} kg."

    # ---------------- CLASS METHOD ----------------
    # Class methods always take 'cls' (the class itself).
    # Use 'cls' to access class variables or construct objects.
    @classmethod
    def american_language(cls):
        return f"The national language of Americans is {cls.national_language}."

    @classmethod
    def american_food(cls):
        return f"The national food of Americans is {cls.national_food}."
    

       # Special method to make instances callable
    def __call__(self):
        return f"Hello, I am {self.name} and I can be called like a function!"


# ---------------- USAGE ----------------

# ✅ Instantiation: creating objects (instances)
noman = American("Noman", 22, 67)
john = American("John", 30, 80)
print(john())  # for this user dunder (magic functions)
# ✅ Instance variables: different per object
print(noman.get_user_detail())   # Noman is 22 years old and weighs 67 kg.
print(john.get_user_detail())    # John is 30 years old and weighs 80 kg.

# ✅ Class variables: shared by all Americans
print(American.national_language)  # English
print(American.national_food)      # Hamburger

# ✅ Access class variables via instances (not recommended, but possible)
print(noman.national_language)  # English
print(john.national_food)       # Hamburger

# ✅ Class methods: called on class (or instance, but better on class)
print(American.american_language())  # The national language of Americans is English.
print(American.american_food())      # The national food of Americans is Hamburger
