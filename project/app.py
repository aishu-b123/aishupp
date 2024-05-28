from flask import Flask, render_template, request
import csv
from flask_paginate import Pagination, get_page_args
import pandas as pd

app = Flask(__name__)

# Function to load data from CSV files into a list of dictionaries
def load_data():
    data = []
    # Add more CSV files here if needed
    csv_files = [ 'flipkart.csv']
    for file_name in csv_files:
        with open(f'csv_files/{file_name}', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
    return data

# Function to get the paginated results
def get_paginated_results(data, page, per_page):
    offset = (page - 1) * per_page
    return data[offset: offset + per_page]



# Homepage
@app.route('/')
def index():
    search_results = []
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination = Pagination(page=page, per_page=per_page, total=0, css_framework='bootstrap4')
    return render_template('index.html', search_results=search_results, pagination=pagination)

# Category page
@app.route('/category/<category_name>')
def category(category_name):
    products = []
    csv_files = [ 'flipkart.csv','products1.csv',]
    for file_name in csv_files:
        with open(f'csv_files/{file_name}', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            data = [row for row in csv_reader if category_name.lower() in row['main_category'].lower()]
            products.extend(data[:20])  # Get 20 products from each CSV
    return render_template('category.html', products=products, category_name=category_name)

# Search functionality
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('search_query', '').lower()
    all_data = load_data()
    search_results = []
    
    # Searching for matches in both 'product_name' and 'main_category' columns
    for product in all_data:
        product_name = product['product_name'].lower()
        category_name = product['main_category'].lower()
        if query in product_name or query in category_name:
            search_results.append(product)
    
    # Pagination for search results
    page, per_page, _ = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(search_results)
    paginated_results = get_paginated_results(search_results, page, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('results.html',
                           search_results=paginated_results,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           query=query)

def fetch_price_and_store(product_name):
    data = load_data()
    price1, store1 = None, None
    price2, store2 = None, None
    for product in data:
        if product['product_name'] == product_name:
            if product['vendor_name'] == 'flipkart':
                price1 = product['actual_price']
                store1 = product['vendor_name']
            elif product['vendor_name'] == 'amazon':
                price2 = product['actual_price']
                store2 = product['vendor_name']
    return price1, store1, price2, store2


def fetch_other_details(product_name):
    data = []
    for file_name in ['flipkart.csv','products1.csv']:
        with open(f'csv_files/{file_name}', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['product_name'] == product_name:
                    data.append(row)
    return data

# Product details page
@app.route('/product/<string:product_name>')
def product(product_name):
    price1, store1, price2, store2 = fetch_price_and_store(product_name)
    other_details = fetch_other_details(product_name)
    return render_template('product.html', product_name=product_name, price1=price1, store1=store1, price2=price2, store2=store2, other_details=other_details)


if __name__ == '__main__':
    app.run(debug=True)

