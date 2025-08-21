import re

hash_dict = {
    "CRC-32": {
        "regex": re.compile(r"^(\$crc32\$)?([a-f0-9]{8}.)?[a-f0-9]{8}$", re.IGNORECASE),
        "hashcat": 11500,
        "john": "crc32"
    },
    "DES(Unix)": {
        "regex": re.compile(r"^[a-z0-9\/.]{12}[.26AEIMQUYcgkosw]{1}$", re.IGNORECASE),
        "hashcat": 1500,
        "john": "descrypt"
    },
    "Traditional DES": {
        "regex": re.compile(r"^[a-z0-9\/.]{12}[.26AEIMQUYcgkosw]{1}$", re.IGNORECASE),
        "hashcat": 1500,
        "john": "descrypt"
    },
    "DEScrypt": {
        "regex": re.compile(r"^[a-z0-9\/.]{12}[.26AEIMQUYcgkosw]{1}$", re.IGNORECASE),
        "hashcat": 1500,
        "john": "descrypt"
    },
    "MySQL323": {
        "regex": re.compile(r"^[a-f0-9]{16}$", re.IGNORECASE),
        "hashcat": 200,
        "john": "mysql"
    },
    "Half MD5": {
        "regex": re.compile(r"^[a-f0-9]{16}$", re.IGNORECASE),
        "hashcat": 5100,
        "john": None
    },
    "Oracle H: Type (Oracle 7+), DES(Oracle)": {
        "regex": re.compile(r"^[a-f0-9]{16}:[a-f0-9]{0,30}$", re.IGNORECASE),
        "hashcat": 3100,
        "john": None
    },
    "Cisco-PIX(MD5)": {
        "regex": re.compile(r"^[a-z0-9\/.]{16}$", re.IGNORECASE),
        "hashcat": 2400,
        "john": "pix-md5"
    },
    "Lotus Notes/Domino 6": {
        "regex": re.compile(r"^\([a-z0-9\/+]{20}\)$", re.IGNORECASE),
        "hashcat": 8700,
        "john": "dominosec"
    },
    "BSDi Crypt": {
        "regex": re.compile(r"^_[a-z0-9\/.]{19}$", re.IGNORECASE),
        "hashcat": 12400,
        "john": "bsdicrypt"
    },
    "PKZIP Master Key": {
        "regex": re.compile(r"^[a-f0-9]{24}$", re.IGNORECASE),
        "hashcat": 20500,
        "john": None
    },
    "PKZIP Master Key (6 byte optimization)": {
        "regex": re.compile(r"^[a-f0-9]{24}$", re.IGNORECASE),
        "hashcat": 20510,
        "john": None
    },
    "Keepass 1 AES / without keyfile": {
        "regex": re.compile(r"^\$keepass\$\*1\*50000\*(0|1)\*([a-f0-9]{32})\*([a-f0-9]{64})\*([a-f0-9]{32})\*([a-f0-9]{64})\*1\*(192|1360)\*([a-f0-9]{384})$"),
        "hashcat": 13400,
        "john": None
    },
    "Keepass 1 Twofish / with keyfile": {
        "regex": re.compile(r"^\$keepass\$\*1\*6000\*(0|1)\*([a-f0-9]{32})\*([a-f0-9]{64})\*([a-f0-9]{32})\*([a-f0-9]{64})\*1\*(192|1360)\*([a-f0-9]{2720})\*1\*64\*([a-f0-9]{64})$"),
        "hashcat": 13400,
        "john": None
    },
    "Keepass 2 AES / with keyfile": {
        "regex": re.compile(r"^\$keepass\$\*2\*6000\*222(\*[a-f0-9]{64}){2}(\*[a-f0-9]{32}){1}(\*[a-f0-9]{64}){2}\*1\*64(\*[a-f0-9]{64}){1}$"),
        "hashcat": 13400,
        "john": None
    },
    "Keepass 2 AES / without keyfile": {
        "regex": re.compile(r"^\$keepass\$\*2\*6000\*222\*(([a-f0-9]{32,64})(\*)?)+$"),
        "hashcat": 13400,
        "john": None
    },
    "MD5": {
        "regex": re.compile(r"^[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 0,
        "john": "raw-md5"
    },
    "MD4": {
        "regex": re.compile(r"^[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 900,
        "john": "raw-md4"
    },
    "Double MD5": {
        "regex": re.compile(r"^[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 2600,
        "john": None
    },
    "Lotus Notes/Domino 5": {
        "regex": re.compile(r"^[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 8600,
        "john": "lotus5"
    },
    "LM": {
        "regex": re.compile(r"^[a-f0-9]{16}$", re.IGNORECASE),
        "hashcat": 3000,
        "john": "lm"
    },
    "Skype": {
        "regex": re.compile(r"^[a-f0-9]{32}:[a-z0-9]+$", re.IGNORECASE),
        "hashcat": 23,
        "john": None
    },
    "PrestaShop": {
        "regex": re.compile(r"^[a-f0-9]{32}:[a-z0-9]{56}$", re.IGNORECASE),
        "hashcat": 11000,
        "john": None
    },
    "NTLM": {
        "regex": re.compile(r"^(\$NT\$)?[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 1000,
        "john": "nt"
    },
    "Domain Cached Credentials": {
        "regex": re.compile(r'^([^\\\/:*?"<>|]{1,20}:)?[a-f0-9]{32}(:[^\\\/:*?"<>|]{1,20})?$', re.IGNORECASE),
        "hashcat": 1100,
        "john": "mscash"
    },
    "Domain Cached Credentials 2": {
        "regex": re.compile(r'^([^\\\/:*?"<>|]{1,20}:)?(\$DCC2\$10240#[^\\\/:*?"<>|]{1,20}#)?[a-f0-9]{32}$', re.IGNORECASE),
        "hashcat": 2100,
        "john": "mscash2"
    },
    "SHA-1(Base64)": {
        "regex": re.compile(r"^{SHA}[a-z0-9\/+]{27}=$", re.IGNORECASE),
        "hashcat": 101,
        "john": "nsldap"
    },
    "Netscape LDAP SHA": {
        "regex": re.compile(r"^{SHA}[a-z0-9\/+]{27}=$", re.IGNORECASE),
        "hashcat": 101,
        "john": "nsldap"
    },
    "MD5 Crypt": {
        "regex": re.compile(r"^\$1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}(:.*)?$", re.IGNORECASE),
        "hashcat": 500,
        "john": "md5crypt"
    },
    "Cisco-IOS(MD5)": {
        "regex": re.compile(r"^\$1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}(:.*)?$", re.IGNORECASE),
        "hashcat": 500,
        "john": "md5crypt"
    },
    "FreeBSD MD5": {
        "regex": re.compile(r"^\$1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}(:.*)?$", re.IGNORECASE),
        "hashcat": 500,
        "john": "md5crypt"
    },
    "phpBB v3.x": {
        "regex": re.compile(r"^\$H\$[a-z0-9\/.]{31}$", re.IGNORECASE),
        "hashcat": 400,
        "john": "phpass"
    },
    "Wordpress v2.6.0/2.6.1": {
        "regex": re.compile(r"^\$H\$[a-z0-9\/.]{31}$", re.IGNORECASE),
        "hashcat": 400,
        "john": "phpass"
    },
    "PHPass' Portable Hash": {
        "regex": re.compile(r"^\$H\$[a-z0-9\/.]{31}$", re.IGNORECASE),
        "hashcat": 400,
        "john": "phpass"
    },
    "Wordpress ≥ v2.6.2": {
        "regex": re.compile(r"^\$P\$[a-z0-9\/.]{31}$", re.IGNORECASE),
        "hashcat": 400,
        "john": "phpass"
    },
    "Joomla ≥ v2.5.18": {
        "regex": re.compile(r"^\$P\$[a-z0-9\/.]{31}$", re.IGNORECASE),
        "hashcat": 400,
        "john": "phpass"
    },
    "osCommerce": {
        "regex": re.compile(r"^[a-f0-9]{32}:[a-z0-9]{2}$", re.IGNORECASE),
        "hashcat": 21,
        "john": None
    },
    "xt:Commerce": {
        "regex": re.compile(r"^[a-f0-9]{32}:[a-z0-9]{2}$", re.IGNORECASE),
        "hashcat": 21,
        "john": None
    },
    "MD5(APR)": {
        "regex": re.compile(r"^\$apr1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}$", re.IGNORECASE),
        "hashcat": 1600,
        "john": None
    },
    "Apache MD5": {
        "regex": re.compile(r"^\$apr1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}$", re.IGNORECASE),
        "hashcat": 1600,
        "john": None
    },
    "AIX(smd5)": {
        "regex": re.compile(r"^{smd5}[a-z0-9$\/.]{31}$", re.IGNORECASE),
        "hashcat": 6300,
        "john": "aix-smd5"
    },
    "IP.Board ≥ v2+": {
        "regex": re.compile(r"^[a-f0-9]{32}:.{5}$", re.IGNORECASE),
        "hashcat": 2811,
        "john": None
    },
    "MyBB ≥ v1.2+": {
        "regex": re.compile(r"^[a-f0-9]{32}:.{8}$", re.IGNORECASE),
        "hashcat": 2811,
        "john": None
    },
    "SHA-1": {
        "regex": re.compile(r"^[a-f0-9]{40}(:.+)?$", re.IGNORECASE),
        "hashcat": 100,
        "john": "raw-sha1"
    },
    "Double SHA-1": {
        "regex": re.compile(r"^[a-f0-9]{40}(:.+)?$", re.IGNORECASE),
        "hashcat": 4500,
        "john": None
    },
    "RIPEMD-160": {
        "regex": re.compile(r"^[a-f0-9]{40}(:.+)?$", re.IGNORECASE),
        "hashcat": 6000,
        "john": "ripemd-160"
    },
    "LinkedIn": {
        "regex": re.compile(r"^[a-f0-9]{40}(:.+)?$", re.IGNORECASE),
        "hashcat": 190,
        "john": "raw-sha1-linkedin"
    },
    "MySQL5.x": {
        "regex": re.compile(r"^[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 300,
        "john": "mysql-sha1"
    },
    "MySQL4.1": {
        "regex": re.compile(r"^[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 300,
        "john": "mysql-sha1"
    },
    "Cisco-IOS(SHA-256)": {
        "regex": re.compile(r"^[a-z0-9]{43}$", re.IGNORECASE),
        "hashcat": 5700,
        "john": None
    },
    "SSHA-1(Base64)": {
        "regex": re.compile(r"^{SSHA}[a-z0-9\/+]{38}==$", re.IGNORECASE),
        "hashcat": 111,
        "john": "nsldaps"
    },
    "Netscape LDAP SSHA": {
        "regex": re.compile(r"^{SSHA}[a-z0-9\/+]{38}==$", re.IGNORECASE),
        "hashcat": 111,
        "john": "nsldaps"
    },
    "Fortigate(FortiOS)": {
        "regex": re.compile(r"^[a-z0-9=]{47}$", re.IGNORECASE),
        "hashcat": 7000,
        "john": "fortigate"
    },
    "OSX v10.4": {
        "regex": re.compile(r"^[a-f0-9]{48}$", re.IGNORECASE),
        "hashcat": 122,
        "john": "xsha"
    },
    "OSX v10.5": {
        "regex": re.compile(r"^[a-f0-9]{48}$", re.IGNORECASE),
        "hashcat": 122,
        "john": "xsha"
    },
    "OSX v10.6": {
        "regex": re.compile(r"^[a-f0-9]{48}$", re.IGNORECASE),
        "hashcat": 122,
        "john": "xsha"
    },
    "AIX(ssha1)": {
        "regex": re.compile(r"^{ssha1}[0-9]{2}\$[a-z0-9$\/.]{44}$", re.IGNORECASE),
        "hashcat": 6700,
        "john": "aix-ssha1"
    },
    "MSSQL(2005)": {
        "regex": re.compile(r"^0x0100[a-f0-9]{48}$", re.IGNORECASE),
        "hashcat": 132,
        "john": "mssql05"
    },
    "MSSQL(2008)": {
        "regex": re.compile(r"^0x0100[a-f0-9]{48}$", re.IGNORECASE),
        "hashcat": 132,
        "john": "mssql05"
    },
    "Sun MD5 Crypt": {
        "regex": re.compile(r"^(\$md5,rounds=[0-9]+\$|\$md5\$rounds=[0-9]+\$|\$md5\$)[a-z0-9\/.]{0,16}(\$|\$\$)[a-z0-9\/.]{22}$", re.IGNORECASE),
        "hashcat": 3300,
        "john": "sunmd5"
    },
    "SHA-224": {
        "regex": re.compile(r"^[a-f0-9]{56}$", re.IGNORECASE),
        "hashcat": 1300,
        "john": "raw-sha224"
    },
    "SHA3-224": {
        "regex": re.compile(r"^[a-f0-9]{56}$", re.IGNORECASE),
        "hashcat": 17300,
        "john": None
    },
    "Keccak-224": {
        "regex": re.compile(r"^[a-f0-9]{56}$", re.IGNORECASE),
        "hashcat": 17700,
        "john": None
    },
    "Blowfish(OpenBSD)": {
        "regex": re.compile(r"^(\$2[abxy]?|\$2)\$[0-9]{2}\$[a-z0-9\/.]{53}$", re.IGNORECASE),
        "hashcat": 3200,
        "john": "bcrypt"
    },
    "bcrypt": {
        "regex": re.compile(r"^(\$2[abxy]?|\$2)\$[0-9]{2}\$[a-z0-9\/.]{53}$", re.IGNORECASE),
        "hashcat": 3200,
        "john": "bcrypt"
    },
    "Android PIN": {
        "regex": re.compile(r"^[a-f0-9]{40}:[a-f0-9]{16}$", re.IGNORECASE),
        "hashcat": 5800,
        "john": None
    },
    "Oracle 11g/12c": {
        "regex": re.compile(r"^(S:)?[a-f0-9]{40}(:)?[a-f0-9]{20}$", re.IGNORECASE),
        "hashcat": 112,
        "john": "oracle11"
    },
    "vBulletin < v3.8.5": {
        "regex": re.compile(r"^[a-f0-9]{32}:.{3}$", re.IGNORECASE),
        "hashcat": 2611,
        "john": None
    },
    "vBulletin ≥ v3.8.5": {
        "regex": re.compile(r"^[a-f0-9]{32}:.{30}$", re.IGNORECASE),
        "hashcat": 2711,
        "john": None
    },
    "SHA-256": {
        "regex": re.compile(r"^[a-f0-9]{64}(:.+)?$", re.IGNORECASE),
        "hashcat": 1400,
        "john": "raw-sha256"
    },
    "GOST R 34.11-94": {
        "regex": re.compile(r"^[a-f0-9]{64}(:.+)?$", re.IGNORECASE),
        "hashcat": 6900,
        "john": "gost"
    },
    "SHA3-256": {
        "regex": re.compile(r"^[a-f0-9]{64}(:.+)?$", re.IGNORECASE),
        "hashcat": 17400,
        "john": "dynamic_380"
    },
    "Joomla < v2.5.18": {
        "regex": re.compile(r"^[a-f0-9]{32}:[a-z0-9]{32}$", re.IGNORECASE),
        "hashcat": 11,
        "john": None
    },
    "MD5(Chap)": {
        "regex": re.compile(r"^(\$chap\$0\*)?[a-f0-9]{32}[\*:][a-f0-9]{32}(:[0-9]{2})?$", re.IGNORECASE),
        "hashcat": 4800,
        "john": "chap"
    },
    "iSCSI CHAP Authentication": {
        "regex": re.compile(r"^(\$chap\$0\*)?[a-f0-9]{32}[\*:][a-f0-9]{32}(:[0-9]{2})?$", re.IGNORECASE),
        "hashcat": 4800,
        "john": "chap"
    },
    "EPiServer 6.x < v4": {
        "regex": re.compile(r"^\$episerver\$\*0\*[a-z0-9\/=+]+\*[a-z0-9\/=+]{27,28}$", re.IGNORECASE),
        "hashcat": 141,
        "john": "episerver"
    },
    "AIX(ssha256)": {
        "regex": re.compile(r"^{ssha256}[0-9]{2}\$[a-z0-9$\/.]{60}$", re.IGNORECASE),
        "hashcat": 6400,
        "john": "aix-ssha256"
    },
    "EPiServer 6.x ≥ v4": {
        "regex": re.compile(r"^\$episerver\$\*1\*[a-z0-9\/=+]+\*[a-z0-9\/=+]{42,43}$", re.IGNORECASE),
        "hashcat": 1441,
        "john": "episerver"
    },
    "MSSQL(2000)": {
        "regex": re.compile(r"^0x0100[a-f0-9]{88}$", re.IGNORECASE),
        "hashcat": 131,
        "john": "mssql"
    },
    "SHA-384": {
        "regex": re.compile(r"^[a-f0-9]{96}$", re.IGNORECASE),
        "hashcat": 10800,
        "john": "raw-sha384"
    },
    "SSHA-512(Base64)": {
        "regex": re.compile(r"^{SSHA512}[a-z0-9\/+]{96}$", re.IGNORECASE),
        "hashcat": 1711,
        "john": "ssha512"
    },
    "LDAP(SSHA-512)": {
        "regex": re.compile(r"^{SSHA512}[a-z0-9\/+]{96}$", re.IGNORECASE),
        "hashcat": 1711,
        "john": "ssha512"
    },
    "AIX(ssha512)": {
        "regex": re.compile(r"^{ssha512}[0-9]{2}\$[a-z0-9\/.]{16,48}\$[a-z0-9\/.]{86}$", re.IGNORECASE),
        "hashcat": 6500,
        "john": "aix-ssha512"
    },
    "SHA-512": {
        "regex": re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE),
        "hashcat": 1700,
        "john": "raw-sha512"
    },
    "Keccak-512": {
        "regex": re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE),
        "hashcat": 1800,
        "john": None
    },
    "Whirlpool": {
        "regex": re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE),
        "hashcat": 6100,
        "john": "whirlpool"
    },
    "Blake2": {
        "regex": re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE),
        "hashcat": 600,
        "john": "raw-blake2"
    },
    "SHA3-512": {
        "regex": re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE),
        "hashcat": 17600,
        "john": "raw-sha3"
    },
    "Keccak-256": {
        "regex": re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE),
        "hashcat": 17800,
        "john": None
    },
    "Keccac-384": {
        "regex": re.compile(r"^[a-f0-9]{96}$", re.IGNORECASE),
        "hashcat": 17900,
        "john": None
    },
    "OSX v10.7": {
        "regex": re.compile(r"^[a-f0-9]{136}$", re.IGNORECASE),
        "hashcat": 1722,
        "john": "xsha512"
    },
    "MSSQL(2012)": {
        "regex": re.compile(r"^0x0200[a-f0-9]{136}$", re.IGNORECASE),
        "hashcat": 1731,
        "john": "mssql12"
    },
    "MSSQL(2014)": {
        "regex": re.compile(r"^0x0200[a-f0-9]{136}$", re.IGNORECASE),
        "hashcat": 1731,
        "john": "mssql12"
    },
    "OSX v10.8": {
        "regex": re.compile(r"^\$ml\$[0-9]+\$[a-f0-9]{64}\$[a-f0-9]{128}$", re.IGNORECASE),
        "hashcat": 7100,
        "john": "pbkdf2-hmac-sha512"
    },
    "OSX v10.9": {
        "regex": re.compile(r"^\$ml\$[0-9]+\$[a-f0-9]{64}\$[a-f0-9]{128}$", re.IGNORECASE),
        "hashcat": 7100,
        "john": "pbkdf2-hmac-sha512"
    },
    "GRUB 2": {
        "regex": re.compile(r"^grub\.pbkdf2\.sha512\.[0-9]+\.([a-f0-9]{128,2048}\.|[0-9]+\.)?[a-f0-9]{128}$", re.IGNORECASE),
        "hashcat": 7200,
        "john": None
    },
    "Django(SHA-1)": {
        "regex": re.compile(r"^sha1\$[a-z0-9]+\$[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 124,
        "john": None
    },
    "Citrix Netscaler": {
        "regex": re.compile(r"^[a-f0-9]{49}$", re.IGNORECASE),
        "hashcat": 8100,
        "john": "citrix_ns10"
    },
    "Drupal > v7.x": {
        "regex": re.compile(r"^\$S\$[a-z0-9\/.]{52}$", re.IGNORECASE),
        "hashcat": 7900,
        "john": "drupal7"
    },
    "SHA-256 Crypt": {
        "regex": re.compile(r"^\$5\$(rounds=[0-9]+\$)?[a-z0-9\/.]{0,16}\$[a-z0-9\/.]{43}$", re.IGNORECASE),
        "hashcat": 7400,
        "john": "sha256crypt"
    },
    "Sybase ASE": {
        "regex": re.compile(r"^0x[a-f0-9]{4}[a-f0-9]{16}[a-f0-9]{64}$", re.IGNORECASE),
        "hashcat": 8000,
        "john": "sybasease"
    },
    "SHA-512 Crypt": {
        "regex": re.compile(r"^\$6\$(rounds=[0-9]+\$)?[a-z0-9\/.]{0,16}\$[a-z0-9\/.]{86}$", re.IGNORECASE),
        "hashcat": 1800,
        "john": "sha512crypt"
    },
    "Minecraft(AuthMe Reloaded)": {
        "regex": re.compile(r"^\$sha\$[a-z0-9]{1,16}\$([a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64}|[a-f0-9]{128}|[a-f0-9]{140})$", re.IGNORECASE),
        "hashcat": 20711,
        "john": None
    },
    "PHPS": {
        "regex": re.compile(r"^\$PHPS\$.+\$[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 2612,
        "john": "phps"
    },
    "1Password(Agile Keychain)": {
        "regex": re.compile(r"^[0-9]{4}:[a-f0-9]{16}:[a-f0-9]{2080}$", re.IGNORECASE),
        "hashcat": 6600,
        "john": None
    },
    "1Password(Cloud Keychain)": {
        "regex": re.compile(r"^[a-f0-9]{64}:[a-f0-9]{32}:[0-9]{5}:[a-f0-9]{608}$", re.IGNORECASE),
        "hashcat": 8200,
        "john": None
    },
    "IKE-PSK MD5": {
        "regex": re.compile(r"^[a-f0-9]{256}:[a-f0-9]{256}:[a-f0-9]{16}:[a-f0-9]{16}:[a-f0-9]{320}:[a-f0-9]{16}:[a-f0-9]{40}:[a-f0-9]{40}:[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 5300,
        "john": None
    },
    "IKE-PSK SHA1": {
        "regex": re.compile(r"^[a-f0-9]{256}:[a-f0-9]{256}:[a-f0-9]{16}:[a-f0-9]{16}:[a-f0-9]{320}:[a-f0-9]{16}:[a-f0-9]{40}:[a-f0-9]{40}:[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 5400,
        "john": None
    },
    "PeopleSoft": {
        "regex": re.compile(r"^[a-z0-9\/+]{27}=$", re.IGNORECASE),
        "hashcat": 133,
        "john": None
    },
    "Django(PBKDF2-HMAC-SHA256)": {
        "regex": re.compile(r"^(\$django\$\*1\*)?pbkdf2_sha256\$[0-9]+\$[a-z0-9]+\$[a-z0-9\/+=]{44}$", re.IGNORECASE),
        "hashcat": 10000,
        "john": "django"
    },
    "Lotus Notes/Domino 8": {
        "regex": re.compile(r"^\([a-z0-9\/+]{49}\)$", re.IGNORECASE),
        "hashcat": 9100,
        "john": None
    },
    "scrypt": {
        "regex": re.compile(r"^SCRYPT:[0-9]{1,}:[0-9]{1}:[0-9]{1}:[a-z0-9:\/+=]{1,}$", re.IGNORECASE),
        "hashcat": 8900,
        "john": None
    },
    "Cisco Type 8": {
        "regex": re.compile(r"^\$8\$[a-z0-9\/.]{14}\$[a-z0-9\/.]{43}$", re.IGNORECASE),
        "hashcat": 9200,
        "john": "cisco8"
    },
    "Cisco Type 9": {
        "regex": re.compile(r"^\$9\$[a-z0-9\/.]{14}\$[a-z0-9\/.]{43}$", re.IGNORECASE),
        "hashcat": 9300,
        "john": "cisco9"
    },
    "Microsoft Office 2007": {
        "regex": re.compile(r"^\$office\$\*2007\*[0-9]{2}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{40}$", re.IGNORECASE),
        "hashcat": 9400,
        "john": "office"
    },
    "Microsoft Office 2010": {
        "regex": re.compile(r"^\$office\$\*2010\*[0-9]{6}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{64}$", re.IGNORECASE),
        "hashcat": 9500,
        "john": "office"
    },
    "Microsoft Office 2016 - SheetProtection": {
        "regex": re.compile(r"^\\$office\\$2016\\$[0-9]\\$[0-9]{6}\\$[^$]{24}\\$[^$]{88}$", re.IGNORECASE),
        "hashcat": 25300,
        "john": None
    },
    "Microsoft Office 2013": {
        "regex": re.compile(r"^\$office\$\*2013\*[0-9]{6}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{64}$", re.IGNORECASE),
        "hashcat": 9600,
        "john": "office"
    },
    "Android FDE ≤ 4.3": {
        "regex": re.compile(r"^\$fde\$[0-9]{2}\$[a-f0-9]{32}\$[0-9]{2}\$[a-f0-9]{32}\$[a-f0-9]{3072}$", re.IGNORECASE),
        "hashcat": 8800,
        "john": "fde"
    },
    "Kerberos 5 TGS-REP etype 23": {
        "regex": re.compile(r"\$krb5tgs\$23\$\*[^*]*\*\$[a-f0-9]{32}\$[a-f0-9]{64,40960}", re.IGNORECASE),
        "hashcat": 13100,
        "john": "krb5tgs"
    },
    "Microsoft Office ≤ 2003 (MD5+RC4)": {
        "regex": re.compile(r"^\$oldoffice\$[01]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 9700,
        "john": "oldoffice"
    },
    "Microsoft Office ≤ 2003 (MD5+RC4) collider-mode #1": {
        "regex": re.compile(r"^\$oldoffice\$[01]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 9710,
        "john": "oldoffice"
    },
    "Microsoft Office ≤ 2003 (SHA1+RC4)": {
        "regex": re.compile(r"^\$oldoffice\$[34]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 9800,
        "john": "oldoffice"
    },
    "Microsoft Office ≤ 2003 (SHA1+RC4) collider-mode #1": {
        "regex": re.compile(r"^\$oldoffice\$[34]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 9810,
        "john": "oldoffice"
    },
    "MS Office ⇐ 2003 $3, SHA1 + RC4, collider #2": {
        "regex": re.compile(r"^\$oldoffice\$[34]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{40}:[a-f0-9]{10}", re.IGNORECASE),
        "hashcat": 9820,
        "john": "oldoffice"
    },
    "RAdmin v2.x": {
        "regex": re.compile(r"^(\$radmin2\$)?[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 9900,
        "john": "radmin"
    },
    "SAP CODVN H (PWDSALTEDHASH) iSSHA-1": {
        "regex": re.compile(r"^{x-issha,\s[0-9]{4}}[a-z0-9\/+=]+$", re.IGNORECASE),
        "hashcat": 10300,
        "john": "saph"
    },
    "CRAM-MD5": {
        "regex": re.compile(r"^\$cram_md5\$[a-z0-9\/+=-]+\$[a-z0-9\/+=-]{52}$", re.IGNORECASE),
        "hashcat": 10200,
        "john": None
    },
    "SipHash": {
        "regex": re.compile(r"^[a-f0-9]{16}:2:4:[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 10100,
        "john": None
    },
    "PostgreSQL Challenge-Response Authentication (MD5)": {
        "regex": re.compile(r"^\$postgres\$.[^\*]+[*:][a-f0-9]{1,32}[*:][a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 11100,
        "john": "postgres"
    },
    "PBKDF2-HMAC-SHA256(PHP)": {
        "regex": re.compile(r"^sha256[:$][0-9]+[:$][a-z0-9\/+=]+[:$][a-z0-9\/+]{32,128}$", re.IGNORECASE),
        "hashcat": 10900,
        "john": None
    },
    "MySQL Challenge-Response Authentication (SHA1)": {
        "regex": re.compile(r"^\$mysqlna\$[a-f0-9]{40}[:*][a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 11200,
        "john": None
    },
    "PDF 1.1 - 1.3 (Acrobat 2 - 4)": {
        "regex": re.compile(r"\$pdf\$1\*[2|3]\*[0-9]{2}\*[-0-9]{1,6}\*[0-9]\*[0-9]{2}\*[a-f0-9]{32,32}\*[0-9]{2}\*[a-f0-9]{64}\*[0-9]{2}\*[a-f0-9]{64}", re.IGNORECASE),
        "hashcat": 10400,
        "john": "pdf"
    },
    "PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #1": {
        "regex": re.compile(r"\$pdf\$1\*[2|3]\*[0-9]{2}\*[-0-9]{1,6}\*[0-9]\*[0-9]{2}\*[a-f0-9]{32,32}\*[0-9]{2}\*[a-f0-9]{64}\*[0-9]{2}\*[a-f0-9]{64}", re.IGNORECASE),
        "hashcat": 10410,
        "john": "pdf"
    },
    "PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #2": {
        "regex": re.compile(r"\$pdf\$1\*[2|3]\*[0-9]{2}\*[-0-9]{1,6}\*[0-9]\*[0-9]{2}\*[a-f0-9]{32}\*[0-9]{2}\*[a-f0-9]{64}\*[0-9]{2}\*[a-f0-9]{64}:[a-f0-9]{10}", re.IGNORECASE),
        "hashcat": 10420,
        "john": None
    },
    "PDF 1.4 - 1.6 (Acrobat 5 - 8)": {
        "regex": re.compile(r"^\$pdf\$[24]\*[34]\*128\*[0-9-]{1,5}\*1\*(16|32)\*[a-f0-9]{32,64}\*32\*[a-f0-9]{64}\*(8|16|32)\*[a-f0-9]{16,64}$", re.IGNORECASE),
        "hashcat": 10500,
        "john": "pdf"
    },
    "PDF 1.7 Level 3 (Acrobat 9)": {
        "regex": re.compile(r"\$pdf\$5\*[5|6]\*[0-9]{3}\*[-0-9]{1,6}\*[0-9]\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}", re.IGNORECASE),
        "hashcat": 10600,
        "john": "pdf"
    },
    "PDF 1.7 Level 8 (Acrobat 10 - 11)": {
        "regex": re.compile(r"\$pdf\$5\*[5|6]\*[0-9]{3}\*[-0-9]{1,6}\*[0-9]\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}\*[0-9]{1,4}\*[a-f0-9]{0,1024}", re.IGNORECASE),
        "hashcat": 10700,
        "john": "pdf"
    },
    "Kerberos 5 AS-REP etype 23": {
        "regex": re.compile(r"^\$krb5asrep\$23\$[^:]+:[a-f0-9]{32,32}\$[a-f0-9]{64,40960}$", re.IGNORECASE),
        "hashcat": 18200,
        "john": "krb5pa-sha1"
    },
    "Kerberos 5 TGS-REP etype 17 (AES128-CTS-HMAC-SHA1-96)": {
        "regex": re.compile(r"^\$krb5tgs\$17\$[^$]{1,512}\$[^$]{1,512}\$[^$]{1,4}?\$?[a-f0-9]{1,32}\$[a-f0-9]{64,40960}$", re.IGNORECASE),
        "hashcat": 19600,
        "john": None
    },
    "Kerberos 5 TGS-REP etype 18 (AES256-CTS-HMAC-SHA1-96)": {
        "regex": re.compile(r"^\$krb5tgs\$18\$[^$]{1,512}\$[^$]{1,512}\$[^$]{1,4}?\$?[a-f0-9]{1,32}\$[a-f0-9]{64,40960}", re.IGNORECASE),
        "hashcat": 19700,
        "john": None
    },
    "Kerberos 5, etype 17, Pre-Auth": {
        "regex": re.compile(r"^\$krb5pa\$17\$[^$]{1,512}\$[^$]{1,512}\$[a-f0-9]{104,112}$", re.IGNORECASE),
        "hashcat": 19800,
        "john": None
    },
    "Kerberos 5, etype 18, Pre-Auth": {
        "regex": re.compile(r"^\$krb5pa\$18\$[^$]{1,512}\$[^$]{1,512}\$[a-f0-9]{104,112}$", re.IGNORECASE),
        "hashcat": 19900,
        "john": None
    },
    "Bitcoin / Litecoin": {
        "regex": re.compile(r"\$bitcoin\$[0-9]{2,4}\$[a-f0-9$]{250,350}", re.IGNORECASE),
        "hashcat": 11300,
        "john": "bitcoin"
    },
    "Ethereum Wallet, PBKDF2-HMAC-SHA256": {
        "regex": re.compile(r"\$ethereum\$[a-z0-9*]{150,250}", re.IGNORECASE),
        "hashcat": 15600,
        "john": "ethereum-opencl"
    },
    "Ethereum Pre-Sale Wallet, PBKDF2-HMAC-SHA256": {
        "regex": re.compile(r"\$ethereum\$[a-z0-9*]{150,250}", re.IGNORECASE),
        "hashcat": 16300,
        "john": "ethereum-presale-opencl"
    },
    "Electrum Wallet (Salt-Type 1-3)": {
        "regex": re.compile(r"^\$electrum\$[1-3]\*[a-f0-9]{32,32}\*[a-f0-9]{32,32}$", re.IGNORECASE),
        "hashcat": 16600,
        "john": "electrum"
    },
    "Electrum Wallet (Salt-Type 4)": {
        "regex": re.compile(r"^\$electrum\$4\*[a-f0-9]{1,66}\*[a-f0-9]{128,32768}\*[a-f0-9]{64,64}$", re.IGNORECASE),
        "hashcat": 21700,
        "john": "electrum"
    },
    "Electrum Wallet (Salt-Type 5)": {
        "regex": re.compile(r"^\$electrum\$5\*[a-f0-9]{66,66}\*[a-f0-9]{2048,2048}\*[a-f0-9]{64,64}$", re.IGNORECASE),
        "hashcat": 21800,
        "john": "electrum"
    },
    "Android Backup": {
        "regex": re.compile(r"\$ab\$[0-9]{1}\*[0-9]{1}\*[0-9]{1,6}\*[a-f0-9]{128}\*[a-f0-9]{128}\*[a-f0-9]{32}\*[a-f0-9]{192}", re.IGNORECASE),
        "hashcat": 18900,
        "john": "androidbackup"
    },
    "WinZip": {
        "regex": re.compile(r"\$zip2\$\*[0-9]{1}\*[0-9]{1}\*[0-9]{1}\*[a-f0-9]{16,32}\*[a-f0-9]{1,6}\*[a-f0-9]{1,6}\*[a-f0-9]+\*[a-f0-9]{20}\*\$\/zip2\$", re.IGNORECASE),
        "hashcat": 13600,
        "john": "zip"
    },
    "iTunes backup >= 10.0": {
        "regex": re.compile(r"\$itunes_backup\$\*[0-9]{1,2}\*[a-f0-9]{80}\*[0-9]{1,6}\*[a-f0-9]{40}\*[0-9]{0,10}\*[a-f0-9]{0,40}", re.IGNORECASE),
        "hashcat": 14800,
        "john": "itunes-backup"
    },
    "iTunes backup < 10.0": {
        "regex": re.compile(r"\$itunes_backup\$\*[0-9]{1,2}\*[a-f0-9]{80}\*[0-9]{1,6}\*[a-f0-9]{40}\*[0-9]{0,10}\*[a-f0-9]{0,40}", re.IGNORECASE),
        "hashcat": 14700,
        "john": "itunes-backup"
    },
    "Telegram Mobile App Passcode (SHA256)": {
        "regex": re.compile(r"\$telegram\$[a-f0-9*]{99}", re.IGNORECASE),
        "hashcat": 22301,
        "john": "Telegram"
    },
    "BLAKE2b-512": {
        "regex": re.compile(r"\$BLAKE2\$[a-f0-9]{128}", re.IGNORECASE),
        "hashcat": 600,
        "john": None
    },
    "MS Office ⇐ 2003 $0/$1, MD5 + RC4, collider #2": {
        "regex": re.compile(r"\$oldoffice\$[a-f0-9*]{100}:[a-f0-9]{10}", re.IGNORECASE),
        "hashcat": 9720,
        "john": "oldoffice"
    },
    "7-zip": {
        "regex": re.compile(r"\$7z\$[0-9]\$[0-9]{1,2}\$[0-9]{1}\$[^$]{0,64}\$[0-9]{1,2}\$[a-f0-9]{32}\$[0-9]{1,10}\$[0-9]{1,6}\$[0-9]{1,6}\$[a-f0-9]{2,}", re.IGNORECASE),
        "hashcat": 11600,
        "john": "7z"
    },
    "SecureZIP AES-256": {
        "regex": re.compile(r"\$zip3\$\*[0-9]\*[0-9]\*256\*[0-9]\*[a-f0-9]{0,32}\*[a-f0-9]{288}\*[0-9]\*[0-9]\*[0-9]\*[^\s]{0,64}", re.IGNORECASE),
        "hashcat": 23003,
        "john": "securezip"
    },
    "SecureZIP AES-192": {
        "regex": re.compile(r"\$zip3\$\*[0-9]\*[0-9]\*192\*[0-9]\*[a-f0-9]{0,32}\*[a-f0-9]{288}\*[0-9]\*[0-9]\*[0-9]\*[^\s]{0,64}", re.IGNORECASE),
        "hashcat": 23002,
        "john": "securezip"
    },
    "SecureZIP AES-128": {
        "regex": re.compile(r"\$zip3\$\*[0-9]\*[0-9]\*128\*[0-9]\*[a-f0-9]{0,32}\*[a-f0-9]{288}\*[0-9]\*[0-9]\*[0-9]\*[^\s]{0,64}", re.IGNORECASE),
        "hashcat": 23001,
        "john": "securezip"
    },
    "PKZIP (Compressed)": {
        "regex": re.compile(r"^\$pkzip2?\$(1)\*[0-9]{1}\*[0-9]{1}\*[0-9a-f]{1,3}\*[0-9a-f]{1,8}\*[0-9a-f]{1,4}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*(8)\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[a-f0-9]+\*\$\/pkzip2?\$", re.IGNORECASE),
        "hashcat": 17200,
        "john": "pkzip"
    },
    "PKZIP (Uncompressed)": {
        "regex": re.compile(r"^\$pkzip2?\$(1)\*[0-9]{1}\*[0-9]{1}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}\*(0)\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[a-f0-9]+\*\$\/pkzip2?\$", re.IGNORECASE),
        "hashcat": 17210,
        "john": "pkzip"
    },
    "PKZIP (Compressed Multi-File)": {
        "regex": re.compile(r"^\$pkzip2?\$([2-8])\*[0-9]{1}(\*[0-9]{1}\*[0-9a-f]{1,3}\*([^0*][0-9a-f]{0,2})\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[0-9a-f]+)+\*(8)\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[a-f0-9]+\*\$\/pkzip2?\$", re.IGNORECASE),
        "hashcat": 17220,
        "john": "pkzip"
    },
    "PKZIP (Mixed Multi-File)": {
        "regex": re.compile(r"^\$pkzip2?\$([2-8])\*[0-9]{1}(\*[0-9]{1}\*[0-9a-f]{1,8}\*([0-9a-f]{1,8})\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[0-9a-f]+)+\*([08])\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[a-f0-9]+\*\$\/pkzip2?\$", re.IGNORECASE),
        "hashcat": 17225,
        "john": "pkzip"
    },
    "PKZIP (Mixed Multi-File Checksum-Only)": {
        "regex": re.compile(r"^\$pkzip2?\$([2-8])\*[0-9]{1}(\*[0-9]{1}\*[0-9a-f]{1,3}\*[0-9a-f]{1,8}\*[0-9a-f]{1,8}(\*[0-9a-f]{1,8})?\*[0-9a-f]{1,8}\*[0-9a-f]+)+\*\$\/pkzip2?\$", re.IGNORECASE),
        "hashcat": 17230,
        "john": "pkzip"
    },
    "BitLocker": {
        "regex": re.compile(r"\$bitlocker\$[0-9]\$[0-9]{2}\$[a-f0-9]{32}\$[a-f0-9]{7}\$[a-f0-9]{2}\$[a-f0-9]{24}\$[a-f0-9]{2}\$[a-f0-9]{120}", re.IGNORECASE),
        "hashcat": 22100,
        "john": "bitlocker"
    },
    "RACF": {
        "regex": re.compile(r"\$racf\$\*.{1,}\*[A-F0-9]{16}", re.IGNORECASE),
        "hashcat": 8500,
        "john": None
    },
    "RSA/DSA/EC/OpenSSH Private Keys ($4$)": {
        "regex": re.compile(r"^\$sshng\$4\$16\$[0-9]{32}\$1232\$[a-f0-9]{2464}$", re.IGNORECASE),
        "hashcat": 22941,
        "john": None
    },
    "RAR3-p (Uncompressed)": {
        "regex": re.compile(r"^\$RAR3\$\*(1)\*[0-9a-f]{1,16}\*[0-9a-f]{1,8}\*[0-9a-f]{1,16}\*[0-9a-f]{1,16}\*[01]\*([0-9a-f]+|[^*]{1,64}\*[0-9a-f]{1,16})\*30$", re.IGNORECASE),
        "hashcat": 23700,
        "john": "rar"
    },
    "RAR3-p (Compressed)": {
        "regex": re.compile(r"^\$RAR3\$\*(1)\*[0-9a-f]{1,16}\*[0-9a-f]{1,8}\*[0-9a-f]{1,16}\*[0-9a-f]{1,16}\*[01]\*([0-9a-f]+|[^*]{1,64}\*[0-9a-f]{1,16})\*(31|32|33|34|35)$", re.IGNORECASE),
        "hashcat": 23800,
        "john": "rar"
    },
    "RAR3-hp": {
        "regex": re.compile(r"^\$RAR3\$\*0\*[0-9a-f]{1,16}\*[0-9a-f]+$", re.IGNORECASE),
        "hashcat": 12500,
        "john": "rar"
    },
    "RAR5": {
        "regex": re.compile(r"^\$rar5\$[0-9a-f]{1,2}\$[0-9a-f]{1,32}\$[0-9a-f]{1,2}\$[0-9a-f]{1,32}\$[0-9a-f]{1,2}\$[0-9a-f]{1,16}$", re.IGNORECASE),
        "hashcat": 13000,
        "john": "rar5"
    },
    "KeePass 1 AES (without keyfile)": {
        "regex": re.compile(r"^\$keepass\$\*1\*\d+\*\d\*[0-9a-f]{32}\*[0-9a-f]{64}\*[0-9a-f]{32}\*[0-9a-f]{64}\*\d\*[^*]*(\*[0-9a-f]+)?$", re.IGNORECASE),
        "hashcat": 13400,
        "john": "KeePass"
    },
    "KeePass 1 TwoFish (with keyfile)": {
        "regex": re.compile(r"^\$keepass\$\*1\*\d+\*\d\*[0-9a-f]{32}\*[0-9a-f]{64}\*[0-9a-f]{32}\*[0-9a-f]{64}\*\d\*[^*]*(\*[0-9a-f]+)?\*\d+\*\d+\*[0-9a-f]{64}$", re.IGNORECASE),
        "hashcat": 13400,
        "john": "KeePass"
    },
    "KeePass 2 AES (without keyfile)": {
        "regex": re.compile(r"^\$keepass\$\*2\*\d+\*\d+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+$", re.IGNORECASE),
        "hashcat": 13400,
        "john": "KeePass"
    },
    "KeePass 2 AES (with keyfile)": {
        "regex": re.compile(r"^\$keepass\$\*2\*\d+\*\d+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+\*[0-9a-f]+\*\d+\*\d+\*[0-9a-f]+$", re.IGNORECASE),
        "hashcat": 13400,
        "john": "KeePass"
    },
    "Open Document Format (ODF) 1.2 (SHA-256, AES)": {
        "regex": re.compile(r"^\$odf\$\*1\*1\*100000\*32\*[a-f0-9]{64}\*16\*[a-f0-9]{32}\*16\*[a-f0-9]{32}\*0\*[a-f0-9]{2048}$", re.IGNORECASE),
        "hashcat": 18400,
        "john": None
    },
    "JWT (JSON Web Token)": {
        "regex": re.compile(r"^[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*$", re.IGNORECASE),
        "hashcat": 16500,
        "john": None
    },
    "FileVault 2": {
        "regex": re.compile(r"\$fvde\$1\$16\$[\d|\D]{32}\$\d{5}\$[\d|\D]{48}", re.IGNORECASE),
        "hashcat": 16700,
        "john": None
    },
    "SAP CODVN B (BCODE)": {
        "regex": re.compile(r"^(.+)?\$[a-f0-9]{16}$", re.IGNORECASE),
        "hashcat": 7700,
        "john": "sapb"
    },
    "SAP CODVN F/G (PASSCODE)": {
        "regex": re.compile(r"^(.+)?\$[a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 7800,
        "john": "sapg"
    },
    "Juniper Netscreen/SSG(ScreenOS)": {
        "regex": re.compile(r"^(.+\$)?[a-z0-9\/.+]{30}(:.+)?$", re.IGNORECASE),
        "hashcat": 22,
        "john": "md5ns"
    },
    "EPi": {
        "regex": re.compile(r"^0x(?:[a-f0-9]{60}|[a-f0-9]{40})$", re.IGNORECASE),
        "hashcat": 123,
        "john": None
    },
    "SMF ≥ v1.1": {
        "regex": re.compile(r"^[a-f0-9]{40}:[^*]{1,25}$", re.IGNORECASE),
        "hashcat": 121,
        "john": None
    },
    "Woltlab Burning Board 3.x": {
        "regex": re.compile(r"^(\$wbb3\$\*1\*)?[a-f0-9]{40}[:*][a-f0-9]{40}$", re.IGNORECASE),
        "hashcat": 8400,
        "john": "wbb3"
    },
    "IPMI2 RAKP HMAC-SHA1": {
        "regex": re.compile(r"^[a-f0-9]{130}(:[a-f0-9]{40})?$", re.IGNORECASE),
        "hashcat": 7300,
        "john": None
    },
    "Lastpass": {
        "regex": re.compile(r"^[a-f0-9]{32}:[0-9]+:[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$", re.IGNORECASE),
        "hashcat": 6800,
        "john": None
    },
    "Cisco-ASA(MD5)": {
        "regex": re.compile(r"^[a-z0-9\/.]{16}([:$].{1,})?$", re.IGNORECASE),
        "hashcat": 2410,
        "john": "asa-md5"
    },
    "DNSSEC(NSEC3)": {
        "regex": re.compile(r"^[a-z0-9]{32}(:([a-z0-9-]+\.)?[a-z0-9-.]+\.[a-z]{2,7}:.+:[0-9]+)?$", re.IGNORECASE),
        "hashcat": 8300,
        "john": None
    },
    "SHA-1 Crypt": {
        "regex": re.compile(r"^\$sha1\$[0-9]+\$[a-z0-9\/.]{0,64}\$[a-z0-9\/.]{28}$", re.IGNORECASE),
        "hashcat": 15100,
        "john": "sha1crypt"
    },
    "hMailServer": {
        "regex": re.compile(r"^[a-f0-9]{70}$", re.IGNORECASE),
        "hashcat": 1421,
        "john": "hmailserver"
    },
    "MediaWiki": {
        "regex": re.compile(r"^[:\$][AB][:\$]([a-f0-9]{1,8}[:\$])?[a-f0-9]{32}$", re.IGNORECASE),
        "hashcat": 3711,
        "john": "mediawiki"
    },
    "PBKDF2-SHA1(Generic)": {
        "regex": re.compile(r"^\$pbkdf2(-sha1)?\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{27}$", re.IGNORECASE),
        "hashcat": 20400,
        "john": None
    },
    "PBKDF2-SHA256(Generic)": {
        "regex": re.compile(r"^\$pbkdf2-sha256\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{43}$", re.IGNORECASE),
        "hashcat": 20300,
        "john": "pbkdf2-hmac-sha256"
    },
    "PBKDF2-SHA512(Generic)": {
        "regex": re.compile(r"^\$pbkdf2-sha512\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{86}$", re.IGNORECASE),
        "hashcat": 20200,
        "john": None
    },
    "NetNTLMv1-VANILLA / NetNTLMv1+ESS": {
        "regex": re.compile(r'^[^\\\/:*?"<>|]{1,20}[:]{2,3}([^\\\/:*?"<>|]{1,20})?:[a-f0-9]{48}:[a-f0-9]{48}:[a-f0-9]{16}', re.IGNORECASE),
        "hashcat": 5500,
        "john": "netntlm"
    },
    "NetNTLMv2": {
        "regex": re.compile(r'^([^\\\/:*?"<>|]{1,20}\\)?[^\\\/:*?"<>|]{1,20}[:]{2,3}([^\\\/:*?"<>|]{1,20}:)?[^\\\/:*?"<>|]{1,20}:[a-f0-9]{32}:[a-f0-9]+', re.IGNORECASE),
        "hashcat": 5600,
        "john": "netntlmv2"
    },
    "Kerberos 5 AS-REQ Pre-Auth": {
        "regex": re.compile(r"^\$(krb5pa|mskrb5)\$(23)?\$.+\$[a-f0-9]{1,}$", re.IGNORECASE),
        "hashcat": 7500,
        "john": "krb5pa-md5"
    },
    "Redmine Project Management Web App": {
        "regex": re.compile(r"^[a-f0-9]{40}:[a-f0-9]{0,32}$", re.IGNORECASE),
        "hashcat": 4521,
        "john": None
    }
}

__all__ = ["hash_dict"]