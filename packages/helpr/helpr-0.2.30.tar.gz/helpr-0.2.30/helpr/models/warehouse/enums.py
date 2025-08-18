from enum import Enum

class WarehouseStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class DeliveryModeEnum(str, Enum):
    same_day = "same_day"
    next_day = "next_day"
    standard = "standard"

class StateCodeEnum(str, Enum):
    ad = "ad"  # Andhra Pradesh (old)
    ar = "ar"  # Arunachal Pradesh
    as_ = "as"  # Assam (using as_ since 'as' is Python keyword)
    br = "br"  # Bihar
    cg = "cg"  # Chhattisgarh
    dl = "dl"  # Delhi
    ga = "ga"  # Goa
    gj = "gj"  # Gujarat
    hr = "hr"  # Haryana
    hp = "hp"  # Himachal Pradesh
    jh = "jh"  # Jharkhand
    jk = "jk"  # Jammu and Kashmir
    ka = "ka"  # Karnataka
    kl = "kl"  # Kerala
    la = "la"  # Ladakh
    mp = "mp"  # Madhya Pradesh
    mh = "mh"  # Maharashtra
    mn = "mn"  # Manipur
    ml = "ml"  # Meghalaya
    mz = "mz"  # Mizoram
    nl = "nl"  # Nagaland
    or_ = "or"  # Odisha (using or_ since 'or' is Python keyword)
    pb = "pb"  # Punjab
    rj = "rj"  # Rajasthan
    sk = "sk"  # Sikkim
    tn = "tn"  # Tamil Nadu
    ts = "ts"  # Telangana
    tr = "tr"  # Tripura
    up = "up"  # Uttar Pradesh
    uk = "uk"  # Uttarakhand
    wb = "wb"  # West Bengal
    
    # Union Territories
    an = "an"  # Andaman and Nicobar Islands
    ch = "ch"  # Chandigarh
    dn = "dn"  # Dadra and Nagar Haveli and Daman and Diu
    ld = "ld"  # Lakshadweep
    py = "py"  # Puducherry