import multiprocessing

#print("load " + '/'.join(__file__.split('/')[-2:]))

# > The `Lock` class is a wrapper around the `multiprocessing.Lock` class
class Lock():
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.islocked = False
    
    def Acquire(self, block:bool=True) -> bool:
        """
        This function acquires the lock, blocking or non-blocking, depending on the value of the block
        argument
        
        :param block: If this is True, the thread will wait until the lock is unlocked. If this is
        False, the thread will return immediately with a value of False if the lock is locked, defaults
        to True
        :type block: bool (optional)
        :return: A boolean value. True is acquired while False not.
        """
        status = self.lock.acquire(block=block)
        if status == True:
            self.islocked = True 
        return status

    def Release(self):
        """
        The function releases the lock
        """
        if self.islocked == True:
            self.lock.release()
            self.islocked = False
    
    def IsLocked(self) -> bool:
        return self.islocked
    
    def __enter__(self):
        return self.Acquire() 
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.Release()
        except:
            pass

if __name__ == "__main__":
    from threading import Thread
    from time import sleep

    counter = 0

    def increase(by, lock):
        global counter

        with lock:
            local_counter = counter
            local_counter += by

            # sleep(0.1)

            counter = local_counter
            print(f'counter={counter}')

    lock = Lock()

    # create threads
    t1 = Thread(target=increase, args=(10, lock))
    t2 = Thread(target=increase, args=(20, lock))

    # start the threads
    t1.start()
    t2.start()

    # wait for the threads to complete
    t1.join()
    t2.join()

    print(f'The final counter is {counter}')