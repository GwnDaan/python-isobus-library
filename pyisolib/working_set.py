import j1939

from . import functions
from .pgns import PGNS
from .vt_objects.object_pool import ObjectPool

class WorkingSet:
    """WorkingSet for indentification to the virtual terminal (VT)."""
    
    class State:
        """The state of the working set, NOTE: it must be in increasing order"""
        NONE = 0
        UNKNOWN = 1
        AWAITING_VT_STATUS = 2
        ANNOUNCING_WORKING_MASTER = 3
        INIT_MAINTENANCE = 4
        AWAIT_HARDWARE = 5
        AWAIT_MEMORY = 6
        UPLOADING_POOL = 7
        AWAITING_POOL_COMPLETE = 8
        NORMAL = 9
        
    def __init__(self, ca: j1939.ControllerApplication):
        """
        :param ControllerApplication ca:
            The controller application class 
        """
        self.ca = ca
        self.state = WorkingSet.State.NONE
        self._object_pool = ObjectPool()
        
    def start(self):
        """Start the working set. The controller application must be started and the object pool set!
        """
        if self.ca.state != j1939.ControllerApplication.State.NORMAL:
            raise RuntimeError("ControllerApplication must be started before initializing WorkingSet!")
        
        if not self._object_pool.is_ready():
            raise RuntimeError("The object pool is not yet ready, make sure you added objects!")
        
        self.ca.subscribe(self._on_message)
        self.ca.add_timer(1, self._tick) # Send the maintenance message every second
        self.state = WorkingSet.State.AWAITING_VT_STATUS
        
    def add_object_to_pool(self, object):
        if self.state >= WorkingSet.State.UPLOADING_POOL:
            # TODO: implement realtime editing of pool
            raise NotImplementedError
        
        self._object_pool.add_object(object)
    
    def _next_state(self):
        """Set current state to next"""
        if self.state + 1 > WorkingSet.State.NORMAL:
            raise RuntimeError("Next state not possible as it is not defined.")
        else:
            self.state += 1
    
    def _on_message(self, priority, pgn, sa, timestamp, data):
        """Used to receive message from the VT.
        """
        if pgn == PGNS.VT_TO_ECU:
            # The format per message is different. However, the function format is common:
            # - byte 0: function
            function = data[0]
            if function == functions.Status.VT_STATUS:
                if self.state == WorkingSet.State.AWAITING_VT_STATUS:
                    self._next_state()
                    
            elif function == functions.TechinalData.GET_HARDWARE:
                assert self.state == WorkingSet.State.AWAIT_HARDWARE
                self.x_pixels = int.from_bytes(data[4:6], 'little')
                self.y_pixels = int.from_bytes(data[6:8], 'little')
                
                # We completed hardware state, next is memory
                self._next_state()
                self.send(PGNS.ECU_TO_VT, 7, 
                        # Data follows below: TODO: remove static memory of 200000 and calculate it
                        functions.TechinalData.GET_MEMORY, 0xFF, (200000).to_bytes(4, 'little'))
            
            elif function == functions.TechinalData.GET_MEMORY:
                assert self.state == WorkingSet.State.AWAIT_MEMORY
                self.vt_version = data[1]
                memory_error = data[2]
                
                # We check if the vt has enough memory. TODO reduce the requested memory size otherwise
                if memory_error == 1:
                    raise RuntimeError("Not enough memory available to hold our object pool!")
                else:
                    self._next_state()
            
            elif function == functions.TransferObjectPool.END_OF_POOL:
                error_code = data[1]
                if error_code != 0:
                    # The pool was not valid!
                    parent_faulty_object = int.from_bytes(data[2:4], 'little')
                    faulty_object = int.from_bytes(data[4:6], 'little')
                    object_pool_error_code = data[6]
                    raise RuntimeError(f"END_OF_POOL_ERROR: error {error_code}, parent_faulty_object {parent_faulty_object}, faulty_object {faulty_object}, object_pool_error {object_pool_error_code}")
                else:
                    self._next_state()
                    
    def _tick(self, _):
        """Check if we need to perform any actions"""
        
        # Announce the current working set as master if state is set
        if self.state == WorkingSet.State.ANNOUNCING_WORKING_MASTER:
            self.send(PGNS.WORKING_SET_MASTER, 7,
                      #Data follows below:
                      1, completer=0)
            self._next_state()
        
        # Send the maintenance message IFF the state is the init maintenance state or above
        if self.state >= WorkingSet.State.INIT_MAINTENANCE:
            initializing = self.state == WorkingSet.State.INIT_MAINTENANCE
            self.send(PGNS.ECU_TO_VT, 7, 
                    # Data follows below:
                    functions.Status.MAINTENANCE, 1 if initializing else 0)
            
            # Get hardware and set to next state if we are currently initializing.
            if initializing:
                self._next_state()
                self.send(PGNS.ECU_TO_VT, 7, 
                        # Data follows below:
                        functions.TechinalData.GET_HARDWARE)
        
        # Upload the object pool IFF the state is set
        if self.state == WorkingSet.State.UPLOADING_POOL:
            body = self._object_pool.get_data()
            self.send(PGNS.ECU_TO_VT, 7, 
                      # Data follows below:
                      functions.TransferObjectPool.TRANSFER, body)
            
            # Successfully uploaded the complete pool, tell the vt it is the end
            self.send(PGNS.ECU_TO_VT, 7, functions.TransferObjectPool.END_OF_POOL)
            self._next_state()
            
        
    def send(self, pgn, priority, *args, length=8, completer=0xFF):
        """Completes and sends the args as pgn.
        
        :param int pgn:
            The parameter group number (pgn) used
        :param list args:
            The data which will be sent
        :param int length:
            The length of the data which will be sent
        :param int completer:
            The value which will be appended to the data to get the length.
        """
        data = bytes(args) + bytes((completer for _ in range(length - len(args))))
        assert len(data) == length
        
        # Disasembling the pgn
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        
        # Send the actual pgn
        success = self.ca.send_pgn(data_page, pdu_format, pdu_specific, priority, data)
        if not success:
            raise RuntimeError("Sending pgn failed!")