from flask import Flask
from project import create_app, db
app = create_app()

@app.before_request
def ping_db():
    '''
    database server keeps closing connection unexpectedly,
    so pind database and pass exception before main request
    to it
    '''
    try:
        db.engine.execute('SELECT 1')
    except Exception as e:
        print('i just executed')

if __name__ == '__main__':
    
    app.run(debug=True)