# -*- coding: UTF-8 -*-

import enum


class LocalCode(enum.IntEnum):
    PG_UTF8 = 1
    PG_GBK = 2
    PG_BIG5 = 3
    PG_ISO_8859_9 = 4
    PG_EUC_JP = 5
    PG_EUC_KR = 6
    PG_KOI8R = 7
    PG_ISO_8859_1 = 8
    PG_SQL_ASCII = 9
    PG_GB18030 = 10
    PG_ISO_8859_11 = 11
