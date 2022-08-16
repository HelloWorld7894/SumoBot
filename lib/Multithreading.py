import threading
import ctypes

#initiate thread construction
class Thread_Inherit(threading.Thread):
    def __init(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target( *self._args, **self._kwargs )

    def join(self, *args):
        threading.Thread.join ( self, *args )
        return self._return

    def get_id(self):
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def kill(self): #really bad programming practice
        ID = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ID, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ID, 0)
            print("Failure killing thread")