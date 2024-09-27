import math
import sys
import warnings
from typing import Dict, List, cast, Union

from dslib.field import Field, DatasheetFields, MpnMfr
from dslib.store import Mfr, Mpn


def fallback_specs(mfr, mpn):
    from dslib import mfr_tag
    mfr = mfr_tag(mfr)

    if mfr == 'epc':
        assert mpn.startswith('EPC')
        return dict(tRise=2, tFall=2)
    elif mfr == 'nxp':
        if mpn.startswith('GAN'):
            return dict(tRise=2, tFall=2)
    return dict()


def reference_data(mfr: Union[str, MpnMfr], mpn=None):
    nan = math.nan

    if hasattr(mfr, 'mfr'):
        mpn = mfr.mpn
        mfr = mfr.mfr

    ref = [

        DatasheetFields("infineon", "BSC050N10NS5ATMA1",
                        fields=[Field("Coss", nan, 490.0, 640.0, "pF"),
                                Field("tRise", nan, 9.0, nan, "ns"),
                                Field("tFall", nan, 7.0, nan, "ns"),
                                Field("Qgs", nan, 16.0, nan, "nC"),
                                Field("Qg_th", nan, 10.0, nan, "nC"),
                                Field("Qgd", nan, 11.0, 16.0, "nC"),
                                Field("Qsw", nan, 16.0, nan, "nc"),
                                Field("Qg", nan, 49.0, 61.0, "nC"),
                                Field("Vpl", nan, 4.7, nan, "V"),
                                Field("Vsd", nan, 0.87, 1.1, "V"),
                                Field("Qrr", nan, 68.0, 136.0, "nC")]),

        DatasheetFields("infineon", "IRF150DM115XTMA1",  # r600_ocrmypdf
                        fields=[Field("Coss", nan, 580.0, 780.0, "pF"),
                                Field("tRise", nan, 21.0, nan, "ns"),
                                Field("tFall", nan, 14.0, nan, "None"),
                                Field("Qgs", nan, 13.2, nan, "nC"),
                                Field("Qg_th", nan, 8.7, nan, "nC"),
                                Field("Qgd", nan, 8.0, 12.0, "nC"),
                                Field("Qsw", nan, 12.5, nan, "nC"),
                                Field("Qg", nan, 33.0, 50.0, "nC"),
                                Field("Vpl", nan, 5.7, nan, "V"),
                                Field("Vsd", nan, 0.9, 1.2, "V"),
                                Field("Qrr", nan, 47.0, 94.0, "nC")]),

        DatasheetFields("infineon", "IRF6644TRPBF",
                        fields=[Field("Qg", nan, 28.0, 42.0, "nC"),
                                Field("Qgs", nan, 7.0, nan, "None"),
                                Field("Qgs2", nan, 3.0, nan, "None"),
                                Field("Qgd", nan, 9.0, nan, "None"),
                                Field("Qsw", nan, 16.0, nan, "None"),
                                Field("tRise", nan, 16.0, nan, "None"),
                                Field("Rg", nan, 1.6, nan, "Ω"),
                                Field("Qg_th", nan, 7.0, nan, "None"),
                                Field("tFall", nan, 5.7, nan, "None"),
                                Field("Coss", nan, 280.0, nan, "None"),
                                Field("Vsd", nan, nan, 1.3, "V"),
                                Field("Qrr", nan, 97.0, 146.0, "nC")])

        #
    ]

    for d in ref:
        if d.part.mfr == mfr and d.part.mpn == mpn:
            return d

    warnings.warn('no reference data for %s %s' % (mfr, mpn))


def get_fields() -> Dict[Mfr, Dict[Mpn, List[Field]]]:
    fields = cast(Dict[Mfr, Dict[Mpn, List[Field]]], sys.modules[__name__].__dict__)
    for a, ff in fields.items():
        if not isinstance(ff, dict) or a[0] == '_':
            continue
        for fl in ff.values():
            for f in fl:
                for k in Field.StatKeys:
                    if not math.isnan(f[k]):
                        f._sources[k] = 'manual'

    return sys.modules[__name__].__dict__


# class FetCharSymbols(Enum):
#    Qg = 'Qg'
#    Qgd = 'Qgd'
#    Qgs = 'Qgs'
#    Qgs2 = 'Qgs2'


# FCS = FetCharSymbols


# need OCR datasheets/infineon/IRF150DM115XTMA1.pdf

infineon = {
    'BSZ070N08LS5ATMA1': [  # need OCR
        Field('Qrr', min=math.nan, typ=27, max=54, unit='nC'),
        Field('tRise', min=math.nan, typ=4.8, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=5.8, max=math.nan, unit='ns'),

        Field('Qgs', min=math.nan, typ=5, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=5, max=7, unit='nC'),
        Field('Qsw', min=math.nan, typ=6.9, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=29, max=39, unit='nC'),
        Field('Vpl', min=math.nan, typ=2.9, max=math.nan, unit='nC'),
    ],

    'BSC019N08NS5ATMA1': [  # tabula failure
        Field('tRise', min=math.nan, typ=17, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=20, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=80, max=160, unit='nC'),

        Field('Qgd', min=math.nan, typ=20, max=29, unit='nC'),
        Field('Qgs', min=math.nan, typ=29, max=math.nan, unit='nC'),

        Field('Qsw', min=math.nan, typ=29, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=110, max=147, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.4, max=math.nan, unit='nC'),
    ],

    'IAUA250N08S5N018AUMA1': [  # tabula failure
        Field('tRise', min=math.nan, typ=11, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=23, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=84, max=math.nan, unit='nC'),
    ],

    'IAUMN08S5N013GAUMA1': [
        Field('tRise', min=math.nan, typ=15, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=51, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=55, max=109, unit='nC'),
    ],

    'IAUMN08S5N012GAUMA1': [
        Field('tRise', min=math.nan, typ=16, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=55, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=56, max=112, unit='nC'),
    ],

    'IST019N08NM5AUMA1': [
        Field('tRise', min=math.nan, typ=29, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=10, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=66, max=math.nan, unit='nC'),
    ],

    'IPA050N10NM5SXKSA1': [
        Field('Qgd', min=math.nan, typ=10, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=16, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=11, max=math.nan, unit='nC'),
        Field('Qsw', min=math.nan, typ=16, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=67, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.25, max=math.nan, unit='V'),
    ],

    'IPB019N08N3GATMA1': [  # scrambled text
        Field('Qgd', min=math.nan, typ=30, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=50, max=math.nan, unit='nC'),
        Field('Qsw', min=math.nan, typ=50, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=210, max=279, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.6, max=math.nan, unit='V'),
    ],

    'BSB056N10NN3GXUMA2': [  # Qgd label mistake
        Field('Qgd', min=math.nan, typ=9.7, max=math.nan, unit='nC'),
        Field('Qsw', min=math.nan, typ=20, max=math.nan, unit='nC'),
    ]
}

onsemi = {
    'NVMFWS2D1N08XT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=10, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=6, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=189, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=8, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=18, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.7, max=math.nan, unit='V'),
        Field('Qg_th', min=math.nan, typ=12, max=math.nan, unit='V'),
    ],

    'NVMFWS6D2N08XT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=6, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=5, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=88, max=math.nan, unit='nC'),

        Field('Qg', min=math.nan, typ=19, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=4, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=6, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=3, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.7, max=math.nan, unit='V'),
    ],
    'NTMFWS1D5N08XT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=9, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=9, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=224, max=math.nan, unit='nC'),

        Field('Qg', min=math.nan, typ=83, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=18, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=27, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=13, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.6, max=math.nan, unit='V'),
    ],

    'NVMFWS1D9N08XT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=12, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=7, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=211, max=math.nan, unit='nC'),

        Field('Qg', min=math.nan, typ=39, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=14, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=21, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=10, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.7, max=math.nan, unit='V'),
    ],
    'NVMFS6H800NT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=89, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=85, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=82, max=math.nan, unit='nC'),
    ],
    'NTMFS6H800NT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=89, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=85, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=82, max=math.nan, unit='nC'),
    ],

    'NVMFS6H800NWFT1G': [  # tabula failure
        Field('tRise', min=math.nan, typ=89, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=85, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=82, max=math.nan, unit='nC'),
    ],

    'FDMC008N08C': [  # tabula failure
        Field('tRise', min=math.nan, typ=3, max=10, unit='ns'),
        Field('tFall', min=math.nan, typ=3, max=10, unit='ns'),
        Field('Qrr', min=math.nan, typ=27, max=44, unit='nC', cond='IF = 10 A, di/dt = 300 A/ms'),
        Field('Qrr', min=math.nan, typ=65, max=105, unit='nC', cond='IF = 10 A, di/dt = 1000 A/ms'),
    ],

    'NTMFS08N2D5C': [
        Field('tRise', min=math.nan, typ=11, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=7, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=139, max=222, unit='nC'),
    ],

    'NVMTS6D0N15MC': [
        # the datasheet has a different definition of Qg_th?
        # here Qg_th = Qgs + Qgd (charge until the end of miller plateau)
        Field('Qg_th', min=math.nan, typ=18, max=math.nan, unit='nC'),
    ],

    'NTMTS6D0N15MC': [
        # the datasheet has a different definition of Qg_th?
        # here Qg_th = Qgs + Qgd (charge until the end of miller plateau)
        Field('Qg_th', min=math.nan, typ=18, max=math.nan, unit='nC'),
    ],

}

diotec = {
    'DI048N08PQ': [
        Field('tRise', min=math.nan, typ=21, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=45, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=45, max=math.nan, unit='nC'),
    ],
    'DI065N08D1-AQ': [
        Field('tRise', min=math.nan, typ=21, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=45, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=45, max=math.nan, unit='nC'),
    ]
}

diodes = {
    'DMT8008SCT': [
        Field('tRise', min=math.nan, typ=15, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=21, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=49, max=math.nan, unit='nC'),

        Field('Qgd', min=math.nan, typ=12, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=6, max=math.nan, unit='nC'),
        Field('Qsw', min=math.nan, typ=15, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.2, max=math.nan, unit='V'),
    ],

    'DMT10H9M9SCT': [
        Field('Qgd', min=math.nan, typ=7.3, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=9.5, max=math.nan, unit='nC'),
        Field('Qsw', min=math.nan, typ=12.5, max=math.nan, unit='nC'),
        Field('Qrr', min=math.nan, typ=68, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=5.2, max=math.nan, unit='V'),
    ],
}

rohm = {
    'RS6N120BHTB1': [
        Field('tRise', min=math.nan, typ=47, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=35, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=115, max=math.nan, unit='nC'),
    ],

    'RX3P07BBHC16': [
        Field('Qsw', min=math.nan, typ=15, max=math.nan, unit='nC'),
        Field('Qgd', min=math.nan, typ=9.8, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=8.5, max=math.nan, unit='nC'),
    ],
}

ao = {
    'AOTL66811': [
        Field('tRise', min=math.nan, typ=16, max=math.nan, unit='ns'),
        Field('tFall', min=math.nan, typ=21, max=math.nan, unit='ns'),
        Field('Qrr', min=math.nan, typ=233, max=math.nan, unit='nC'),
    ],

    'AOT66811L': [
        Field('Qgd', min=math.nan, typ=15, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=21, max=math.nan, unit='nC'),
        # Field('Qg_th', min=math.nan, typ=15, max=math.nan, unit='nC'), # TODO?
        Field('Qoss', min=math.nan, typ=112, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.2, max=math.nan, unit='V'),
    ]
}

vishay = {
    'SUM70042E-GE3': [
        Field('Qrr', min=math.nan, typ=126, max=189, unit='nC'),
    ],

    'SUP70042E-GE3': [
        Field('Qrr', min=math.nan, typ=126, max=189, unit='nC'),
    ]
}

ti = {
    'CSD19503KCS': [
        Field('Qgd', min=math.nan, typ=5.4, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=9.8, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=6.1, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=71, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.8, max=math.nan, unit='V'),
    ],

    'CSD19506KCS': [
        Field('Qgd', min=math.nan, typ=20, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=37, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=25, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=345, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.25, max=math.nan, unit='V'),
    ],

    'CSD19536KCS': [
        Field('Qgd', min=math.nan, typ=17, max=math.nan, unit='nC'),
        Field('Qgs', min=math.nan, typ=37, max=math.nan, unit='nC'),
        Field('Qg_th', min=math.nan, typ=24, max=math.nan, unit='nC'),
        Field('Qoss', min=math.nan, typ=335, max=math.nan, unit='nC'),
        Field('Vpl', min=math.nan, typ=4.2, max=math.nan, unit='V'),
    ],
}
