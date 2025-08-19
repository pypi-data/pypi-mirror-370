import shutil
import string
import sys
from pathlib import Path

from r00adb import adb, Transport




def command(cmd: str):
    adb.connect(Transport.SSH, '192.168.1.68', 1030, 28)
    res = adb.shell(cmd, stream=False, log_off=True)
    print(res)

def find_prop():
    adb.connect(Transport.SSH, '192.168.1.68', 1030, 28)
    root_dir = '/dev/__properties__'
    output = adb.shell(f'ls -1 {root_dir}')
    for filename in output.split('\n'):
        filepath = root_dir + '/' + filename
        data_filepath = adb.shell(f'cat {filepath}', log_off=True)
        if 'product.model' in data_filepath:
            # Создаем новую строку, содержащую только печатные ASCII символы
            printable_data = ''.join(char for char in data_filepath if char in string.printable and char.isascii())
            print(printable_data)
        # if 'g950f' in data_filepath.lower():
        #     print(filepath)




def llkd():
    adb.connect(Transport.SSH, '192.168.1.68', 1030, 28)
    # adb.shell('chmod 755 /data/local/tmp/prop_trigger')
    # adb.shell('chmod +x /data/local/tmp/prop_trigger')
    #adb.shell('id')
    # adb.shell("/data/local/tmp/prop_trigger ro.crypto.state encrypted", ignore_errors=True)
    # adb.shell("/data/local/tmp/prop_trigger vold.has_quota 0", ignore_errors=True)
    # adb.shell("/data/local/tmp/prop_trigger sys.usb.config adb", ignore_errors=True)
    #adb.pull('/dev/__properties__/u:object_r:default_prop:s0', '/home/user/temp/default_prop.txt')
    # adb.shell("/data/local/tmp/prop_trigger ro.product.model 'SM-G999F'", ignore_errors=True)
    #adb.shell("/data/local/tmp/resetprop -n ro.product.model TEST", ignore_errors=True)
    #adb.shell("/data/local/tmp/resetprop -n ril.serialnumber XXXXXXXXXX", ignore_errors=True)
    adb.shell("ls -la /")
    # adb.shell("/resetprop -n ril.serialnumber XA-XA-XA", ignore_errors=True)
    # adb.shell("getprop ril.serialnumber")
    # res = adb.shell('dmesg | grep -E "(r00|prop_data)"', log_off=True, stream=False)
    # print(res)


if __name__ == '__main__':
    # install_magisk_mod()
    # exit()
    if len(sys.argv) == 2:
        command(sys.argv[1].strip())
    else:
        llkd()