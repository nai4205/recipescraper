import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkinter import *

class RecipeScraper:
    def __init__(self, url):
        self.url = url
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.results = self.soup.find(class_="layout-md-rail__primary")  # List of all recipes
        self.recipe_elements = self.results.find_all("div", class_="card__section card__content")  # Content of individual recipe (just preview)

    def get_recipe_links(self):
        links_list = []
        for recipe_element in self.recipe_elements:
            links = recipe_element.find_all("a")
            for link in links:
                link_url = link["href"]
                links_list.append(link_url)
        links_list.pop(0)
        return links_list

    def get_matching_ingredient_count(self, ingredients, search_terms):
        count = 0
        for term in search_terms:
            for ingredient in ingredients:
                if term.lower() in ingredient.lower():
                    count += 1
        return count

    def get_ingredients_with_search(self, search_terms):
        recipe_info = []  # List to store recipe information tuples
        for link in self.get_recipe_links():
            #GET INGREDIENTS
            recipe_page = requests.get("https://www.bbcgoodfood.com" + link)
            new_soup = BeautifulSoup(recipe_page.content, "html.parser")
            recipe_name = new_soup.find("h1").text.strip()
            ingredients_and_recipe_section = new_soup.find("div", class_="row recipe__instructions")
            ingredients_section = ingredients_and_recipe_section.find(class_="recipe__ingredients col-12 mt-md col-lg-6")
            ingredients_list = ingredients_section.find_all("li")
            ingredients = [ingredient.get_text() for ingredient in ingredients_list]

            #GET METHOD
            method_section = ingredients_and_recipe_section.find(class_="recipe__method-steps mb-lg col-12 col-lg-6")
            method_list = method_section.find_all("li")
            method = [method.get_text() for method in method_list]

            matching_count = self.get_matching_ingredient_count(ingredients, search_terms)
            matching_terms = [term for term in search_terms if any(term.lower() in ingredient.lower() for ingredient in ingredients)]

            if matching_count > 0:
                recipe_info.append((recipe_name, matching_count, ingredients, method, link, matching_terms))

        
        sorted_results = sorted(recipe_info, key=lambda x: x[1], reverse=True) #Sorts the list by element 1 (matching_count) then reverses the order to get
                                                                               #a descending list 
        return sorted_results

class RecipeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Search")

        tk.Label(root, text="Choose type: ").pack()
        self.drop_down = ttk.Combobox(root)
        self.drop_down["values"] = ("Lunch", "Dinner", "Chicken", "Beef", "Cheese", "Pasta", "Dessert")
        self.drop_down.set("Lunch")
        self.drop_down["state"] = "readonly"
        self.drop_down.pack()
        
        self.search_label = tk.Label(root, text="Enter ingredients available: (seperated by commas):")
        self.search_label.pack()

        self.search_entry = tk.Entry(root)
        self.search_entry.pack()

        self.search_button = tk.Button(root, text="Search", command=self.search_recipes)
        self.search_button.pack()

        self.result_text = tk.Text(root, height=60, width=120)
        self.result_text.pack()



    def search_recipes(self):
        # Example usage
        scraper = RecipeScraper("https://www.bbcgoodfood.com/recipes/collection/"+self.drop_down.get().lower()+"-recipes")
        search_terms = self.search_entry.get().split(",")
        matching_ingredient_results = scraper.get_ingredients_with_search(search_terms)
        
        self.result_text.delete("1.0", tk.END)
        for recipe_name, count, ingredients, method, link, matching_terms in matching_ingredient_results:
            self.result_text.insert(tk.END, f"Recipe: {recipe_name} - Matching Ingredient Count: {count}\n")
            self.result_text.insert(tk.END, f"Matching Search Terms: {', '.join(matching_terms)}\n")
            self.result_text.insert(tk.END, "Ingredients:\n")
            for ingredient in ingredients:
                self.result_text.insert(tk.END, f"- {ingredient}\n")
            self.result_text.insert(tk.END, "\n")
            
            self.result_text.insert(tk.END, "Method:\n")
            for step in method:
                self.result_text.insert(tk.END, f"- {step}")
            self.result_text.insert(tk.END, "\n")

            self.result_text.insert(tk.END, "Link: ")
            self.result_text.insert(tk.END, "https://www.bbcgoodfood.com" + link)
            self.result_text.insert(tk.END, "\n\n\n")

root = tk.Tk()
app = RecipeGUI(root)
root.mainloop()
