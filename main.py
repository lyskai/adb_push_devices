from lib.device import *
from lib.shell import *
import os
import sys, getopt
import argparse
import time

device_id = ""
push_only = False
tools_source_folder = "D:\\tool\\0_push_tool"

def parse_option():
    # Fix me: what's the graceful way to handle global variable
    global push_only
    global device_id
    global tools_source_folder
    parser = argparse.ArgumentParser()
    #parser.add_argument("square", type=int,
    #                help="display a square of a given number")
    parser.add_argument("-d", "--device_id", help="the device we want operate")
    parser.add_argument("-p", "--push_only", action="store_true", help="push tool only, don't reboot device")
    parser.add_argument("-s", "--source_folder", help="tools source folder", default = tools_source_folder)
    args = parser.parse_args()
    if args.push_only:
        push_only = True
    device_id = args.device_id

if __name__ == "__main__":
    parse_option()
    # if there is device id paramter, then use user setting
    # else if only one device then use default
    # otherwise ask user to input
    dev_list = []
    dev_list = adb_devices()
    if device_id:
        if device_id not in dev_list:
            print("device %s is not enuneramted !!!"%(device_id))
            print("current device id ", dev_list)
            exit()
    elif len(dev_list) == 1:
        device_id = dev_list[0]
    elif len(dev_list) == 0:
        print("No devices found, pls recheck")
        exit()
    else:
        print("there are multiple devices, pls select correct on by index")
        idx = 0
        for dev in dev_list:
            print("  %d: dev %s"%(idx, dev))
            idx = idx+1
        try:
            idx = int(input("selection:"))
        except ValueError:
            print("selection is invalid, pls input Integer.")
            exit()
        if idx not in range(0, len(dev_list)):
            print("selection %d is not in range [0, %d], exit\n"%(idx, len(dev_list)-1))
            exit()
        device_id = dev_list[idx]

    print("selected id is: ", device_id)

    adb_root(device_id)
    adb_disable_verity(device_id)

    if not push_only:
        reboot = input("device will reboot, to let disable verity take effect, Y/N ?")
        if reboot.lower() == "y":
            # according output log to device reboot or not
            adb_reboot(device_id)

    adb_wait_for_device(device_id)
    time.sleep(1)
    adb_root(device_id)
    time.sleep(1)
    adb_remount(device_id)
    adb_mount(device_id, "/system")

    file_list = {"iperf" : 0, "iwpriv" : 0, "datatop" : 0, "mpstat" : 0, "lspci" : 0, "setpci" : 0, "perf" : 0}
    path = "/system/bin"
    # fix: should clarify source folder of tools or not

    for file in file_list:
        ret = adb_push(device_id, os.path.join(tools_source_folder, file), path)
        if not ret:
            adb_chmod_exec(device_id, file, path)
            file_list[file] = 1
        else:
            print("file or folder doesn't exist folder %s file %s"%(tools_source_folder, file))

    adb_sync(device_id)

    print("============== push status ==============")
    for file in file_list:
        print("file %s push %s"%(file, "success "if file_list[file] else "===========> failed"))
    print("=========================================")
    input("exit ?")
