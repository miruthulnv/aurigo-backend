from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
    app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    api = Api(app)

    from app.services.home import Home
    from app.services.tender import Tender
    from app.services.bid_optimization import BidOptimization

    api.add_resource(Home, '/api/home')
    api.add_resource(Tender, '/api/tender')
    api.add_resource(BidOptimization, '/api/optimize-bid')

    return app