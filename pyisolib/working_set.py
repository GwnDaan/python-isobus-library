import j1939

from . import functions
from .extended_tp import ExtendedTP
from .technical_data import TechnicalData
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
        AWAIT_SOFT_KEYS = 7
        UPLOADING_POOL = 8
        AWAITING_POOL_COMPLETE = 9
        NORMAL = 10
        
    def __init__(self, ca: j1939.ControllerApplication):
        """
        :param ControllerApplication ca:
            The controller application class 
        """
        self.ca = ca
        self.__state = WorkingSet.State.NONE
        self.__object_pool = ObjectPool()
        self.technical_data = TechnicalData()
        self.__listeners = []
        self.__function_listeners = []

    @property
    def state(self):
        return self.__state

    def add_listener(self, listener, is_function_listener: bool):
        """The function provided will be called with a packed recieved in the canbus
        :param listener:
            Should have the 'pgn/function' and 'data' parameter
        :param bool is_event_listener:
            Whether this is an event listener or not
        """
        if is_function_listener:
            self.__function_listeners.append(listener)
        else:
            self.__listeners.append(listener)
        
    def start(self):
        """Start the working set. The controller application must be started and the object pool set!
        """
        if self.ca.state != j1939.ControllerApplication.State.NORMAL:
            raise RuntimeError("ControllerApplication must be started before initializing WorkingSet!")
        
        self.__object_pool.cache_data()
        if not self.__object_pool.is_ready():
            raise RuntimeError("The object pool is not yet ready, make sure you added objects!")
        
        self.ca.subscribe(self.__on_message)
        self.ca.add_timer(1, self.__tick, cookie=self.ca) # Send the maintenance message every second
        self.__state = WorkingSet.State.AWAITING_VT_STATUS
        
    def add_object_to_pool(self, object):
        if self.__state >= WorkingSet.State.UPLOADING_POOL:
            # TODO: implement realtime editing of pool
            raise NotImplementedError()
        
        self.__object_pool.add_object(object)
    
    def __next_state(self):
        """Set current state to next"""
        if self.__state + 1 > WorkingSet.State.NORMAL:
            raise RuntimeError("Next state not possible as it is not defined.")
        else:
            self.__state += 1
    
    def __on_message(self, priority, pgn, sa, timestamp, data):
        """Used to receive message from the VT.
        """
        if pgn == PGNS.VT_TO_ECU:
            # The format per message is different. However, the function format is common:
            # - byte 0: function
            function = data[0]
            if function == functions.Status.VT_STATUS:
                if self.__state == WorkingSet.State.AWAITING_VT_STATUS:
                    self.__next_state()
                    
            elif function == functions.TechinalData.GET_HARDWARE:
                assert self.__state == WorkingSet.State.AWAIT_HARDWARE
                self.technical_data.screen_width = int.from_bytes(data[4:6], 'little')
                self.technical_data.screen_height = int.from_bytes(data[6:8], 'little')
                
                # We completed hardware state, next is memory
                self.__next_state()
                mem_required = len(self.__object_pool.cached_data)
                print(f"Requesting memory info: {mem_required} bytes")
                self.send_to_vt(functions.TechinalData.GET_MEMORY, 0xFF, mem_required.to_bytes(4, 'little'))
            
            elif function == functions.TechinalData.GET_MEMORY:
                assert self.__state == WorkingSet.State.AWAIT_MEMORY
                self.technical_data.vt_version = data[1]
                memory_error = data[2]
                
                # We check if the vt has enough memory. TODO reduce the requested memory size otherwise
                if memory_error == 1:
                    raise RuntimeError("Not enough memory available to hold our object pool!")
                else:
                    # We completed memory state, next is soft keys
                    self.__next_state()
                    print("Requesting softkey info")
                    self.send_to_vt(functions.TechinalData.GET_SOFT_KEYS)            
                    
            elif function == functions.TechinalData.GET_SOFT_KEYS:
                assert self.__state == WorkingSet.State.AWAIT_SOFT_KEYS
                self.technical_data.soft_key_width = data[4]
                self.technical_data.soft_key_height = data[5]
                self.technical_data.soft_key_virtual_amount = data[6]
                self.technical_data.soft_key_physical_amount = data[7]
                
                self.__next_state()
            elif function == functions.TransferObjectPool.END_OF_POOL:
                error_code = data[1]
                if error_code != 0:
                    # The pool was not valid!
                    parent_faulty_object = int.from_bytes(data[2:4], 'little')
                    faulty_object = int.from_bytes(data[4:6], 'little')
                    object_pool_error_code = data[6]
                    raise RuntimeError(f"END_OF_POOL_ERROR: error {error_code}, parent_faulty_object {parent_faulty_object}, faulty_object {faulty_object}, object_pool_error {object_pool_error_code}")
                else:
                    self.__next_state()
            else:
                for listener in self.__function_listeners:
                    listener(function, data[1:])
        else:
            for listener in self.__function_listeners:
                listener(pgn, data)
                    
    def __tick(self, _):
        """Check if we need to perform any actions"""
        
        # Announce the current working set as master if state is set
        if self.__state == WorkingSet.State.ANNOUNCING_WORKING_MASTER:
            self.send(PGNS.WORKING_SET_MASTER, 7,
                      #Data follows below:
                      1, completer=0)
            self.__next_state()
        
        # Send the maintenance message IFF the state is the init maintenance state or above
        elif self.__state >= WorkingSet.State.INIT_MAINTENANCE:
            initializing = self.__state == WorkingSet.State.INIT_MAINTENANCE
            self.send_to_vt(functions.Status.MAINTENANCE, 1 if initializing else 0)
            
            # Get hardware and set to next state if we are currently initializing.
            if initializing:
                self.__next_state()
                print("Requesting hardware info")
                self.send_to_vt(functions.TechinalData.GET_HARDWARE)
        
        # # Upload the object pool IFF the state is set
        if self.__state == WorkingSet.State.UPLOADING_POOL:
            etp = self.send_to_vt(functions.TransferObjectPool.TRANSFER, self.__object_pool.cached_data)
            print(f"Uploading pool data (using etp: {etp is not None})")

            # Successfully uploaded the complete pool, tell the vt it is the end
            self.ca.add_timer(1 if etp else 15, self.send_end_of_pool, etp)
            self.__next_state()
        
        return True
    
    def send_end_of_pool(self, etp):
        if isinstance(etp, ExtendedTP):
            if etp.state != ExtendedTP.State.COMPLETED:
                return True # Request to run this again in the future
        print("Sending end of pool message")
        self.send_to_vt(functions.TransferObjectPool.END_OF_POOL)
    
    def send_to_vt(self, *data, length=8, completer=0xFF):
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
        return self.send(PGNS.ECU_TO_VT, 7, *data, length=length, completer=completer)
                    
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
        # Assert that we can actually send data
        if self.__state <= WorkingSet.State.AWAITING_VT_STATUS:
            raise RuntimeError("WorkingSet not yet ready to send data", self.__state)

        data = bytes(0)
        for element in args:
            data += element if isinstance(element, bytes) else bytes([element])
       
       # We only need to complete if len of data is less than length.
       # The transport protocol and extended transport protocol will handle it themselves
        if len(data) < length:
            data += bytes((completer for _ in range(length - len(data))))
        
        # Disasembling the pgn
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        
        # Send the actual pgn, if length is 1786 we use ETP otherwise we use j1939 python module to send it
        if len(data) >= 1786:
            etp = ExtendedTP(self.ca, priority)
            etp.send(data_page, pdu_format, pdu_specific, data)
            return etp
        else:
            success = self.ca.send_pgn(data_page, pdu_format, pdu_specific, priority, bytearray(data))
            if not success:
                raise RuntimeError("Sending pgn failed!")
