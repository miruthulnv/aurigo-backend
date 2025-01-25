from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os


load_dotenv()
jwt = None
def create_app():
    global jwt
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
    app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'
    jwt = JWTManager(app)
    jwt.init_app(app)
    api = Api(app)

    from app.services.home import Home
    from app.services.bid_optimization import BidOptimization
    from app.services.user import UserResource
    from app.services.tender import TenderResource
    from app.services.bids import BidResource
    from app.services.company_scores import company_scores_bp
    from app.services.rankedBids import ranked_bids_bp

    api.add_resource(Home, '/api/home')
    api.add_resource(TenderResource, '/api/tender/<string:tender_id>', '/api/tender')
    api.add_resource(BidOptimization, '/api/optimize-bid')
    api.add_resource(UserResource, '/api/user/<int:user_id>')
    api.add_resource(BidResource, '/api/bid/<int:bid_id>','/api/bid')
    app.register_blueprint(company_scores_bp)
    app.register_blueprint(ranked_bids_bp)
    return app