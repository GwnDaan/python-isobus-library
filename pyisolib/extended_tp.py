import math
import time
from j1939.controller_application import ControllerApplication
from j1939.message_id import MessageId
from j1939.parameter_group_number import ParameterGroupNumber


class ExtendedTP:
    """Represents the Extended Transport Protocol defined in ISO-11783:3. NOTE: only the outgoing part is implemented"""
    
    class ControlByte:
        RTS = 20 # Request to send
        CTS = 21 # Clear to send
        DPO = 22 # Data packet offset
        EOMA = 23 # End-of-Message acknowledgment
        ABORT = 255 # Coonnection abort
    
    class ConnectionAbortReason:
        BUSY = 1        # Already  in  one  or  more  connection  managed  sessions  and  cannot  support another
        RESOURCES = 2   # System  resources  were  needed  for  another  task  so  this  connection  managed session was terminated
        TIMEOUT = 3     # A timeout occured
        CTS_WHILE_DT = 4 # CTS messages received when data transfer is in progress
        #TODO: add the rest of reasons
        # 251..255 Per ISO 11783-7 definitions - but there are none?
    
    class Timeout:
        """Timeouts according ISO 11783-3"""
        Tr = 0.200 # Response Time
        Th = 0.500 # Holding Time
        T1 = 0.750
        T2 = 1.250
        T3 = 1.250
        T4 = 1.050
        # timeout for multi packet broadcast messages 50..200ms
        # Tb = 0.050
        
    class State:
        WAITING_CTS = 0        # waiting for CTS
        SENDING_IN_CTS = 1     # sending packages (temporary state)
        SENDING_BM = 2         # sending broadcast packages
        ABORTED = 3            # Aborted session
        COMPLETED = 4          # Successfully send data
    
    def __init__(self, ca: ControllerApplication, priority: int):
        self.ca = ca
        self.priority = priority
        
    def send(self, data_page, pdu_format, pdu_specific, data):
        pgn = ParameterGroupNumber(data_page, pdu_format, pdu_specific)
        
        message_size = len(data)
        self.total_num_packets = math.ceil(message_size / 7)

        # send RTS
        pgn.pdu_specific = 0  # this is 0 for peer-to-peer transfer
        self.pgn_target = pgn.value
        self.dest_address = pdu_specific
        # init new buffer for this connection
        # self._snd_buffer[buffer_hash] = {
        #         "pgn": pgn.value,
        #         "priority": priority,
        #         "message_size": message_size,
        #         "num_packages": num_packets,
        #         "data": data,
        #         "state": self.SendBufferState.WAITING_CTS,
        #         "deadline": time.time() + ExtendedTP.Timeout.T3,
        #         'src_address' : src_address,
        #         'dest_address' : pdu_specific,
        #         'next_packet_to_send' : 0,
        #         'next_wait_on_cts': 0,
        #     }
        self.deadline = time.time() + ExtendedTP.Timeout.T3
        self.state = ExtendedTP.State.WAITING_CTS
        self.next_packet_to_send = 0
        self.next_wait_on_cts = 0
        self.data = bytearray(data)

        self.ca.subscribe(self.listen_cm)        
        self.__send_rts(message_size)

        self.ca.add_timer(0, self.async_job)
        
    def async_job(self, _):
        next_wakeup = time.time() + 5.0 # wakeup in 5 seconds

        if self.deadline != 0:
            if self.deadline > time.time():
                if next_wakeup > self.deadline:
                    next_wakeup = self.deadline
            else:
                # deadline reached
                if self.state == self.State.WAITING_CTS:
                    print("Deadline WAITING_CTS reached for snd_buffer src 0x%02X dst 0x%02X", self.ca.device_address, self.dest_address)
                    self.__send_abort(ExtendedTP.ConnectionAbortReason.TIMEOUT)
                    self.state = ExtendedTP.State.ABORTED
                elif self.state == self.State.SENDING_IN_CTS:
                    while self.next_packet_to_send < self.total_num_packets:
                        offset = self.next_packet_to_send * 7
                        data = self.data[offset:]
                        if len(data) > 7:
                            data = data[:7]
                        else:
                            while len(data)<7:
                                data.append(255)
                        
                        self.next_packet_to_send += 1
                        data.insert(0, self.sequence_number)
                        self.sequence_number += 1
                        self.__send_dt(data)


                        # set end of message status
                        if self.next_packet_to_send == self.next_wait_on_cts:
                            # wait on next cts
                            self.state = ExtendedTP.State.WAITING_CTS
                            print(f"Send complete, current index {self.next_packet_to_send}")
                            self.deadline = time.time() + self.Timeout.T3
                            break
                        # elif self.minimum_tp_rts_cts_dt_interval != None:
                        #     self.deadline = time.time() + self.minimum_tp_rts_cts_dt_interval
                        #     break

                    # recalc next wakeup
                    if next_wakeup > self.deadline:
                        next_wakeup = self.deadline

        self.ca.add_timer(next_wakeup, self.async_job)

    def listen_cm(self, priority, pgn, src_address, timestamp, data):
        """Processes aa Extended Transport Protocol Connection Management (ETP.CM) message
        """
        # if pgn != ParameterGroupNumber(0, 200, self.ca.device_address).value:
        if pgn != 51200:
            return
        
        control_byte = data[0]
        # pgn = data[5] | (data[6] << 8) | (data[7] << 16)

        if control_byte == ExtendedTP.ControlByte.CTS:
            if self.state == ExtendedTP.State.SENDING_IN_CTS:
                print("Received CTS message but still sending, delaying...")
                time.sleep(ExtendedTP.Timeout.Th) # Delay CTS
                assert(self.state == ExtendedTP.State.WAITING_CTS)

            num_packages = data[1]
            next_package_number = int.from_bytes(data[2:6], 'little') - 1
            if num_packages == 0:
                # SAE J1939/21
                # receiver requests a pause
                print("CTS: requested timeout")
                self.deadline = time.time() + self.Timeout.Th
                self.ca.add_timer(0, self.async_job)
                return

            if num_packages > self.total_num_packets:
                print("CTS: Allowed more packets %d than complete transmission %d", num_packages, self.total_num_packets)
                num_packages = self.total_num_packets
            if next_package_number + num_packages > self.total_num_packets:
                print("CTS: Allowed more packets %d than needed to complete transmission %d", num_packages, self.total_num_packets - next_package_number)
                num_packages = self.total_num_packets - next_package_number

            self.next_wait_on_cts = self.next_packet_to_send + num_packages
            self.sequence_number = 1
            print(f"CTS: allowed {num_packages} more, index {next_package_number}, waitwhen {self.next_wait_on_cts}")

            self.__send_dpo(num_packages, next_package_number)
            self.state = ExtendedTP.State.SENDING_IN_CTS
            self.deadline = time.time()
            self.ca.add_timer(0, self.async_job)

        elif control_byte == ExtendedTP.ControlByte.EOMA:
            self.state = ExtendedTP.State.COMPLETED
            self.ca.add_timer(0, self.async_job)
            print("Job completed!")
        elif control_byte == ExtendedTP.ControlByte.ABORT:
            reason = data[1]
            print(f"CTS ABORTED: reason {reason}")
            
        else:
            raise RuntimeError(f"Received TP.CM with unknown control_byte {control_byte}")
    
    def __send_dt(self, data):
        pgn = ParameterGroupNumber(0, 199, self.dest_address)
        self.ca.send_message(self.priority, pgn.value, data)
    
    def __send_rts(self, message_size):
        pgn = ParameterGroupNumber(0, 200, self.dest_address)
        data = [ExtendedTP.ControlByte.RTS, message_size & 0xFF, (message_size >> 8) & 0xFF, (message_size >> 16) & 0xFF, (message_size >> 24) & 0xFF, self.pgn_target & 0xFF, (self.pgn_target >> 8) & 0xFF, (self.pgn_target >> 16) & 0xFF]
        self.ca.send_message(self.priority, pgn.value, data)
        
    def __send_dpo(self, num_packets, data_offset):
        pgn = ParameterGroupNumber(0, 200, self.dest_address)
        data = [ExtendedTP.ControlByte.DPO, num_packets, data_offset & 0xFF, (data_offset >> 8) & 0xFF, (data_offset >> 16) & 0xFF, self.pgn_target & 0xFF, (self.pgn_target >> 8) & 0xFF, (self.pgn_target >> 16) & 0xFF]
        self.ca.send_message(self.priority, pgn.value, data)

    def __send_abort(self, reason):
        pgn = ParameterGroupNumber(0, 200, self.dest_address)
        data = [ExtendedTP.ControlByte.ABORT, reason, 0xFF, 0xFF, 0xFF, self.pgn_target & 0xFF, (self.pgn_target >> 8) & 0xFF, (self.pgn_target >> 16) & 0xFF]
        self.ca.send_message(self.priority, pgn.value, data)