import time 
import functools

def calculate_time(func):
    @functools.wraps(func)
    def timer(*args, **kwargs):
        time_start   = time.clock() 
        value        = func(*args, **kwargs) 
        time_end     = time.clock() 
        time_elapsed = time_end - time_start 
        print("\nScript Set up elapsed time: %f" %(time_elapsed))
        return value
    return timer 
