import hashlib
import io
import socket

def get_name(uuid):
    m = hashlib.sha1()
    m.update(uuid.encode('utf-8'))
    n = int(m.hexdigest(), 16)

    try:
        with open("names.txt", "r") as f:
            lines = f.readlines()
            if not lines:
                return "default_name"  # Handle the case where the file is empty
            return lines[n % len(lines)].strip().lower()
    except FileNotFoundError:
        return "default_name"  # Handle the case where the file does not exist

def get_thing(secret):
    """Get dweet thing name from secret.
    """

    m = hashlib.sha1()
    m.update(secret.encode())

    return m.hexdigest()

pi_cached = None

def is_raspberry_pi(raise_on_errors=False):
    """Checks if Raspberry PI.
    Thanks https://raspberrypi.stackexchange.com/a/74541
    """

    global pi_cached

    if pi_cached != None:
        return pi_cached

    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            found = False
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    found = True
                    label, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value not in (
                        'BCM2708',
                        'BCM2709',
                        'BCM2835',
                        'BCM2836'
                    ):
                        if raise_on_errors:
                            raise ValueError(
                                'This system does not appear to be a '
                                'Raspberry Pi.'
                            )
                        else:
                            pi_cached = False
                            return False
            if not found:
                if raise_on_errors:
                    raise ValueError(
                        'Unable to determine if this system is a Raspberry Pi.'
                    )
                else:
                    pi_cached = False
                    return False
    except IOError:
        if raise_on_errors:
            raise ValueError('Unable to open `/proc/cpuinfo`.')
        else:
            pi_cached = False
            return False

    pi_cached = True
    return True

def get_ip():
    """Gets the IP address as a string.
    ty https://stackoverflow.com/a/1267524
    """

    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]