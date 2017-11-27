from app import DataSeries
from access import CustomAPI

def test_DataSeries_filter_limits_variable_length():
    assert DataSeries('a', 'GDP_yoy').filter(2000,2001).dict == \
        {'x': [2000, 2001], 'y': [110.0, 105.1], 'name': 'GDP_yoy'}
        
def test_CustomAPI_endpoint():
    ca = CustomAPI(freq="d", name="BRENT")
    assert ca.endpoint == \
        'http://minikep-db.herokuapp.com/all/series/BRENT/d'        
