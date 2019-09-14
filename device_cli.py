import paramiko
import time
import getpass
from IPy import IP


def rewriteprompt(typeofdev):
    elif typeofdev == "cucm":
        prompt = "admin:"

    elif typeofdev == "rpi":
        prompt = "pi@raspberrypi:"

    if typeofdev == "cisco ios":
        prompt = "#"


def getdevtype():
    devtype = input("What type of device is this? ")
    rewriteprompt(devtype)


def waitforprompt():
    print("\nWaiting for admin prompt.\n")
    while True:
        output = remote_conn.recv(5000)
        if prompt in str(output):
            print("Admin prompt received!!!!!\n")
            break


def waitfortermdata():
    sleep_sec = 5
    print("Waiting for output. Sleeping {} seconds.".format(sleep_sec))
    time.sleep(sleep_sec)


def getcmd():
    cmd = input("What command to run? ")
    return cmd


def getoutput(cmd_exec):
    print('\nTrying to get output from "{}".\n'.format(cmd_exec))
    remote_conn.send(cmd_exec + "\r")
    waitfortermdata()
    while True:
        output = remote_conn.recv(5000).decode('utf-8')
        if prompt in str(output):
            print("\n"*2)
            output_list = output.split("\r\n")
            formatbrackets = "\t{}\n"*len(output_list)
            print(formatbrackets.format(*output_list))
            break


def validIPonly():
    funcIPaddress = input("\nWhat is the IP address of the device? ")

    while True:
        try:
            IP(funcIPaddress)
            break
        except:
            funcIPaddress = input("\nThat doesn't seem valid.\nWhat is the IP address of the device? ")
            continue

    return funcIPaddress


def whattodo():
    tocloseornottoclose = input("\nWould you like to run another command (yes or no)? ").lower()

    if tocloseornottoclose == 'yes':
        command = getcmd()
        getoutput(command)
        whattodo()

    else tocloseornottoclose == 'no':
        remote_conn.close()

devip = validIPonly()
username = input("\nWhat is the username? ")
password = getpass.getpass("\nWhat is the password? ")


print("\nInitializing SSHClient.\n")
remote_conn_pre=paramiko.SSHClient()

print("Setting auto accept of host keys.\n")
remote_conn_pre.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())

print("Specifying parameters for connection.\n")
remote_conn_pre.connect(devip, username=username, password=password, look_for_keys=False, allow_agent=False)

print("Invoking the interactive shell.\n")
remote_conn = remote_conn_pre.invoke_shell()


prompt = ""

device = getdevtype()

waitforprompt()

command = getcmd()

getoutput(command)

whattodo()
