"""Which indicators to collect, and from where."""

SERIES = [
    {
        "name": "eur_usd",
        "source": "ecb",
        "flow": "EXR",
        "key": "D.USD.EUR.SP00.A",
        "frequency": "daily",
    },
    {
        "name": "ecb_policy_rate",
        "source": "ecb",
        "flow": "FM",
        "key": "D.U2.EUR.4F.KR.MRR_FR.LEV",
        "frequency": "daily",
    },
    {
        "name": "hicp_euro_area",
        "source": "eurostat",
        "dataset": "prc_hicp_manr",
        "filters": {"geo": "EA20", "coicop": "CP00", "unit": "RCH_A"},
        "frequency": "monthly",
    },
    {
        "name": "unemployment_euro_area",
        "source": "eurostat",
        "dataset": "une_rt_m",
        "filters": {"geo": "EA21", "s_adj": "SA", "age": "TOTAL", "sex": "T", "unit": "PC_ACT"},
        "frequency": "monthly",
    },
    {
        "name": "us_cpi",
        "source": "fred",
        "series_id": "CPIAUCSL",
        "frequency": "monthly",
    },
    {
        "name": "us_fed_funds_rate",
        "source": "fred",
        "series_id": "FEDFUNDS",
        "frequency": "monthly",
    },
]