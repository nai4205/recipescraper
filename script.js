document.addEventListener('DOMContentLoaded', function () {
    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', searchRecipes);
});

function searchRecipes() {
    const recipeType = document.getElementById('recipeType').value;
    const ingredientsInput = document.getElementById('ingredients').value;
    const ingredients = ingredientsInput.split(',');

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    fetchRecipeData(recipeType, ingredients)
        .then(recipeData => displayResults(recipeData, resultsDiv))
        .catch(error => console.error(error));
}

async function fetchRecipeData(recipeType, ingredients) {
    const response = await fetch(`https://www.bbcgoodfood.com/recipes/collection/${recipeType}-recipes`);
    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    const linksContainer = doc.querySelector('.layout-md-rail__primary');
    const links = Array.from(linksContainer.querySelectorAll('.card__content a'));

    const matchingIngredientResults = [];

    for (const link of links) {
        const linkUrl = link.getAttribute('href');
        const recipeResponse = await fetch(`https://www.bbcgoodfood.com${linkUrl}`);
        const recipeHtml = await recipeResponse.text();
        const recipeDoc = parser.parseFromString(recipeHtml, 'text/html');

        const recipeName = recipeDoc.querySelector('h1').textContent.trim();
        const ingredientsContainer = recipeDoc.querySelector('.recipe__ingredients.col-12');
        const ingredientsList = Array.from(ingredientsContainer.querySelectorAll('li'));
        const ingredientsArray = ingredientsList.map(ingredient => ingredient.textContent.trim());

        const methodContainer = recipeDoc.querySelector('.recipe__method-steps.col-12');
        const methodList = Array.from(methodContainer.querySelectorAll('li'));
        const methodArray = methodList.map(method => method.textContent.trim());

        const matchingCount = getMatchingIngredientCount(ingredientsArray, ingredients);
        const matchingTerms = ingredients.filter(term =>
            ingredientsArray.some(ingredient => ingredient.toLowerCase().includes(term.trim().toLowerCase()))
        );

        if (matchingCount > 0) {
            matchingIngredientResults.push({
                recipeName,
                matchingCount,
                ingredients: ingredientsArray,
                method: methodArray,
                link: linkUrl,
                matchingTerms
            });
        }
    }

    return matchingIngredientResults.sort((a, b) => b.matchingCount - a.matchingCount);
}

function getMatchingIngredientCount(ingredientsArray, searchTerms) {
    let count = 0;
    for (const term of searchTerms) {
        for (const ingredient of ingredientsArray) {
            if (ingredient.toLowerCase().includes(term.trim().toLowerCase())) {
                count++;
            }
        }
    }
    return count;
}

function displayResults(recipeData, resultsDiv) {
    for (const recipe of recipeData) {
        const recipeDiv = document.createElement('div');
        recipeDiv.innerHTML = `
            <p><strong>Recipe:</strong> ${recipe.recipeName} - Matching Ingredient Count: ${recipe.matchingCount}</p>
            <p><strong>Matching Search Terms:</strong> ${recipe.matchingTerms.join(', ')}</p>
            <p><strong>Ingredients:</strong></p>
            <ul>
                ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
            </ul>
            <p><strong>Method:</strong></p>
            <ol>
                ${recipe.method.map(step => `<li>${step}</li>`).join('')}
            </ol>
            <p><strong>Link:</strong> <a href="https://www.bbcgoodfood.com${recipe.link}" target="_blank">Recipe Link</a></p>
            <hr>
        `;
        resultsDiv.appendChild(recipeDiv);
    }
}
