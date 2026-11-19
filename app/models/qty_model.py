from extensions import db

class Qty(db.Model):
    __tablename__ = "qtys"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Qty {self.name}>"