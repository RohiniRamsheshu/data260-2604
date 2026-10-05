import json
import logging
import urllib.parse
import urllib.request

from mcp.server.fastmcp import FastMCP


logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

mcp = FastMCP("meals")


def call_mealdb(endpoint: str, params: dict | None = None):
    query_string = ""

    if params:
        query_string = "?" + urllib.parse.urlencode(params)

    url = f"{BASE_URL}/{endpoint}{query_string}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.load(response)
    except Exception as error:
        raise RuntimeError(f"TheMealDB request failed: {error}")


def meal_card(meal: dict) -> dict:
    return {
        "id": meal.get("idMeal"),
        "name": meal.get("strMeal"),
        "area": meal.get("strArea"),
        "category": meal.get("strCategory"),
        "thumb": meal.get("strMealThumb"),
    }


def full_meal(meal: dict) -> dict:
    ingredients = []

    for index in range(1, 21):
        name = (meal.get(f"strIngredient{index}") or "").strip()
        measure = (meal.get(f"strMeasure{index}") or "").strip()

        if name:
            ingredients.append({
                "name": name,
                "measure": measure,
            })

    return {
        "id": meal.get("idMeal"),
        "name": meal.get("strMeal"),
        "category": meal.get("strCategory"),
        "area": meal.get("strArea"),
        "instructions": meal.get("strInstructions"),
        "image": meal.get("strMealThumb"),
        "source": meal.get("strSource"),
        "youtube": meal.get("strYoutube"),
        "ingredients": ingredients,
    }


@mcp.tool()
def search_meals_by_name(query: str, limit: int = 5) -> list[dict]:
    """Search meals by name."""
    if not 1 <= limit <= 25:
        raise ValueError("limit must be between 1 and 25")

    response = call_mealdb(
        "search.php",
        {"s": query}
    )

    meals = response.get("meals") or []

    return [
        meal_card(meal)
        for meal in meals[:limit]
    ]


@mcp.tool()
def meals_by_ingredient(
    ingredient: str,
    limit: int = 12
) -> list[dict]:
    """Find meals that use an ingredient."""
    if not 1 <= limit <= 25:
        raise ValueError("limit must be between 1 and 25")

    response = call_mealdb(
        "filter.php",
        {"i": ingredient}
    )

    meals = response.get("meals") or []

    return [
        {
            "id": meal.get("idMeal"),
            "name": meal.get("strMeal"),
            "thumb": meal.get("strMealThumb"),
        }
        for meal in meals[:limit]
    ]


@mcp.tool()
def meal_details(id: str | int) -> dict:
    """Return full details for one meal."""
    response = call_mealdb(
        "lookup.php",
        {"i": str(id)}
    )

    meals = response.get("meals") or []

    if not meals:
        return {"message": "no matches"}

    return full_meal(meals[0])


@mcp.tool()
def random_meal() -> dict:
    """Return one random meal."""
    response = call_mealdb("random.php")

    meals = response.get("meals") or []

    if not meals:
        return {"message": "no matches"}

    return full_meal(meals[0])


if __name__ == "__main__":
    mcp.run(transport="stdio")