import time
import multiprocessing
import threading

win = multiprocessing.Event()

def worker(numberone):
    time.sleep(2)
    print(numberone)
    print("is a name")
    #do some work.
    win.set()

def function():
    # The gist is:
    # We have an important process. If we finish the important process before the timeout, then we can print the result.
    # If we don't we display timeout.
    print("starting...")

    p1 = multiprocessing.Process(target=worker, name="worker function", args=('fiddy',))
    p1.start()

    for i in range(5):
        time.sleep(1)
        print(i)
        print(p1.is_alive)
        if win.is_set():
            break
        
    if not win.is_set():
        print("Process still running after timeout. stopping...")
        p1.terminate()
    else:
        print("Display results of process...")
    
    
    print("done")
        

function()