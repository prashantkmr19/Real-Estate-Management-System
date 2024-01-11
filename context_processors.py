from datetime import datetime

def inject_globals():
    current_year = datetime.now().year
    return {'current_year': current_year}
