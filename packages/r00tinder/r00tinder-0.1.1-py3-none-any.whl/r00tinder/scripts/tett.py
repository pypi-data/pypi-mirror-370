import json
from pathlib import Path

from r00adb import adb
import requests

r = requests.get('https://csapi.samsung.com/v1/services/imei?imei=355259099024500')
print(r)
exit()


root = Path('/media/user/Soft/Bases/Snapchat/projects/snapchat/source/random/guids/imei/all')
for filepath in root.rglob("*.json"):
    with open(filepath) as f:
        data = f.read()
        json_data = json.loads(data)
        model = json_data.get('ro.product.model')
        if model and 'SM-G950F' == model.upper():
            imei = json_data.get('imei')
            if imei:
                print(imei, model)
                print(json_data)

exit()

adb.shell('echo "358793084662202,355258093708344" > /sys/kernel/k_helper/params')
adb.shell('echo 1 > /sys/kernel/k_helper/active')
adb.shell('setprop ctl.restart ril-daemon')
adb.shell('cat /sys/kernel/k_helper/params')
adb.shell('cat /sys/kernel/k_helper/active')
exit()
# adb.shell('ip addr')
# adb.shell('netstat -tulpn')
# adb.shell('ls /proc/sys/net/ipv6')
# adb.shell('cat /proc/sys/net/ipv6/conf/all/disable_ipv6')
# # Пингуем loopback IPv6-адрес. Должен вернуть ошибку "Network is unreachable" или подобную.
# adb.shell('ping6 -c 3 ::1')
# # Пингуем публичный IPv6 DNS Google. Тоже должен провалиться.
# adb.shell('ping6 -c 3 2001:4860:4860::8888')
# adb.shell('ip6tables -L -n -v')
# adb.shell('netstat -tulpn | grep com.google.android.gms')


# adb.shell('echo 0 > /sys/kernel/ipv6_hotplug/forced_disable')
# adb.shell('cat /sys/kernel/ipv6_hotplug/forced_disable')
# Пинг должен проходить успешно
# adb.shell('ping6 -c 3 ::1')
# adb.shell('ping6 -c 3 2001:4860:4860::8888')

# print('-------------------------')
#
# adb.shell('echo 1 > /sys/kernel/ipv6_hotplug/forced_disable')
# adb.shell('cat /sys/kernel/ipv6_hotplug/forced_disable')
# adb.shell('ping6 -c 3 ::1')
# adb.shell('ping6 -c 3 2001:4860:4860::8888')


gms_clear="""
#!/system/bin/sh

# --- ШАГ 1: Уничтожение данных ВСЕХ сторонних и пользовательских приложений ---
echo "[*] Шаг 1: Очистка данных ключевых пакетов Google..."
# Список пакетов, нацеленных на очистку
PACKAGES_TO_CLEAR=(
    # --- Ядро Google ---
    "com.android.vending"
    "com.google.android.gms"
    "com.google.android.gsf"
    "com.google.android.gsf.login"

    # --- Приложения и сервисы Google ---
    "com.google.android.googlequicksearchbox"
    "com.google.android.webview"
    "com.google.android.syncadapters.contacts"
    "com.google.android.syncadapters.calendar"
    "com.google.android.backuptransport"
    "com.google.android.feedback"
    "com.google.android.partnersetup"
    "com.google.android.apps.restore"
    "com.google.android.ext.services"
    "com.google.android.ext.shared"
    "com.android.chrome"

    # --- Мастера первоначальной настройки ---
    "com.google.android.setupwizard"
    "com.sec.android.app.SecSetupWizard" # (Важно, так как он взаимодействует с Google)
)

for pkg in "${PACKAGES_TO_CLEAR[@]}"; do
    if pm path "$pkg" > /dev/null 2>&1; then
        echo "  - Очистка: $pkg"
        pm clear "$pkg"
    fi
done

pm disable-user --user 0 com.google.android.gms
rm -rf /data/data/com.google.android.gms/*
stop # Останавливает Zygote и большинство системных сервисов
echo "[+] Очистка пакетов Google завершена."

# --- ШАГ 2: Тотальное уничтожение директорий приложений в /data ---
echo "[*] Шаг 2: Физическое уничтожение остаточных данных приложений..."
find /data/user/0 -maxdepth 1 -type d -name "com.google.android.*" -exec rm -rf {} +
find /data/user_de/0 -maxdepth 1 -type d -name "com.google.android.*" -exec rm -rf {} +
find /data/user/0 -maxdepth 1 -type d -name "com.android.vending" -exec rm -rf {} +
find /data/user_de/0 -maxdepth 1 -type d -name "com.android.vending" -exec rm -rf {} +
rm -rf /data/user/0/com.samsung.android.svcagent
rm -rf /data/user_de/0/com.samsung.android.svcagent

# --- ШАГ 3: Хирургическое уничтожение "памяти" системы ---
echo "[*] Шаг 3: Стирание системной 'памяти' (аккаунты, история, настройки)..."
# --- Пользовательские данные в /data/system ---
rm -rf /data/system_ce/0/accounts_ce.db*
rm -rf /data/system_de/0/accounts_de.db*
rm -rf /data/system/sync/*

# НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ 0 - сбрасываем все к дефолту
#rm -rf /data/system/users/0/*
find /data/system/users/0/ -mindepth 1 -not -name 'package-restrictions.xml.mbak' -exec rm -rf {} +

# ИСТОРИЯ АКТИВНОСТИ
rm -rf /data/system/usagestats/0/*
rm -rf /data/system/procstats/*
rm -rf /data/system/batterystats*
rm -rf /data/system/netstats/*

# ОГРАНИЧЕНИЯ И ЗАДАЧИ
rm -f /data/system/appops.xml
rm -f /data/system/job/jobs.xml
rm -f /data/system/notification_policy.xml

# --- Данные в /data/misc ---
rm -rf /data/misc/bluetooth/*
rm -rf /data/misc/bluedroid/*
rm -rf /data/misc/keystore/user_0/*
rm -rf /data/misc/profiles/* # Полная очистка JIT/AOT кэша
rm -rf /data/misc/gatekeeper/* # Сброс паролей/графических ключей
rm -rf /data/misc/net/*

# --- Биометрия (лицо, отпечатки) ---
rm -rf /data/bio/*
rm -rf /data/vendor/biometrics/*

# --- ШАГ 4: Зачистка всех кэшей, логов и временных файлов ---
echo "[*] Шаг 4: Глубокая зачистка всех артефактов..."
rm -rf /data/anr/*
rm -rf /data/tombstones/*
rm -rf /data/log/*
rm -rf /data/system/dropbox/*
rm -rf /data/system/package_cache/*
rm -rf /data/cache/*
#rm -rf /data/dalvik-cache/* # Критически важно
rm -rf /data/backup/*
rm -rf /data/bootchart/*
rm -rf /data/ota_package/*


# --- ШАГ 5: Стерилизация пользовательского хранилища ---
echo "[*] Шаг 5: Стерилизация /storage/emulated/0..."
rm -rf /storage/emulated/0/*
# Создаем стандартные пустые папки
mkdir -p /storage/emulated/0/{Alarms,DCIM,Download,Movies,Music,Notifications,Pictures,Podcasts,Ringtones,Android}
sync
"""

adb.shell(gms_clear)
adb.reboot()