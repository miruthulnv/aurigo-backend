from flask_restful import Resource, reqparse
from app.models.tender import Tender
from app.models.database import session_scope
from sqlalchemy.exc import SQLAlchemyError

class TenderResource(Resource):
    @staticmethod
    def tender_to_dict(tender):
        return {
            'id': tender.id,
            'title': tender.title,
            'description': tender.description,
            'publish_date': tender.publish_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'closing_date': tender.closing_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'estimated_value': tender.estimated_value,
            'currency': tender.currency,
            'category': tender.category,
            'requirements': tender.requirements,
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
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while fetching tender(s)'}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('publish_date', type=str, required=True)
        parser.add_argument('closing_date', type=str, required=True)
        parser.add_argument('estimated_value', type=float, required=True)
        parser.add_argument('currency', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('requirements', type=dict, required=True)
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                new_tender = Tender(
                    id=args['id'],
                    title=args['title'],
                    description=args['description'],
                    publish_date=args['publish_date'],
                    closing_date=args['closing_date'],
                    estimated_value=args['estimated_value'],
                    currency=args['currency'],
                    category=args['category'],
                    requirements=args['requirements'],
                    status=args['status']
                )
                session.add(new_tender)
                session.flush()
                return {'message': 'Tender created successfully'}, 201
        except SQLAlchemyError as e:
            # Log the error here
            print(e)
            return {'message': 'An error occurred while creating the tender'}, 500

    def patch(self, tender_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('publish_date', type=str)
        parser.add_argument('closing_date', type=str)
        parser.add_argument('estimated_value', type=float)
        parser.add_argument('currency', type=str)
        parser.add_argument('category', type=str)
        parser.add_argument('requirements', type=dict)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                tender = session.query(Tender).get(tender_id)
                if not tender:
                    return {'message': 'Tender not found'}, 404

                for key, value in args.items():
                    if value is not None:
                        setattr(tender, key, value)

                session.flush()
                return self.tender_to_dict(tender)
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while updating the tender'}, 500

    def delete(self, tender_id):
        try:
            with session_scope() as session:
                tender = session.query(Tender).get(tender_id)
                if not tender:
                    return {'message': 'Tender not found'}, 404

                session.delete(tender)
                return {'message': 'Tender deleted successfully'}, 200
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while deleting the tender'}, 500