import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, SelectField

load_dotenv() #load .env file

all_data = pd.read_pickle('./static/data/data.pkl')
items = pd.read_pickle('./static/data/items.pkl')

tags = pd.DataFrame(all_data.loc[:,'tag'])
all_professions = ['alchemy', 'blacksmithing', 'cooking', 'enchanting', 'engineering', 'inscription', 'jewelcrafting', 'leatherworking', 'tailoring']

item_tags = [('none', 'None')] #have None at the top of the list (it also isn't in the dataframe to begin with)
for tag in tags.sort_values(by='tag').loc[:,'tag'].to_numpy():
    if tag != 'Other':
        item_tags.append((tag.lower(), tag))
item_tags.append(('other', 'Other')) #put Other at the end of the list

valid_tags = [a for a,_ in item_tags]
valid_tags = dict(zip(all_professions, [None]*len(all_professions)))
for p in all_professions:
    valid_tags[p] = ['None'] + list(np.sort(np.unique([tag for tag in all_data.loc[all_data['profession']==p.title(), 'tag'] if tag != 'Other']))) + ['Other']

learned = dict(zip(all_professions, [None]*len(all_professions)))
unlearned = dict(zip(all_professions, [None]*len(all_professions)))
for p in all_professions:
    learned[p] = all_data.loc[(~all_data['character'].isna())&(all_data['profession']==p.title())].to_dict(orient='records')
    unlearned[p] = all_data.loc[(all_data['character'].isna())&(all_data['profession']==p.title())].to_dict(orient='records')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

class SearchForm(FlaskForm):
    search = SearchField(label='Search', render_kw={'placeholder': 'Search'})
    #select = SelectField(label='Filter:', choices=item_tags)
    clear = SubmitField(label='Clear')
    submit = SubmitField(label='Search')

@app.before_first_request
def initialize():
    session.permanent=False

@app.route('/')
def index():
    return render_template('index.html', all_professions=all_professions)

@app.route('/alchemy', methods=['GET', 'POST'])
def alchemy():
    profession_name = 'alchemy'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/blacksmithing', methods=['GET', 'POST'])
def blacksmithing():
    profession_name = 'blacksmithing'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/cooking', methods=['GET', 'POST'])
def cooking():
    profession_name = 'cooking'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/enchanting', methods=['GET', 'POST'])
def enchanting():
    profession_name = 'enchanting'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/engineering', methods=['GET', 'POST'])
def engineering():
    profession_name = 'engineering'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    profession_name = 'inscription'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/jewelcrafting', methods=['GET', 'POST'])
def jewelcrafting():
    profession_name = 'jewelcrafting'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/leatherworking', methods=['GET', 'POST'])
def leatherworking():
    profession_name = 'leatherworking'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

@app.route('/tailoring', methods=['GET', 'POST'])
def tailoring():
    profession_name = 'tailoring'
    for p in all_professions:
        if p != profession_name:
            session[p+'_search'] = None
            session[p+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_search'):
        session[profession_name+'_search'] = ''
    if not session.get(profession_name+'_select'):
        session[profession_name+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[profession_name], unlearned[profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_search'] = ''
            session[profession_name+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_search'] = form.search.data
            session[profession_name+'_select'] = form.select.data

        return redirect(url_for(profession_name)) #prevents asking to resubmit every time refresh happens
    
    if session[profession_name+'_search'] != '':
        form.search.data = session[profession_name+'_search']
    if session[profession_name+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_select']

    return render_template(profession_name+'.html', form=form, profession_name=profession_name, valid_tags=valid_tags[profession_name], items=items, datasets=datasets)

if __name__ == '__main__':
    app.run(debug=True)