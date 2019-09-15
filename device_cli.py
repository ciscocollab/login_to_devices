import paramiko
import time
import getpass
from IPy import IP
import os
import sys
import re


def rewriteprompt(typeofdev):
    
    if typeofdev.lower() == "cucm":
        prompt = "admin:"

    elif typeofdev.lower() == "rpi":
        prompt = "pi@raspberrypi:"

    elif typeofdev.lower() == "cisco_ios":
        prompt = "#"

    else:
        print("Invalid entry. The entry can be cucm, rpi, or cisco_ios.")
        getdevtype()


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


def paramiko_bytes(passed_conn):
    strlist = str(passed_conn).split(" ")
    for item in strlist:
        match = re.search("in-buffer=(.*)", item)
        if match:
            buffered_bytes = match.group(1)
            return int(buffered_bytes)


def getoutput(cmd_exec):
    print('\nTrying to get output from "{}".\n'.format(cmd_exec))
    time.sleep(4)
    output = remote_conn.recv(paramiko_bytes(remote_conn)).decode('utf-8')
    remote_conn.send(cmd_exec + "\r")
    waitfortermdata()
    while True:
        output = remote_conn.recv(paramiko_bytes(remote_conn)).decode('utf-8')
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


def caniping(passedip):
    res = os.system("ping -c 1 " + passedip)
    if res == 0:
        return True
    else:
        shouldpingfail = input("\nPing failed.\nAre pings disabled on the device or blocked in some way?: ")
        if shouldpingfail.lower() == "yes":
            return True
        elif shouldpingfail.lower() == "no":
            print("\n\nThe script will terminate now. Run the script again, but use a different IP address which can ping.\n")
            sys.exit()
    

def whattodo():
    while True:
        tocloseornottoclose = input("\nWould you like to run another command (yes or no)? ").lower()

        if tocloseornottoclose == 'yes':
            command = getcmd()
            getoutput(command)
            continue

        elif tocloseornottoclose == 'no':
            remote_conn.close()
            print("\n\nThe remote connection was closed. The script will terminate now.\n")
            sys.exit()
        
        else:
            continue


devip = validIPonly()
print("\nChecking if the device is pingable.\n")
caniping(devip)
username = input("\nWhat is the username? ")
password = getpass.getpass("\nWhat is the password? ")


print("\nInitializing SSHClient.\n")
remote_conn_pre=paramiko.SSHClient()

print("Setting auto accept of host keys.\n")
remote_conn_pre.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())

print("Specifying parameters for connection.\n")
remote_conn_pre.connect(devip, username=username, password=password, look_for_keys=False, allow_agent=False, timeout=2,)

print("Invoking the interactive shell.\n")
remote_conn = remote_conn_pre.invoke_shell()


prompt = ""

device = getdevtype()

waitforprompt()

command = getcmd()

getoutput(command)

whattodo()

