import shutil
import time
from pathlib import Path

from dotenv import dotenv_values

from r00adb import adb, Transport
from r00android_fake import generate_prop_by_country
from r00android_patch import PatchAPI
from r00arango_connector import AndroidDB
from r00arango_connector.tinder import DevicesDB
from r00docker import DockerClient
from r00flash.devices.G950.manager_boot import BootManager
from r00flash.devices.G950.manager_efs import EFSRecoveryMode
from r00flash.devices.G950.manager_firmware import FirmwareManager
from r00flash.devices.G950.manager_kernel import KernelManager
from r00logger import log, set_level
from r00pykit import time_it
from r00server import serv
from r00textutil import patch_file
from .tui_menu import MenuTui

FIRMWARE_ROOT_DIR = Path('/media/user/Android/Devices/GalaxyS8/Fireware/Android_9.0_SDK28/horizon_rom/patched')


def get_imei():
    for _ in range(10):
        imei_raw = adb.get_imei()
        try:
            if len(imei_raw) == 15:
                imei = int(imei_raw)
                return imei
            raise
        except Exception as e:
            log.warning(f"Invalid IMEI: {imei_raw}: {e}")
            time.sleep(2)
    return None


def ask_answers(db: DevicesDB, tui: MenuTui, model: str):
    if db.is_recovery is None:
        db.is_recovery = tui.is_recovery()

    if db.spath_recovery is None:
        db.spath_recovery = f'{model}/new_device/twrp.tar'

    if db.firmware_name is None:
        firmware_dir = tui.ask_firmware_name(FIRMWARE_ROOT_DIR)
        db.firmware_name = str(firmware_dir)
    else:
        firmware_dir = Path(db.firmware_name)

    if db.country_iso is None:
        db.country_iso = tui.ask_country_iso()

    if db.spath_magisk_zip is None:
        db.spath_magisk_zip = tui.ask_spath_magisk_zip()

    if db.proxy_server is None:
        db.proxy_server = tui.ask_proxy_server()

    if db.device_server is None:
        db.device_server = tui.ask_proxy_server()

    if db.proxy_service is None:
        proxy_service = tui.ask_proxy_service()
        db.proxy_service = proxy_service.lower()

    return db.is_recovery, db.spath_recovery, firmware_dir, db.country_iso, db.spath_magisk_zip


@time_it
def initialize_new_device(id_phone, model, recompile_kernel):
    set_level("TRACE")
    model = model.upper()
    id_phone = str(id_phone)
    docker = DockerClient('r00ft1h/horizon_pie:v2')
    db_roid = AndroidDB()
    device_db = DevicesDB(id_phone)
    fm = FirmwareManager()
    km = KernelManager(docker)
    bm = BootManager()
    em = EFSRecoveryMode(id_phone)
    patch = PatchAPI(model, docker)
    tui = MenuTui()

    is_recovery, spath_recovery, firmware_dir, country_iso, spath_magisk_zip = ask_answers(device_db, tui, model)

    # Recovery
    if is_recovery:
        log.info('Прошиваем recovery')
        lpath_recovery = serv.download(spath_recovery)
        fm.flash_recovery(lpath_recovery)
        device_db.is_recovery = False

    # Format data
    log.info("Format /data ...")
    adb.reboot(recovery_mode=True, reconnect=False)
    adb.switch_connect(Transport.ADB_USB)
    if not adb.is_recovery_mode(): raise ValueError("Я не вижу где твой TWRP")
    adb.twrp.wipe()

    # Generate build.prop
    war_files = firmware_dir.parent / 'war_files'
    prop_spath = f'configs/firmware/{model}.json'
    template_prop_path = serv.download(prop_spath)
    generated_params = generate_prop_by_country(template_prop_path, country_iso)
    csc_code = generated_params['ro.csc.sales_code']
    local_ip = f'192.168.1.{id_phone}'

    # -- SYSTEM ---
    #    Patch system build.prop's
    patch.system_prop(firmware_dir, generated_params)

    #    Patch system/omc/sales_code.dat
    sales_code_dat = firmware_dir / 'system/omc/sales_code.dat'
    patch_file(sales_code_dat, sales_code_dat.read_text().split('\n')[0], csc_code)

    # --- BOOT ---
    # Patch boot default.prop
    war_kernel = war_files / 'kernel'
    job_boot = firmware_dir / f'HoriOne/Kernel/{model}/boot.img'
    orig_boot = firmware_dir / f'HoriOne/Kernel/{model}/boot_orig.img'

    # Unpack boot.img
    boot_dir = bm.unpack(orig_boot)
    ramdisk = boot_dir / 'ramdisk'

    kernel_boot_host = f'{boot_dir}/split_img/boot.img-kernel'
    if not war_kernel.exists():
        recompile_kernel = True

    if recompile_kernel:
        # --- KERNEL ---
        log.info("Сборка ядра")
        kernel_env_path = serv.download('configs/firmware/kernel.env')
        kernel_env = dotenv_values(kernel_env_path)
        kernel_env['KBUILD_BUILD_HOST'] = generated_params['ro.build.user']
        km.start_container(is_new=True, env_data=kernel_env)
        patch.kernel_fake_bssid()
        patch.kernel_cmdline()
        patch.kernel_imei()
        patch.kernel_kallsyms()
        patch.kernel_location_nmea()
        patch.kernel_control_ipv6()
        patch.kernel_defconfig(is_debug=False, changelist=generated_params['ro.build.changelist'])
        patch.kernel_samsung_lsm()
        patch.kernel_uname(f'#1 SMP PREEMPT {generated_params['ro.build.date']}')
        km.build(no_clean=False)
        docker.copy_from_container('/root/horizon/arch/arm64/boot/Image', kernel_boot_host)
        shutil.copy(kernel_boot_host, war_kernel)
    else:
        log.info("Используем уже собранное ядро")
        shutil.copy(war_kernel, kernel_boot_host)

    # Patch boot default.prop
    patch.boot_prop_host(boot_dir, generated_params)
    bm.add_resetprop(ramdisk)  # atrace
    bm.enable_static_wifi(ramdisk, local_ip, device_db.gateway, '8.8.8.8', '8.8.4.4')
    bm.disable_setupwizard(ramdisk)
    bm.disable_ipv6(ramdisk)

    # Repack boot.img
    bm.repack(boot_dir, job_boot)

    # --- EFS ---
    mount_dir = em.mount()
    patch.efs_csc(mount_dir, csc_code)
    em.flash()

    # --- HORIZON FIRMWARE---
    updater_script = firmware_dir / 'META-INF/com/google/android/updater-script'
    bin_folder = firmware_dir / 'HoriOne/Bin'
    magisk_folder = firmware_dir / 'HoriOne/Root/Magisk'

    fm.remove_all_added_blocks_in_updater_script(updater_script)
    fm.add_magisk(updater_script, magisk_folder, device_db.spath_magisk_zip)
    fm.add_busybox(updater_script, bin_folder)  # /system/etc/busybox
    fm.add_magiskboot(updater_script, bin_folder)  # /system/etc/mboot
    fm.add_ssh_root(updater_script, bin_folder)  # llkd

    device_path = f'/sdcard/firmware.zip'

    firmware_zip = fm.create_firmware_zip(firmware_dir)
    adb.push(firmware_zip, device_path, timeout=1500)
    log.info("Устанавливаем прошивку...")
    adb.twrp.install_zip(device_path)
    time.sleep(70)
    adb.switch_connect(Transport.SSH)
    time.sleep(20)
    adb.reboot()
    time.sleep(15)

    # Set flag "Done" for setup_wifi.sh
    imei_orig = get_imei()
    if not imei_orig:
        raise ValueError("Не смог получить IMEI")
    imei_orig = str(imei_orig)

    log.debug('Отключаем запуск деактивации SetupWizard')
    adb.shell('touch /data/misc/wifi/.my_wifi_configured')
    adb.shell('chown system:system /data/misc/wifi/.my_wifi_configured')
    adb.shell('chmod 644 /data/misc/wifi/.my_wifi_configured')
    adb.shell('chcon u:object_r:wifi_data_file:s0 /data/misc/wifi/.my_wifi_configured')

    device_db.add_info_device(
        {
            "local_ip": local_ip,
            "gateway": device_db.gateway,
            "model_phone": model,
            "spath_prop": prop_spath,
            "dpath_magiskboot": "/system/etc/mboot",
            "dpath_busybox": "/system/etc/busybox",
            "dpath_resetprop": "/atrace",
            "imei_orig": imei_orig,
            "proxy_current": "",
            "general": False,
            "status": 'new'
        }
    )
    device_db.sort_document_keys()
    db_roid.add_tac_code(imei_orig, model)
