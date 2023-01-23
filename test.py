# from db import GlobalVar

# db = GlobalVar("tiny.db.elephantsql.com", "ljbdoibm", "ljbdoibm", "TQeeYTeq6MXBw1EAnyW-7MrRwK4Qugk7")
# greet_value = db.fetch_column_value("123", "greet")

from ml_models import nlp

nlp=nlp()
nlp.x=20
print(nlp.x)