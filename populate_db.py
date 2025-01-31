from app import app, db
from models import ExamType, Class, Subject, Chapter
import json

def populate_database(recreate_db=True):
    with app.app_context():
        if recreate_db:
            db.drop_all()
            db.create_all()

        print("Database created")

        # Create exam types
        cbse = ExamType(name="CBSE", description="Central Board of Secondary Education")
        iit_jee = ExamType(name="IIT JEE", description="Indian Institutes of Technology Joint Entrance Examination")
        db.session.add_all([cbse, iit_jee])
        db.session.commit()
        print("Added Exam Type")
        
        with open("data/iit-syllabus.json") as f:
            data = json.load(f)
            data = data["IIT JEE Syllabus"]
            for class_name, class_data in data.items():
                class_ = Class(name=class_name, exam_type_id=iit_jee.id)
                db.session.add(class_)
                print(class_.name)
                for subject_name, chapters in class_data.items():
                    
                    subject = Subject.query.filter_by(name=subject_name, class_id=class_.id).first()
                    if subject is None:
                        subject = Subject(name=subject_name, class_id=class_.id)
                        db.session.add(subject)
                        db.session.commit()
                        print("Added ",subject)
                    for chapter in chapters:
                        db.session.add(Chapter(name=chapter, subject_id=subject.id))


        
        
        print("Added Chapters for IIT JEE")


        with open("data/syllabus.json") as f:
            syllabus_data = json.load(f)
            for class_name, class_data in syllabus_data.items():
                class_ = Class(name=class_name, exam_type_id=cbse.id)
                db.session.add(class_)
                print(class_.name)
                for subject_name, subject_data in class_data.items():
                    subject = Subject.query.filter_by(name=subject_name, class_id=class_.id).first()
                    if subject is None:
                        subject = Subject(name=subject_name, class_id=class_.id)
                        db.session.add(subject)
                        db.session.commit()
                        print("Added ",subject)
                    if isinstance(subject_data, dict):  # Check if it has 'part' element
                        for part, chapters_in_part in subject_data.items():
                            for chapter_name in chapters_in_part:
                                db.session.add(Chapter(name=chapter_name, subject_id=subject.id))   
                    else:
                        for chapter_name in subject_data:
                            db.session.add(Chapter(name=chapter_name, subject_id=subject.id))   

        print("Added Chapters for CBSE")

        chapters = Chapter.query.all ()
        for chapter in chapters:
            print("{},{},{},{}".format(chapter.subject.class_.exam_type.name,chapter.subject.class_.name,chapter.subject.name,chapter.name))
        db.session.commit()

if __name__ == "__main__":
    populate_database(recreate_db=True)
    print("Database populated successfully!")

