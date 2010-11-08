#!/usr/bin/env python

import sys, os, time, serial, threading

class ParallaxServo:
    def __init__(self, port, baudrate, parity, rtscts, xonxoff):
        try:
            self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
            print "OMGSRSLY: pyserial may be way too old here..."

        # Let's use the faster method of talking to the board... I mean, why not?
        # the board may already be in this state in which case we don't get the
        # command echoed back to us
        self.send("\r!SCSBR1\r", False)

        ## Need to wait for things to calm down on the board for some reason
        # Let command get flushed through the buffers etc
        time.sleep(0.04)
        # change the port baud rate
        self.baud(38400)
        # wait for thing to settle down
        time.sleep(0.08)
        # make sure no goonies exist
        self.flush_serial()

    def flush_serial(self):
        self.serial.flush()
        self.serial.flushInput()
        self.serial.flushOutput()

    def baud(self, newRate):
        backup = self.serial.baudrate
        try:
            self.serial.baudrate = newRate
        except ValueError, e:
            sys.stderr.write('--- ERROR setting baudrate: %s ---\n' % (e,))
            self.serial.baudrate = backup

    def position( self, chan, ramp, position ):
        """set the position of a channel"""
        p_low  = position & 255
        p_high = ( position >> 8 ) & 255
        self.send( "!SC" + chr(chan) + chr(ramp) + chr(p_low) + chr(p_high) + '\r' )

    # We should old expect a few valid sequences back form the board
    def decode( self, string ):
        """decode a string received from the board"""
        ret = ''
        for data in string:
            if data in '\r\n':
                ret += '\n'
            elif data in '!SCBRPEV?':
                ret += data
            else:
                ret += "\t%d " % ord(data)
        return ret

    # Send some data to the port and make sure we get it back in the same form we sent it
    # It seems that the act of waiting for the command to come back fixes issues with
    # incorrect/corrupted data being sent/received.
    def send(self, data, validate=True):
        """send some data to the serial port"""
        self.serial.write(data)
        read_back = self.serial.read(len(data))
        if validate and read_back != data:
            print "!! (%s)" % self.decode(read_back)

class ServoScriptHandler:
    def __init__(self, servo_controller):
        self.servo_controller = servo_controller
        self.commands = {
            'defaults': self.cmd_defaults,
            'nop':      self.cmd_nop,
            'set':      self.cmd_set,
            'sleep':    self.cmd_sleep,
        }

    def parse(self, command):
        if len(command) > 0:
            pieces = command.split()
            cmd = self.commands[pieces[0]]
            if cmd:
                cmd( pieces )
            return True
        return False

    def cmd_defaults(self, args):
        '''defaults
           sets all 16 servo channels to position "750"
           approx command time: 249 ms - 251 ms
        '''
        for chan in range(16):
            ramp     = 0
            position = 750
            self.servo_controller.position( chan, ramp, position )

    def cmd_nop(self, args):
        '''nop ...'''
        pass

    def cmd_set(self, args):
        '''set <chan> <ramp> <position>
           approx command time: 14.6 ms - 16.2 ms
        '''
        position = int(args[3])
        ramp = int(args[2])
        chan = int(args[1])
        self.servo_controller.position( chan, ramp, position )

    def cmd_sleep(self, args):
        '''sleep <num>
           num: time in seconds (can be a float)
        '''
        delay = float(args[1])
        time.sleep(delay)

def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "ParallaxServo - A simple terminal program for the serial port."
    )

    parser.add_option("-p", "--port",
        dest = "port",
        help = "port, a number (default 0) or a device name (deprecated option)",
        default = None
    )

    (options, args) = parser.parse_args()

    options.parity = 'N'
    port = options.port
    # Default baud on the Parallax board is 2400
    baudrate = 2400
    if args:
        if options.port is not None:
            parser.error("no arguments are allowed, options only when --port is given")
        port = args.pop(0)
        if args:
            try:
                baudrate = int(args[0])
            except ValueError:
                parser.error("baud rate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: port = 0

    try:
        servo_controller = ParallaxServo(
            port,
            baudrate,
            options.parity,
            rtscts=False,
            xonxoff=False,
        )
    except serial.SerialException, e:
        sys.stderr.write("could not open port %r: %s\n" % (port, e))
        sys.exit(1)

    servo_parser = ServoScriptHandler( servo_controller )
    # servo_parser.defaults()

    while servo_parser.parse( sys.stdin.readline() ):
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
