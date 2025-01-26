from flask_restful import Resource, reqparse
from app.models.bids import Bid
from app.models.database import session_scope
from sqlalchemy.exc import SQLAlchemyError
from app.models.tender import Tender
import json
import requests


def convert_tender_to_json(session, tender_id: str):
    # Query the tender table
    tender = session.query(Tender).filter_by(id=tender_id).first()

    if not tender:
        return None

    # Convert the tender to the specified JSON format
    tender_json = {

            "id": tender.id,
            "requirements": {
                "estimated_cost": tender.est_cost,
                "estimated_timeline": tender.est_timeline,
                "cost_weight": tender.cost_weight,
                "timeline_weight": tender.timeline_weight,
                "compliance_weight": tender.compliance_weight,
                "current_factors_weight": tender.current_factors_weight,
                "historical_rating_weight": tender.historical_rating_weight

        }
    }

    return tender_json

class BidResource(Resource):
    def get(self, bid_id=None):
        try:
            with session_scope() as session:
                if bid_id:
                    bid = session.query(Bid).get(bid_id)
                    if not bid:
                        return {'message': 'Bid not found'}, 404
                    return self.bid_to_dict(bid)
                else:
                    bids = session.query(Bid).all()
                    return [self.bid_to_dict(bid) for bid in bids]
        except SQLAlchemyError as e:
            return {'message': 'An error occurred while fetching bid(s)'}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('bidder_id', type=int, required=True)
        parser.add_argument('company_name', type=str, required=True)
        parser.add_argument('bid_cost', type=float, required=True)
        parser.add_argument('proposed_timeline', type=int, required=True)
        parser.add_argument('tender_id', type=str, required=True)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                new_bid = Bid(
                    bidder_id=args['bidder_id'],
                    company_name=args['company_name'],
                    bid_cost=args['bid_cost'],
                    proposed_timeline=args['proposed_timeline'],
                    tender_id=args['tender_id']
                )
                url="http://localhost:5000/api/evaluate-bids"
                tender_details= convert_tender_to_json(session, args['tender_id'])
                bidder_details = [{"bidder_id": args['company_name'], "bid_cost": args['bid_cost'], "proposed_timeline": args['proposed_timeline'], "compliance": True}]
                data={"tender": tender_details, "bids": bidder_details}
                headers = {'Content-Type': 'application/json'}
                print(data)
                response = requests.post(url, data=json.dumps(data), headers=headers)
                print(response)
                try:
                    parsed = response.json()
                    print(parsed)
                    new_bid.overall_score = parsed['ranked_bidders'][0]['final_score']
                    new_bid.readable_insights = parsed['ranked_bidders'][0]['readable_insights']

                except ValueError:  # catches JSONDecodeError as well
                    print("Response did not return valid JSON.")
                    parsed = None
                    new_bid.overall_score =  0
                # print(parsed)

                session.add(new_bid)
                session.flush()
                return self.bid_to_dict(new_bid), 201
        except SQLAlchemyError as e:
            return {'message': 'An error occurred while creating the bid'}, 500

    def patch(self, bid_id):
        parser = reqparse.RequestParser()
        parser.add_argument('company_name', type=str)
        parser.add_argument('bid_cost', type=float)
        parser.add_argument('proposed_timeline', type=int)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                bid = session.query(Bid).get(bid_id)
                if not bid:
                    return {'message': 'Bid not found'}, 404

                for key, value in args.items():
                    if value is not None:
                        setattr(bid, key, value)

                session.flush()
                return self.bid_to_dict(bid)
        except SQLAlchemyError as e:
            return {'message': 'An error occurred while updating the bid'}, 500

    def delete(self, bid_id):
        try:
            with session_scope() as session:
                bid = session.query(Bid).get(bid_id)
                if not bid:
                    return {'message': 'Bid not found'}, 404

                session.delete(bid)
                return {'message': 'Bid deleted successfully'}, 200
        except SQLAlchemyError as e:
            return {'message': 'An error occurred while deleting the bid'}, 500

    @staticmethod
    def bid_to_dict(bid):
        return {
            'id': bid.id,
            'bidder_id': bid.bidder_id,
            'company_name': bid.company_name,
            'bid_cost': bid.bid_cost,
            'proposed_timeline': bid.proposed_timeline,
            'tender_id': bid.tender_id,
        }

class BidsByUserResource(Resource):
    @staticmethod
    def bid_to_dict(bid):
        return {
            'id': bid.id,
            'bidder_id': bid.bidder_id,
            'company_name': bid.company_name,
            'bid_cost': bid.bid_cost,
            'proposed_timeline': bid.proposed_timeline,
            'tender_id': bid.tender_id,
            'overall_score': bid.overall_score,
            'readable_insights': bid.readable_insights
        }

    def get(self, user_id):
        try:
            with session_scope() as session:
                bids = session.query(Bid).filter(Bid.bidder_id == user_id).all()
                if not bids:
                    return {'message': 'No bids found for the specified user'}, 404
                return [self.bid_to_dict(bid) for bid in bids]
        except SQLAlchemyError:
            return {'message': 'An error occurred while fetching bids'}, 500


class BidsByTenderResource(Resource):
    @staticmethod
    def bid_to_dict(bid):
        return {
            'id': bid.id,
            'bidder_id': bid.bidder_id,
            'company_name': bid.company_name,
            'bid_cost': bid.bid_cost,
            'proposed_timeline': bid.proposed_timeline,
            'tender_id': bid.tender_id,
            'overall_score': bid.overall_score,
            'readable_insights': bid.readable_insights
        }

    def get(self, tender_id):
        try:
            with session_scope() as session:
                bids = session.query(Bid).filter(Bid.tender_id == tender_id).all()
                if not bids:
                    return {'message': 'No bids found for the specified tender'}, 404
                return [self.bid_to_dict(bid) for bid in bids]
        except SQLAlchemyError:
            return {'message': 'An error occurred while fetching bids'}, 500
