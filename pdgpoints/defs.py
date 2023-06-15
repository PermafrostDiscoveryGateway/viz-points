from pathlib import Path
from ._version import __version__
from datetime import datetime

Y = datetime.now().year
HELP_TXT = '''
~~ pdgpoints version %s ~~
 Ian Nesbitt / NCEAS %s
''' % (__version__, Y)

MOD_LOC = Path(__file__).parent.absolute()
BIN_LOC = MOD_LOC.joinpath('bin')
LAS2LAS_LOC = BIN_LOC.joinpath('las2las')
LASINFO_LOC = BIN_LOC.joinpath('lasinfo')

NGS_MODELS = {
    # geoid model numbers in NGS API
    # from https://www.ngs.noaa.gov/web_services/geoid.shtml
    'GEOID99': 1,
    'G99SSS': 2,
    'GEOID03': 3,
    'USGG2003': 4,
    'GEOID06': 5,
    'USGG2009': 6,
    'GEOID09': 7,
    'XUSHG': 9,
    'USGG2012': 11,
    'GEOID12A': 12,
    'GEOID12B': 13,
    'GEOID18': 14,
}

NGS_URL = 'https://geodesy.noaa.gov/api/geoid/ght?lat=%s&lon=%s&model=%s'

VDATUM_MODELS = [
    # geoid models in VDatum API (US only)
    # from https://vdatum.noaa.gov/docs/services.html#step160
    'NAVD88', 'NGVD29', 'ASVD02', 'W0_USGG2012', 'GUVD04', 'NMVD03', 'PRVD02',
    'VIVD09', 'CRD', 'EGM2008', 'EGM1996', 'EGM1984', 'XGEOID16B', 'XGEOID17B',
    'XGEOID18B', 'XGEOID19B', 'XGEOID20B', 'IGLD85', 'LWD_IGLD85',
    'OHWM_IGLD85', 'CRD', 'LMSL', 'MLLW', 'MLW', 'MTL', 'DTL', 'MHW', 'MHHW',
    'LWD', 'NAD27', 'NAD83_1986', 'NAD83_2011', 'NAD83_NSRS2007',
    'NAD83_MARP00', 'NAD83_PACP00', 'WGS84_G1674', 'ITRF2014', 'IGS14',
    'ITRF2008', 'IGS08', 'ITRF2005', 'IGS2005', 'WGS84_G1150', 'ITRF2000',
    'IGS00', 'IGb00', 'ITRF96', 'WGS84_G873', 'ITRF94', 'ITRF93', 'ITRF92',
    'SIOMIT92', 'WGS84_G730', 'ITRF91', 'ITRF90', 'ITRF89', 'ITRF88',
    'WGS84_TRANSIT', 'WGS84_G1762', 'WGS84_G2139'
]

REGIONS = [
    # VDatum regions (from https://vdatum.noaa.gov/docs/services.html#step140)
    'contiguous', 'ak', 'seak', 'as', 'chesapeak_delaware',
    'westcoast', 'gcnmi', 'hi', 'prvi', 'sgi', 'spi', 'sli'
]

VDATUM_URL = 'https://vdatum.noaa.gov/vdatumweb/api/convert?s_x=%s&s_y=%s&s_h_frame=%s&s_v_frame=%s&s_v_geoid=%s&t_h_frame=%s&t_v_frame=%s&t_v_geoid=%s&region=%s'

MODEL_LIST = []
for m in NGS_MODELS:
    MODEL_LIST.append(m)
for m in VDATUM_MODELS:
    MODEL_LIST.append(m)
