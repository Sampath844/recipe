from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import csv
import os

application = Flask(__name__)

# # Set a strong secret key from environment variable or fallback
# application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
#     'SQLALCHEMY_DATABASE_URI',
#     'mysql+pymysql://recipe_admin:Babbu2004@recipe-database.ctyiycc2065c.eu-north-1.rds.amazonaws.com/recipe_db'
# )

# db = SQLAlchemy(application)

# --- Recipe Recommendation Functionality --- #

def load_recipes(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Load recipes data once when the app starts.
basedir = os.path.abspath(os.path.dirname(__file__))
RECIPES = load_recipes(os.path.join(basedir, 'data', 'IndianFoodDatasetCSVV.csv'))


def search(recipes, ingredients, course, diet, threshold):
    results = []
    for row in recipes:
        # Convert ingredients from CSV to a cleaned list.
        ing_list = [i.strip().lower() for i in row.get('TranslatedIngredients', '').split(',')]
        # Check for existence of each user-provided ingredient within the list.
        matched = [i for i in ingredients if any(i.lower() in item for item in ing_list)]
        score = len(matched) / len(ingredients) if ingredients else 0
        if score >= threshold:
            if course.lower() in row.get('Course', '').lower() and diet.lower() in row.get('Diet', '').lower():
                results.append({
                    'name': row.get('TranslatedRecipeName', ''),
                    'cuisine': row.get('Cuisine', ''),
                    'course': row.get('Course', ''),
                    'diet': row.get('Diet', ''),
                    'matched': matched,
                    'all': ing_list,
                    'instructions': row.get('TranslatedInstructions', ''),
                    'score': score,
                    'URL': row.get('URL', '')
                })
    # Return results sorted by highest score (relevance)
    return sorted(results, key=lambda x: x['score'], reverse=True)

# --- Routes for Recipe Recommendation --- #

@application.route('/', methods=['GET'])
def recipe_search():
    return render_template('index.html')

@application.route('/search', methods=['POST'])
def do_search():
    ingredients = [i.strip() for i in request.form['ingredients'].split(',') if i.strip()]
    course = request.form.get('course', '')
    diet = request.form.get('diet', '')
    threshold = float(request.form.get('threshold', 0.4))
    found = search(RECIPES, ingredients, course, diet, threshold)[:10]
    return render_template('results.html', recipes=found)

if __name__ == "__main__": 
    application.run(debug=True)