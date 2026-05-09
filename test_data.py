import app as myapp
from flask import request

with myapp.app.test_request_context('/api/data'):
    try:
        response = myapp.get_dashboard_data()
        print(response.json)
    except Exception as e:
        import traceback
        traceback.print_exc()
