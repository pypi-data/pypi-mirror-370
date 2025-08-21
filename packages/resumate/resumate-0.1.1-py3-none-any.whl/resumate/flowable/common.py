# Global state for rendered details
rendered_details = []

def capture_details(flowable, x, y):
    """Capture rendering details for a flowable at given coordinates."""
    global rendered_details
    if hasattr(flowable, 'parent'):
        return
    
    # Store information about this flowable
    rendered_details.append({
        "x": x,
        "y": y,
        "flowable": flowable
    })

def get_rendered_details():
    """Get a copy of all rendered details."""
    global rendered_details
    return rendered_details.copy()

def clear_rendered_details():
    """Clear all rendered details."""
    global rendered_details
    rendered_details.clear()

def set_rendered_details(details):
    """Replace rendered details with new list."""
    global rendered_details
    rendered_details = details

# Export these functions
__all__ = [
    'capture_details',
    'rendered_details',
    'get_rendered_details',
    'clear_rendered_details',
    'set_rendered_details'
]