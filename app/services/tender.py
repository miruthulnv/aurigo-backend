from flask_restful import Resource, reqparse
from app.models.tender import Tender
from app.models.database import session_scope
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


class TenderResource(Resource):

    @staticmethod
    def tender_to_dict(tender):
        return {
            'id': tender.id,
            'title': tender.title,
            'department': tender.department,
            'description': tender.description,
            'est_cost': tender.est_cost,
            'est_timeline': tender.est_timeline,
            'cost_weight': tender.cost_weight,
            'timeline_weight': tender.timeline_weight,
            'compliance_weight': tender.compliance_weight,
            'current_factors_weight': tender.current_factors_weight,
            'historical_rating_weight': tender.historical_rating_weight,
            'currency': tender.currency,
            'email': tender.email,
            'category': tender.category,
            'publish_date': tender.publish_date,
            'closing_date': tender.closing_date,
            'status': tender.status
        }

    def get(self, tender_id=None):
        try:
            with session_scope() as session:
                if tender_id:
                    tender = session.query(Tender).get(tender_id)
                    if not tender:
                        return {'message': 'Tender not found'}, 404
                    return self.tender_to_dict(tender)
                else:
                    tenders = session.query(Tender).all()
                    return [self.tender_to_dict(tender) for tender in tenders]
        except SQLAlchemyError:
            return {'message': 'An error occurred while fetching tender(s)'}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('department', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('est_cost', type=float, required=True)
        parser.add_argument('est_timeline', type=int, required=True)
        parser.add_argument('cost_weight', type=float, required=True)
        parser.add_argument('timeline_weight', type=float, required=True)
        parser.add_argument('compliance_weight', type=float, required=True)
        parser.add_argument('current_factors_weight', type=float, required=True)
        parser.add_argument('historical_rating_weight', type=float, required=True)
        parser.add_argument('currency', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('publish_date', type=str, required=True)
        parser.add_argument('closing_date', type=str, required=True)
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                new_tender = Tender(
                    id=args['id'],
                    title=args['title'],
                    department=args['department'],
                    description=args['description'],
                    est_cost=args['est_cost'],
                    est_timeline=args['est_timeline'],
                    cost_weight=args['cost_weight'],
                    timeline_weight=args['timeline_weight'],
                    compliance_weight=args['compliance_weight'],
                    current_factors_weight=args['current_factors_weight'],
                    historical_rating_weight=args['historical_rating_weight'],
                    currency=args['currency'],
                    email=args['email'],
                    category=args['category'],
                    publish_date=(datetime.strptime(args['publish_date'], "%Y-%m-%dT%H:%M:%SZ")),
                    closing_date=(datetime.strptime(args['closing_date'], "%Y-%m-%dT%H:%M:%SZ")),
                    status=args['status']
                )
                session.add(new_tender)
                session.flush()
                return {'message': 'Tender created successfully'}, 201
        except SQLAlchemyError as e:
            print(e)
            return {'message': 'An error occurred while creating the tender'}, 500

    def patch(self, tender_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('department', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('est_cost', type=float)
        parser.add_argument('est_timeline', type=int)
        parser.add_argument('cost_weight', type=float)
        parser.add_argument('timeline_weight', type=float)
        parser.add_argument('compliance_weight', type=float)
        parser.add_argument('current_factors_weight', type=float)
        parser.add_argument('historical_rating_weight', type=float)
        parser.add_argument('currency', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('category', type=str)
        parser.add_argument('publish_date', type=str)
        parser.add_argument('closing_date', type=str)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                tender = session.query(Tender).get(tender_id)
                if not tender:
                    return {'message': 'Tender not found'}, 404

                for key, value in args.items():
                    if value is not None:
                        if key in ['publish_date', 'closing_date']:
                            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                        setattr(tender, key, value)

                session.flush()
                return self.tender_to_dict(tender)
        except SQLAlchemyError:
            return {'message': 'An error occurred while updating the tender'}, 500

    def delete(self, tender_id):
        try:
            with session_scope() as session:
                tender = session.query(Tender).get(tender_id)
                if not tender:
                    return {'message': 'Tender not found'}, 404
                session.delete(tender)
                return {'message': 'Tender deleted successfully'}, 200
        except SQLAlchemyError:
            return {'message': 'An error occurred while deleting the tender'}, 500
