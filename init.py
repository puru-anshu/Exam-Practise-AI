from app import app, db

with app.app_context():
    db.drop_all()
    db.create_all()

# from app import app, db
# from models import ExamType, Subject

# with app.app_context():
#     # Add exam types
#     cbse = ExamType(name="CBSE", description="Central Board of Secondary Education")
#     iit_jee = ExamType(name="IIT JEE", description="Indian Institutes of Technology Joint Entrance Examination")
#     db.session.add(cbse)
#     db.session.add(iit_jee)
#     db.session.commit()

#     # Add subjects
#     subjects = [
#         Subject(name="Physics", exam_type_id=cbse.id),
#         Subject(name="Chemistry", exam_type_id=cbse.id),
#         Subject(name="Mathematics", exam_type_id=cbse.id),
#         Subject(name="Physics", exam_type_id=iit_jee.id),
#         Subject(name="Chemistry", exam_type_id=iit_jee.id),
#         Subject(name="Mathematics", exam_type_id=iit_jee.id),
#     ]
#     db.session.add_all(subjects)
#     db.session.commit()
