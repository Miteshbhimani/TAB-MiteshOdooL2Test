{
    'name': 'Product Return Request',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage customer return requests linked to sale orders',
    'description': """
Product Return Request
=======================
Allows customers' return requests to be created against confirmed sale orders,
submitted for approval, and approved/rejected by users in the Return Manager group.

Features:
- Return request with reference number (RET/00001...)
- Validation so return quantity cannot exceed delivered quantity
- Approval workflow restricted to Return Manager group
- Chatter log on the related sale order when a return is approved
- Smart button on Sale Order showing related return requests
""",
    'author': 'Mitesh',
    'depends': ['sale', 'mail'],
    'data': [
        'security/return_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/product_return_request_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
