#!/usr/bin/env python
# coding=utf-8
"""
Convert EANET filter measurements files to ebas
"""

FILTER_PERSON_DEFAULT = [{
    'PS_LAST_NAME': 'EANET',
    'PS_FIRST_NAME': 'EXPORT',
    'PS_EMAIL': None,
    'PS_ORG_NAME': None,
    'PS_ORG_ACR': None,
    'PS_ORG_UNIT': None,
    'PS_ADDR_LINE1': None,
    'PS_ADDR_LINE2': None,
    'PS_ADDR_ZIP': None,
    'PS_ADDR_CITY': None,
    'PS_ADDR_COUNTRY': None,
    'PS_ORCID': None,
    }]


# #org is used for organization on line 2 i nasa/ames file

EANET_SITES = {
    #CN: sites
    'CNA003': {
        'EANET': {
            'site_name': 'Haifu',
        },
        'EBAS': {
            'station_code': 'CN0010U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA004': {
        'EANET': {
            'site_name': 'Jinyunshan',
        },
        'EBAS': {
            'station_code': 'CN1003R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA005': {
        'EANET': {
            'site_name': 'Shizhan',
        },
        'EBAS': {
            'station_code': 'CN1004U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA007': {
        'EANET': {
            'site_name': 'XianJiwozi',
        },
        'EBAS': {
            'station_code': 'CN1007R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA008': {
        'EANET': {
            'site_name': 'Hongwen',
        },
        'EBAS': {
            'station_code': 'CN1008U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA009': {
        'EANET': {
            'site_name': 'Xiaoping',
        },
        'EBAS': {
            'station_code': 'CN1009R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA010': {
        'EANET': {
            'site_name': 'Xiang Zhou',
        },
        'EBAS': {
            'station_code': 'CN1010U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },
    'CNA011': {
        'EANET': {
            'site_name': 'Zhuxiandong',
        },
        'EBAS': {
            'station_code': 'CN1011U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'CN11L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'CN11L',
        },
    },

    #ID: sites
    'IDA001': {
        'EANET': {
            'site_name': 'Jakarta',
        },
        'EBAS': {
            'station_code': 'ID1012U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'ID05L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'ID05L',
        },
    },
    'IDA002': {
        'EANET': {
            'site_name': 'Serpong',
        },
        'EBAS': {
            'station_code': 'ID1014R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'ID05L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'ID05L',
        },
    },
    'IDA003': {
        'EANET': {
            'site_name': 'Kototabang',
        },
        'EBAS': {
            'station_code': 'ID1013R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'ID05L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'ID05L',
        },
    },
    'IDA004': {
        'EANET': {
            'site_name': 'Bandung',
        },
        'EBAS': {
            'station_code': 'ID1015U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'ID05L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'ID05L',
        },
    },
    'IDA005': {
        'EANET': {
            'site_name': 'Maros',
        },
        'EBAS': {
            'station_code': 'ID1001R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'ID05L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'ID05L',
        },
    },

    #JP: sites
    'JPA001': {
        'EANET': {
            'site_name': 'Rishiri',
        },
        'EBAS': {
            'station_code': 'JP1016R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadeta is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA002': {
        'EANET': {
            'site_name': 'Ochiishi',
        },
        'EBAS': {
            'station_code': 'JP1050R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA003': {
        'EANET': {
            'site_name': 'Tappi',
        },
        'EBAS': {
            'station_code': 'JP1017R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA004': {
        'EANET': {
            'site_name': 'Sadoseki',
        },
        'EBAS': {
            'station_code': 'JP1019R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA005': {
        'EANET': {
            'site_name': 'Happo',
        },
        'EBAS': {
            'station_code': 'JP1021R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA006': {
        'EANET': {
            'site_name': 'Ijira',
        },
        'EBAS': {
            'station_code': 'JP1022R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA007': {
        'EANET': {
            'site_name': 'Oki',
        },
        'EBAS': {
            'station_code': 'JP1023R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA008': {
        'EANET': {
            'site_name': 'Banryu',
        },
        'EBAS': {
            'station_code': 'JP1024U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA009': {
        'EANET': {
            'site_name': 'Yusuhara',
        },
        'EBAS': {
            'station_code': 'JP1025R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA010': {
        'EANET': {
            'site_name': 'Hedo',
        },
        'EBAS': {
            'station_code': 'JP1027R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA011': {
        'EANET': {
            'site_name': 'Ogasawara',
        },
        'EBAS': {
            'station_code': 'JP1018R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA012': {
        'EANET': {
            'site_name': 'Tokyo',
        },
        'EBAS': {
            'station_code': 'JP1057U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA013': {
        'EANET': {
            'site_name': 'Niigata - Maki',
        },
        'EBAS': {
            'station_code': 'JP1030U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },
    'JPA014': {
        'EANET': {
            'site_name': 'Tsushima',
        },
        'EBAS': {
            'station_code': 'JP1031R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'JP01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'JP01L',
        },
    },

    #KH: sites
    'KHA001': {
        'EANET': {
            'site_name': 'PhnomPenh',
        },
        'EBAS': {
            'station_code': 'KH1052U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'KH02L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'KH02L',
        },
    },

    #KR: sites
    'KRA001': {
        'EANET': {
            'site_name': 'Kanghwa',
        },
        'EBAS': {
            'station_code': 'KR1035R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'KR01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'KR01L',
        },
    },
    'KRA002': {
        'EANET': {
            'site_name': 'Cheju',
#            'site_name': 'Cheju (Kosan)',
        },
        'EBAS': {
            'station_code': 'KR1036R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'KR01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'KR01L',
        },
    },
    'KRA003': {
        'EANET': {
            'site_name': 'Imsil',
        },
        'EBAS': {
            'station_code': 'KR1037R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'KR01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'KR01L',
        },
    },

    #MM: sites
    'MMA001': {
        'EANET': {
            'site_name': 'Yangon',
        },
        'EBAS': {
            'station_code': 'MM1056U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MM01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MM01L',
        },
    },
    'MMA002': {
        'EANET': {
            'site_name': 'Mandalay',
        },
        'EBAS': {
            'station_code': 'MM1002U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MM01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MM01L',
        },
    },
    
    #MN: sites
    'MNA001': {
        'EANET': {
            'site_name': 'Ulaanbaatar',
        },
        'EBAS': {
            'station_code': 'MN1031U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MM01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MN01L',
        },
    },
    'MNA002': {
        'EANET': {
            'site_name': 'Terelj',
        },
        'EBAS': {
            'station_code': 'MN1032R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MN01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MN01L',
        },
    },

    #MY: sites
    'MYA001': {
        'EANET': {
            'site_name': 'PetalingJaya',
        },
        'EBAS': {
            'station_code': 'MY1029U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MY03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MY03L',
        },
    },
    'MYA002': {
        'EANET': {
            'site_name': 'TanahRata',
        },
        'EBAS': {
            'station_code': 'MY1030R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MY03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MY03L',
        },
    },
    'MYA003': {
        'EANET': {
            'site_name': 'DanumValley',
        },
        'EBAS': {
            'station_code': 'MY1053R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MY03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MY03L',
        },
    },
    'MYA004': {
        'EANET': {
            'site_name': 'Kuching',
        },
        'EBAS': {
            'station_code': 'MY0001U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'MY03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'MY03L',
        },
    },
    
    #PH: sites
    'PHA001': {
        'EANET': {
            'site_name': 'MetroManila',
        },
        'EBAS': {
            'station_code': 'PH1033U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'PH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'PH01L',
        },
    },
    'PHA002': {
        'EANET': {
            'site_name': 'Los Banos',
        },
        'EBAS': {
            'station_code': 'PH1034R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'PH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'PH01L',
        },
    },
    'PHA003': {
        'EANET': {
            'site_name': 'MtStoTomas',
        },
        'EBAS': {
            'station_code': 'PH1055R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'PH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'PH01L',
        },
    },

    #RU: sites
    'RUA001': {
        'EANET': {
            'site_name': 'Mondy',
        },
        'EBAS': {
            'station_code': 'RU1038R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'RU03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'RU03L',
        },
    },
    'RUA002': {
        'EANET': {
            'site_name': 'Listvyanka',
        },
        'EBAS': {
            'station_code': 'RU1039R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'RU03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'RU03L',
        },
    },
    'RUA003': {
        'EANET': {
            'site_name': 'Irkutsk',
        },
        'EBAS': {
            'station_code': 'RU1040U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'RU03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'RU03L',
        },
    },
    'RUA004': {
        'EANET': {
            'site_name': 'Primorskaya',
        },
        'EBAS': {
            'station_code': 'RU1041R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'RU03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'RU03L',
        },
    },

    #TH: sites
    'THA001': {
        'EANET': {
            'site_name': 'Bangkok',
        },
        'EBAS': {
            'station_code': 'TH1042U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA002': {
        'EANET': {
            'site_name': 'Samutprakarn',
        },
        'EBAS': {
            'station_code': 'TH1043U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA003': {
        'EANET': {
            'site_name': 'Patumthani',
        },
        'EBAS': {
            'station_code': 'TH1044R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA004': {
        'EANET': {
            'site_name': 'Khanchanaburi',
#            'site_name': 'Khanchanaburi',            
        },
        'EBAS': {
            'station_code': 'TH1045R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA005': {
        'EANET': {
            'site_name': 'ChangMai-MaeHia',
        },
        'EBAS': {
            'station_code': 'TH1046R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA006': {
        'EANET': {
            'site_name': 'Chiang Mai - Chang Phueak',
        },
        'EBAS': {
            'station_code': 'TH1006U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA008': {
        'EANET': {
            'site_name': 'NakhonRatchasima-Sakaerat',
        },
        'EBAS': {
            'station_code': 'TH1054R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },
    'THA009': {
        'EANET': {
            'site_name': 'Nakhon Ratchasima - Nai Mueang',
        },
        'EBAS': {
            'station_code': 'TH1009U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'TH01L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'TH01L',
        },
    },

    #VN: sites
    'VNA001': {
        'EANET': {
            'site_name': 'Hanoi',
        },
        'EBAS': {
            'station_code': 'VN1047U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA002': {
        'EANET': {
            'site_name': 'HoaBinh',
        },
        'EBAS': {
            'station_code': 'VN1048R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA003': {
        'EANET': {
            'site_name': 'Cuc Phuong',
        },
        'EBAS': {
            'station_code': 'VN1003R',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA004': {
        'EANET': {
            'site_name': 'Da Nang',
        },
        'EBAS': {
            'station_code': 'VN1004U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA005': {
        'EANET': {
            'site_name': 'Can Tho',
        },
        'EBAS': {
            'station_code': 'VN1005U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA006': {
        'EANET': {
            'site_name': 'Ho Chi Minh',
        },
        'EBAS': {
            'station_code': 'VN1006U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
    'VNA007': {
        'EANET': {
            'site_name': 'Yen Bai',
        },
        'EBAS': {
            'station_code': 'VN1007U',
            # rest of station metadata is set from ebas master data by default
            # (based on station_code)
            # override it here or in _DETAIL config if needed
            'org': {
                'OR_CODE': 'VN03L'
                # rest of org metadata is set from ebas master data by default
                # override it here or in _DETAIL config if needed
            },
            'lab_code': 'VN03L',
        },
    },
}



####
####  Precipitation
####

# Metadata hirarchy:
# 1) First PRECIP_GLOBAL is used
# 2) then EANET_SITES overrules
# 3) for each paraeter EANET_PRECIP_PARAMS
# 4) in EANET_PRECIP_DETAIL, site and paramter specific metadata

EANET_PRECIP_GLOBAL = {
    'EANET': {},
    'EBAS': {
        'projects': ['EANET'],
        'datalevel': '2',
    }
}

EANET_PRECIP_REPORTERS = {
    'Asri Indrawati & Dyah Aries Tanti': [{
        'PS_LAST_NAME': 'Indrawati',
        'PS_FIRST_NAME': 'Asri',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    },
    {
        'PS_LAST_NAME': 'Tanti',                                     
        'PS_FIRST_NAME': 'Dyah Aries',

    }],    
    'Bold ALTANTUYA': [{
        'PS_LAST_NAME': 'Altantuya',
        'PS_FIRST_NAME': 'Bold',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Dr. Hathairatana  Garivait':[{
	'PS_LAST_NAME': 'Garivait',
	'PS_FIRST_NAME': 'Hathairatana',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Dyah Aries Tanti': [{
        'PS_LAST_NAME': 'Tanti',
        'PS_FIRST_NAME': 'Dyah Aries',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Emalya Rachmawati': [{
        'PS_LAST_NAME': 'Rachmawati',
        'PS_FIRST_NAME': 'Emalya',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Haslina Binti Abdullah':[{
	'PS_LAST_NAME': 'Abdullah',
	'PS_FIRST_NAME': 'Haslina Binti',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Haslina binti Abdullah':[{
	'PS_LAST_NAME': 'Abdullah',
	'PS_FIRST_NAME': 'Haslina Binti',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'He zhidong': [{
        'PS_LAST_NAME': 'He',
        'PS_FIRST_NAME': 'Zhidong',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Husako Kuwao': [{
        'PS_LAST_NAME': 'Kuwao',
        'PS_FIRST_NAME': 'Husako',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Jessada  Koongammak, Wassana  Toruksa':[{
	'PS_LAST_NAME': 'Koongammak',
	'PS_FIRST_NAME': 'Jessada  Koongammak',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    },
    {
       'PS_LAST_NAME': 'Toruksa',
       'PS_FIRST_NAME': 'Wassana',
    }],
    'Kenichi Koide': [{
        'PS_LAST_NAME': 'Koide',
        'PS_FIRST_NAME': 'Kenichi',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Mengxiaoxing': [{
        'PS_LAST_NAME': 'Meng',
        'PS_FIRST_NAME': 'xiaoxing',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Min-do Lee':[{
	'PS_LAST_NAME': 'Lee',
	'PS_FIRST_NAME': 'Min-do',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    ' Mr. KONG Savuth':[{
	'PS_LAST_NAME': 'Savuth',
	'PS_FIRST_NAME': 'KONG',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Ms.Htwe Htwe Win':[{
	'PS_LAST_NAME': 'Win',
	'PS_FIRST_NAME': 'Htwe Htwe',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Ms.Jeeranant Juthong':[{
	'PS_LAST_NAME': 'Juthong',
	'PS_FIRST_NAME': 'Jeeranant',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    ' Netsvetaeva O.G., Sezjko N.P., Zimnik E.A.':[{
	'PS_LAST_NAME': 'Netsvetaeva',
	'PS_FIRST_NAME': 'O.G.',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
	},
	{
	   'PS_LAST_NAME': 'Sezjko',
	   'PS_FIRST_NAME': 'N.P.',
	},
	{
	   'PS_LAST_NAME': 'Zimnik',
	   'PS_FIRST_NAME': 'E.A.',
    }],
    'Nguyen Minh Thien':[{
	'PS_LAST_NAME': 'Thien',
	'PS_FIRST_NAME': 'Nguyen Minh',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Pilipushka Ludmila,  Ivanova Nadya ':[{
	'PS_LAST_NAME': 'Ludmila',
	'PS_FIRST_NAME': 'Pilipushka',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    },
    {
        'PS_LAST_NAME': 'Nadya',
        'PS_FIRST_NAME': 'Ivanova',
    }],
    'Riri Indriani Nasution': [{
        'PS_LAST_NAME': 'Nasution',
        'PS_FIRST_NAME': 'Riri Indriani',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Sopittaporn  Sillapapiromsuk':[{
	'PS_LAST_NAME': 'Sillapapiromsuk',
	'PS_FIRST_NAME': 'Sopittaporn',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Takahiro Tabe':[{
	'PS_LAST_NAME': 'Tabe',
	'PS_FIRST_NAME': 'Takahiro',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Takashi Yamaguchi': [{
        'PS_LAST_NAME': 'Yamaguchi',
        'PS_FIRST_NAME': 'Takashi',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Tomokazu Nagai, Huo Mingqun': [{
        'PS_LAST_NAME': 'Nagai',
        'PS_FIRST_NAME': 'Tomokazu',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    },
    {
        'PS_LAST_NAME': 'Huo',
        'PS_FIRST_NAME': 'Mingqun',
    }],
    'Toshiyuki MIHARA': [{
        'PS_LAST_NAME': 'MIHARA',
        'PS_FIRST_NAME': 'Toshiyuki',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Tran Son':[{
	'PS_LAST_NAME': 'Son',
	'PS_FIRST_NAME': 'Tran',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Tsutomu Harada': [{
        'PS_LAST_NAME': 'Harada',
        'PS_FIRST_NAME': 'Tsutomu',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Wassana  Toruksa':[{
	'PS_LAST_NAME': 'Toruksa',
	'PS_FIRST_NAME': 'Wassana',
	# if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
	# 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
	# 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Wataru Kadena': [{
        'PS_LAST_NAME': 'Kadena',
        'PS_FIRST_NAME': 'Wataru',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Yuta Kobayashi': [{
        'PS_LAST_NAME': 'Kobayashi',
        'PS_FIRST_NAME': 'Yuta',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'zhangyashuang': [{
        'PS_LAST_NAME': 'Zhang',
        'PS_FIRST_NAME': 'Yashuang',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
    'Zhu jian': [{
        'PS_LAST_NAME': 'Zhu',
        'PS_FIRST_NAME': 'Jian',
        # if known, following could be added: 'PS_EMAIL', 'PS_ORG_NAME',
        # 'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
        # 'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID',
    }],
}

# Analytical laboratory mapping (only allpies to precip files, which has
# laboratory name)
# Maps the EANET lab name to ebas org code which will be used as prefix for
# method ref (method metadata are given as special "#method_name", which means
# the method ref is constructed in the conversion script)
EANET_PRECIP_ANALYTICAL_LABS = {
    # CN: ana_lab
    'Chongqing': 'CN06L',
    'xi`an': 'CN07L',
    'Xiamen environmental central station': 'CN08L',
    'Zhuhai Environmental Monitoring Station': 'CN09L',

    # ID: ana_lab
    'Air Quality BMKG': 'ID01L',
    'Air Laboratory': 'ID01L',
    'LAPAN BANDUNG': 'ID06L',
    
    # JP; org
    'Asia Center for Air Pollution Research': 'JP01L',
    'Institute of Environmental Sciences, Hokkaido Research Organization': \
        'JP03L',
    'Nagano Environmental Conservation Reseach Institute': 'JP05L',
    'Gifu Prefectural Institute for Health and Environmental Sciences': 'JP06L',
    'Shimane Prefectual Institute of Public Health and Environmental Science': \
        'JP07L',
    'Kochi Prefectural Environmental Research Center': 'JP08L',
    'Okinawa prefectural institute of health and environment': 'JP09L',

    # KH: ana_lab
    'Laboratory of Ministry of Environment': 'KH03L',
    
    # KR: ana_lab
    'Air Quality / National Institute of Environmental Research': 'KR01L',
    
    # MM: ana_lab
    'Department of Meteorology & Hydrology': 'MM01L',
    
    # MN: ana_lab
    'Central Laboratory of Environment and Metrology (CLEM)': 'MN01L',
    
    # MY: ana_lab
    'Chemistry Department of Malaysia': 'MY01L',

    # PH: ana_lab
    'Environmental Management Bureau - Cental Office Laboratory': 'PH02L',
    'Environmental Management Bureau - CAR': 'PH02L',
    
    # RU: ana_lab
    'Hydrochemistry and atmospheric chemistry of Limnological Institute SB RAS': \
        'RU03L',
    'Hydrochemistry and atmospheric chemistry': 'RU03L',
    'Primorskgidromet': 'RU04L',

    # TH: ana_lab
    'Pollution Control Department': 'TH01L',
    'Environmental Research and Training Center': 'TH03L',
    'Environmental Chemistry Research Laboratory (ECRL)': 'TH05L',
    'Environmental Engineering, KKU': 'TH99L',
    
    # VN: ana_lab
    'CENRE -NIMHE- MoNRE - Viet Nam': 'VN01L',
    'Center for Hydro-Meteorological and Environmental Networks (National Hydro-Meteorological Service of Vietnam)': 'VN02L',
    'Middle of Central regional Hydrorological Observatory (NHMS)': 'VN02L',
}

EANET_PRECIP_PARAMS = {
    #form 0: anions
    #form 1: cations
    #form 2: mm, cond, ph
    #form 3: organic
    #form 4: summary 1 calculations
    #form 5: summary 2 calculations
    #form 6: summary 3 calculations
    #form 7: summary 4 calculations

    'so4': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'SO42-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'sulphate_total',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'no3': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'NO3-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'nitrate',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'cl': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'Cl-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'chloride',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'hco3': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'HCO3-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'bicarbonate',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            # ?? '#method_name': 'IC',
        },
    },
    'f': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'F-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'fluoride',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'br': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'Br-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'bromide',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'no2-': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'NO2-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'nitrite',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'po4': {
        'EANET': {
            'form_number': 0,
            'variable_name': 'PO43-',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'phosphate',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'nh4': {
        'EANET': {
            'form_number': 1,
            'variable_name': 'NH4+',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'ammonium',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'na': {
        'EANET': {
            'form_number': 1,
            'variable_name': 'Na+',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'sodium',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'k': {
        'EANET': {
            'form_number': 1,
            'variable_name': 'K+',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'potassium',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'ca': {
        'EANET': {
            'form_number': 1,
            'variable_name': 'Ca2+',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'calcium',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    'mg': {
        'EANET': {
            'form_number': 1,
            'variable_name': 'Mg2+',
            'unit': 'umol L-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'magnesium',
            'statistics': 'arithmetic mean',
            'unit': 'umol/l',
            '#method_name': 'IC',
        },
    },
    
    'cond': {
        'EANET': {
            'form_number': 2,
            'variable_name': 'EC',
            'unit': 'mS m-1',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'conductivity',
            'statistics': 'arithmetic mean',
            'unit': 'mS/m',
        },
    },
    'ph': {
        'EANET': {
            'form_number': 2,
            'variable_name': 'pH',
            'unit': '',
            # enhet mangler i JPA001_2014_wet_deposition.csv? men er opplagt ph enheter
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'pH',
            'statistics': 'arithmetic mean',
            'unit': 'pH units',
        },
    },
    'mm': {
        'EANET': {
            'form_number': 2,
            'variable_name': 'Amount of precipitation',
            'unit': 'mm',
        },
        'EBAS': {
            'regime': 'IMG',
            'matrix': 'precip',
            'comp_name': 'precipitation_amount_off',
            'statistics': 'arithmetic mean',
            'unit': 'mm',
        },
    },
}


EANET_PRECIP_DETAIL = {
    #CN: precip CNA003-CNA005, CNA007-CNA011
    'CNA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn0010',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn0010',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn0010',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn0010',
                '#method_name': 'IC',
            }
        },
    },
    'CNA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1003',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1003',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1003',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1003',
                '#method_name': 'IC',
            }
        },
    },
    'CNA005': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1004',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1004',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1004',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1004',
                '#method_name': 'IC',
            }
        },
    },
    'CNA007': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1007',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1007',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1007',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1007',
                '#method_name': 'IC',
            }
        },
    },
    'CNA008': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1008',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1008',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1008',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1008',
                '#method_name': 'IC',
            }
        },
    },
    'CNA009': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1009',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1008',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1009',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1009',
                '#method_name': 'IC',
            }
        },
    },
    'CNA010': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1010',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1010',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1010',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1010',
                '#method_name': 'IC',
            }
        },
    },
    'CNA011': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_cn1011',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1011',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1011',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_cn1011',
                '#method_name': 'IC',
            }
        },
    },
    
    #ID: precip IDA001, IDA003-IDA005
    'IDA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_id1012',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1012',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1012',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1012',
                '#method_name': 'IC',
            }
        },
    },
    'IDA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_id1014',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1014',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1014',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1014',
                '#method_name': 'IC',
            }
        },
    },
    'IDA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_id1013',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1013',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1013',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1013',
                '#method_name': 'IC',
            }
        },
    },
    'IDA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_id1015',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1015',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1015',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1015',
                '#method_name': 'IC',
            }
        },
    },
    'IDA005': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_id1001',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1001',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1001',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_id1001',
                '#method_name': 'IC',
            }
        },
    },

    #JP: precip
    'JPA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1016',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1016',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1016',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1016',
                '#method_name': 'IC',
            }
        },
    },
    'JPA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1050',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1050',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1050',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1050',
                '#method_name': 'IC',
            }
        },
    },
    'JPA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1017',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1017',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1017',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1017',
                '#method_name': 'IC',
            }
        },
    },
    'JPA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1019',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1019',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1019',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1019',
                '#method_name': 'IC',
            }
        },
    },
    'JPA005': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1021',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1021',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1021',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1021',
                '#method_name': 'IC',
            }
        },
    },
    'JPA006': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1022',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1022',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1022',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1022',
                '#method_name': 'IC',
            }
        },
    },
    'JPA007': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1023',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1023',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1023',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1023',
                '#method_name': 'IC',
            }
        },
    },
    'JPA008': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1024',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1024',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1024',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1024',
                '#method_name': 'IC',
            }
        },
    },
    'JPA009': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1025',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1025',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1025',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1025',
                '#method_name': 'IC',
            }
        },
    },
    'JPA010': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1027',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1027',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1027',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1027',
                '#method_name': 'IC',
            }
        },
    },
    'JPA011': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1018',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1018',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1018',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1018',
                '#method_name': 'IC',
            }
        },
    },
    'JPA012': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1057',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1057',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1057',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1057',
                '#method_name': 'IC',
            }
        },
    },
    'JPA013': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1030',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1030',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1030',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1030',
                '#method_name': 'IC',
            }
        },
    },
    'JPA014': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_jp1031',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1031',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1031',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_jp1031',
                '#method_name': 'IC',
            }
        },
    },

    #KH: precip KHA001
    'KHA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_kh1052',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kh1052',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kh1052',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kh1052',
                '#method_name': 'IC',
            }
        },
    },

    #KR: precip KRA001-KRA003
    'KRA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_kr1035',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1035',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1035',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1035',
                '#method_name': 'IC',
            }
        },
    },
    'KRA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_kr1036',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1036',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1036',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1036',
                '#method_name': 'IC',
            }
        },
    },
    'KRA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_kr1037',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1037',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1037',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_kr1037',
                '#method_name': 'IC',
            }
        },
    },

    #MN: precip MNA001-MNA002
    'MNA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_mn1031',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1031',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1031',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1031',
                '#method_name': 'IC',
            }
        },
    },
    'MNA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_mn1032',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1032',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1032',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_mn1032',
                '#method_name': 'IC',
            }
        },
    },

    #MY: precip MYA001-MYA004
    'MYA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_my1029',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1029',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1029',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1029',
                '#method_name': 'IC',
            }
        },
    },
    'MYA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_my1030',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1030',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1030',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1030',
                '#method_name': 'IC',
            }
        },
    },
    'MYA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_my1053',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1053',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1053',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my1053',
                '#method_name': 'IC',
            }
        },
    },    
    'MYA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_my0001',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my0001',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my0001',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_my0001',
                '#method_name': 'IC',
            }
        },
    },

    #PH: precip PHA001-PHA003
    'PHA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ph1033',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1033',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1033',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1033',
                '#method_name': 'IC',
            }
        },
    },
    'PHA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ph1034',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1034',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1034',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1034',
                '#method_name': 'IC',
            }
        },
    },
    'PHA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ph1055',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1055',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1055',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ph1055',
                '#method_name': 'IC',
            }
        },
    },    

    #RU: precip:
    'RUA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ru1038',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'ph_meter',
            }
        },
        # nh4, na, k, ca, mg: AES
        'nh4': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'spectrophotometric',
            }
        },
        'na': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'aes',
            }
        },
        'k': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'aes',
            }
        },
        'ca': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'aes',
            }
        },
        'mg': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'aes',
            }
        },
        None: {  # anions left
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1038',
                '#method_name': 'IC',
            }
        },
    },
    'RUA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ru1039',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'ph_meter',
            }
        },
        # nh4, na, k, ca, mg: AES
        'nh4': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'spectrophotometric',
            }
        },
        'na': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'aes',
            }
        },
        'k': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'aes',
            }
        },
        'ca': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'aes',
            }
        },
        'mg': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'aes',
            }
        },
        None: {  # anions left
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1039',
                '#method_name': 'IC',
            }
        },
    },
    'RUA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ru1040',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'ph_meter',
            }
        },
        # nh4, na, k, ca, mg: AES
        'nh4': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'spectrophotometric',
            }
        },
        'na': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'aes',
            }
        },
        'k': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'aes',
            }
        },
        'ca': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'aes',
            }
        },
        'mg': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'aes',
            }
        },
        None: {  # anions left
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1040',
                '#method_name': 'IC',
            }
        },
    },
    'RUA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_ru1041',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'ph_meter',
            }
        },
        'nh4': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'spectrophotometric',
            }
        },
        'na': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'aas_aes',
            }
        },
        'k': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'aas_aes',
            }
        },
        'ca': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'aas_aes',
            }
        },
        'mg': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'aas_aes',
            }
        },
        None: {  # anions left
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_ru1041',
                '#method_name': 'spectro_titr_nephelom',
            }
        },
    },
    
    #TH: precip THA001-THA004, THA0005, THA008
    'THA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1042',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1042',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1042',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1042',
                '#method_name': 'IC',
            }
        },
    },
    'THA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1043',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1043',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1043',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1043',
                '#method_name': 'IC',
            }
        },
    },
    'THA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1044',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1044',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1044',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1044',
                '#method_name': 'IC',
            }
        },
    },    
    'THA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1045',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1045',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1045',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1045',
                '#method_name': 'IC',
            }
        },
    },    
    'THA005': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1046',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1046',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1046',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1046',
                '#method_name': 'IC',
            }
        },
    },
    'THA008': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_th1054',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1054',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1054',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_th1054',
                '#method_name': 'IC',
            }
        },
    },

    #VN: precip VNA001 - VNA004
    'VNA001': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_vn1047',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1047',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1047',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1047',
                '#method_name': 'IC',
            }
        },
    },
    'VNA002': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_vn1048',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1048',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1048',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1048',
                '#method_name': 'IC',
            }
        },
    },
    'VNA003': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_vn1003',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1003',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1003',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1047',
                '#method_name': 'IC',
            }
        },
    },
    'VNA004': {
        'mm': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'precip_gauge',
                'instr_name': 'precip_gauge_vn1004',
                '#method_name': 'prec',
            }
        },
        'cond': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1004',
                '#method_name': 'cond_meter',
            }
        },
        'ph': {
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1004',
                '#method_name': 'ph_meter',
            }
        },
        None: {  # default
            'EANET': {},
            'EBAS': {
                'instr_type': 'wet_only_sampler',
                'instr_name': 'wet_only_vn1004',
                '#method_name': 'IC',
            }
        },
    },

    
}


####
####  Filter
####

# Metadata hirarchy:
# 1) First FILTER_GLOBAL is used
# 2) then EANET_SITES overrules
# 3) for each paraeter EANET_FILTER_PARAMS
# 4) in EANET_FILTER_DETAIL, site and paramter specific metadata

EANET_FILTER_GLOBAL = {
    'EANET': {},
    'EBAS': {
        'projects': ['EANET'],
        'datalevel': '2',
    }
}

EANET_FILTER_PARAMS = {
    'SO2': {
        'EANET': {
            'unit': 'ppb',
        },
        'EBAS': {
            'matrix': 'air',
            'comp_name': 'sulphur_dioxide',
            'unit': 'nmol/mol',
        },
    },
    'HNO3': {
        'EANET': {
            'unit': 'ppb',
        },
        'EBAS': {
            'matrix': 'air',
            'comp_name': 'nitric_acid',
            'unit': 'nmol/mol',
        },
    },
    'HCl': {
        'EANET': {
            'unit': 'ppb',
        },
        'EBAS': {
            'matrix': 'air',
            'comp_name': 'hydrochloric_acid',
            'unit': 'nmol/mol',
        },
    },
    'NH3': {
        'EANET': {
            'unit': 'ppb',
        },
        'EBAS': {
            'matrix': 'air',
            'comp_name': 'ammonia',
            'unit': 'nmol/mol',
        },
    },
    'SO42-': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'sulphate_total',
            'unit': 'ug/m3',
        },
    },
    'NO3-': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'nitrate',
            'unit': 'ug/m3',
        },
    },
    'Cl-': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'chloride',
            'unit': 'ug/m3',
        },
    },
    'NH4+': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'ammonium',
            'unit': 'ug/m3',
        },
    },
    'Na+': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'sodium',
            'unit': 'ug/m3',
        },
    },
    'K+': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'potassium',
            'unit': 'ug/m3',
        },
    },
    'Mg2+': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'magnesium',
            'unit': 'ug/m3',
        },
    },
    'Ca2+': {
        'EANET': {
            'unit': 'ug/m3',
        },
        'EBAS': {
            'matrix': 'aerosol',
            'comp_name': 'calcium',
            'unit': 'ug/m3',
        },
    },
}

# Metadata hirarchy:
# 1) First EANET_SITES is used
# 2) then for each paraeter FILTER_PARAMS
# 3) in EANET_FILTER, site specific metadata can be set specifically for
#    filter conversion
EANET_FILTER_DETAIL = {
    #CN: filter
    'CNA008': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_cn1008',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },        

    #ID:
    'IDA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_id1012',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'IDA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_id1014',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'IDA004': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_id1015',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #JP:
    'JPA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1016',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1050',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1017',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA004': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1019',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA005': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1021',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA006': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1022',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA007': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1023',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA008': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1024',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA009': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1025',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA010': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1027',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA011': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1018',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'JPA012': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_jp1057',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },

    #KH:
    'KHA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_kh1052',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #KR:
    'KRA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_3pack',
                # 3 Stages with an impactor
                'instr_name': 'f3p_kr1035',
                'method': 'JP01L_f3p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'KRA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_3pack',
                # 3 Stages with an impactor
                'instr_name': 'f3p_kr1036',
                'method': 'JP01L_f3p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'KRA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_3pack',
                # 3 Stages with an impactor
                'instr_name': 'f3p_kr1037',
                'method': 'JP01L_f3p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #MM:
    'MMA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_mm1056',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
   
    #MN:
    'MNA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_mn1031',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'MNA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_mn1032',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #MY;
    'MYA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_my1029',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'MYA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_my1030',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'MYA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_my1053',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    
    #PH:
    'PHA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_ph1033',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'PHA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_ph1034',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'PHA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                'instr_name': 'f4p_ph1055',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
   
    #RU:
    'RUA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_ru1038',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'RUA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_ru1039',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'RUA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_ru1040',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'RUA004': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_ru1041',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #TH:
    'THA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_th1042',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'THA003': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_th1044',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'THA004': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_th1045',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'THA005': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_th1046',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    
    'THA008': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_th1054',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },    

    #VN:
    'VNA001': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_vn1047',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'VNA002': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_vn1048',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'VNA005': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_vn1005',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'VNA006': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_vn1006',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
    'VNA007': {
        None: {  # default parameter
            'EANET': {},
            'EBAS': {
                'instr_type': 'filter_4pack',
                # nilu 4 stage
                'instr_name': 'f4p_vn1007',
                'method': 'JP01L_f4p',
                'originator': FILTER_PERSON_DEFAULT,
                'submitter': FILTER_PERSON_DEFAULT,
            },
        }
    },
}

