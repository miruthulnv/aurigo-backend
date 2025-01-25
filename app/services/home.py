from flask_restful import Resource

class Home(Resource):
    def get(self):
        return {"message": "Welcome to the AI-Based Tender and Bid Optimization API!"}
