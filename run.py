from app import create_app
from app.models.database import engine, Base

app = create_app()

with app.app_context():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(debug=True)