# Plotly/Dash charts for mini-kep dataset 

Run locally: `python app.py`

Deployed at: <http://macrodash.herokuapp.com> 

# Proposed enhancements
    
## Todo 1: Presentation
 
#### Current 
- [ ] show latest value for time series (WIP)
- [ ] plot on extra axis (NOT TODO)
- [ ] hover day in date for daily data (NOT TODO)
 
#### Shorthand 
 - [ ] show shorthand url in  data footer
 - [ ] fix when shorthand url not working
 
## Todo 2: API change 

#### Whole dataframes
 - new annual, quarterly, monthly backends

#### Variable descriptions
 - some info about variables as text
 - human varname description in Russian/English
  
## Todo 3: data map/data integrity

#### Data integrity
 - list all time series URLs for download                 
 - rog/yoy name substitution + integrity check
 
#### Data transformation:
 - diff accumulated time series
 
## Todo 4: ipython notebook
 - make case list
 - make notebooks

## Todo 5: seasonal adjustment
 - make seasonal adjustment 
 - add to db schema
 - add to interfaces
 - add to graph 
 
## Todo 6: parsers 
 - webhook on repo change for data upload
 - scheduler

## Todo 7 social: 
 - permanent addresses for the graph
 - social links footer 
 - make page more search-friendly
 
## Todo 8 completeness:
 - monthly data map
