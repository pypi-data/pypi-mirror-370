import random
import re, sys
import struct
import time
from collections import defaultdict, deque
import re, math, zlib, hashlib
from collections import Counter
import dsnparse

from r00android_patch import PatchDeviceAPI
from r00server import serv
# Предполагается, что эти импорты у тебя есть и работают
from r00android_fake import get_csc_profile, create_geo_walk_enhanced, create_geographically_accurate_nmea
from r00arango_connector.tinder import DevicesDB
from r00proxy.api import ProxyAPI
from r00adb import adb
from r00logger import log




import struct, time, subprocess, shlex

def _adb_shell(cmd, su=False):
    full = ["adb", "shell"]
    if su:
        full += ["su", "-c", cmd]
    else:
        full += [cmd]
    subprocess.run(full, check=True)

def _hex(bytes_like):
    return ' '.join(f'{b:02x}' for b in bytes_like)

def build_j92_hex(gps_data: dict, flags: int = 0x1F, utc_ms: int = None) -> str:
    lat = float(gps_data['latitude'])
    lon = float(gps_data['longitude'])
    alt = float(gps_data['altitude'])
    spd = float(gps_data['speed'])     # м/с
    brg = float(gps_data['bearing'])   # градусы [0..360)
    acc = float(gps_data['accuracy'])  # метры

    if utc_ms is None:
        utc_ms = int(time.time() * 1000)

    b = bytearray()
    # Заголовок
    b += struct.pack('<I', 0x5C)             # длина = 92
    b += struct.pack('<I', 0x5245FF02)       # магия
    b += struct.pack('<I', 1)                # msg_id
    b += struct.pack('<I', 0x5245FF02)       # магия
    b += struct.pack('<I', 0x100)            # подтип
    b += struct.pack('<Q', 0x40)             # константа A
    b += struct.pack('<Q', 0x40)             # константа B
    b += struct.pack('<Q', flags)            # FLAGS (см. таблицу выше)

    # Поля
    b += struct.pack('<d', lat)
    b += struct.pack('<d', lon)
    b += struct.pack('<d', alt)
    b += struct.pack('<f', spd)
    b += struct.pack('<f', brg)
    b += struct.pack('<f', acc)
    b += struct.pack('<f', 0.0)              # extra/unused
    b += struct.pack('<Q', utc_ms)

    assert len(b) == 92, f"J92 size must be 92, got {len(b)}"
    return _hex(b)

def send_j92_to_kernel(gps_data: dict, hz: int = 2,
                       path="/data/vendor/gps/.gps.interface.pipe.to_jni"):
    hex92 = build_j92_hex(gps_data, flags=0x1F)
    adb.shell(f"echo '{hex92}' > /sys/kernel/r00_loc/j92_hex_override", su=True)


# Пример использования под твои входные данные:
# if __name__ == "__main__":
#     gps_data = {
#         'latitude':  40.72145599495525,
#         'longitude': -74.01091480854055,
#         'altitude':  100.78429207299463,
#         'speed':     44.008448158365237324,  # м/с
#         'bearing':   21.43314973297984194,   # градусы
#         'accuracy':  2.107136012817226,     # м
#         'timestamp': 0.0,                   # возьмём текущее время
#     }
#     # hex92 = build_j92_hex(gps_data)
#     # print("J92 HEX:", hex92)
#     send_j92_to_kernel(gps_data)
#     exit()







def _ru_byt(n: int) -> str:
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:  return "байт"
    if 2 <= n10 <= 4 and not (12 <= n100 <= 14): return "байта"
    return "байтов"

def _entropy(b: bytes) -> float:
    if not b: return 0.0
    cnt = Counter(b)
    n = len(b)
    return -sum((c/n) * math.log2(c/n) for c in cnt.values())

def _find_ascii_runs(b: bytes, min_len: int):
    runs, i, n = [], 0, len(b)
    while i < n:
        j = i
        while j < n and 32 <= b[j] <= 126:
            j += 1
        if j - i >= min_len:
            runs.append((i, b[i:j].decode('ascii', 'ignore')))
        i = j + 1 if j == i else j
    return runs

def _format_offsets(offsets, width):
    return ", ".join(f"0x{off:0{width}X}" for off in offsets)

def _parse_pattern(pat: str) -> bytes:
    s = re.sub(r'[^0-9A-Fa-f]', '', pat)
    if len(s) % 2 != 0:
        raise ValueError(f"HEX шаблон нечётной длины: {pat!r}")
    return bytes.fromhex(s)

def hexinfo(filepath: str, *,
            preview: int = 32,
            hist_top: int = 8,
            ascii_min: int = 4,
            patterns: list[str] | None = None,
            show_floats: bool = False):
    """
    Читает файл с плоской HEX-строкой и печатает сводку.
    Возвращает словарь метрик.
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        hexstr = ''.join(f.read().split())

    # Валидация
    if not hexstr:
        raise ValueError("Пустой файл/HEX.")
    bad = re.search(r'[^0-9A-Fa-f]', hexstr)
    if bad:
        pos = bad.start()
        snippet = hexstr[max(0, pos-8):pos+8]
        raise ValueError(f"Невалидный символ HEX на позиции {pos}: «{hexstr[pos]}», контекст: …{snippet}…")
    if len(hexstr) % 2 != 0:
        raise ValueError(f"Нечётное число символов HEX: {len(hexstr)}")

    data = bytes.fromhex(hexstr)
    nbytes = len(data)
    nhex = len(hexstr)

    # Базовая инфа
    crc32 = zlib.crc32(data) & 0xFFFFFFFF
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    ent = _entropy(data)
    zeros = data.count(0)
    # Длиннейшая серия нулей
    cur = longest_zero = 0
    for b in data:
        if b == 0:
            cur += 1
            if cur > longest_zero: longest_zero = cur
        else:
            cur = 0

    # Гистограмма
    cnt = Counter(data)
    top = cnt.most_common(hist_top)
    uniq = len(cnt)

    # ASCII
    ascii_runs = _find_ascii_runs(data, ascii_min)
    ascii_ratio = sum(len(s.encode('ascii', 'ignore')) for _, s in ascii_runs) / nbytes if nbytes else 0.0

    # Поиск сигнатур
    sig = []
    width = max(4, len(f"{nbytes:X}"))
    if patterns:
        for p in patterns:
            pat = _parse_pattern(p)
            offs, start = [], 0
            while True:
                idx = data.find(pat, start)
                if idx < 0: break
                offs.append(idx); start = idx + 1
            sig.append({
                "pattern": p,
                "count": len(offs),
                "first_offsets": offs[:10],
            })

    # (опц.) превью float32/float64 LE
    floats32 = []
    floats64 = []
    if show_floats:
        import struct
        for i in range(0, min(nbytes, 4*6), 4):
            if i + 4 <= nbytes:
                v = struct.unpack_from("<f", data, i)[0]
                if math.isfinite(v):
                    floats32.append(v)
        for i in range(0, min(nbytes, 8*4), 8):
            if i + 8 <= nbytes:
                v = struct.unpack_from("<d", data, i)[0]
                if math.isfinite(v):
                    floats64.append(v)

    # Печать
    print(f"0x{nbytes:04X} ({nbytes} {_ru_byt(nbytes)} → {nhex} hex-символов)")
    print(f"Выравнивание: /2 {'✓' if nbytes % 2 == 0 else '✗'}  /4 {'✓' if nbytes % 4 == 0 else '✗'}  "
          f"/8 {'✓' if nbytes % 8 == 0 else '✗'}  /16 {'✓' if nbytes % 16 == 0 else '✗'}")
    print(f"CRC32=0x{crc32:08X}  SHA1={sha1}  SHA256={sha256}")
    print(f"Энтропия: {ent:.2f} бит/байт")
    print(f"Нули: {zeros} ({zeros/nbytes*100:.1f}%), макс. серия: {longest_zero}")
    print(f"Уникальных байтов: {uniq}/256")
    if top:
        top_str = ", ".join(f"{b:02x}({c} / {c/nbytes*100:.1f}%)" for b, c in top)
        print(f"Топ-{hist_top}: {top_str}")
    if ascii_runs:
        sample = ", ".join(f"0x{off:0{width}X}:'{s[:32] + ('…' if len(s)>32 else '')}'"
                           for off, s in ascii_runs[:5])
        print(f"ASCII-строки ≥{ascii_min}: {len(ascii_runs)} (доля {ascii_ratio*100:.1f}%). Примеры: {sample}")
    else:
        print(f"ASCII-строки ≥{ascii_min}: 0")
    if patterns:
        for rec in sig:
            offs = rec["first_offsets"]
            off_str = _format_offsets(offs, width) if offs else "—"
            print(f"Сигнатура {rec['pattern']}: найдено {rec['count']}. Первые: {off_str}")
    print(f"Первые {min(preview, nbytes)} байт: {data[:preview].hex()}")
    print(f"Последние {min(preview, nbytes)} байт: {data[-preview:].hex()}")

    if show_floats:
        if floats32:
            print("float32 LE (первые): " + ", ".join(f"{v:.3f}" for v in floats32[:6]))
        if floats64:
            print("float64 LE (первые): " + ", ".join(f"{v:.3f}" for v in floats64[:4]))

    # Возврат метрик
    print('-' * 50)
    print()
    return {
        "bytes": nbytes,
        "hex_chars": nhex,
        "crc32": crc32,
        "sha1": sha1,
        "sha256": sha256,
        "entropy_bits_per_byte": ent,
        "zeros": zeros,
        "longest_zero_run": longest_zero,
        "unique_bytes": uniq,
        "hist_top": top,
        "ascii_runs": ascii_runs,
        "patterns": sig if patterns else None,
        "head_hex": data[:preview].hex(),
        "tail_hex": data[-preview:].hex(),
        "floats32_le": floats32 if show_floats else None,
        "floats64_le": floats64 if show_floats else None,
    }




def strace2hex(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    # Ищем: write(fd<...>, "PAYLOAD", N) = N
    m = re.search(
        r'write\([^,]+,\s*"([^"]+)"\s*,\s*(\d+)\)\s*=\s*(\d+)',
        data,
        flags=re.S
    )
    if not m:
        raise ValueError("Не найден шаблон write(..., \"...\", N) = N")

    payload, arg_len_s, ret_len_s = m.group(1), m.group(2), m.group(3)
    expected_arg = int(arg_len_s)
    expected_ret = int(ret_len_s)

    # Собираем пары: поддерживаем \xHH и \HH
    pairs = re.findall(r'\\x?([0-9A-Fa-f]{2})', payload)
    hexstr = ''.join(p.lower() for p in pairs)

    actual_len = len(hexstr) // 2

    # Проверки целостности
    if expected_arg != expected_ret:
        raise ValueError(
            f"Несовпадение аргумента и возвращённого значения write: "
            f"{expected_arg} != {expected_ret}"
        )

    if actual_len != expected_arg:
        # Немного диагностики для удобства
        preview = hexstr[:64] + ('...' if len(hexstr) > 64 else '')
        raise ValueError(
            "Длина не совпадает: "
            f"извлечено {actual_len} байт, ожидалось {expected_arg}. "
            f"Найдено пар: {len(pairs)}. Превью: {preview}"
        )

    # Перезаписываем исходный файл «плоским» hex
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(hexstr)

    return hexstr



# hexinfo('/home/user/temp/gnss_2092.hex', preview=48, hist_top=10, ascii_min=5)
# strace2hex('/home/user/temp/gnss_3004.hex')
# strace2hex('/home/user/temp/gnss_2092.hex')
# exit()

id_pglors = 0
pglors = """$PGLOR,0,RID,47531,89,19,20,410397*32
$PGLOR,9,STA,091707.27,0.000,0.000,39,98,9999,0,P,F,L,1,C,0,S,00000000,0,1,R,00000000,TPeF,0,124,LC,,,*16
$PGLOR,2,PFM,HAL,-,0,0,0,0,RF,-,-180,0.0,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,,,*63
$PGLOR,0,RID,47531,89,19,20,410397*32
$PGLOR,9,STA,091708.05,0.000,0.000,39,98,9999,0,P,F,L,1,C,0,S,00100000,0,1,R,00000000,TPeF,9,903,LC,,,*1C
$PGLOR,9,STA,091708.27,0.000,0.000,39,98,9999,0,P,F,L,1,C,2,S,00100000,0,1,R,00000000,TPeF,9,1124,LC,,,*22
$PGLOR,9,STA,091709.27,0.002,0.500,26,98,6,0,P,F,L,0,C,2,S,00100002,0,1,R,00000000,TPeF,9,2124,LC,,,*1C
$PGLOR,9,STA,091710.27,0.005,0.500,28,98,16,0,P,F,L,0,C,2,S,00100002,2,3,R,00000000,TPeF,9,3124,LC,,,*2D
$PGLOR,9,STA,091711.27,-0.012,0.500,29,98,24,0,P,F,L,0,C,2,S,00100002,4,3,R,00000000,TPeF,9,4124,LC,,,*06
$PGLOR,9,STA,091712.26,0.011,0.001,28,98,24,0,P,F,L,0,C,3,S,00100002,5,3,R,00000000,TPeF,9,5124,LC,,,*2E
$PGLOR,9,STA,091713.26,0.011,0.000,28,98,48,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,6124,LC,,3,*5A
$PGLOR,9,STA,091714.26,0.011,0.000,28,1,32,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,7124,LC,,,*52
$PGLOR,9,STA,091715.00,0.011,0.000,28,1,24,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,7863,LC,,,*5A
$PGLOR,2,PFM,HAL,-,0,0,0,0,RF,-,-180,3.3,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,,,*63
$PGLOR,9,STA,091716.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,8863,LC,,,*57
$PGLOR,9,STA,091717.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,9863,LC,,,*58
$PGLOR,9,STA,091718.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,24,4,R,000833F4,TPeF,9,10863,LC,,,*6F
$PGLOR,9,STA,091719.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,11863,LC,,,*6E
$PGLOR,9,STA,091720.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,12863,LC,,,*66
$PGLOR,9,STA,091721.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,13863,LC,,,*67
$PGLOR,9,STA,091722.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,14863,LC,,,*62
$PGLOR,9,STA,091723.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,15863,LC,,,*62
$PGLOR,2,PFM,HAL,-,0,0,0,0,RF,-,-180,0.9,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,P,*16
$PGLOR,9,STA,091724.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,16863,LC,,,*66
$PGLOR,9,STA,091725.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,17863,LC,,,*66
$PGLOR,9,STA,091726.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,18863,LC,,,*6A
$PGLOR,9,STA,091727.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,19863,LC,,,*6B
$PGLOR,9,STA,091728.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,20863,LC,,,*6E
$PGLOR,9,STA,091729.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,34,4,R,000833F4,TPeF,9,21863,LC,,,*61
$PGLOR,9,STA,091730.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,22863,LC,,,*62
$PGLOR,9,STA,091731.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,23863,LC,,,*6D
$PGLOR,9,STA,091732.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,24863,LC,,,*69
$PGLOR,9,STA,091733.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,25863,LC,,,*66
$PGLOR,2,PFM,HAL,-,0,0,0,0,RF,-,-180,0.5,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,PPP*36
$PGLOR,9,STA,091734.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,26863,LC,,,*62
$PGLOR,9,STA,091735.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,27863,LC,,,*62
$PGLOR,9,STA,091736.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,28863,LC,,,*6F
$PGLOR,9,STA,091737.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,29863,LC,,,*6F
$PGLOR,9,STA,091738.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,30863,LC,,,*68
$PGLOR,9,STA,091739.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,31863,LC,,,*68
$PGLOR,9,STA,091740.00,0.011,0.000,25,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,32863,LC,,,*66
$PGLOR,9,STA,091741.00,0.011,0.000,25,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,33863,LC,,,*66
$PGLOR,9,STA,091742.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,34863,LC,,,*61
$PGLOR,9,STA,091743.00,0.011,0.000,25,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,35863,LC,,,*62
$PGLOR,9,STA,091744.00,0.011,0.000,25,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,36863,LC,,,*66
$PGLOR,9,STA,091745.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,37863,LC,,,*65
$PGLOR,9,STA,091746.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,38863,LC,,,*69
$PGLOR,9,STA,091747.00,0.011,0.000,26,1,16,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,39863,LC,,,*69
$PGLOR,9,STA,091748.00,0.011,0.000,27,1,12,0,P,F,L,0,C,3,S,00100002,44,4,R,000833F4,TPeF,9,40863,LC,,,*6D
$PGLOR,9,STA,091749.00,0.011,0.000,27,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,41863,LC,,,*6C
$PGLOR,9,STA,091750.00,0.011,0.000,27,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,42863,LC,,,*67
$PGLOR,9,STA,091751.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,43863,LC,,,*63
$PGLOR,9,STA,091752.00,0.011,0.000,27,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,44863,LC,,,*67
$PGLOR,9,STA,091753.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,45863,LC,,,*68
$PGLOR,9,STA,091754.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,46863,LC,,,*6C
$PGLOR,9,STA,091755.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,47863,LC,,,*6D
$PGLOR,9,STA,091756.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,48863,LC,,,*61
$PGLOR,9,STA,091757.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,49863,LC,,,*61
$PGLOR,9,STA,091758.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,50863,LC,,,*67
$PGLOR,9,STA,091759.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,51863,LC,,,*67
$PGLOR,9,STA,091800.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,52863,LC,,,*67
$PGLOR,9,STA,091801.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,53863,LC,,,*67
$PGLOR,9,STA,091802.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,54863,LC,,,*63
$PGLOR,9,STA,091803.00,0.011,0.000,28,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,55863,LC,,,*67
$PGLOR,9,STA,091804.00,0.011,0.000,28,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,56863,LC,,,*63
$PGLOR,9,STA,091805.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,57863,LC,,,*67
$PGLOR,9,STA,091806.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,58863,LC,,,*6B
$PGLOR,9,STA,091807.00,0.011,0.000,28,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,59863,LC,,,*6B
$PGLOR,9,STA,091808.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,60863,LC,,,*6F
$PGLOR,2,PFM,HAL,P,0,0,100,0,RF,-,39,0.5,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,PPP*54
$PGLOR,9,STA,091809.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,61863,LC,,,*6F
$PGLOR,9,STA,091810.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,62863,LC,,,*64
$PGLOR,9,STA,091811.00,0.011,0.000,29,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,63863,LC,,,*64
$PGLOR,9,STA,091812.00,0.011,0.000,30,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,64863,LC,,,*68
$PGLOR,9,STA,091813.00,0.011,0.000,30,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,65863,LC,,,*68
$PGLOR,9,STA,091814.00,0.011,0.000,30,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,66863,LC,,,*6C
$PGLOR,9,STA,091815.00,0.011,0.000,31,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,67863,LC,,,*6D
$PGLOR,9,STA,091816.00,0.011,0.000,30,1,16,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,68863,LC,,,*60
$PGLOR,9,STA,091817.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,69863,LC,,,*64
$PGLOR,9,STA,091818.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,70863,LC,,,*63
$PGLOR,9,STA,091819.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,71863,LC,,,*63
$PGLOR,9,STA,091820.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,72863,LC,,,*6A
$PGLOR,9,STA,091821.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,73863,LC,,,*6A
$PGLOR,9,STA,091822.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,74863,LC,,,*6E
$PGLOR,9,STA,091823.00,0.011,0.000,29,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,75863,LC,,,*66
$PGLOR,9,STA,091824.00,0.011,0.000,29,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,76863,LC,,,*62
$PGLOR,9,STA,091825.00,0.011,0.000,29,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,77863,LC,,,*62
$PGLOR,9,STA,091826.00,0.011,0.000,29,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,78863,LC,,,*6E
$PGLOR,9,STA,091827.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,79863,LC,,,*66
$PGLOR,9,STA,091828.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,80863,LC,,,*6F
$PGLOR,9,STA,091829.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,81863,LC,,,*6F
$PGLOR,9,STA,091830.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,82863,LC,,,*64
$PGLOR,9,STA,091831.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,83863,LC,,,*64
$PGLOR,9,STA,091832.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,84863,LC,,,*60
$PGLOR,9,STA,091833.00,0.011,0.000,30,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,85863,LC,,,*60
$PGLOR,9,STA,091834.00,0.011,0.000,31,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,86863,LC,,,*65
$PGLOR,9,STA,091835.00,0.011,0.000,31,1,12,0,P,F,L,0,C,3,S,00100002,44,5,R,000833F4,TPeF,9,87863,LC,,,*65
"""

def clear_gms():
    adb.shell('pm clear com.google.android.gms')
    adb.shell('pm clear com.google.android.gms.policy_sidecar_aps')
    adb.shell('pm clear com.android.vending')
    adb.shell('pm clear com.android.location.fused')
    adb.shell('pm clear com.google.android.gsf')
    adb.shell('pm clear com.sec.location.nsflp2')
    adb.shell('pm clear com.samsung.android.location')
    adb.shell('rm -rf /data/vendor/gps/*', su=True)

def _degrees_to_nmea_components(value: float):
    """
    Конвертирует десятичные градусы в целочисленные компоненты для NMEA.
    Например: 40.711345 -> (40, 42, 680700)
    """
    if value < 0:
        value = -value

    degrees = int(value)
    minutes_decimal = (value - degrees) * 60
    minutes_int = int(minutes_decimal)
    # Берем 6 знаков после запятой для минут, как в твоем примере
    minutes_frac = int(round((minutes_decimal - minutes_int) * 1_000_000))

    return degrees, minutes_int, minutes_frac

def set_location(gps_data: dict):
    """ Генерирует payload из словаря с данными и отправляет его на устройство. """
    print(f'route: {gps_data}')
    latitude = gps_data['latitude']
    longitude = gps_data['longitude']
    altitude = gps_data['altitude']
    speed = gps_data['speed']
    bearing = gps_data['bearing']
    accuracy = gps_data['accuracy']

    # 1. Пакуем float/double в байты (little-endian)
    lat_bytes = struct.pack('<d', latitude)
    lon_bytes = struct.pack('<d', longitude)
    alt_bytes = struct.pack('<d', altitude)
    speed_bytes = struct.pack('<f', speed)
    bearing_bytes = struct.pack('<f', bearing)
    accuracy_bytes = struct.pack('<f', accuracy)

    # 2. Конвертируем байты в u64/u32 целые числа
    lat_u64 = struct.unpack('<Q', lat_bytes)[0]
    lon_u64 = struct.unpack('<Q', lon_bytes)[0]
    alt_u64 = struct.unpack('<Q', alt_bytes)[0]
    speed_u32 = struct.unpack('<I', speed_bytes)[0]
    bearing_u32 = struct.unpack('<I', bearing_bytes)[0]
    accuracy_u32 = struct.unpack('<I', accuracy_bytes)[0]

    # 3. Предвычисляем компоненты для NMEA
    lat_deg, lat_min, lat_frac = _degrees_to_nmea_components(latitude)
    lon_deg, lon_min, lon_frac = _degrees_to_nmea_components(longitude)
    lat_dir = ord('N' if latitude >= 0 else 'S')
    lon_dir = ord('E' if longitude >= 0 else 'W')

    # 4. Формируем ПОЛНЫЙ payload-строку для отправки в ядро
    payload = (
        f"{lat_u64},{lon_u64},{alt_u64},{speed_u32},{bearing_u32},{accuracy_u32},"
        f"{lat_deg},{lat_min},{lat_frac},{lat_dir},"
        f"{lon_deg},{lon_min},{lon_frac},{lon_dir}"
    )

    # 5. Отправляем команду. Одинарные кавычки обязательны!
    adb.shell(f"echo '{payload}' > /sys/kernel/livepatch/location", su=True)

def set_nmea(nmea_data: list) -> None:
    global id_pglors, pglors
    """
       Возвращает строку:
       cat <<'EOF' > /sys/kernel/livepatch/rules
       GPGGA $GPGGA,...
       GPGSA $GPGSA,...
       GNGSA $GNGSA,...   (если нет — random, не $GPGGA/$GPRMC)
       QZGSA $GAGSA,...   (если нет — random, не $GPGGA/$GPRMC)
       IMGSA $GPGSV,...
       BDGSA $GLGSV,...
       GAGSA $GPGSV,...
       GPRMC $GPRMC,...
       <оставшиеся строки как есть>
       EOF
       """
    # 1) Нормализуем окончания строк
    lines = []
    for x in nmea_data:
        if x is None:
            continue
        s = str(x).rstrip("\r\n")
        if s:
            lines.append(s)

    # 2) Индексация по типам
    def nmea_type(s: str) -> str | None:
        if s.startswith("$"):
            p = s.find(",")
            if p > 0:
                return s[:p]
        return None

    type_to_indices = defaultdict(deque)
    for idx, s in enumerate(lines):
        t = nmea_type(s)
        if t:
            type_to_indices[t].append(idx)

    # 3) Заголовок (метка, требуемый тип)
    header_spec = [
        ("GPGGA", "$GPGGA"),
        ("GPGSA", "$GPGSA"),
        ("GNGSA", "$GNGSA"),
        ("QZGSA", "$GAGSA"),
        ("IMGSA", "$GPGSV"),
        ("BDGSA", "$GLGSV"),
        ("GAGSA", "$GPGSV"),
        ("GPRMC", "$GPRMC"),
        ("PGLOR", "$PGLOR"),
    ]

    # 4) Обязательные типы: должны быть
    if not type_to_indices.get("$GPGGA"):
        raise ValueError("В nmea_data отсутствует обязательный тип $GPGGA.")
    if not type_to_indices.get("$GPRMC"):
        raise ValueError("В nmea_data отсутствует обязательный тип $GPRMC.")

    # Возьмём первый $GPGGA и $GPRMC, но НЕ помечаем их used до вставки в header
    primary_gga = type_to_indices["$GPGGA"][0]
    primary_rmc = type_to_indices["$GPRMC"][0]

    used = set()
    header_lines = []

    def pop_first(typ: str) -> int | None:
        dq = type_to_indices.get(typ)
        while dq:
            i = dq.popleft()
            if i not in used:
                return i
        return None

    def pick_random_fallback() -> int:
        candidates = []
        for i, s in enumerate(lines):
            if i in used:
                continue
            t = nmea_type(s)
            if not t:
                continue
            if t in ("$GPGGA", "$GPRMC"):
                continue
            candidates.append(i)
        if not candidates:
            raise ValueError("Нет кандидатов для рандомной подстановки (кроме $GPGGA/$GPRMC).")
        return random.choice(candidates)

    # 5) Собираем заголовок в нужном порядке
    for label, needed_type in header_spec:
        if needed_type == "$GPGGA":
            idx = primary_gga
        elif needed_type == "$GPRMC":
            idx = primary_rmc
        else:
            idx = pop_first(needed_type)
            if idx is None:
                idx = pick_random_fallback()

        # Гарантируем уникальность
        if idx in used:
            # Для обязательных этого быть не должно — но на всякий случай fallback
            if needed_type in ("$GPGGA", "$GPRMC"):
                raise ValueError(f"Неожиданное дублирование обязательного типа {needed_type}.")
            tries = 16
            while idx in used and tries > 0:
                idx = pick_random_fallback()
                tries -= 1
            if idx in used:
                raise ValueError("Не удалось подобрать уникальный элемент для заголовка.")

        used.add(idx)
        # if label == 'PGLOR':
        #     pg_list = [item.strip() for item in pglors.split('\n') if item.strip()]
        #     pglor = pg_list[id_pglors]
        #     id_pglors += 1
        #     # test_pglor = '$PGLOR,2,PFM,HAL,-,0,0,0,0,RF,-,-180,3.3,0,RTC,,P,STO,P,LTO,F,SW,P,,,OSC,,,*63'
        #     header_lines.append(f"{label} {pglor}")
        # else:
        #     header_lines.append(f"{label} {lines[idx]}")

        header_lines.append(f"{label} {lines[idx]}")

    # 6) Убираем ДУБЛИКАТЫ $GPGGA/$GPRMC из хвоста (кроме уже выбранных)
    for typ, primary in (("$GPGGA", primary_gga), ("$GPRMC", primary_rmc)):
        dq = type_to_indices.get(typ, deque())
        # первичный уже добавлен в header и находится в used; остальные — тоже в used
        for i in list(dq):
            if i != primary:
                used.add(i)

    # 7) Хвост — всё неиспользованное, «как есть», в исходном порядке
    tail_lines = [lines[i] for i in range(len(lines)) if i not in used]

    body = "\n".join(header_lines + tail_lines)
    script_fake_nmea = "cat <<'EOF' > /sys/kernel/livepatch/rules\n" + body + "\nEOF"
    print(script_fake_nmea)
    adb.shell(script_fake_nmea, su=True, script=True)



@log.catch
def main():
    device_db = DevicesDB('14')
    proxy_api = ProxyAPI(device_db)
    patch = PatchDeviceAPI(device_db.model_phone, '14')
    proxy = proxy_api.get_proxy(is_project=False)
    proxydsn = dsnparse.parse(proxy)
    csc_profile = get_csc_profile(proxydsn.host, proxydsn.port)
    routies_gps_data = create_geo_walk_enhanced(csc_profile, save_gpx=True)

    # hexinfo('/home/user/temp/gnss_3004.hex', show_floats=True)
    # hexinfo('/home/user/temp/gnss_2092.hex', show_floats=True)
    # hexinfo('/home/user/temp/gnss_2092.hex', patterns=['02ff4552'], show_floats=True)

    # clear_session_sh = serv.download('scripts/clear_session.sh')
    # adb.shell(clear_session_sh, su=True, script=True)


    # adb.start_app('com.r00cli')
    # adb.kernel_location_enable(1)

    # time.sleep(2)
    # adb.shell('am broadcast -a com.r00cli.GET_FUSED_LOCATION -n com.r00cli/.LocationReceiver')
    # adb.shell('am start-service -a com.r00cli.COLLECT_NMEA -n com.r00cli/.NmeaService', su=True)

    # adb.shell('echo 0 > /sys/kernel/livepatch/log_enable', su=True)
    # exit()

    # clear_gms()
    # adb.reboot()
    # time.sleep(5)

    # adb.shell("echo 'IPC Thread,gpsd,Thread-42,gnss@1.0-servic' > /sys/kernel/livepatch/log_include_procs", su=True)
    # adb.shell("echo 'IPC Thread' > /sys/kernel/livepatch/log_include_procs", su=True)
    # adb.shell("echo '/data/vendor/gps/.gps.interface.pipe.to_jni,/data/vendor/gps/.pipe.gpsd_to_lhd.to_server' > /sys/kernel/livepatch/log_include_paths", su=True)
    # adb.shell("echo 'bgExecutor #2,HubConnection,VerifierDataSto,CFMS Handler Th,process-tracker,PowerManagerSer,composer@2.1-se,mali-cmar-backe,argosd,watchdog,android.fg,iod,lmkd,RenderThread,SharedPreferenc,InstallQueueDat,com.r00cli,dex2oat,android.ui,highpool[7],main,Db-scheduler_ma,magiskd,_MODULES_ACTION,app_process,firebase-instal,PrimaryWorkingT,.gms.persistent,cat,main,com.r00app,lowpool[4]' > /sys/kernel/livepatch/log_exclude_procs", su=True)
    # adb.shell("echo '/dev/cpuset/foreground/tasks,/dev/cpuctl/tasks' > /sys/kernel/livepatch/log_exclude_paths", su=True)
    # adb.shell('echo 1 > /sys/kernel/livepatch/log_enable', su=True)
    # adb.shell('echo 1 > /sys/kernel/livepatch/erfix_enabled', su=True)



    # adb.shell(gnss_script, script=True, su=True)
    # exit()


    # adb.shell('echo 1 > /sys/kernel/livepatch/log_enable', su=True)
    adb.shell('setenforce 0', su=True)
    adb.shell('echo 1 > /sys/kernel/livepatch/loc_enabled', su=True)
    adb.shell('echo 0 > /sys/kernel/livepatch/pglor_passthru', su=True)

    adb.shell('echo 1 > /sys/kernel/r00_loc/j92_mode', su=True)
    adb.shell('echo 2 > /sys/kernel/r00_loc/push_hz', su=True)
    adb.shell('echo 1 > /sys/kernel/r00_loc/j92_enable', su=True)

    location_data = []
    while True:
        # Ходим по тратуару в new uork
        for route in routies_gps_data:
            print(route)
            if route.get('_metadata'):
                del route['_metadata']
            nmea_data = create_geographically_accurate_nmea(route, count=16, for_spoof_broadcom=True)
            location_data.append([route, nmea_data])



            send_j92_to_kernel(route)
            set_location(route)
            set_nmea(nmea_data)
            time.sleep(1)

        # Идём в обратную сторону
        for route in reversed(routies_gps_data[1:-1]):
            nmea_data = create_geographically_accurate_nmea(route, count=16, for_spoof_broadcom=True)
            send_j92_to_kernel(route)
            set_location(route)
            set_nmea(nmea_data)
            time.sleep(1)



if __name__ == '__main__':
    main()

    aaaa = """# 1) шумовой блок (не мешает запуску)
    echo 1 > /sys/kernel/r00_loc/block_mode
    echo "120,124,176,180,188,196" > /sys/kernel/r00_loc/block_sizes

    # 2) wake (handshake 168) + start FLP
    echo "/data/vendor/gps/.gps.interface.pipe.to_jni" > /sys/kernel/r00_loc/push_path
    echo "168" > /sys/kernel/r00_loc/push_sizes
    echo 2 > /sys/kernel/r00_loc/push_hz
    echo 1 > /sys/kernel/r00_loc/enable_push
    echo restart_flp_log.sh
    sleep 20
    # тут запускаем restart_flp_log.sh
    # через ~5–10с:
    echo "168,92" > /sys/kernel/r00_loc/push_sizes
    echo 1 > /sys/kernel/r00_loc/push_hz"""

    gnss_script = """# включаем всё нужное
    echo 1 > /sys/kernel/livepatch/erfix_enabled
    echo 1 > /sys/kernel/livepatch/erfix_debug
    echo 1 > /sys/kernel/livepatch/erfix_to_jni
    echo 1 > /sys/kernel/livepatch/erfix_to_server

    # === Загрузка 0x0BBC (3004 байта, 6008 hex-символов) ===
    echo -n 0bbc > /sys/kernel/livepatch/erfix_begin
    # очищаем вход от всего лишнего, кроме [0-9a-fA-F]; режем на куски <= PAGE_SIZE
    tr -cd '0-9a-fA-F' < /data/local/tmp/gnss_3004.hex | /system/etc/busybox fold -w 4096 | \
    while read -r chunk; do
      printf '%s' "$chunk" > /sys/kernel/livepatch/erfix_append
    done
    echo 1 > /sys/kernel/livepatch/erfix_commit

    # === Загрузка 0x082C (2092 байта, 4184 hex-символов) ===
    echo -n 082c > /sys/kernel/livepatch/erfix_begin
    tr -cd '0-9a-fA-F' < /data/local/tmp/gnss_2092.hex | /system/etc/busybox fold -w 4096 | \
    while read -r chunk; do
      printf '%s' "$chunk" > /sys/kernel/livepatch/erfix_append
    done
    echo 1 > /sys/kernel/livepatch/erfix_commit

    # проверяем
    cat /sys/kernel/livepatch/erfix_stats"""

    """
tr -cd '0-9A-Fa-f' < /data/local/tmp/gnss_3004.hex \
| /system/etc/busybox fold -w 4096 \
| while read -r chunk; do
    printf '%s' "$chunk" > /sys/kernel/livepatch/erfix_append
done

tr -cd '0-9A-Fa-f' < /data/local/tmp/gnss_2092.hex \
| /system/etc/busybox fold -w 4096 \
| while read -r chunk; do
    printf '%s' "$chunk" > /sys/kernel/livepatch/erfix_append
done

tr -cd '0-9a-fA-F' < /data/local/tmp/gnss_3004.hex | /system/etc/busybox fold -w 4096 | \
while read -r chunk; do
  printf '%s' "$chunk"
done



echo -n 0bbc > /sys/kernel/livepatch/erfix_begin
tr -d '[:space:]' < /data/local/tmp/gnss_3004.hex | /system/etc/busybox fold -w 4096 | while read -r chunk; do
  printf "%s" "$chunk" > /sys/kernel/livepatch/erfix_append
done
echo 1 > /sys/kernel/livepatch/erfix_commit

# 3004
echo 0bbc > /sys/kernel/livepatch/erfix_begin
cat /data/local/tmp/gnss_3004.hex | /system/etc/busybox xxd -r -p > /sys/kernel/livepatch/erfix_append
echo 1 > /sys/kernel/livepatch/erfix_commit

# 2092
echo 082c > /sys/kernel/livepatch/erfix_begin
cat gnss_2092.hex | xxd -r -p > /sys/kernel/livepatch/erfix_append
echo 1 > /sys/kernel/livepatch/erfix_commit

# проверка
cat /sys/kernel/livepatch/erfix_stats
# должно стать: tpl_0bbc=3004 tpl_082c=2092

    """