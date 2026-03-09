# 🍽️ CookBook — OOP Web Application

> **BSc WI — Objektorientierte Programmierung 1 · Group Project 2026**

A browser-based recipe management application built with **NiceGUI**, **SQLAlchemy** (ORM), and **SQLite**. Users can browse recipes, view step-by-step instructions, leave star ratings, add their own recipes, and generate aggregated shopping lists.

---

## 📸 Screenshots

| Home — Recipe Grid | Recipe Detail |
|---|---|
| ![Home page](https://github.com/user-attachments/assets/281d2005-b968-467a-87c5-41a545552c49) | ![Recipe detail](https://github.com/user-attachments/assets/125da58d-fb27-4db6-abb8-90de3d56c0fc) |

| Add Recipe Form | Shopping List Generator |
|---|---|
| *(form with dynamic ingredient & step rows)* | ![Shopping list](https://github.com/user-attachments/assets/f15cb746-99a1-4b75-b174-a9faf57e0cbf) |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Search** | Live search by recipe title or description |
| 🏷️ **Category filter** | Filter by Breakfast, Lunch, Dinner, Dessert, Snack, or Drink |
| 📋 **Recipe cards** | See category badge, average star rating, and total time at a glance |
| 🍳 **Recipe detail** | Full ingredients list + numbered step-by-step instructions |
| ⭐ **Star ratings** | Submit a 1–5 star review with an optional comment |
| ➕ **Add recipe** | Dynamic form — add/remove ingredient rows and instruction steps |
| 🛒 **Shopping list** | Select multiple recipes; ingredients are aggregated by name + unit |
| 🗑️ **Delete recipe** | Remove a recipe and all its related data |

---

## 🏗️ Architecture

The application follows the three-layer architecture required by the module:

```
┌────────────────────────────────────────────────────┐
│  Presentation Layer (Thin Client)                  │
│  Browser — renders Vue.js / Quasar components      │
└──────────────────────┬─────────────────────────────┘
                       │  WebSocket (NiceGUI)
┌──────────────────────▼─────────────────────────────┐
│  Application Logic (Server-side Frontend)          │
│  NiceGUI pages + Python OOP service classes        │
│  app/views/   <->   app/services/                  │
└──────────────────────┬─────────────────────────────┘
                       │  SQLAlchemy ORM
┌──────────────────────▼─────────────────────────────┐
│  Persistence Layer                                 │
│  SQLite database  ·  app/models/                   │
└────────────────────────────────────────────────────┘
```

### Project structure

```
Advanced-Programming/
├── main.py                  # Entry point – starts NiceGUI server
├── requirements.txt         # Python dependencies
├── app/
│   ├── models/
│   │   ├── database.py      # SQLAlchemy engine, session factory, Base
│   │   ├── recipe.py        # Recipe model + Category enum
│   │   ├── ingredient.py    # Ingredient model (belongs to Recipe)
│   │   ├── step.py          # Step model (ordered instructions)
│   │   └── rating.py        # Rating model (1–5 stars + comment)
│   ├── services/
│   │   ├── recipe_service.py  # CRUD + search for recipes
│   │   └── rating_service.py  # Submit + read ratings
│   ├── views/
│   │   ├── shared.py          # Reusable: header/footer, star display
│   │   ├── home.py            # "/" — recipe grid with search & filter
│   │   ├── recipe_detail.py   # "/recipe/{id}" — full recipe view
│   │   ├── add_recipe.py      # "/add" — dynamic add-recipe form
│   │   └── shopping_list.py   # "/shopping" — ingredient aggregator
│   └── seed.py              # Sample recipes inserted on first run
└── readme.md
```

---

## 🗄️ Data Model

```
Recipe
  ├── id, title, description, category, servings
  ├── prep_time, cook_time, created_at
  ├── ── Ingredient (name, amount, unit)   [1 → *]
  ├── ── Step       (number, description) [1 → *]
  └── ── Rating     (score 1–5, comment)  [1 → *]
```

All relationships use **cascade delete**: removing a recipe automatically removes all its ingredients, steps, and ratings.

---

## 📚 Libraries Used

| Library | Version | Purpose |
|---|---|---|
| [NiceGUI](https://nicegui.io/) | >= 2.0 | Browser-based UI built in pure Python (Vue.js + Quasar under the hood) |
| [SQLAlchemy](https://www.sqlalchemy.org/) | >= 2.0 | ORM — no raw SQL; all queries go through Python model classes |
| SQLite (stdlib) | — | Embedded database; no external server required |

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python main.py
```

The server starts at **http://localhost:8080**.
On the first run the database is created and seeded with **6 sample recipes** automatically.

---

## 👤 User Stories

| ID | As a … | I want to … | So that … |
|---|---|---|---|
| US-1 | visitor | browse all recipes on the home page | I can find inspiration quickly |
| US-2 | visitor | filter recipes by category | I only see recipes relevant to the meal I'm planning |
| US-3 | visitor | search recipes by keyword | I can find a specific recipe without scrolling |
| US-4 | visitor | click a recipe card to see full details | I know exactly what ingredients and steps are needed |
| US-5 | visitor | submit a star rating and comment | I can share feedback with other users |
| US-6 | cook | add a new recipe via a form | I can contribute my own recipes to the collection |
| US-7 | cook | dynamically add/remove ingredient rows | I have full flexibility without reloading the page |
| US-8 | cook | select multiple recipes and generate a shopping list | I can do one combined grocery run |
| US-9 | admin | delete a recipe | I can remove incorrect or duplicate entries |

---

## 📐 Use Cases

### UC-1: Browse & Filter Recipes
- **Actor**: Visitor
- **Precondition**: Application is running; recipes exist in the database
- **Flow**: Open `/` → optionally type in search box → click a category chip → recipe grid updates live
- **Outcome**: User sees a filtered set of recipe cards

### UC-2: View Recipe Detail
- **Actor**: Visitor
- **Flow**: Click any recipe card → `/recipe/{id}` renders ingredients, steps, and all ratings
- **Outcome**: User has all information needed to cook the dish

### UC-3: Submit a Rating
- **Actor**: Visitor
- **Flow**: On the detail page → click stars → optionally type a comment → click "Submit Rating"
- **Outcome**: Rating saved; average score updates immediately

### UC-4: Add a New Recipe
- **Actor**: Cook
- **Flow**: Click "Add Recipe" in the nav → fill in title / description / category / times → add ingredients and steps → click "Save Recipe"
- **Outcome**: New recipe appears in the home grid

### UC-5: Generate a Shopping List
- **Actor**: Cook
- **Flow**: Navigate to `/shopping` → check one or more recipes → click "Generate List"
- **Outcome**: All ingredients are combined (same name + unit are summed), displayed as a printable list

---

## 👥 Team & Work Distribution

| Member | Responsibility |
|---|---|
| Member 1 | Data models (`app/models/`), database setup, seed data |
| Member 2 | Service layer (`app/services/`), business logic, validation |
| Member 3 | NiceGUI views (`app/views/`), UI design, README |

> Every member commits independently to this repository. GitHub commit history reflects the individual contributions.

---

## 🗓️ Milestones

| Milestone | Target | Status |
|---|---|---|
| Project setup & data models | Week 3 | ✅ |
| Service layer & CRUD operations | Week 5 | ✅ |
| NiceGUI views (home, detail, add) | Week 8 | ✅ |
| Shopping list & ratings | Week 10 | ✅ |
| Final polish & README | Week 12 | ✅ |
| Presentation | Last week | 🔜 |
