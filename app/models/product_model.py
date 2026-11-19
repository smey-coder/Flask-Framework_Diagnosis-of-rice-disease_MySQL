from extensions import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product {self.name}>"