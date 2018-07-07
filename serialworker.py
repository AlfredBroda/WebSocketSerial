import serial
import time
import multiprocessing

## Change this to match your local settings
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 115200

class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = None

    def open(self):
        print "opening serial " + SERIAL_PORT
        self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        #TODO: Determine if flushing is required
        self.sp.flushInput()

    def close(self):
        if self.sp:
            print "closing serial " + SERIAL_PORT
            self.sp.close()
            self.sp = None
        else:
            print "serial " + SERIAL_PORT + " is not open, cannot close"

    def writeSerial(self, data):
        if self.sp:
            self.sp.write(bytes(data))
            # time.sleep(1)
        else:
            print "serial " + SERIAL_PORT + " is not open, cannot write"

    def readSerial(self):
        if self.sp:
            return self.sp.readline().replace("\n", "")
        else:
            print "serial " + SERIAL_PORT + " is not open, cannot read"
            return ""

    def flushInput(self):
        if self.sp:
    	    self.sp.flushInput()

    def run(self):
        # self.sp.flushInput()

        while True:
            # look for incoming serial data
            if (self.sp and self.sp.inWaiting() > 0):
            	data = self.readSerial()
                print "reading from serial: " + data
                # send it back to tornado
            	self.output_queue.put(data)
                continue

            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()

                # send it to the serial device
                self.writeSerial(data)
                print "writing to serial: " + data
