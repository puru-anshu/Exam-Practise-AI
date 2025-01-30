from app import app, db
from models import ExamType, Class, Subject, Chapter
import json

def populate_database():
    with app.app_context():
        # Create exam types
        cbse = ExamType(name="CBSE", description="Central Board of Secondary Education")
        iit_jee = ExamType(name="IIT JEE", description="Indian Institutes of Technology Joint Entrance Examination")
        db.session.add_all([cbse, iit_jee])
        db.session.commit()
        print("Added Exam Type")
        # Create classes
        cbse_classes = [Class(name=f"Class {i}", exam_type_id=cbse.id) for i in range(9, 13)]
        iit_jee_classes = [Class(name="11th", exam_type_id=iit_jee.id), Class(name="12th", exam_type_id=iit_jee.id)]
        db.session.add_all(cbse_classes + iit_jee_classes)
        db.session.commit()
        print("Added Classes")

        # Create subjects
        cbse_subjects = ["Mathematics", "Physics", "Chemistry", "Computer Science"]
        iit_jee_subjects = ["Mathematics", "Physics", "Chemistry"]
        
        for class_ in cbse_classes:
            for subject_name in cbse_subjects:
                subject = Subject(name=subject_name, class_id=class_.id)
                db.session.add(subject)
                db.session.commit()
                
                with open("data/syllabus.json") as f:
                    data = json.load(f)
                    if class_.name in data:
                        for subject_name in cbse_subjects:
                            if subject_name in data[class_.name]:
                                for chapter_name in data[class_.name][subject_name]:
                                    chapter = Chapter(name=chapter_name, subject_id=subject.id)
                                    db.session.add(chapter)
                
                print("Added ",subject)
                db.session.commit()
                
            

        for class_ in iit_jee_classes:
            for subject_name in iit_jee_subjects:
                subject = Subject(name=subject_name, class_id=class_.id)
                db.session.add(subject)
                db.session.commit()
                # Load chapters from syllabus.json
                with open("data/syllabus.json") as f:
                    syllabus_data = json.load(f)
                
                if class_.name in syllabus_data and subject_name in syllabus_data[class_.name]:
                    chapters = [
                        Chapter(name=chapter_name, subject_id=subject.id)
                        for chapter_name in syllabus_data[class_.name][subject_name]
                    ]
                    db.session.add_all(chapters)

        db.session.commit()

def populate_chapters():
    with app.app_context():
        with open("data/syllabus.json") as f:
            syllabus_data = json.load(f)
        classes = Class.query.all()
        subjects = Subject.query.all()
        chapters = []
        for class_name, class_data in syllabus_data.items():
            class_ = next((c for c in classes if c.name == class_name), None)
            if class_ is None:
                print(f"Class {class_name} not found in database, skipping")
                continue
            
            for subject_name, subject_data in class_data.items():
                subject = next((s for s in subjects if s.name == subject_name and s.class_.id == class_.id), None)
                if subject is None:
                    print(f"Subject {subject_name} not found in database, skipping")
                    continue

                if isinstance(subject_data, dict):  # Check if it has 'part' element

                    for part, chapters_in_part in subject_data.items():
                        chapters.extend([
                            Chapter(name=chapter_name, subject=subject)
                            for chapter_name in chapters_in_part
                        ])
                else:
                    chapters.extend([
                        Chapter(name=chapter_name, subject=subject)
                        for chapter_name in subject_data
                    ])

                
        
        print(chapters)
        db.session.add_all(chapters)
        db.session.commit()


if __name__ == "__main__":
    # populate_database()
    populate_chapters()
    print("Database populated successfully!")

