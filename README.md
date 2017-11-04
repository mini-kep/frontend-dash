# Plotly/Dash charts for mini-kep dataset 

<table>
<tr>
 <td>
     <img src="https://user-images.githubusercontent.com/9265326/32409472-5543875e-c1bd-11e7-8573-df77492858f8.png">
 </td> 
 <td>
  Run locally: `python app.py`
  <br> 
  Deployed at: <http://macrodash.herokuapp.com/> 
</td> 
</tr>
</table>

## Screenshot


# Done
- [x] download data footer as single line
- [x] page information in header 
 
# Proposed enhancements
    
## Todo 1 (presentation):
    
- [ ] add x axis margin on right and left 
- [ ] show latest value for time series
- [ ] show shorthand url in the data footer

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
 
#### Todo 9 completeness:
 - monthly data map

 
# Github
  - [This app code](https://github.com/mini-kep/frontend-dash)
  - [Project home](https://github.com/mini-kep/intro) 
  - [Dev notes](https://github.com/mini-kep/intro/blob/master/DEV.md)
