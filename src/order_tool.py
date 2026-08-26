
import json

def get_order_status(order_id: str) -> str:
    """
    Look up the status, item, shipping date, and carrier of a customer's order by their order ID.
    
    Args:
        order_id (str): The unique order identifier (e.g., ORD-123, ORD-1007).
        
    Returns:
        str: JSON string containing order details or an error message if not found.
    """
    print(f"\n  [System: Tool executed -> get_order_status(order_id='{order_id}')]")
    
    # Comprehensive mock database matching official test cases & custom cases
    mock_db = {
        "ORD-123": {
            "order_id": "ORD-123",
            "status": "shipped",
            "item": "Breeze Tumbler",
            "shipping_date": "2026-08-20",
            "carrier": "UPS",
            "eta": "August 24, 2026"
        },
        "ORD-456": {
            "order_id": "ORD-456",
            "status": "processing",
            "item": "Ceramic Mug",
            "shipping_date": "TBD",
            "carrier": "Pending"
        },
        "ORD-1007": {
            "order_id": "ORD-1007",
            "status": "shipped",
            "item": "Standard Item",
            "shipping_date": "August 22, 2026",
            "carrier": "UPS",
            "eta": "August 26, 2026"
        },
        "ORD-1004": {
            "order_id": "ORD-1004",
            "status": "cancelled",
            "item": "Cancelled Item",
            "shipping_date": "N/A",
            "carrier": "N/A"
        }
    }
    
    # Normalize order_id lookup (case-insensitive)
    clean_id = order_id.strip().upper()
    order = mock_db.get(clean_id)
    
    if order:
        return json.dumps(order)
    
    return json.dumps({
        "error": f"Order ID '{order_id}' not found in the system. Please verify the order number."
    })