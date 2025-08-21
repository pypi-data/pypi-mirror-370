from reportlab.lib.pagesizes import letter
from reportlab.platypus import Frame,PageTemplate
from reportlab.lib.units import inch

def ucfirst(string):
    return string[0].upper() + string[1:] if string else ''
    
def get_style(name,style,styles):
    style=f"{name}_{style}"

    return styles[style]

def _eval_with_units(expression, frames={}):
    # Define units and dimensions
    page_width, page_height = letter

    # Create a local dictionary to include frames and global measurements
    frames['inch']= inch
    frames['page_width']= page_width
    frames['page_height']= page_height
    
    if not isinstance(expression, int):
        #print (expression)
        expression  = expression.replace("inch", "*inch")
        result = eval(expression  , {}, frames)
            
        #print (expression,":",result)
        return result
    # if its alreadyu calculated/int
    return expression
