import serial
import time
import multiprocessing

# Change this to match your local settings
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 115200


class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)

    def open(self):
        if not self.sp.is_open:
            print "opening serial " + SERIAL_PORT
            self.sp.open()
            self.sp.flushInput()

    def reset(self):
        print "reopening serial " + SERIAL_PORT
        if self.sp.is_open:
            self.sp.close()
        self.sp.open()
        self.sp.flushInput()

    def close(self):
        print "closing serial " + SERIAL_PORT
        self.sp.close()
        self.sp = None

    def writeSerial(self, data):
        self.sp.write(bytes(data))
        # time.sleep(1)

    def readSerial(self):
        return self.sp.readline().replace("\n", "")

    def run(self):
        while True:
            # look for incoming serial data
            if self.sp.inWaiting() > 0:
                data = self.readSerial()
                print "recieved from serial: " + data
                # send it back to tornado
                self.output_queue.put(data)
                continue

            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()

                # send it to the serial device
                print "writing to serial: " + data
                self.writeSerial(data)
