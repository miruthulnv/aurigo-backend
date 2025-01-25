from flask_restful import Resource, reqparse
from app.models.bids import Bid
from app.models.database import session_scope
from sqlalchemy.exc import SQLAlchemyError

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