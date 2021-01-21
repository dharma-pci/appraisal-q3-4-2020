{
    "name": "Sale Delivery by Date",
    "version": "13.0.1.0.0",
    "author": "Port Cities",
    "website": "https://www.portcities.net",
    "category": "Sales",
    "summary": "Make delivery order date automatically generated based on described delivery date on each sale order line",
    "description": """
        author : MFM <fakhry@portcities.net>\n
    """,
    "depends": [
        'sale_stock', 
    ],
    "data": [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    "qweb": [],
    "active": False,
    "installable": True,
    "application": False,
    "auto_install": False
}
