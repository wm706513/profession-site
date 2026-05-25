import numpy as np
import pandas as pd
import os
from copy import deepcopy
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, SelectField

load_dotenv() #load .env file

last_update = '2026-05-02'

expansions = ['DF', 'TWW', 'Midnight']
all_professions = ['alchemy', 'blacksmithing', 'cooking', 'enchanting', 'engineering', 'inscription', 'jewelcrafting', 'leatherworking', 'tailoring']

#BASE_DIR = os.getcwd() + '/mysite/' #for pythonanywhere
BASE_DIR = os.getcwd() + '/' #for local processing
DATA_DIR = BASE_DIR + 'static/data/' #use absolute path since code is run in backend and out of expected folder
IMAGE_DIR = '../static/images/' #use relative path since code is run in front end and hence from the URL and not base directories

data_df = pd.read_pickle(DATA_DIR+'data_DF.pkl')
items_df = pd.read_pickle(DATA_DIR+'items_DF.pkl')

data_tww = pd.read_pickle(DATA_DIR+'data_TWW.pkl')
items_tww = pd.read_pickle(DATA_DIR+'items_TWW.pkl')

data_midnight = pd.read_pickle(DATA_DIR+'data_midnight.pkl')
items_midnight = pd.read_pickle(DATA_DIR+'items_midnight.pkl')

data_cols = dict(zip(expansions, [None for _ in expansions]))
items_cols = dict(zip(expansions, [None for _ in expansions]))

data_cols['DF'] = list(data_df.columns)
data_cols['TWW'] = list(data_tww.columns)
data_cols['Midnight'] = list(data_midnight.columns)

items_cols['DF'] = list(items_df.columns)
items_cols['TWW'] = list(items_tww.columns)
items_cols['Midnight'] = list(items_midnight.columns)

data_df['expansion'] = 'DF'
data_tww['expansion'] = 'TWW'
data_midnight['expansion'] = 'Midnight'

items_df['expansion'] = 'DF'
items_tww['expansion'] = 'TWW'
items_midnight['expansion'] = 'Midnight'

all_data = pd.concat((data_df, data_tww, data_midnight), ignore_index=True)
items = pd.concat((items_df, items_tww, items_midnight), ignore_index=True)

del data_df
del data_tww
del data_midnight
del items_df
del items_tww
del items_midnight

item_tags = [('none', 'None')] #have None at the top of the list (it also isn't in the dataframe to begin with)
tags = np.sort(all_data.loc[:, 'tag'].to_numpy())
for tag in tags:
    if tag != 'Other':
        item_tags.append((tag.lower(), tag))
item_tags.append(('other', 'Other')) #put Other at the end of the list

valid_tags = [a for a,_ in item_tags]
valid_tags = dict(zip(all_professions, [None for _ in all_professions]))
valid_tags = {xpac:deepcopy(valid_tags) for xpac in expansions}
for expansion in expansions:
    for p in all_professions:
        valid_tags[expansion][p] = ['None'] + list(np.sort(np.unique([tag for tag in all_data.loc[(all_data['expansion']==expansion)&(all_data['profession']==p.title()), 'tag'] if tag != 'Other']))) + ['Other']

learned = dict(zip(all_professions, [None for _ in all_professions]))
unlearned = dict(zip(all_professions, [None for _ in all_professions]))
learned = {xpac:deepcopy(learned) for xpac in expansions}
unlearned = {xpac:deepcopy(unlearned) for xpac in expansions}

for xpac in expansions:
    neededColumns = data_cols[xpac]
    for p in all_professions:
        isThisExpansion = all_data['expansion']==xpac
        isThisProfession = all_data['profession']==p.title()
        learned[xpac][p] = all_data.loc[isThisExpansion&isThisProfession&(~all_data['character'].isna()), neededColumns].to_dict(orient='records')
        unlearned[xpac][p] = all_data.loc[isThisExpansion&isThisProfession&(all_data['character'].isna()), neededColumns].to_dict(orient='records')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

class SearchForm(FlaskForm):
    search = SearchField(label='Search', render_kw={'placeholder': 'Search'})
    clear = SubmitField(label='Clear')
    submit = SubmitField(label='Search')


### generalization functions ###
def expansion_pages(expansion):
    full_names = {'DF':'Dragonflight', 'TWW':'The War Within', 'Midnight':'Midnight'}
    for xpac in expansions:
        for p in all_professions:
            session[p+'_'+xpac+'_search'] = None
            session[p+'_'+xpac+'_select'] = None

    return render_template('expansion.html', all_professions=all_professions, expansion=expansion, last_update=last_update, full_name=full_names.get(expansion))

def profession_pages(profession_name, expansion):
    for xpac in expansions:
        for p in all_professions:
            if p != profession_name or xpac != expansion:
                session[p+'_'+xpac+'_search'] = None
                session[p+'_'+xpac+'_select'] = None

    #initialize session search values
    if not session.get(profession_name+'_'+expansion+'_search'):
        session[profession_name+'_'+expansion+'_search'] = ''
    if not session.get(profession_name+'_'+expansion+'_select'):
        session[profession_name+'_'+expansion+'_select'] = 'none'

    datasets = zip(['Learned Recipes', 'Unlearned Recipes'], [learned[expansion][profession_name], unlearned[expansion][profession_name]])

    SearchForm.select = SelectField(label='Filter:', choices=((tag.lower(), tag) for tag in valid_tags[expansion][profession_name]))
    form = SearchForm()

    if form.validate_on_submit():
        if form.clear.data:
            session[profession_name+'_'+expansion+'_search'] = ''
            session[profession_name+'_'+expansion+'_select'] = 'none'
        elif form.submit.data:
            session[profession_name+'_'+expansion+'_search'] = form.search.data
            session[profession_name+'_'+expansion+'_select'] = form.select.data

        return redirect(url_for(profession_name+'_'+expansion)) #prevents asking to resubmit every time refresh happens

    if session[profession_name+'_'+expansion+'_search'] != '':
        form.search.data = session[profession_name+'_'+expansion+'_search']
    if session[profession_name+'_'+expansion+'_select'].lower() != 'none':
        form.select.data = session[profession_name+'_'+expansion+'_select']

    if expansion == 'DF':
        template = 'professionDF.html'
    elif expansion == 'TWW':
        template = 'professionTWW.html'
    elif expansion == 'Midnight':
        template = 'professionMidnight.html'
    else:
        raise FileNotFoundError(f'No template created for {expansion}')

    return render_template(template, form=form, profession_name=profession_name, last_update=last_update, valid_tags=valid_tags[expansion][profession_name],
                           items=items.loc[items['expansion']==expansion, items_cols[expansion]], datasets=datasets)

### web functions ###
@app.before_first_request
#@app.before_request #for PythonAnywhere
def initialize():
    session.permanent=False

@app.route('/')
def index():
    return render_template('index.html', all_professions=all_professions, last_update=last_update)

### expansion pages ###
@app.route('/dragonflight')
def dragonflight():
    return expansion_pages(expansion='DF')

@app.route('/the_war_within')
def the_war_within():
    return expansion_pages(expansion='TWW')

@app.route('/midnight')
def midnight():
    return expansion_pages(expansion='Midnight')

### dragonflight pages ###
@app.route('/dragonflight/alchemy', methods=['GET', 'POST'])
def alchemy_DF():
    return profession_pages(profession_name='alchemy', expansion='DF')

@app.route('/dragonflight/blacksmithing', methods=['GET', 'POST'])
def blacksmithing_DF():
    return profession_pages(profession_name='blacksmithing', expansion='DF')

@app.route('/dragonflight/cooking', methods=['GET', 'POST'])
def cooking_DF():
    return profession_pages(profession_name='cooking', expansion='DF')

@app.route('/dragonflight/enchanting', methods=['GET', 'POST'])
def enchanting_DF():
    return profession_pages(profession_name='enchanting', expansion='DF')

@app.route('/dragonflight/engineering', methods=['GET', 'POST'])
def engineering_DF():
    return profession_pages(profession_name='engineering', expansion='DF')

@app.route('/dragonflight/inscription', methods=['GET', 'POST'])
def inscription_DF():
    return profession_pages(profession_name='inscription', expansion='DF')

@app.route('/dragonflight/jewelcrafting', methods=['GET', 'POST'])
def jewelcrafting_DF():
    return profession_pages(profession_name='jewelcrafting', expansion='DF')

@app.route('/dragonflight/leatherworking', methods=['GET', 'POST'])
def leatherworking_DF():
    return profession_pages(profession_name='leatherworking', expansion='DF')

@app.route('/dragonflight/tailoring', methods=['GET', 'POST'])
def tailoring_DF():
    return profession_pages(profession_name='tailoring', expansion='DF')

### the war within pages ###
@app.route('/the_war_within/alchemy', methods=['GET', 'POST'])
def alchemy_TWW():
    return profession_pages(profession_name='alchemy', expansion='TWW')

@app.route('/the_war_within/blacksmithing', methods=['GET', 'POST'])
def blacksmithing_TWW():
    return profession_pages(profession_name='blacksmithing', expansion='TWW')

@app.route('/the_war_within/cooking', methods=['GET', 'POST'])
def cooking_TWW():
    return profession_pages(profession_name='cooking', expansion='TWW')

@app.route('/the_war_within/enchanting', methods=['GET', 'POST'])
def enchanting_TWW():
    return profession_pages(profession_name='enchanting', expansion='TWW')

@app.route('/the_war_within/engineering', methods=['GET', 'POST'])
def engineering_TWW():
    return profession_pages(profession_name='engineering', expansion='TWW')

@app.route('/the_war_within/inscription', methods=['GET', 'POST'])
def inscription_TWW():
    return profession_pages(profession_name='inscription', expansion='TWW')

@app.route('/the_war_within/jewelcrafting', methods=['GET', 'POST'])
def jewelcrafting_TWW():
    return profession_pages(profession_name='jewelcrafting', expansion='TWW')

@app.route('/the_war_within/leatherworking', methods=['GET', 'POST'])
def leatherworking_TWW():
    return profession_pages(profession_name='leatherworking', expansion='TWW')

@app.route('/the_war_within/tailoring', methods=['GET', 'POST'])
def tailoring_TWW():
    return profession_pages(profession_name='tailoring', expansion='TWW')

### midnight pages ###
@app.route('/midnight/alchemy', methods=['GET', 'POST'])
def alchemy_Midnight():
    return profession_pages(profession_name='alchemy', expansion='Midnight')

@app.route('/midnight/blacksmithing', methods=['GET', 'POST'])
def blacksmithing_Midnight():
    return profession_pages(profession_name='blacksmithing', expansion='Midnight')

@app.route('/midnight/cooking', methods=['GET', 'POST'])
def cooking_Midnight():
    return profession_pages(profession_name='cooking', expansion='Midnight')

@app.route('/midnight/enchanting', methods=['GET', 'POST'])
def enchanting_Midnight():
    return profession_pages(profession_name='enchanting', expansion='Midnight')

@app.route('/midnight/engineering', methods=['GET', 'POST'])
def engineering_Midnight():
    return profession_pages(profession_name='engineering', expansion='Midnight')

@app.route('/midnight/inscription', methods=['GET', 'POST'])
def inscription_Midnight():
    return profession_pages(profession_name='inscription', expansion='Midnight')

@app.route('/midnight/jewelcrafting', methods=['GET', 'POST'])
def jewelcrafting_Midnight():
    return profession_pages(profession_name='jewelcrafting', expansion='Midnight')

@app.route('/midnight/leatherworking', methods=['GET', 'POST'])
def leatherworking_Midnight():
    return profession_pages(profession_name='leatherworking', expansion='Midnight')

@app.route('/midnight/tailoring', methods=['GET', 'POST'])
def tailoring_Midnight():
    return profession_pages(profession_name='tailoring', expansion='Midnight')

# this won't get run when deployed on PythonAnywhere
if __name__ == '__main__':
    app.run(debug=True)