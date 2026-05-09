from flask import Flask, render_template, request, jsonify
from sqlalchemy import func, extract, distinct
from database import get_session
from models import Customer, Order, OrderDetail, Segment, Location, Product, SubCategory, Category

app = Flask(__name__)

def get_base_query(session, *entities):
    """
    Retorna una query base uniendo todas las tablas necesarias
    para procesar filtros y agregaciones.
    """
    return session.query(*entities)\
        .join(Order, OrderDetail.order_id == Order.order_id)\
        .join(Customer, Order.customer_id == Customer.customer_id)\
        .join(Segment, Customer.segment_id == Segment.segment_id)\
        .join(Location, Order.location_id == Location.location_id)\
        .join(Product, OrderDetail.product_pk == Product.product_pk)\
        .join(SubCategory, Product.subcategory_id == SubCategory.subcategory_id)\
        .join(Category, SubCategory.category_id == Category.category_id)

def apply_filters(query, request_args):
    """Aplica los filtros de segmentación en base a query params."""
    segment = request_args.get('segment')
    region = request_args.get('region')
    year = request_args.get('year')
    category = request_args.get('category')

    if segment and segment != 'All':
        query = query.filter(Segment.segment_name == segment)
    if region and region != 'All':
        query = query.filter(Location.region == region)
    if year and year != 'All':
        query = query.filter(extract('year', Order.order_date) == int(year))
    if category and category != 'All':
        query = query.filter(Category.category_name == category)
        
    return query

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/filters')
def get_filter_options():
    session = get_session()
    try:
        segments = [r[0] for r in session.query(Segment.segment_name).distinct().all()]
        regions = [r[0] for r in session.query(Location.region).distinct().all()]
        categories = [r[0] for r in session.query(Category.category_name).distinct().all()]
        years = [int(r[0]) for r in session.query(extract('year', Order.order_date)).distinct().all() if r[0]]
        
        return jsonify({
            'segments': sorted(segments),
            'regions': sorted(regions),
            'categories': sorted(categories),
            'years': sorted(years, reverse=True)
        })
    finally:
        session.close()

@app.route('/api/data')
def get_dashboard_data():
    session = get_session()
    try:
        # === 1. KPIs ===
        # Query base para order details (ventas)
        q_sales = apply_filters(get_base_query(session, 
            func.sum(OrderDetail.sales).label('total_sales'),
            func.count(distinct(Order.order_id)).label('total_orders'),
            func.count(distinct(Customer.customer_id)).label('active_customers')
        ), request.args).one()

        total_sales = float(q_sales.total_sales or 0)
        total_orders = int(q_sales.total_orders or 0)
        active_customers = int(q_sales.active_customers or 0)
        
        # Total de clientes registrados (sin filtros, solo total histórico)
        total_customers = session.query(func.count(Customer.customer_id)).scalar()

        avg_ticket = total_sales / total_orders if total_orders > 0 else 0
        avg_sales_per_customer = total_sales / active_customers if active_customers > 0 else 0

        kpis = {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'avg_ticket': round(avg_ticket, 2),
            'avg_sales_per_customer': round(avg_sales_per_customer, 2)
        }

        # === 2. Gráfico 1: Ventas por Segmento ===
        q_sales_segment = apply_filters(get_base_query(session, 
            Segment.segment_name, 
            func.sum(OrderDetail.sales)
        ), request.args).group_by(Segment.segment_name).all()
        
        ventas_por_segmento = [{'segment': r[0], 'sales': float(r[1])} for r in q_sales_segment]

        # === 3. Gráfico 2: Top 10 Clientes por Ventas ===
        q_top_10 = apply_filters(get_base_query(session, 
            Customer.customer_name, 
            func.sum(OrderDetail.sales)
        ), request.args).group_by(Customer.customer_name).order_by(func.sum(OrderDetail.sales).desc()).limit(10).all()
        
        top_10_clientes = [{'customer': r[0], 'sales': float(r[1])} for r in q_top_10]

        # === 4. Gráfico 3: Clientes por Región ===
        q_customers_region = apply_filters(get_base_query(session, 
            Location.region, 
            func.count(distinct(Customer.customer_id))
        ), request.args).group_by(Location.region).all()
        
        clientes_por_region = [{'region': r[0], 'customers': r[1]} for r in q_customers_region]

        # === 5. Gráfico 4: Ticket promedio por Segmento ===
        q_orders_segment = apply_filters(get_base_query(session, 
            Segment.segment_name, 
            func.sum(OrderDetail.sales),
            func.count(distinct(Order.order_id))
        ), request.args).group_by(Segment.segment_name).all()
        
        ticket_promedio_segmento = []
        for r in q_orders_segment:
            seg = r[0]
            val = float(r[1]) / r[2] if r[2] > 0 else 0
            ticket_promedio_segmento.append({'segment': seg, 'avg_ticket': round(val, 2)})

        # === 6. Tabla DataTables: Ranking de clientes ===
        q_table = apply_filters(get_base_query(session, 
            Customer.customer_name,
            Segment.segment_name,
            Location.region,
            func.count(distinct(Order.order_id)),
            func.sum(OrderDetail.sales),
            func.sum(OrderDetail.profit)
        ), request.args).group_by(Customer.customer_name, Segment.segment_name, Location.region).all()

        ranking_clientes = []
        for r in q_table:
            pedidos = r[3]
            ventas = float(r[4] or 0)
            ganancia = float(r[5] or 0)
            ticket = ventas / pedidos if pedidos > 0 else 0
            ranking_clientes.append({
                'customer_name': r[0],
                'segment': r[1],
                'region': r[2],
                'total_orders': pedidos,
                'total_sales': round(ventas, 2),
                'total_profit': round(ganancia, 2),
                'avg_ticket': round(ticket, 2)
            })

        return jsonify({
            'kpis': kpis,
            'ventas_por_segmento': ventas_por_segmento,
            'top_10_clientes': top_10_clientes,
            'clientes_por_region': clientes_por_region,
            'ticket_promedio_segmento': ticket_promedio_segmento,
            'ranking_clientes': ranking_clientes
        })

    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
