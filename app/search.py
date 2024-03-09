from app import app
from flask import render_template, request

from search.get import Search_Data

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template(
        '/index.html',
    )

@app.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('q', '')
    type = request.args.get('type', '')
    if type == '':
        type = 'Text'
    
    search_result = Search_Data(type, keyword)
    print(search_result)
    if search_result == []:
        return render_template(
            '/search/index.html',
            query=keyword,
            note='No results found.'
        )
    else:
        return render_template(
            '/search/index.html',
            query=keyword,
            results=search_result
        )