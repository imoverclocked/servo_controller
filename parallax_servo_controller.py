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
            'chan_alias': self.cmd_chan_alias,
            'chan_range': self.cmd_chan_range,
            'defaults':   self.cmd_defaults,
            'echo':       self.cmd_echo,
            '#':          self.cmd_nop,
            'nop':        self.cmd_nop,
            'pos':        self.cmd_pos,
            'set':        self.cmd_set,
            'sleep':      self.cmd_sleep,
        }
        # We can alias names to specific channels
        self.__channel_aliases = {}
        # We have the default range for each servo (320-1180)
        # but some servos and some setups need that range to be tweaked for
        # optimal positioning
        self.__channel_ranges = {}
        # Watch to see what commands we are getting
        self.__verbose = False

    def parse(self, command):
        if len(command) > 0:
            if len(command) <= 1:
                return True

            pieces = command.split()
            if pieces[0][0] == '#':
                pieces[0] = '#'

            if self.__verbose:
                print command,

            try:
                cmd = self.commands[pieces[0]]
            except:
                self.warn("unrecognized command: %s" % pieces[0])
                cmd = self.commands['nop']

            try:
                cmd( pieces )
            except:
                self.warn("Error while executing command: %s" % (command))
                raise

            return True
        return False

    def warn(self, mesg):
        print "Warning: %s" % (mesg)

    def chan_alias(self, chan_name, chan=None):
        ''' get/set the channel for an alias '''
        if chan != None:
            self.__channel_aliases[ chan_name ] = chan
        try:
            return self.__channel_aliases[ chan_name ]
        except:
            return None

    def chan_range(self, chan_name, range=None):
        ''' get/set the range for a channel '''
        if range != None:
            self.__channel_ranges[ chan_name ] = range
        try:
            return self.__channel_ranges[ chan_name ]
        except:
            return [ 320, 1180, 750 ]

    def cmd_chan_alias(self, args):
        '''chan_alias <alias> <chan>
           sets a name to easily reference a channel
        '''
        self.chan_alias( args[1], int(args[2]))

    def cmd_chan_range(self, args):
        '''chan_range <alias> <min> <max> <default>
           sets a range beyond the default for a chan_alias
           the default range is 320 1180 750
        '''
        self.chan_range( args[1], [ int(args[2]), int(args[3]), int(args[4]) ] )

    def cmd_defaults(self, args):
        '''defaults
           sets all 16 servo channels to position "750"
           approx command time: 249 ms - 251 ms
        '''
        for chan in range(16):
            ramp     = 0
            position = 750
            self.servo_controller.position( chan, ramp, position )

    def cmd_echo(self, args):
        '''echo [args]
           send a string to stdout
        '''
        args.pop(0)
        print " ".join(args)

    def cmd_nop(self, args):
        '''nop ...'''
        pass

    def cmd_pos(self, args):
        '''pos <chan> <ramp> <position>
           approx command time: 14.6 ms - 16.2 ms
        '''

        try:
            chan = int(args[1])
            chan_range = [ 320, 1180, 750 ]
        except ValueError:
            chan_name = args[1]
            chan = self.chan_alias( chan_name )
            chan_range = self.chan_range( chan_name )

        ramp = int(args[2])

        try:
            position_float = float(args[3])
            position = (chan_range[1] - chan_range[0])*position_float
            position = int( position ) + chan_range[0]
        except ValueError:
            if args[3] == 'default':
                position = chan_range[2]
            else:
                raise

        self.servo_controller.position( chan, ramp, position )

    def cmd_sleep(self, args):
        '''sleep <num>
           num: time in seconds (can be a float)
        '''
        delay = float(args[1])
        time.sleep(delay)

    def cmd_set(self, args):
        '''set <var> <value>
           set some variable name to some value
           eg: set verbose True
        '''
        var = args[1]
        value = args[2]
        if var == 'verbose':
            if value == 'True':
                self.__verbose = True
            else:
                self.__verbose = False

def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] < script",
        description = "ParallaxServo - A simple terminal program for the serial port."
    )

    parser.add_option("-p", "--port",
        dest = "port",
        help = "port, a number (default 0) or a device name (deprecated option)",
        default = 0
    )

    (options, args) = parser.parse_args()

    options.parity = 'N'
    port = options.port
    # Default baud on the Parallax board is 2400
    baudrate = 2400
    # if args:
    #     script_fn = args.pop(0)

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
