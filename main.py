from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import  Product
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ['*']
)

database_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def greet():
    return "Welcome to Telusko Trac" 

products = [
    Product(id = 1, name = "Phone", description = "A SmartPhone", price = 699.99, quantity=50),
    Product(id = 2, name = "laptop", description = "A Powerful laptop", price = 999.99, quantity=30),
    Product(id = 5, name = "Pen", description = "A blue ink pen", price = 1.99, quantity=100),
    Product(id = 6, name = "Table", description = "A wooden table", price = 199.99, quantity=20),

]

# Dependancy Injection

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = session()
    try:
        count = db.query(database_models.Product).count()

        if count == 0:
            for product in products:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()



# here we are fetching all  the products 
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    
    db_products = db.query(database_models.Product).all()
   
    return db_products

# if id is in seq no missing id
'''
@app.get("/product")
def get_product_by_id():
    return products[0]
'''
# or id is not in seq then we create it dynamic
'''
@app.get("/product/{id}")
def get_product_by_id(id: int):
    return products[id-1]
'''
# here we are fetching product by its id
@app.get("/product/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
        db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
        if db_product:
            return db_product
        return "Product not found...!"
  

# to add records

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product

# to update record

@app.put("/products/{id}")
def update_product(id: int, product:Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product Updated"
    else:
        return "No product found"

# to delete record
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):

    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    else:
        return "Product not found"