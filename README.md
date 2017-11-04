# Plotly/Dash charts for mini-kep dataset 

Run locally: `python app.py`

Deployed at: <http://macrodash.herokuapp.com/> 

## Screenshot

![](https://user-images.githubusercontent.com/9265326/32327157-89eb18f6-bfe6-11e7-89da-2306c9591647.png)

# Done
- download data footer as single line

# Proposed enhancements
    
## Todo 1 (presentation):
    
#### Existing: 
 - add x axis margin on right and left 
 - page information in header 

#### New: 
 - show latest value for time series
 - show shorthand url in the data footer

#### Not todo:
 - plot on extra axis 
 - truncate by start year
 - hover day in date for daily data
 
## Todo 2 (requires schema/API/data model change):

#### Existing: 
 - fix when shorthand url not working
 - some info about variables
 
#### New:
 - sections of variables ('GDP components', 'Prices'...) 
 - human varname description in Russian/English
 - more info about variables as text
 - new annual, quarterly, monthly backends
 
#### Todo 3 (data map/data integrity):
 - list all time series URLs for download                 
 - rog/yoy name substitution + integrity check
 
#### Todo 4 (data transformation):
 - diff accumulated time series
 
#### Todo 5 (ipython notebook):
 - make case list

#### Todo 6 seasonal adjustment:
 - make seasonal adjustment 
 - add to db schema
 - add to interfaces
 - add to graph 
 
#### Todo 7 parser work: 
 - webhook on repo change for data upload
 - scheduler

#### Todo 8 social: 
 - permanent addresses for the graph
 - social links footer 
 - make page more search-friendly
 
# Github
  - [This app code](https://github.com/mini-kep/frontend-dash)
  - [Project home](https://github.com/mini-kep/intro) 
  - [Dev notes](https://github.com/mini-kep/intro/blob/master/DEV.md)
