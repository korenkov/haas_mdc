import os, re, time, telnetlib

#========================================

class parametr:

    def __init__(self, name, command):
        self.name = name        # custom name of macro variable (for example: "x")
        self.command = command  # 4-digit macro variable number (for example: "5021")
        self.value = None       # result of measuring (for example: 182.633)
        self.__pattern = re.compile('[-+]?[0-9]*\.?[0-9]+', re.IGNORECASE)

    # parsing of string & convert value to float number
    # for example: text=">>MACRO, -182.633216" ==> self.value=-182.633
    def set_value(self, text):
        self.value = round(float(self.__pattern.findall(text)[0]), 3)

#========================================

# Network configuration
host = '172.21.16.35'
port = 5051
timeout = 5 # timeout in seconds

telnet = telnetlib.Telnet()

# Connection to CNC
try:
    telnet.open(host, port, timeout)
except Exception as err:
    telnet.close()
    print ('Connection time out')
    print(err)

# Set HAAS macro or system variables
variables = []
variables.append(parametr('x', 5021))       # Current X position in machine coordinates
variables.append(parametr('y', 5022))       # Current Y position in machine coordinates
variables.append(parametr('z', 5023))       # Current Z position in machine coordinates
variables.append(parametr('s', 3027))       # Spindle RPM
variables.append(parametr('timer', 3001))   # Millisecond timer

# Measuring with timeout=0.01 sec & wrile log-file
try:
    file = open('monitoring.log', 'w')

    while True:
        for item in variables:
            # send request
            telnet.write('?Q600 %s\r' % item.command)
            # get response: read all symbols & parse
            item.set_value(telnet.read_until('\r'))
        # output result as formatted string
        s = ''
        for x in variables:
            s += '{:>12}'.format( x.value )

        file.write(s + '\n')
        print(s)

        time.sleep(0.01)

# If press CTRL-C in terminal (exit from loop)
except KeyboardInterrupt:
    file.close()
    telnet.close()
    print("Catched KeyboardInterrupt exception")

# Close record & connection
file.close()
telnet.close()
