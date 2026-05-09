import app as myapp
with myapp.app.app_context():
    try:
        response = myapp.get_filter_options()
        print(response.json)
    except Exception as e:
        import traceback
        traceback.print_exc()
