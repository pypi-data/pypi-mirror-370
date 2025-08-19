import time
from typing import Optional

import dsnparse

from r00adb import adb, Transport
from r00android_fake import generate_prop_by_ipinfo, get_fake_imei
from r00android_patch import PatchDeviceAPI
from r00arango_connector.tinder import DevicesDB
from r00logger import log
from r00proxy.api import ProxyAPI
from r00arango_connector.globaldb.android import AndroidDB
from r00server import serv
from r00pykit import time_it

class Session:
    def __init__(self, id_phone: str):
        self.id_phone = str(id_phone)
        self.device_db = DevicesDB(self.id_phone)
        self.android_db = AndroidDB()
        self.proxy_api = ProxyAPI(self.device_db)
        self.patch = PatchDeviceAPI(self.device_db.model_phone, self.id_phone)
        self.generated_props: Optional[dict] = None
        self.proxydsn: Optional[dsnparse.ParseResult] = None
        self.new_imei = None

    @time_it
    def create_new(self):
        self.proxydsn = self.proxy_api.start_proxy_on_device()
        self.generated_props = self.generate_props_by_ip()

        if adb.is_recovery_mode():
            adb.reboot(reconnect=False)
            adb.switch_connect(Transport.SSH)

        self.patch_device_before_reboot()
        adb.reboot()
        self.patch_device_after_reboot()
        self.check_emulated()
        adb.clear_sdcard()
        log.info("Сессия создана. Маскировка применена.")

    def generate_props_by_ip(self):
        template_prop_path = serv.download(self.device_db.spath_prop)
        return generate_prop_by_ipinfo(template_prop_path, self.proxydsn.host, self.proxydsn.port)

    def patch_device_before_reboot(self):
        tac_code = self.android_db.get_tac_code(self.device_db.model_phone)
        self.new_imei = get_fake_imei(tac_code)
        self.patch.unpack_boot()
        self.patch.extract_default_prop()
        self.patch.extract_init_rc()
        self.patch.update_default_prop(self.generated_props)
        self.patch.inject_prop_initrc(self.generated_props)
        self.patch.inject_imei(self.device_db.imei_orig, self.new_imei)
        self.patch.repack_default_prop()
        self.patch.repack_init_rc()
        self.patch.firmware_boot()

        csc = self.generated_props['ro.csc.sales_code']
        self.patch.efs_csc(csc)
        self.patch.efs_factory()

    def patch_device_after_reboot(self):
        self.repeat_patch_imei(check=False)
        self.repeat_patch_props()

    def repeat_patch_props(self):
        """
        Патчит системные свойства 'на лету' после полной загрузки устройства.

        Этот метод предназначен для исправления свойств, которые были перезаписаны
        системными процессами (например, ril-daemon) уже после выполнения
        сервисов из init.rc.

        Использует /atrace с флагом -n (resetprop -n), что позволяет изменять
        даже read-only (ro.*) свойства напрямую в памяти. Все изменения
        применяются одной атомарной shell-командой для максимальной
        эффективности.
        """

        hot_keys = [
            "ril.rfcal_date",
            "ril.model_id",
            "ril.serialnumber",
            "debug.enable",
            "vendor.ril.product_code",
            "ril.product_code",
            "gsm.sim.state",
            "vendor.gsm.sim.state",
            "gsm.operator.numeric",  # меняется через какоето время на 25002
            "gsm.sim.operator.numeric",
            "ril.simoperator",
            "gsm.operator.alpha",  # меняется через какоето время на 25002
            "gsm.sim.operator.alpha",
            "gsm.operator.iso-country",  # меняется через какоето время на 25002
            "gsm.sim.operator.iso-country",
            "gsm.operator.isroaming",
            "gsm.network.type",  # меняется через какоето время на 25002
            "vendor.gsm.network.type",  # меняется через какоето время на 25002
        ]
        commands = []
        for prop_name, prop_value in self.generated_props.items():
            if prop_name in hot_keys:
                escaped_value = str(prop_value).replace('"', '\\"')
                commands.append(f'/atrace -n {prop_name} "{escaped_value}"')
        full_patch_script = f"set -e; " + " && ".join(commands)
        adb.shell(full_patch_script)
        log.info("Горячий патчинг свойств успешно завершен.")

    def repeat_patch_imei(self, check=True) -> bool:
        if not self.new_imei:
            raise ValueError("Не сгенерирован новый IMEI")

        adb.shell(f'echo "{self.device_db.imei_orig},{self.new_imei}" > /sys/kernel/k_helper/params && '
                  'echo 1 > /sys/kernel/k_helper/active && '
                  'setprop ctl.restart ril-daemon')

        if check:
            t0 = time.time()
            while time.time() - t0 < 30:
                current_imei = adb.get_imei()
                if current_imei != self.new_imei:
                    log.warning(f"Invalid IMEI: {current_imei=}")
                    time.sleep(1)
                else:
                    log.info(f"Current IMEI NEW: {current_imei}")
                    return True
            raise RuntimeError("Не установлен новый IMEI в систему")
        return True

    def check_emulated(self):
        device_props = adb.get_resetprops()
        discrepancies = []
        for key, value in self.generated_props.items():
            str_value = str(value)
            if key not in device_props:
                msg = f"[ОТСУТСТВУЕТ] Ключ '{key}' должен быть '{str_value}', но он не найден на устройстве."
                log.warning(msg)
                discrepancies.append(msg)
            elif str(device_props[key]) != str_value:
                msg = f"[{key}]: (ЦЕЛЬ) '{str_value}' != '{device_props[key]}' (УСТРОЙСТВО)"
                log.warning(msg)
                discrepancies.append(msg)

        return discrepancies


    def finish(self):
        self.proxy_api.reset_status_proxy()
