import random
from datetime import date
from database import engine, get_session
from models import Base, Segment, Customer, Location, Category, SubCategory, Product, ShipMode, Order, OrderDetail

def seed_data():
    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    session = get_session()
    
    # Check if data already exists
    if session.query(Segment).count() > 0:
        print("Data already exists. Exiting.")
        session.close()
        return

    print("Inserting mock data...")
    # 1. Segments
    seg1 = Segment(segment_name="Consumer")
    seg2 = Segment(segment_name="Corporate")
    seg3 = Segment(segment_name="Home Office")
    session.add_all([seg1, seg2, seg3])
    session.flush()

    # 2. Customers
    cust1 = Customer(customer_id="C001", customer_name="Alice Anderson", segment_id=seg1.segment_id)
    cust2 = Customer(customer_id="C002", customer_name="Bob Brown", segment_id=seg2.segment_id)
    cust3 = Customer(customer_id="C003", customer_name="Charlie Clark", segment_id=seg3.segment_id)
    cust4 = Customer(customer_id="C004", customer_name="David Doe", segment_id=seg1.segment_id)
    session.add_all([cust1, cust2, cust3, cust4])

    # 3. ShipModes
    sm1 = ShipMode(ship_mode_name="Standard Class")
    sm2 = ShipMode(ship_mode_name="First Class")
    session.add_all([sm1, sm2])
    session.flush()

    # 4. Locations
    loc1 = Location(country="USA", city="New York", state="NY", postal_code="10001", region="East")
    loc2 = Location(country="USA", city="Los Angeles", state="CA", postal_code="90001", region="West")
    loc3 = Location(country="USA", city="Chicago", state="IL", postal_code="60007", region="Central")
    loc4 = Location(country="USA", city="Houston", state="TX", postal_code="77001", region="South")
    session.add_all([loc1, loc2, loc3, loc4])
    session.flush()

    # 5. Categories & Subcategories
    cat1 = Category(category_name="Technology")
    cat2 = Category(category_name="Furniture")
    cat3 = Category(category_name="Office Supplies")
    session.add_all([cat1, cat2, cat3])
    session.flush()

    sub1 = SubCategory(subcategory_name="Phones", category_id=cat1.category_id)
    sub2 = SubCategory(subcategory_name="Chairs", category_id=cat2.category_id)
    sub3 = SubCategory(subcategory_name="Binders", category_id=cat3.category_id)
    session.add_all([sub1, sub2, sub3])
    session.flush()

    # 6. Products
    p1 = Product(product_code="TEC-PH-100", product_name="iPhone 13", subcategory_id=sub1.subcategory_id)
    p2 = Product(product_code="FUR-CH-200", product_name="Office Chair", subcategory_id=sub2.subcategory_id)
    p3 = Product(product_code="OFF-BI-300", product_name="Avery Binders", subcategory_id=sub3.subcategory_id)
    session.add_all([p1, p2, p3])
    session.flush()

    # 7. Orders
    o1 = Order(order_id="ORD-2023-01", order_date=date(2023, 5, 10), ship_date=date(2023, 5, 15),
               customer_id=cust1.customer_id, ship_mode_id=sm1.ship_mode_id, location_id=loc1.location_id)
    o2 = Order(order_id="ORD-2023-02", order_date=date(2023, 6, 20), ship_date=date(2023, 6, 22),
               customer_id=cust2.customer_id, ship_mode_id=sm2.ship_mode_id, location_id=loc2.location_id)
    o3 = Order(order_id="ORD-2022-03", order_date=date(2022, 1, 10), ship_date=date(2022, 1, 12),
               customer_id=cust3.customer_id, ship_mode_id=sm1.ship_mode_id, location_id=loc3.location_id)
    o4 = Order(order_id="ORD-2022-04", order_date=date(2022, 11, 5), ship_date=date(2022, 11, 10),
               customer_id=cust4.customer_id, ship_mode_id=sm1.ship_mode_id, location_id=loc4.location_id)
    o5 = Order(order_id="ORD-2021-05", order_date=date(2021, 3, 15), ship_date=date(2021, 3, 20),
               customer_id=cust1.customer_id, ship_mode_id=sm2.ship_mode_id, location_id=loc1.location_id)
    session.add_all([o1, o2, o3, o4, o5])
    session.flush()

    # 8. Order Details
    od1 = OrderDetail(row_id=1, order_id=o1.order_id, product_pk=p1.product_pk, sales=1200.0, quantity=2, discount=0.0, profit=300.0)
    od2 = OrderDetail(row_id=2, order_id=o1.order_id, product_pk=p2.product_pk, sales=350.5, quantity=1, discount=0.1, profit=50.0)
    od3 = OrderDetail(row_id=3, order_id=o2.order_id, product_pk=p1.product_pk, sales=2400.0, quantity=4, discount=0.05, profit=580.0)
    od4 = OrderDetail(row_id=4, order_id=o3.order_id, product_pk=p3.product_pk, sales=45.0, quantity=5, discount=0.0, profit=20.0)
    od5 = OrderDetail(row_id=5, order_id=o4.order_id, product_pk=p2.product_pk, sales=700.0, quantity=2, discount=0.15, profit=80.0)
    od6 = OrderDetail(row_id=6, order_id=o5.order_id, product_pk=p3.product_pk, sales=90.0, quantity=10, discount=0.0, profit=40.0)
    session.add_all([od1, od2, od3, od4, od5, od6])

    session.commit()
    session.close()
    print("Mock data inserted successfully!")

if __name__ == "__main__":
    seed_data()
