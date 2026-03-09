"""
app/seed.py

Populates the database with sample recipes so that the application
starts with useful demo data.

This module is safe to call multiple times: it checks whether
any recipes already exist and skips seeding if they do.
"""

from app.models.database import SessionLocal
from app.models.recipe import Category
from app.services.recipe_service import RecipeService


# ---------------------------------------------------------------------------
# Sample recipe definitions
# ---------------------------------------------------------------------------

SEED_RECIPES: list[dict] = [
    {
        "title": "Classic Spaghetti Carbonara",
        "description": (
            "A rich and creamy Roman pasta dish made with eggs, "
            "Pecorino Romano, guanciale, and black pepper."
        ),
        "category": Category.DINNER,
        "servings": 4,
        "prep_time": 10,
        "cook_time": 20,
        "ingredients": [
            {"name": "Spaghetti",        "amount": 400,  "unit": "g"},
            {"name": "Guanciale",        "amount": 200,  "unit": "g"},
            {"name": "Egg yolks",        "amount": 4,    "unit": "pcs"},
            {"name": "Pecorino Romano",  "amount": 100,  "unit": "g"},
            {"name": "Black pepper",     "amount": 2,    "unit": "tsp"},
            {"name": "Salt",             "amount": 1,    "unit": "tsp"},
        ],
        "steps": [
            "Bring a large pot of salted water to a boil and cook the spaghetti "
            "until al dente according to the package instructions.",
            "Meanwhile, cut the guanciale into small cubes and fry in a dry pan "
            "over medium heat until crispy. Remove from heat.",
            "In a bowl, whisk together the egg yolks, grated Pecorino Romano, "
            "and plenty of freshly ground black pepper.",
            "Reserve one cup of pasta cooking water, then drain the spaghetti.",
            "Add the hot spaghetti to the pan with the guanciale. Remove from "
            "heat and pour in the egg mixture, tossing quickly and adding a "
            "splash of pasta water to create a creamy sauce.",
            "Serve immediately topped with extra Pecorino and black pepper.",
        ],
    },
    {
        "title": "Fluffy Blueberry Pancakes",
        "description": (
            "Light, golden pancakes packed with juicy blueberries — "
            "perfect for a lazy weekend breakfast."
        ),
        "category": Category.BREAKFAST,
        "servings": 3,
        "prep_time": 10,
        "cook_time": 15,
        "ingredients": [
            {"name": "All-purpose flour", "amount": 200, "unit": "g"},
            {"name": "Milk",              "amount": 250, "unit": "ml"},
            {"name": "Eggs",              "amount": 2,   "unit": "pcs"},
            {"name": "Baking powder",     "amount": 2,   "unit": "tsp"},
            {"name": "Sugar",             "amount": 30,  "unit": "g"},
            {"name": "Butter",            "amount": 30,  "unit": "g"},
            {"name": "Fresh blueberries", "amount": 150, "unit": "g"},
            {"name": "Vanilla extract",   "amount": 1,   "unit": "tsp"},
        ],
        "steps": [
            "Melt the butter and let it cool slightly.",
            "In a large bowl, whisk together the flour, sugar, and baking powder.",
            "In a separate bowl, beat the eggs with the milk, melted butter, "
            "and vanilla extract.",
            "Pour the wet ingredients into the dry ingredients and stir until "
            "just combined — a few lumps are fine, do not over-mix.",
            "Fold in the blueberries gently.",
            "Heat a non-stick pan over medium heat and lightly grease it. "
            "Pour roughly 80 ml of batter per pancake and cook until bubbles "
            "form on the surface, then flip and cook for one more minute.",
            "Serve warm with maple syrup and extra blueberries.",
        ],
    },
    {
        "title": "Avocado Toast with Poached Egg",
        "description": (
            "Creamy smashed avocado on toasted sourdough topped with "
            "a perfectly poached egg and chilli flakes."
        ),
        "category": Category.BREAKFAST,
        "servings": 2,
        "prep_time": 5,
        "cook_time": 10,
        "ingredients": [
            {"name": "Sourdough bread", "amount": 2,  "unit": "slices"},
            {"name": "Avocado",        "amount": 1,  "unit": "pcs"},
            {"name": "Eggs",           "amount": 2,  "unit": "pcs"},
            {"name": "Lemon juice",    "amount": 1,  "unit": "tbsp"},
            {"name": "Chilli flakes",  "amount": 0.5,"unit": "tsp"},
            {"name": "Salt",           "amount": 1,  "unit": "pinch"},
            {"name": "Olive oil",      "amount": 1,  "unit": "tbsp"},
        ],
        "steps": [
            "Toast the sourdough slices until golden and crispy.",
            "Halve and pit the avocado. Scoop the flesh into a bowl, add lemon "
            "juice and a pinch of salt, then roughly mash with a fork.",
            "Bring a small saucepan of water to a gentle simmer. Add a dash of "
            "vinegar. Crack each egg into a small cup and gently lower into the "
            "water. Poach for 3 minutes for a runny yolk.",
            "Spread the smashed avocado on the toast, drizzle with olive oil, "
            "top with the poached egg and sprinkle with chilli flakes.",
        ],
    },
    {
        "title": "Chocolate Lava Cake",
        "description": (
            "Individual warm chocolate cakes with a gooey molten centre — "
            "a classic dinner-party showstopper."
        ),
        "category": Category.DESSERT,
        "servings": 4,
        "prep_time": 15,
        "cook_time": 12,
        "ingredients": [
            {"name": "Dark chocolate (70%)", "amount": 200, "unit": "g"},
            {"name": "Butter",               "amount": 100, "unit": "g"},
            {"name": "Eggs",                 "amount": 4,   "unit": "pcs"},
            {"name": "Egg yolks",            "amount": 2,   "unit": "pcs"},
            {"name": "Caster sugar",         "amount": 80,  "unit": "g"},
            {"name": "Plain flour",          "amount": 40,  "unit": "g"},
            {"name": "Cocoa powder",         "amount": 1,   "unit": "tbsp"},
        ],
        "steps": [
            "Preheat your oven to 200 °C. Butter four ramekins and dust them "
            "with cocoa powder.",
            "Melt the chocolate and butter together in a heatproof bowl over "
            "simmering water (bain-marie), stirring until smooth. Let cool slightly.",
            "In a large bowl, whisk the eggs, egg yolks, and sugar until the "
            "mixture is pale and slightly thickened.",
            "Fold the chocolate mixture into the egg mixture, then sift in the "
            "flour and fold gently until just combined.",
            "Divide the batter evenly between the prepared ramekins.",
            "Bake for 10–12 minutes until the edges are set but the centre is "
            "still slightly wobbly.",
            "Run a knife around the edge and carefully invert onto serving plates. "
            "Serve immediately with a scoop of vanilla ice cream.",
        ],
    },
    {
        "title": "Greek Salad",
        "description": (
            "Fresh, vibrant salad with tomatoes, cucumber, olives, "
            "and creamy feta — ready in 10 minutes."
        ),
        "category": Category.LUNCH,
        "servings": 2,
        "prep_time": 10,
        "cook_time": 0,
        "ingredients": [
            {"name": "Cherry tomatoes",     "amount": 200, "unit": "g"},
            {"name": "Cucumber",            "amount": 1,   "unit": "pcs"},
            {"name": "Red onion",           "amount": 0.5, "unit": "pcs"},
            {"name": "Kalamata olives",     "amount": 80,  "unit": "g"},
            {"name": "Feta cheese",         "amount": 150, "unit": "g"},
            {"name": "Olive oil",           "amount": 3,   "unit": "tbsp"},
            {"name": "Red wine vinegar",    "amount": 1,   "unit": "tbsp"},
            {"name": "Dried oregano",       "amount": 1,   "unit": "tsp"},
        ],
        "steps": [
            "Halve the cherry tomatoes and slice the cucumber into half-moons. "
            "Thinly slice the red onion.",
            "Combine the tomatoes, cucumber, onion, and olives in a large bowl.",
            "Whisk together the olive oil, red wine vinegar, and oregano to make "
            "the dressing.",
            "Pour the dressing over the salad and toss gently.",
            "Top with a block or crumbled slices of feta cheese and serve immediately.",
        ],
    },
    {
        "title": "Mango Lassi",
        "description": (
            "A cool and creamy Indian yoghurt drink blended with "
            "ripe mango and a hint of cardamom."
        ),
        "category": Category.DRINK,
        "servings": 2,
        "prep_time": 5,
        "cook_time": 0,
        "ingredients": [
            {"name": "Ripe mango",    "amount": 1,   "unit": "pcs"},
            {"name": "Plain yoghurt", "amount": 250, "unit": "ml"},
            {"name": "Milk",          "amount": 100, "unit": "ml"},
            {"name": "Sugar",         "amount": 2,   "unit": "tbsp"},
            {"name": "Cardamom",      "amount": 0.25,"unit": "tsp"},
            {"name": "Ice cubes",     "amount": 4,   "unit": "pcs"},
        ],
        "steps": [
            "Peel the mango and cut the flesh away from the stone.",
            "Place the mango, yoghurt, milk, sugar, and cardamom in a blender.",
            "Add the ice cubes and blend on high until completely smooth.",
            "Taste and adjust sweetness if needed. Pour into tall glasses "
            "and serve immediately.",
        ],
    },
]


def seed_database() -> None:
    """
    Insert the sample recipes into the database if it is empty.

    This function is called once at application startup.
    It does nothing if the database already contains recipes.
    """
    with SessionLocal() as db:
        existing = RecipeService.get_all(db)
        if existing:
            return  # Already seeded — skip

        for recipe_data in SEED_RECIPES:
            RecipeService.create(
                db=db,
                title=recipe_data["title"],
                description=recipe_data["description"],
                category=recipe_data["category"],
                servings=recipe_data["servings"],
                prep_time=recipe_data["prep_time"],
                cook_time=recipe_data["cook_time"],
                ingredients=recipe_data["ingredients"],
                steps=recipe_data["steps"],
            )

    print(f"✅  Database seeded with {len(SEED_RECIPES)} sample recipes.")
