import threading


def my_constrain(value, lower_order, upper_order):
    value = value if value >= lower_order else lower_order 
    value = value if value <= upper_order else upper_order
    return value

def my_count_decimals(value):
    s = format(value, 'f')          
    s = s.rstrip('0').rstrip('.') 
    if '.' in s:
        return len(s.split('.')[1])
    else:
        return 0

def my_round(value, step_size):
    return round(value, my_count_decimals(step_size))

def start_timer(func, seconds, *args):
    timer = threading.Timer(seconds, func, args=args)
    timer.start()
    
