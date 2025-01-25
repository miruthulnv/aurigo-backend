from app import create_app
from app.models.database import engine, Base
from app.services.login import login_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS

jwt = None
app = create_app()
CORS(app)
app.register_blueprint(login_bp)


with app.app_context():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(debug=True)