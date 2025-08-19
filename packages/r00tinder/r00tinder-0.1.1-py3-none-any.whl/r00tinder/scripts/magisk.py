from r00android_patch import PatchAPI
from r00adb import adb, Transport

# boot_dir = '/media/user/Android/Devices/GalaxyS8/Fireware/Android_9.0_SDK28/horizon_rom/patched/source_combat/HoriOne/Kernel/G950/aik_boot_device'
# patch = PatchAPI('g950')
# patch.push_resetprop(boot_dir)


adb.connect(Transport.SSH, '192.168.1.68', 1030, 28)
adb.shell('/atrace -n ro.product.model "MyPhone"')
adb.shell('getprop ro.product.model')
