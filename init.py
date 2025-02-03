from app import app, db
from models import Chapter

with app.app_context():
    # db.drop_all()
    # db.create_all()

    chapters = Chapter.query.all ()
    lines = []
    lines.append("Type,Class,Subject,Chapter")
    for chapter in chapters:
        lines.append("{},{},{},\"{}\"".format(chapter.subject.class_.exam_type.name,chapter.subject.class_.name,chapter.subject.name,chapter.name))
    with open("data/courses.csv", "w") as f:
        f.write("\n".join(lines))
