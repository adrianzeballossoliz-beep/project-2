from database import get_session
from sqlalchemy import text
from app import get_filter_options

try:
    session = get_session()
    session.execute(text("SELECT 1"))
    print("Conexion exitosa")
    session.close()

    app_context = app.app_context() if hasattr(app, 'app_context') else None
    
except Exception as e:
    import traceback
    traceback.print_exc()
