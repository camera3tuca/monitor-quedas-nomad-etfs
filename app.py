import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Monitor ETFs Nomad — Swing Trade Pro",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f4c81 0%, #1565c0 60%, #0288d1 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .main-title {
        color: white; font-size: 2.2rem; font-weight: 700;
        margin: 0; text-align: center;
    }
    .main-subtitle {
        color: rgba(255,255,255,0.9); font-size: 1rem;
        text-align: center; margin-top: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0f4c81 0%, #0288d1 100%) !important;
        color: white !important; font-weight: 600 !important;
        border: none !important; padding: 0.75rem 2rem !important;
        border-radius: 8px !important; transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(2,136,209,0.45) !important;
    }
    .section-header {
        color: #0288d1; font-size: 1.4rem; font-weight: 600;
        margin-top: 1.5rem; margin-bottom: 0.75rem;
        padding-bottom: 0.4rem; border-bottom: 2px solid #0288d1;
    }
    .tip-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 0.85rem 1rem; border-radius: 8px; margin-bottom: 1rem;
    }
    .tip-box p { margin: 0; color: #0d47a1; font-size: 0.9rem; }
    .select-prompt {
        background: linear-gradient(135deg, #e3f2fd 0%, #b3e5fc 100%);
        padding: 1.75rem 2rem; border-radius: 8px;
        text-align: center; margin: 1.5rem 0;
    }
    .select-prompt p { margin: 0; color: #01579b; font-size: 1rem; font-weight: 500; }
    div[data-testid="metric-container"] {
        background: white; border: 1px solid #e2e8f0;
        padding: 0.8rem 1rem; border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stAlert { border-radius: 8px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# UNIVERSO COMPLETO DE ETFs — NOMAD / NYSE / NASDAQ
# Categorias: Amplos EUA | Internacional | Setoriais | Temáticos | Bonds |
#             Commodities | Alavancados | Cripto | Dividendos | Volatilidade
# =============================================================================
NOMAD_ETFS = {

    # ══════════════════════════════════════════════════════════════════════════
    # AMPLOS EUA
    # ══════════════════════════════════════════════════════════════════════════
    'SPY':   ('SPDR S&P 500 ETF',                    'Amplo EUA'),
    'VOO':   ('Vanguard S&P 500 ETF',                'Amplo EUA'),
    'IVV':   ('iShares Core S&P 500 ETF',            'Amplo EUA'),
    'QQQ':   ('Invesco Nasdaq 100 ETF',              'Amplo EUA'),
    'QQQM':  ('Invesco Nasdaq 100 ETF (mini)',        'Amplo EUA'),
    'VTI':   ('Vanguard Total Stock Market ETF',     'Amplo EUA'),
    'SCHB':  ('Schwab US Broad Market ETF',          'Amplo EUA'),
    'ITOT':  ('iShares Core S&P Total US Mkt ETF',   'Amplo EUA'),
    'IWM':   ('iShares Russell 2000 ETF',            'Amplo EUA'),
    'IWV':   ('iShares Russell 3000 ETF',            'Amplo EUA'),
    'DIA':   ('SPDR Dow Jones Industrial ETF',       'Amplo EUA'),
    'MDY':   ('SPDR S&P MidCap 400 ETF',             'Amplo EUA'),
    'IJH':   ('iShares Core S&P Mid-Cap ETF',        'Amplo EUA'),
    'IJR':   ('iShares Core S&P Small-Cap ETF',      'Amplo EUA'),
    'VB':    ('Vanguard Small-Cap ETF',              'Amplo EUA'),
    'VO':    ('Vanguard Mid-Cap ETF',                'Amplo EUA'),
    'VV':    ('Vanguard Large-Cap ETF',              'Amplo EUA'),
    'SCHX':  ('Schwab US Large-Cap ETF',             'Amplo EUA'),
    'SCHA':  ('Schwab US Small-Cap ETF',             'Amplo EUA'),
    'SCHM':  ('Schwab US Mid-Cap ETF',               'Amplo EUA'),
    'OEF':   ('iShares S&P 100 ETF',                 'Amplo EUA'),
    'RSP':   ('Invesco S&P 500 Equal Weight ETF',    'Amplo EUA'),

    # ══════════════════════════════════════════════════════════════════════════
    # SETORIAIS — Select Sector SPDRs
    # ══════════════════════════════════════════════════════════════════════════
    'XLK':   ('Technology Select Sector SPDR',       'Setor Tecnologia'),
    'XLF':   ('Financial Select Sector SPDR',        'Setor Financeiro'),
    'XLE':   ('Energy Select Sector SPDR',           'Setor Energia'),
    'XLV':   ('Health Care Select Sector SPDR',      'Setor Saúde'),
    'XLI':   ('Industrial Select Sector SPDR',       'Setor Industrial'),
    'XLB':   ('Materials Select Sector SPDR',        'Setor Materiais'),
    'XLY':   ('Consumer Discret. Select SPDR',       'Setor Consumo Cíclico'),
    'XLP':   ('Consumer Staples Select SPDR',        'Setor Consumo Básico'),
    'XLRE':  ('Real Estate Select Sector SPDR',      'Setor Imobiliário'),
    'XLU':   ('Utilities Select Sector SPDR',        'Setor Utilities'),
    'XLC':   ('Communication Services SPDR',         'Setor Comunicação'),
    # Vanguard setoriais
    'VGT':   ('Vanguard Info Technology ETF',        'Setor Tecnologia'),
    'VHT':   ('Vanguard Health Care ETF',            'Setor Saúde'),
    'VFH':   ('Vanguard Financials ETF',             'Setor Financeiro'),
    'VDE':   ('Vanguard Energy ETF',                 'Setor Energia'),
    'VAW':   ('Vanguard Materials ETF',              'Setor Materiais'),
    'VIS':   ('Vanguard Industrials ETF',            'Setor Industrial'),
    'VCR':   ('Vanguard Consumer Discret. ETF',      'Setor Consumo Cíclico'),
    'VDC':   ('Vanguard Consumer Staples ETF',       'Setor Consumo Básico'),
    'VOX':   ('Vanguard Communication Svcs ETF',     'Setor Comunicação'),
    'VPU':   ('Vanguard Utilities ETF',              'Setor Utilities'),
    'VNQ':   ('Vanguard Real Estate ETF',            'Setor Imobiliário'),
    # iShares setoriais
    'IYW':   ('iShares US Technology ETF',           'Setor Tecnologia'),
    'IYF':   ('iShares US Financials ETF',           'Setor Financeiro'),
    'IYE':   ('iShares US Energy ETF',               'Setor Energia'),
    'IYH':   ('iShares US Healthcare ETF',           'Setor Saúde'),
    'IYJ':   ('iShares US Industrials ETF',          'Setor Industrial'),
    'IYR':   ('iShares US Real Estate ETF',          'Setor Imobiliário'),
    'IYC':   ('iShares US Consumer Discret. ETF',    'Setor Consumo Cíclico'),
    'IYK':   ('iShares US Consumer Staples ETF',     'Setor Consumo Básico'),
    'IDU':   ('iShares US Utilities ETF',            'Setor Utilities'),
    # Outros setoriais
    'KBWB':  ('Invesco KBW Bank ETF',                'Setor Financeiro'),
    'KRE':   ('SPDR S&P Regional Banking ETF',       'Setor Financeiro'),
    'KBE':   ('SPDR S&P Bank ETF',                   'Setor Financeiro'),
    'IAI':   ('iShares US Broker-Dealers ETF',       'Setor Financeiro'),
    'XBI':   ('SPDR Biotech ETF',                    'Setor Saúde'),
    'IBB':   ('iShares Biotechnology ETF',           'Setor Saúde'),
    'IHI':   ('iShares US Medical Devices ETF',      'Setor Saúde'),
    'IHF':   ('iShares US Healthcare Providers ETF', 'Setor Saúde'),
    'XPH':   ('SPDR Pharmaceuticals ETF',            'Setor Saúde'),
    'XES':   ('SPDR Oil & Gas Equip. Svcs ETF',      'Setor Energia'),
    'XOP':   ('SPDR Oil & Gas Exploration ETF',      'Setor Energia'),
    'OIH':   ('VanEck Oil Services ETF',             'Setor Energia'),
    'JETS':  ('US Global Jets ETF',                  'Setor Industrial'),
    'ITA':   ('iShares US Aerospace & Defense ETF',  'Setor Industrial'),
    'PPA':   ('Invesco Aerospace & Defense ETF',     'Setor Industrial'),
    'XHB':   ('SPDR Homebuilders ETF',               'Setor Imobiliário'),
    'ITB':   ('iShares US Home Construction ETF',    'Setor Imobiliário'),
    'SCHH':  ('Schwab US REIT ETF',                  'Setor Imobiliário'),
    'REM':   ('iShares Mortgage Real Estate ETF',    'Setor Imobiliário'),
    'XRT':   ('SPDR S&P Retail ETF',                 'Setor Consumo Cíclico'),
    'IAK':   ('iShares US Insurance ETF',            'Setor Financeiro'),

    # ══════════════════════════════════════════════════════════════════════════
    # TECNOLOGIA / IA / SEMIS / NUVEM / CIBERSEGURANÇA
    # ══════════════════════════════════════════════════════════════════════════
    'SOXX':  ('iShares Semiconductor ETF',           'Tech & IA'),
    'SMH':   ('VanEck Semiconductor ETF',            'Tech & IA'),
    'SOXQ':  ('Invesco PHLX Semiconductor ETF',      'Tech & IA'),
    'CIBR':  ('First Trust Cybersecurity ETF',       'Tech & IA'),
    'BUG':   ('Global X Cybersecurity ETF',          'Tech & IA'),
    'HACK':  ('ETFMG Prime Cyber Security ETF',      'Tech & IA'),
    'CLOU':  ('Global X Cloud Computing ETF',        'Tech & IA'),
    'SKYY':  ('First Trust Cloud Computing ETF',     'Tech & IA'),
    'WCLD':  ('WisdomTree Cloud Computing ETF',      'Tech & IA'),
    'BOTZ':  ('Global X Robotics & AI ETF',          'Tech & IA'),
    'ROBO':  ('ROBO Global Robotics ETF',            'Tech & IA'),
    'AIQ':   ('Global X AI & Technology ETF',        'Tech & IA'),
    'ARKK':  ('ARK Innovation ETF',                  'Tech & IA'),
    'ARKW':  ('ARK Next Gen Internet ETF',           'Tech & IA'),
    'ARKQ':  ('ARK Autonomous Tech & Robotics ETF',  'Tech & IA'),
    'ARKF':  ('ARK Fintech Innovation ETF',          'Tech & IA'),
    'ARKG':  ('ARK Genomic Revolution ETF',          'Tech & IA'),
    'QQEW':  ('First Trust Nasdaq-100 Equal Wt ETF', 'Tech & IA'),
    'BKCH':  ('Global X Blockchain ETF',             'Tech & IA'),
    'DRIV':  ('Global X Autonomous & EV ETF',        'Tech & IA'),
    'IDAT':  ('iShares Data & AI Innovation ETF',    'Tech & IA'),
    'IGPT':  ('Invesco AI & Next Gen Software ETF',  'Tech & IA'),
    'CHAT':  ('Roundhill Generative AI & Tech ETF',  'Tech & IA'),

    # ══════════════════════════════════════════════════════════════════════════
    # FINTECH / CRIPTO / BITCOIN
    # ══════════════════════════════════════════════════════════════════════════
    'IBIT':  ('iShares Bitcoin Trust ETF',           'Cripto & Fintech'),
    'FBTC':  ('Fidelity Wise Origin Bitcoin ETF',    'Cripto & Fintech'),
    'BITB':  ('Bitwise Bitcoin ETF',                 'Cripto & Fintech'),
    'ARKB':  ('ARK 21Shares Bitcoin ETF',            'Cripto & Fintech'),
    'HODL':  ('VanEck Bitcoin ETF',                  'Cripto & Fintech'),
    'BRRR':  ('Canary Bitcoin ETF',                  'Cripto & Fintech'),
    'ETHA':  ('iShares Ethereum Trust ETF',          'Cripto & Fintech'),
    'FETH':  ('Fidelity Ethereum Fund ETF',          'Cripto & Fintech'),
    'GBTC':  ('Grayscale Bitcoin Trust ETF',         'Cripto & Fintech'),
    'BITO':  ('ProShares Bitcoin Strategy ETF',      'Cripto & Fintech'),
    'FINX':  ('Global X FinTech ETF',                'Cripto & Fintech'),
    'BLOK':  ('Amplify Transformational Data ETF',   'Cripto & Fintech'),

    # ══════════════════════════════════════════════════════════════════════════
    # ENERGIA LIMPA / ESG / SUSTENTABILIDADE
    # ══════════════════════════════════════════════════════════════════════════
    'ICLN':  ('iShares Global Clean Energy ETF',     'Energia Limpa'),
    'QCLN':  ('First Trust NASDAQ Clean Edge ETF',   'Energia Limpa'),
    'TAN':   ('Invesco Solar ETF',                   'Energia Limpa'),
    'FAN':   ('First Trust Global Wind Energy ETF',  'Energia Limpa'),
    'ACES':  ('ALPS Clean Energy ETF',               'Energia Limpa'),
    'CNRG':  ('SPDR S&P Kensho Clean Power ETF',     'Energia Limpa'),
    'ESGU':  ('iShares ESG Aware MSCI USA ETF',      'ESG'),
    'ESGE':  ('iShares ESG Aware MSCI EM ETF',       'ESG'),
    'ESGD':  ('iShares ESG Aware MSCI EAFE ETF',     'ESG'),
    'SNPE':  ('Xtrackers S&P 500 ESG ETF',           'ESG'),
    'SUSL':  ('iShares ESG MSCI USA Leaders ETF',    'ESG'),

    # ══════════════════════════════════════════════════════════════════════════
    # INTERNACIONAL — Desenvolvidos
    # ══════════════════════════════════════════════════════════════════════════
    'EFA':   ('iShares MSCI EAFE ETF',               'Internacional Desenv.'),
    'VEA':   ('Vanguard FTSE Dev Markets ETF',       'Internacional Desenv.'),
    'SCHF':  ('Schwab International Equity ETF',     'Internacional Desenv.'),
    'IEFA':  ('iShares Core MSCI EAFE ETF',          'Internacional Desenv.'),
    'EWJ':   ('iShares MSCI Japan ETF',              'Internacional Desenv.'),
    'EWG':   ('iShares MSCI Germany ETF',            'Internacional Desenv.'),
    'EWU':   ('iShares MSCI United Kingdom ETF',     'Internacional Desenv.'),
    'EWL':   ('iShares MSCI Switzerland ETF',        'Internacional Desenv.'),
    'EWQ':   ('iShares MSCI France ETF',             'Internacional Desenv.'),
    'EWI':   ('iShares MSCI Italy ETF',              'Internacional Desenv.'),
    'EWP':   ('iShares MSCI Spain ETF',              'Internacional Desenv.'),
    'EWD':   ('iShares MSCI Sweden ETF',             'Internacional Desenv.'),
    'EWN':   ('iShares MSCI Netherlands ETF',        'Internacional Desenv.'),
    'EWA':   ('iShares MSCI Australia ETF',          'Internacional Desenv.'),
    'EWC':   ('iShares MSCI Canada ETF',             'Internacional Desenv.'),
    'EWH':   ('iShares MSCI Hong Kong ETF',          'Internacional Desenv.'),
    'EWS':   ('iShares MSCI Singapore ETF',          'Internacional Desenv.'),
    'BBJP':  ('JPMorgan BetaBuilders Japan ETF',     'Internacional Desenv.'),
    'BBEU':  ('JPMorgan BetaBuilders Europe ETF',    'Internacional Desenv.'),
    'ACWX':  ('iShares MSCI ACWI ex US ETF',         'Internacional Desenv.'),
    'ACWI':  ('iShares MSCI ACWI ETF',               'Internacional Desenv.'),
    'URTH':  ('iShares MSCI World ETF',              'Internacional Desenv.'),

    # ══════════════════════════════════════════════════════════════════════════
    # INTERNACIONAL — Emergentes
    # ══════════════════════════════════════════════════════════════════════════
    'EEM':   ('iShares MSCI Emerging Markets ETF',   'Mercados Emergentes'),
    'VWO':   ('Vanguard FTSE Emerging Markets ETF',  'Mercados Emergentes'),
    'IEMG':  ('iShares Core MSCI Emerging Mkt ETF',  'Mercados Emergentes'),
    'SCHE':  ('Schwab Emerging Markets Equity ETF',  'Mercados Emergentes'),
    'FXI':   ('iShares China Large-Cap ETF',         'Mercados Emergentes'),
    'MCHI':  ('iShares MSCI China ETF',              'Mercados Emergentes'),
    'KWEB':  ('KraneShares CSI China Internet ETF',  'Mercados Emergentes'),
    'EWZ':   ('iShares MSCI Brazil ETF',             'Mercados Emergentes'),
    'EWT':   ('iShares MSCI Taiwan ETF',             'Mercados Emergentes'),
    'EWY':   ('iShares MSCI South Korea ETF',        'Mercados Emergentes'),
    'INDA':  ('iShares MSCI India ETF',              'Mercados Emergentes'),
    'INDY':  ('iShares India 50 ETF',                'Mercados Emergentes'),
    'SMIN':  ('iShares MSCI India Small-Cap ETF',    'Mercados Emergentes'),
    'EWW':   ('iShares MSCI Mexico ETF',             'Mercados Emergentes'),
    'ECH':   ('iShares MSCI Chile ETF',              'Mercados Emergentes'),
    'ILF':   ('iShares Latin America 40 ETF',        'Mercados Emergentes'),
    'GXG':   ('Global X MSCI Colombia ETF',          'Mercados Emergentes'),
    'ARGT':  ('Global X MSCI Argentina ETF',         'Mercados Emergentes'),
    'EZA':   ('iShares MSCI South Africa ETF',       'Mercados Emergentes'),
    'EPHE':  ('iShares MSCI Philippines ETF',        'Mercados Emergentes'),
    'THD':   ('iShares MSCI Thailand ETF',           'Mercados Emergentes'),
    'EWM':   ('iShares MSCI Malaysia ETF',           'Mercados Emergentes'),
    'TUR':   ('iShares MSCI Turkey ETF',             'Mercados Emergentes'),
    'EPOL':  ('iShares MSCI Poland ETF',             'Mercados Emergentes'),
    'GEM':   ('Goldman Sachs ActiveBeta EM ETF',     'Mercados Emergentes'),

    # ══════════════════════════════════════════════════════════════════════════
    # DIVIDENDOS / RENDA
    # ══════════════════════════════════════════════════════════════════════════
    'SCHD':  ('Schwab US Dividend Equity ETF',       'Dividendos'),
    'VIG':   ('Vanguard Dividend Appreciation ETF',  'Dividendos'),
    'VYM':   ('Vanguard High Dividend Yield ETF',    'Dividendos'),
    'HDV':   ('iShares Core High Dividend ETF',      'Dividendos'),
    'DVY':   ('iShares Select Dividend ETF',         'Dividendos'),
    'SDY':   ('SPDR S&P Dividend ETF',               'Dividendos'),
    'NOBL':  ('ProShares S&P 500 Div Aristocrats',   'Dividendos'),
    'DGRO':  ('iShares Core Dividend Growth ETF',    'Dividendos'),
    'DIVO':  ('Amplify CWP Enhanced Div Inc ETF',    'Dividendos'),
    'SPHD':  ('Invesco S&P 500 High Div Low Vol ETF','Dividendos'),
    'SPYD':  ('SPDR Portfolio S&P 500 High Div ETF', 'Dividendos'),
    'JEPI':  ('JPMorgan Equity Premium Income ETF',  'Dividendos'),
    'JEPQ':  ('JPMorgan Nasdaq Equity Prem Inc ETF', 'Dividendos'),
    'QYLD':  ('Global X Nasdaq 100 Covered Call ETF','Dividendos'),
    'XYLD':  ('Global X S&P 500 Covered Call ETF',   'Dividendos'),
    'RYLD':  ('Global X Russell 2000 Covered Call',  'Dividendos'),
    'DGRW':  ('WisdomTree US Quality Div Growth ETF','Dividendos'),
    'PFF':   ('iShares Preferred & Income Sec ETF',  'Dividendos'),
    'PGX':   ('Invesco Preferred ETF',               'Dividendos'),

    # ══════════════════════════════════════════════════════════════════════════
    # RENDA FIXA — Tesouro / Governos / Corporativos / HY
    # ══════════════════════════════════════════════════════════════════════════
    'TLT':   ('iShares 20+ Year Treasury ETF',       'Renda Fixa'),
    'TLH':   ('iShares 10-20 Year Treasury ETF',     'Renda Fixa'),
    'IEF':   ('iShares 7-10 Year Treasury ETF',      'Renda Fixa'),
    'IEI':   ('iShares 3-7 Year Treasury ETF',       'Renda Fixa'),
    'SHY':   ('iShares 1-3 Year Treasury ETF',       'Renda Fixa'),
    'SHV':   ('iShares Short Treasury Bond ETF',     'Renda Fixa'),
    'SGOV':  ('iShares 0-3 Month Treasury ETF',      'Renda Fixa'),
    'BIL':   ('SPDR Bloomberg 1-3M T-Bill ETF',      'Renda Fixa'),
    'USFR':  ('WisdomTree Floating Rate ETF',        'Renda Fixa'),
    'TFLO':  ('iShares Treasury Float Rate ETF',     'Renda Fixa'),
    'AGG':   ('iShares Core US Aggregate Bond ETF',  'Renda Fixa'),
    'BND':   ('Vanguard Total Bond Market ETF',      'Renda Fixa'),
    'SCHZ':  ('Schwab US Aggregate Bond ETF',        'Renda Fixa'),
    'LQD':   ('iShares iBoxx Investm. Grade Bond ETF','Renda Fixa'),
    'VCIT':  ('Vanguard Interm-Term Corp Bond ETF',  'Renda Fixa'),
    'VCSH':  ('Vanguard Short-Term Corp Bond ETF',   'Renda Fixa'),
    'VCLT':  ('Vanguard Long-Term Corp Bond ETF',    'Renda Fixa'),
    'HYG':   ('iShares iBoxx High Yield Bond ETF',   'Renda Fixa'),
    'JNK':   ('SPDR Bloomberg High Yield Bond ETF',  'Renda Fixa'),
    'FALN':  ('iShares Fallen Angels USD Bond ETF',  'Renda Fixa'),
    'TIP':   ('iShares TIPS Bond ETF',               'Renda Fixa'),
    'SCHP':  ('Schwab US TIPS ETF',                  'Renda Fixa'),
    'STIP':  ('iShares 0-5 Year TIPS Bond ETF',      'Renda Fixa'),
    'MBB':   ('iShares MBS ETF',                     'Renda Fixa'),
    'EMB':   ('iShares JPMorgan EM Bond ETF',        'Renda Fixa'),
    'VWOB':  ('Vanguard Emerging Mkt Govt Bd ETF',   'Renda Fixa'),
    'PCY':   ('Invesco Emerging Mkts Sovereign ETF', 'Renda Fixa'),
    'BWX':   ('SPDR Bloomberg Intl Treasury ETF',    'Renda Fixa'),
    'IGOV':  ('iShares Intl Treasury Bond ETF',      'Renda Fixa'),
    'BNDX':  ('Vanguard Total Intl Bond ETF',        'Renda Fixa'),
    'FLRN':  ('SPDR Bloomberg Investment Grade ETF', 'Renda Fixa'),
    'SPTI':  ('SPDR Portfolio Intermediate ETF',     'Renda Fixa'),
    'SPTS':  ('SPDR Portfolio Short Term ETF',       'Renda Fixa'),
    'SPTL':  ('SPDR Portfolio Long Term ETF',        'Renda Fixa'),
    'GOVT':  ('iShares US Treasury Bond ETF',        'Renda Fixa'),
    'VGSH':  ('Vanguard Short-Term Govt Bond ETF',   'Renda Fixa'),
    'VGIT':  ('Vanguard Interm-Term Govt Bond ETF',  'Renda Fixa'),
    'VGLT':  ('Vanguard Long-Term Govt Bond ETF',    'Renda Fixa'),
    'BSV':   ('Vanguard Short-Term Bond ETF',        'Renda Fixa'),
    'BIV':   ('Vanguard Interm-Term Bond ETF',       'Renda Fixa'),
    'BLV':   ('Vanguard Long-Term Bond ETF',         'Renda Fixa'),
    'IGSB':  ('iShares Short-Term Corp Bond ETF',    'Renda Fixa'),
    'IGIB':  ('iShares Interm-Term Corp Bond ETF',   'Renda Fixa'),
    'IGLB':  ('iShares Long-Term Corp Bond ETF',     'Renda Fixa'),
    'USHY':  ('iShares Broad USD High Yield ETF',    'Renda Fixa'),
    'HYSA':  ('PGIM US Short Duration HY Bond ETF',  'Renda Fixa'),
    'SHYG':  ('iShares 0-5 Year High Yield Bond ETF','Renda Fixa'),
    'HYLB':  ('Xtrackers USD High Yield Corp ETF',   'Renda Fixa'),
    'SJNK':  ('SPDR Bloomberg Short-Term HY ETF',    'Renda Fixa'),

    # ══════════════════════════════════════════════════════════════════════════
    # COMMODITIES — Ouro / Prata / Petróleo / Metais / Agrícolas
    # ══════════════════════════════════════════════════════════════════════════
    'GLD':   ('SPDR Gold Shares ETF',                'Commodities'),
    'IAU':   ('iShares Gold Trust ETF',              'Commodities'),
    'GLDM':  ('SPDR Gold MiniShares ETF',            'Commodities'),
    'BAR':   ('GraniteShares Gold Trust ETF',        'Commodities'),
    'AAAU':  ('Goldman Sachs Physical Gold ETF',     'Commodities'),
    'SLV':   ('iShares Silver Trust ETF',            'Commodities'),
    'SIVR':  ('Aberdeen Standard Physical Silver ETF','Commodities'),
    'PPLT':  ('Aberdeen Standard Platinum ETF',      'Commodities'),
    'PALL':  ('Aberdeen Standard Palladium ETF',     'Commodities'),
    'COPX':  ('Global X Copper Miners ETF',          'Commodities'),
    'URA':   ('Global X Uranium ETF',                'Commodities'),
    'LIT':   ('Global X Lithium & Battery ETF',      'Commodities'),
    'REMX':  ('VanEck Rare Earth/Strat. Metals ETF', 'Commodities'),
    'SIL':   ('Global X Silver Miners ETF',          'Commodities'),
    'GDX':   ('VanEck Gold Miners ETF',              'Commodities'),
    'GDXJ':  ('VanEck Junior Gold Miners ETF',       'Commodities'),
    'RING':  ('iShares MSCI Global Gold Miners ETF', 'Commodities'),
    'USO':   ('United States Oil Fund ETF',          'Commodities'),
    'BNO':   ('United States Brent Oil Fund ETF',    'Commodities'),
    'UNG':   ('United States Nat Gas Fund ETF',      'Commodities'),
    'BOIL':  ('ProShares Ultra Bloomberg Nat Gas',   'Commodities'),
    'PDBC':  ('Invesco DB Opt Yield Div Com ETF',    'Commodities'),
    'GSG':   ('iShares S&P GSCI Commodity ETF',      'Commodities'),
    'DJP':   ('iPath Bloomberg Commodity Index ETN', 'Commodities'),
    'CORN':  ('Teucrium Corn Fund ETF',              'Commodities'),
    'WEAT':  ('Teucrium Wheat Fund ETF',             'Commodities'),
    'SOYB':  ('Teucrium Soybean Fund ETF',           'Commodities'),
    'CANE':  ('Teucrium Sugar Fund ETF',             'Commodities'),

    # ══════════════════════════════════════════════════════════════════════════
    # TEMÁTICOS / MEGATENDÊNCIAS
    # ══════════════════════════════════════════════════════════════════════════
    'PAVE':  ('Global X US Infrastructure Dev ETF',  'Temático'),
    'BETZ':  ('Roundhill Sports Betting ETF',        'Temático'),
    'HERO':  ('Global X Video Games & Esports ETF',  'Temático'),
    'ESPO':  ('VanEck Video Gaming & eSports ETF',   'Temático'),
    'SOCL':  ('Global X Social Media ETF',           'Temático'),
    'AWAY':  ('ETF Managers Travel Tech ETF',        'Temático'),
    'NERD':  ('Roundhill Video Games & eSports ETF', 'Temático'),
    'BLOK':  ('Amplify Blockchain Innovators ETF',   'Temático'),
    'POTX':  ('Global X Cannabis ETF',               'Temático'),
    'MJ':    ('ETFMG Alternative Harvest ETF',       'Temático'),
    'MSOS':  ('AdvisorShares Pure US Cannabis ETF',  'Temático'),
    'GNOM':  ('Global X Genomics & Biotech ETF',     'Temático'),
    'EDUT':  ('Global X Education ETF',              'Temático'),
    'HERO':  ('Global X Video Games & Esports ETF',  'Temático'),
    'PINK':  ('LGBTQ100 ESG ETF',                    'Temático'),
    'NANC':  ('Unusual Whales Subversive Demo ETF',  'Temático'),
    'KRUZ':  ('Unusual Whales Subversive Rep ETF',   'Temático'),
    'DSPY':  ('VanEck Defense ETF',                  'Temático'),
    'SHLD':  ('Global X Defense Tech ETF',           'Temático'),
    'PRNT':  ('3D Printing ETF',                     'Temático'),
    'LNGR':  ('Global X Longevity Thematic ETF',     'Temático'),
    'SNSR':  ('Global X Internet of Things ETF',     'Temático'),
    'CTEC':  ('Global X CleanTech ETF',              'Temático'),
    'BATT':  ('Amplify Lithium & Battery Tech ETF',  'Temático'),
    'NXTG':  ('First Trust Indxx NextG ETF',         'Temático'),
    'FIVG':  ('Defiance Next Gen Connectivity ETF',  'Temático'),
    'UFO':   ('Procure Space ETF',                   'Temático'),
    'ROKT':  ('SPDR S&P Kensho Final Frontiers ETF', 'Temático'),
    'SKYQ':  ('SPDR S&P Aerospace & Def ETF',        'Temático'),
    'MOO':   ('VanEck Agribusiness ETF',             'Temático'),
    'DIET':  ('VanEck Future of Food ETF',           'Temático'),
    'EATV':  ('VegTech Plant-based ETF',             'Temático'),
    'STKS':  ('Stocks & Bonds ETF',                  'Temático'),

    # ══════════════════════════════════════════════════════════════════════════
    # FATOR / SMART BETA / LOW VOL / QUALITY / MOMENTUM / VALUE
    # ══════════════════════════════════════════════════════════════════════════
    'QUAL':  ('iShares MSCI USA Quality Factor ETF', 'Fator / Smart Beta'),
    'MTUM':  ('iShares MSCI USA Momentum Factor ETF','Fator / Smart Beta'),
    'VLUE':  ('iShares MSCI USA Value Factor ETF',   'Fator / Smart Beta'),
    'SIZE':  ('iShares MSCI USA Size Factor ETF',    'Fator / Smart Beta'),
    'USMV':  ('iShares MSCI USA Min Vol Factor ETF', 'Fator / Smart Beta'),
    'ACWV':  ('iShares MSCI Global Min Vol ETF',     'Fator / Smart Beta'),
    'EFAV':  ('iShares MSCI EAFE Min Vol ETF',       'Fator / Smart Beta'),
    'EEMV':  ('iShares MSCI EM Min Vol ETF',         'Fator / Smart Beta'),
    'SPLV':  ('Invesco S&P 500 Low Vol ETF',         'Fator / Smart Beta'),
    'SPHQ':  ('Invesco S&P 500 Quality ETF',         'Fator / Smart Beta'),
    'PRF':   ('Invesco FTSE RAFI US 1000 ETF',       'Fator / Smart Beta'),
    'COWZ':  ('Pacer US Cash Cows 100 ETF',          'Fator / Smart Beta'),
    'CALF':  ('Pacer US Small Cap Cash Cows ETF',    'Fator / Smart Beta'),
    'VFMO':  ('Vanguard US Momentum Factor ETF',     'Fator / Smart Beta'),
    'VFMV':  ('Vanguard US Min Volatility ETF',      'Fator / Smart Beta'),
    'VFQY':  ('Vanguard US Quality Factor ETF',      'Fator / Smart Beta'),
    'VFVA':  ('Vanguard US Value Factor ETF',        'Fator / Smart Beta'),
    'DFLV':  ('Dimensional US Large Value ETF',      'Fator / Smart Beta'),
    'DFSV':  ('Dimensional US Small Value ETF',      'Fator / Smart Beta'),
    'DFAC':  ('Dimensional US Core Equity 2 ETF',    'Fator / Smart Beta'),
    'DFAS':  ('Dimensional US Small Cap ETF',        'Fator / Smart Beta'),
    'AVUV':  ('Avantis US Small Cap Value ETF',      'Fator / Smart Beta'),
    'AVLV':  ('Avantis US Large Cap Value ETF',      'Fator / Smart Beta'),
    'AVDV':  ('Avantis Intl Small Cap Value ETF',    'Fator / Smart Beta'),
    'AVES':  ('Avantis Emerging Mkts Value ETF',     'Fator / Smart Beta'),
    'XSVM':  ('Invesco S&P SmallCap Val w Mom ETF',  'Fator / Smart Beta'),
    'QVAL':  ('Alpha Architect US Quant Value ETF',  'Fator / Smart Beta'),

    # ══════════════════════════════════════════════════════════════════════════
    # ALAVANCADOS (2x / 3x) e INVERSOS
    # ══════════════════════════════════════════════════════════════════════════
    'TQQQ':  ('ProShares UltraPro QQQ 3x',           'Alavancado / Inverso'),
    'SQQQ':  ('ProShares UltraPro Short QQQ 3x',     'Alavancado / Inverso'),
    'QLD':   ('ProShares Ultra QQQ 2x',              'Alavancado / Inverso'),
    'QID':   ('ProShares UltraShort QQQ 2x',         'Alavancado / Inverso'),
    'UPRO':  ('ProShares UltraPro S&P 500 3x',       'Alavancado / Inverso'),
    'SPXU':  ('ProShares UltraPro Short S&P 3x',     'Alavancado / Inverso'),
    'SSO':   ('ProShares Ultra S&P 500 2x',          'Alavancado / Inverso'),
    'SDS':   ('ProShares UltraShort S&P 500 2x',     'Alavancado / Inverso'),
    'SPXL':  ('Direxion Daily S&P 500 Bull 3x',      'Alavancado / Inverso'),
    'SPXS':  ('Direxion Daily S&P 500 Bear 3x',      'Alavancado / Inverso'),
    'SOXL':  ('Direxion Daily Semicon Bull 3x',      'Alavancado / Inverso'),
    'SOXS':  ('Direxion Daily Semicon Bear 3x',      'Alavancado / Inverso'),
    'TECL':  ('Direxion Daily Tech Bull 3x',         'Alavancado / Inverso'),
    'TECS':  ('Direxion Daily Tech Bear 3x',         'Alavancado / Inverso'),
    'FAS':   ('Direxion Daily Financial Bull 3x',    'Alavancado / Inverso'),
    'FAZ':   ('Direxion Daily Financial Bear 3x',    'Alavancado / Inverso'),
    'TNA':   ('Direxion Daily S&P Small Bull 3x',    'Alavancado / Inverso'),
    'TZA':   ('Direxion Daily S&P Small Bear 3x',    'Alavancado / Inverso'),
    'LABU':  ('Direxion Daily Biotech Bull 3x',      'Alavancado / Inverso'),
    'LABD':  ('Direxion Daily Biotech Bear 3x',      'Alavancado / Inverso'),
    'NAIL':  ('Direxion Daily Homebuilders Bull 3x',  'Alavancado / Inverso'),
    'CURE':  ('Direxion Daily Healthcare Bull 3x',   'Alavancado / Inverso'),
    'NUGT':  ('Direxion Daily Gold Miners Bull 2x',  'Alavancado / Inverso'),
    'DUST':  ('Direxion Daily Gold Miners Bear 2x',  'Alavancado / Inverso'),
    'GUSH':  ('Direxion Daily S&P Oil&Gas Bull 2x',  'Alavancado / Inverso'),
    'DRIP':  ('Direxion Daily S&P Oil&Gas Bear 2x',  'Alavancado / Inverso'),
    'ERX':   ('Direxion Daily Energy Bull 2x',       'Alavancado / Inverso'),
    'ERY':   ('Direxion Daily Energy Bear 2x',       'Alavancado / Inverso'),
    'TMF':   ('Direxion Daily 20+ Yr Trs Bull 3x',   'Alavancado / Inverso'),
    'TMV':   ('Direxion Daily 20+ Yr Trs Bear 3x',   'Alavancado / Inverso'),
    'TBT':   ('ProShares UltraShort 20+ Yr Trs 2x',  'Alavancado / Inverso'),
    'UBT':   ('ProShares Ultra 20+ Yr Treasury 2x',  'Alavancado / Inverso'),
    'SH':    ('ProShares Short S&P 500',             'Alavancado / Inverso'),
    'PSQ':   ('ProShares Short QQQ',                 'Alavancado / Inverso'),
    'DOG':   ('ProShares Short Dow30',               'Alavancado / Inverso'),
    'RWM':   ('ProShares Short Russell 2000',        'Alavancado / Inverso'),
    'UVXY':  ('ProShares Ultra VIX Short-Term ETF',  'Alavancado / Inverso'),
    'SVXY':  ('ProShares Short VIX Short-Term ETF',  'Alavancado / Inverso'),
    'VXX':   ('iPath S&P 500 VIX Short-Term ETN',    'Alavancado / Inverso'),
    'BITI':  ('ProShares Short Bitcoin ETF',         'Alavancado / Inverso'),
    'UGL':   ('ProShares Ultra Gold 2x',             'Alavancado / Inverso'),
    'GLL':   ('ProShares UltraShort Gold 2x',        'Alavancado / Inverso'),
    'AGQ':   ('ProShares Ultra Silver 2x',           'Alavancado / Inverso'),
    'ZSL':   ('ProShares UltraShort Silver 2x',      'Alavancado / Inverso'),

    # ══════════════════════════════════════════════════════════════════════════
    # MULTI-ASSET / ALOCAÇÃO / BALANCEADOS
    # ══════════════════════════════════════════════════════════════════════════
    'AOR':   ('iShares Core Growth Alloc ETF',       'Multi-Asset'),
    'AOM':   ('iShares Core Moderate Alloc ETF',     'Multi-Asset'),
    'AOA':   ('iShares Core Aggressive Alloc ETF',   'Multi-Asset'),
    'AOK':   ('iShares Core Conservative Alloc ETF', 'Multi-Asset'),
    'GAL':   ('SPDR SSGA Global Allocation ETF',     'Multi-Asset'),
    'MDIV':  ('First Trust Multi-Asset Div ETF',     'Multi-Asset'),
    'RPAR':  ('RPAR Risk Parity ETF',                'Multi-Asset'),
    'GDE':   ('WisdomTree Efficient Gold Plus ETF',  'Multi-Asset'),
    'NTSX':  ('WisdomTree Efficient Core ETF',       'Multi-Asset'),
    'SWAN':  ('Amplify BlackSwan Growth ETF',        'Multi-Asset'),

    # ══════════════════════════════════════════════════════════════════════════
    # ETFs DE AÇÃO ÚNICA ALAVANCADOS (Single-Stock Leveraged ETFs)
    # ══════════════════════════════════════════════════════════════════════════
    'CONL': ('GraniteShares 2x Long COIN Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 22.6M
    'BTCZ': ('T-Rex 2X Inverse Bitcoin Daily Target ETF', 'ETF Ação Única Alavancado'),  # Vol 18.5M
    'AMDD': ('Direxion Daily AMD Bear 1X ETF', 'ETF Ação Única Alavancado'),  # Vol 15.9M
    'BITX': ('2x Bitcoin Strategy ETF', 'ETF Ação Única Alavancado'),  # Vol 14.4M
    'AMDL': ('GraniteShares 2x Long AMD Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 11.2M
    'AAPD': ('Direxion Daily AAPL Bear 1X ETF', 'ETF Ação Única Alavancado'),  # Vol 9.9M
    'AMZD': ('Direxion Daily AMZN Bear 1X ETF', 'ETF Ação Única Alavancado'),  # Vol 9.7M
    'BITU': ('ProShares Ultra Bitcoin ETF', 'ETF Ação Única Alavancado'),  # Vol 5.5M
    'AMZU': ('Direxion Daily AMZN Bull 2X ETF', 'ETF Ação Única Alavancado'),  # Vol 3.9M
    'AAPU': ('Direxion Daily AAPL Bull 2X ETF', 'ETF Ação Única Alavancado'),  # Vol 1.7M
    'FBL': ('GraniteShares 2x Long META Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 1.0M
    'CRWL': ('GraniteShares 2x Long CRWD Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 0.5M
    'CONI': ('GraniteShares 2x Short COIN Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 0.4M
    'AMZZ': ('GraniteShares 2x Long AMZN Daily ETF', 'ETF Ação Única Alavancado'),  # Vol 0.3M
    'DAMD': ('Defiance Daily Target 2X Short AMD ETF', 'ETF Ação Única Alavancado'),  # Vol 0.3M

    # ── Novos: Amplo EUA ──
    'BLCR': ('iShares Large Cap Core Active ETF', 'Amplo EUA'),  # Vol 4.1M
    'FEZ': ('State Street SPDR EURO STOXX 50 ETF', 'Amplo EUA'),  # Vol 2.6M
    'EZU': ('iShares MSCI Eurozone ETF', 'Amplo EUA'),  # Vol 2.2M
    'DBMF': ('iMGP DBi Managed Futures Strategy ETF', 'Amplo EUA'),  # Vol 2.1M
    'BOXX': ('Alpha Architect 1-3 Month Box ETF', 'Amplo EUA'),  # Vol 1.8M
    'DUHP': ('Dimensional US High Profitability ETF', 'Amplo EUA'),  # Vol 1.6M
    'AMLP': ('Alerian MLP ETF', 'Amplo EUA'),  # Vol 1.5M
    'BUFR': ('FT Vest Laddered Buffer ETF', 'Amplo EUA'),  # Vol 1.4M
    'CGBL': ('Capital Group Core Balanced ETF', 'Amplo EUA'),  # Vol 1.4M
    'FDL': ('First Trust Morningstar ETF', 'Amplo EUA'),  # Vol 1.3M
    'FELC': ('Fidelity Enhanced Large Cap Core ETF', 'Amplo EUA'),  # Vol 1.2M
    'CGUS': ('Capital Group Core Equity ETF', 'Amplo EUA'),  # Vol 1.2M
    'DFUS': ('Dimensional U.S. Equity Market ETF', 'Amplo EUA'),  # Vol 1.2M
    'BTAL': ('AGF U.S. Market Neutral Anti-Beta Fund', 'Amplo EUA'),  # Vol 1.1M
    'ALLW': ('State Street Bridgewater All Weather ETF', 'Amplo EUA'),  # Vol 1.1M
    'DBA': ('Invesco DB Agriculture Fund', 'Amplo EUA'),  # Vol 1.1M
    'CLOZ': ('Eldridge BBB-B CLO ETF', 'Amplo EUA'),  # Vol 1.0M
    'AKRE': ('Akre Focus ETF', 'Amplo EUA'),  # Vol 0.9M
    'CWB': ('State Street SPDR Bloomberg Convertible Se', 'Amplo EUA'),  # Vol 0.9M
    'CGMM': ('Capital Group U.S. Small and Mid Cap ETF', 'Amplo EUA'),  # Vol 0.9M
    'DFAU': ('Dimensional US Core Equity Market ETF', 'Amplo EUA'),  # Vol 0.8M
    'EIDO': ('iShares MSCI Indonesia ETF', 'Amplo EUA'),  # Vol 0.8M
    'CGNG': ('Capital Group New Geography Equity ETF', 'Amplo EUA'),  # Vol 0.7M
    'AIA': ('iShares Asia 50 ETF', 'Amplo EUA'),  # Vol 0.6M
    'CTA': ('Simplify Managed Futures Strategy ETF', 'Amplo EUA'),  # Vol 0.5M
    'DAPP': ('VanEck Digital Transformation ETF', 'Amplo EUA'),  # Vol 0.5M
    'BILS': ('State Street SPDR Bloomberg 3-12 Month T-B', 'Amplo EUA'),  # Vol 0.5M
    'BDVL': ('iShares Disciplined Volatility Equity Acti', 'Amplo EUA'),  # Vol 0.5M
    'CLOA': ('iShares AAA CLO Active ETF', 'Amplo EUA'),  # Vol 0.4M
    'BDYN': ('iShares Dynamic Equity Active ETF', 'Amplo EUA'),  # Vol 0.4M
    'EAGL': ('Eagle Capital Select Equity ETF', 'Amplo EUA'),  # Vol 0.4M
    'FEOE': ('First Eagle Overseas Equity ETF', 'Amplo EUA'),  # Vol 0.3M
    'BBCA': ('JPMorgan BetaBuilders Canada ETF', 'Amplo EUA'),  # Vol 0.3M
    'BALT': ('Innovator Defined Wealth Shield ETF', 'Amplo EUA'),  # Vol 0.3M
    'BDRY': ('Breakwave Dry Bulk Shipping ETF', 'Amplo EUA'),  # Vol 0.3M
    'CGCV': ('Capital Group Conservative Equity ETF', 'Amplo EUA'),  # Vol 0.3M
    'CNEQ': ('Alger Concentrated Equity ETF', 'Amplo EUA'),  # Vol 0.3M
    'CLOX': ('Eldridge AAA CLO ETF', 'Amplo EUA'),  # Vol 0.3M
    'AVUS': ('Avantis U.S. Equity ETF', 'Amplo EUA'),  # Vol 0.3M
    'BBUS': ('JPMorgan BetaBuilders U.S. Equity ETF', 'Amplo EUA'),  # Vol 0.3M
    'BUFD': ('FT Vest Laddered Deep Buffer ETF', 'Amplo EUA'),  # Vol 0.3M
    'BUZZ': ('VanEck Social Sentiment ETF', 'Amplo EUA'),  # Vol 0.2M
    'CLOI': ('VanEck CLO ETF', 'Amplo EUA'),  # Vol 0.2M
    'EIS': ('iShares MSCI Israel ETF', 'Amplo EUA'),  # Vol 0.2M

    # ── Novos: Setor Imobiliário ──
    'DFAR': ('Dimensional US Real Estate ETF', 'Setor Imobiliário'),  # Vol 1.4M

    # ── Novos: Tech & IA ──
    'BAI': ('iShares A.I. Innovation and Tech Active ET', 'Tech & IA'),  # Vol 1.9M
    'FDN': ('First Trust DJ Internet Index Fund', 'Tech & IA'),  # Vol 0.9M
    'AIRR': ('First Trust RBA American Industrial Renais', 'Tech & IA'),  # Vol 0.7M
    'ARTY': ('iShares Future AI & Tech ETF', 'Tech & IA'),  # Vol 0.5M
    'BUYW': ('Main BuyWrite ETF', 'Tech & IA'),  # Vol 0.4M
    'AIPO': ('Defiance AI & Power Infrastructure ETF', 'Tech & IA'),  # Vol 0.4M

    # ── Novos: Cripto & Fintech ──
    'ETH': ('Grayscale Ethereum Staking Mini ETF Shares', 'Cripto & Fintech'),  # Vol 7.4M
    'BTC': ('Grayscale Bitcoin Mini Trust (BTC)', 'Cripto & Fintech'),  # Vol 5.9M
    'ETHE': ('Grayscale Ethereum Staking ETF Shares', 'Cripto & Fintech'),  # Vol 5.1M
    'BSOL': ('Bitwise Solana Staking ETF', 'Cripto & Fintech'),  # Vol 2.5M
    'ETHB': ('iShares Staked Ethereum Trust ETF', 'Cripto & Fintech'),  # Vol 1.7M
    'ETHW': ('Bitwise Ethereum ETF ', 'Cripto & Fintech'),  # Vol 1.7M
    'BTCI': ('NEOS Bitcoin High Income ETF', 'Cripto & Fintech'),  # Vol 0.5M
    'BLOX': ('Nicholas Crypto Income ETF', 'Cripto & Fintech'),  # Vol 0.3M
    'EZBC': ('Franklin Templeton Digital Holdings Trust ', 'Cripto & Fintech'),  # Vol 0.2M
    'ETHV': ('VanEck Ethereum ETF VanEck Ethereum ETF', 'Cripto & Fintech'),  # Vol 0.2M

    # ── Novos: Energia Limpa ──
    'ESGV': ('Vanguard ESG U.S. Stock ETF', 'Energia Limpa'),  # Vol 0.2M

    # ── Novos: Internacional Desenv. ──
    'EFG': ('iShares MSCI EAFE Growth ETF', 'Internacional Desenv.'),  # Vol 4.7M
    'EFV': ('iShares MSCI EAFE Value ETF', 'Internacional Desenv.'),  # Vol 4.0M
    'EUFN': ('iShares MSCI Europe Financials ETF', 'Internacional Desenv.'),  # Vol 2.7M
    'CORO': ('iShares International Country Rotation Act', 'Internacional Desenv.'),  # Vol 2.5M
    'DFAI': ('Dimensional International Core Equity Mark', 'Internacional Desenv.'),  # Vol 2.5M
    'FENI': ('Fidelity Enhanced International ETF', 'Internacional Desenv.'),  # Vol 1.9M
    'DFIV': ('Dimensional International Value ETF', 'Internacional Desenv.'),  # Vol 1.6M
    'AVDE': ('Avantis International Equity ETF', 'Internacional Desenv.'),  # Vol 1.4M
    'DFIC': ('Dimensional International Core Equity 2 ET', 'Internacional Desenv.'),  # Vol 1.3M
    'CGGO': ('Capital Group Global Growth Equity ETF', 'Internacional Desenv.'),  # Vol 1.3M
    'AAXJ': ('iShares MSCI All Country Asia ex Japan ETF', 'Internacional Desenv.'),  # Vol 1.3M
    'CGXU': ('Capital Group International Focus Equity E', 'Internacional Desenv.'),  # Vol 1.2M
    'CGGE': ('Capital Group Global Equity ETF', 'Internacional Desenv.'),  # Vol 1.1M
    'DFAX': ('Dimensional World ex U.S. Core Equity 2 ET', 'Internacional Desenv.'),  # Vol 1.0M
    'DTCR': ('Global X Data Center & Digital Infrastruct', 'Internacional Desenv.'),  # Vol 0.8M
    'DBEF': ('Xtrackers MSCI EAFE Hedged Equity ETF', 'Internacional Desenv.'),  # Vol 0.8M
    'CGIE': ('Capital Group International Equity ETF', 'Internacional Desenv.'),  # Vol 0.7M
    'DXJ': ('WisdomTree Japan Hedged Equity Fund', 'Internacional Desenv.'),  # Vol 0.6M
    'CGIC': ('Capital Group International Core Equity ET', 'Internacional Desenv.'),  # Vol 0.6M
    'EPP': ('iShares MSCI Pacific Ex-Japan Index Fund', 'Internacional Desenv.'),  # Vol 0.6M
    'EUAD': ('Select STOXX Europe Aerospace & Defense ET', 'Internacional Desenv.'),  # Vol 0.6M
    'DIHP': ('Dimensional International High Profitabili', 'Internacional Desenv.'),  # Vol 0.6M
    'DISV': ('Dimensional International Small Cap Value ', 'Internacional Desenv.'),  # Vol 0.5M
    'DFIS': ('Dimensional International Small Cap ETF', 'Internacional Desenv.'),  # Vol 0.5M
    'FEGE': ('First Eagle Global Equity ETF', 'Internacional Desenv.'),  # Vol 0.5M
    'BCGS': ('Bancreek Global Select ETF', 'Internacional Desenv.'),  # Vol 0.4M
    'DFGR': ('Dimensional Global Real Estate ETF', 'Internacional Desenv.'),  # Vol 0.4M
    'BBAX': ('JPMorgan BetaBuilders Developed Asia Pacif', 'Internacional Desenv.'),  # Vol 0.3M
    'FDD': ('First Trust STOXX European Select Dividend', 'Internacional Desenv.'),  # Vol 0.3M
    'DIV': ('Global X Super Dividend ETF', 'Internacional Desenv.'),  # Vol 0.3M
    'EWJV': ('iShares MSCI Japan Value ETF', 'Internacional Desenv.'),  # Vol 0.3M
    'CLIP': ('Global X 1-3 Month T-Bill ETF', 'Internacional Desenv.'),  # Vol 0.3M
    'DIVI': ('Franklin International Core Dividend Tilt ', 'Internacional Desenv.'),  # Vol 0.3M
    'CWI': ('State Street SPDR MSCI ACWI ex-US ETF', 'Internacional Desenv.'),  # Vol 0.3M

    # ── Novos: Mercados Emergentes ──
    'ASHR': ('Xtrackers Harvest CSI 300 China A-Shares E', 'Mercados Emergentes'),  # Vol 8.7M
    'EMXC': ('iShares MSCI Emerging Markets ex China ETF', 'Mercados Emergentes'),  # Vol 4.6M
    'AVEM': ('Avantis Emerging Markets Equity ETF', 'Mercados Emergentes'),  # Vol 2.4M
    'DFAE': ('Dimensional Emerging Core Equity Market ET', 'Mercados Emergentes'),  # Vol 1.3M
    'CQQQ': ('Invesco China Technology ETF', 'Mercados Emergentes'),  # Vol 1.2M
    'DFEM': ('Dimensional Emerging Markets Core Equity 2', 'Mercados Emergentes'),  # Vol 1.0M
    'EWZS': ('iShares MSCI Brazil Small-Cap ETF', 'Mercados Emergentes'),  # Vol 1.0M
    'EPI': ('WisdomTree India Earnings Fund', 'Mercados Emergentes'),  # Vol 0.9M
    'EEMA': ('iShares MSCI Emerging Markets Asia ETF', 'Mercados Emergentes'),  # Vol 0.6M
    'DEM': ('WisdomTree Emerging Markets High Dividend ', 'Mercados Emergentes'),  # Vol 0.3M
    'DVYE': ('iShares Emerging Markets Dividend Index Fu', 'Mercados Emergentes'),  # Vol 0.3M
    'DFEV': ('Dimensional Emerging Markets Value ETF', 'Mercados Emergentes'),  # Vol 0.3M
    'EDIV': ('State Street SPDR S&P Emerging Markets Div', 'Mercados Emergentes'),  # Vol 0.2M

    # ── Novos: Dividendos ──
    'CGDV': ('Capital Group Dividend Value ETF', 'Dividendos'),  # Vol 5.1M
    'DGRW': ('WisdomTree U.S. Quality Dividend Growth Fu', 'Dividendos'),  # Vol 1.3M
    'FDVV': ('Fidelity High Dividend ETF', 'Dividendos'),  # Vol 1.1M
    'CGDG': ('Capital Group Dividend Growers ETF', 'Dividendos'),  # Vol 1.0M

    # ── Novos: Renda Fixa ──
    'BKLN': ('Invesco Senior Loan ETF', 'Renda Fixa'),  # Vol 32.8M
    'EMLC': ('VanEck J. P. Morgan EM Local Currency Bond', 'Renda Fixa'),  # Vol 5.7M
    'BIZD': ('VanEck BDC Income ETF', 'Renda Fixa'),  # Vol 4.8M
    'FBND': ('Fidelity Total Bond ETF', 'Renda Fixa'),  # Vol 3.0M
    'BINC': ('iShares Flexible Income Active ETF', 'Renda Fixa'),  # Vol 3.0M
    'CGCP': ('Capital Group Core Plus Income ETF', 'Renda Fixa'),  # Vol 1.8M
    'CGCB': ('Capital Group Core Bond ETF', 'Renda Fixa'),  # Vol 1.5M
    'EDV': ('Vanguard Extended Duration Treasury ETF', 'Renda Fixa'),  # Vol 1.1M
    'CGMS': ('Capital Group U.S. Multi-Sector Income ETF', 'Renda Fixa'),  # Vol 1.1M
    'CGMU': ('Capital Group Municipal Income ETF', 'Renda Fixa'),  # Vol 1.1M
    'ANGL': ('VanEck Fallen Angel High Yield Bond ETF', 'Renda Fixa'),  # Vol 1.1M
    'DFCF': ('Dimensional Core Fixed Income ETF', 'Renda Fixa'),  # Vol 1.0M
    'EBND': ('SPDR Bloomberg Emerging Markets Local Bond', 'Renda Fixa'),  # Vol 0.6M
    'CGSD': ('Capital Group Short Duration Income ETF', 'Renda Fixa'),  # Vol 0.6M
    'BOND': ('PIMCO Active Bond Exchange-Traded Fund Exc', 'Renda Fixa'),  # Vol 0.6M
    'EVTR': ('Eaton Vance Total Return Bond ETF', 'Renda Fixa'),  # Vol 0.5M
    'CARY': ('Angel Oak Income ETF', 'Renda Fixa'),  # Vol 0.5M
    'DFSD': ('Dimensional Short-Duration Fixed Income ET', 'Renda Fixa'),  # Vol 0.5M
    'CMF': ('iShares California Muni Bond ETF', 'Renda Fixa'),  # Vol 0.5M
    'AMZY': ('YieldMax AMZN Option Income Strategy ETF', 'Renda Fixa'),  # Vol 0.5M
    'CAIE': ('Calamos Autocallable Income ETF', 'Renda Fixa'),  # Vol 0.4M
    'CHPY': ('YieldMax Semiconductor Portfolio Option In', 'Renda Fixa'),  # Vol 0.4M
    'CGHM': ('Capital Group Municipal High-Income ETF', 'Renda Fixa'),  # Vol 0.4M
    'CONY': ('YieldMax COIN Option Income Strategy ETF', 'Renda Fixa'),  # Vol 0.4M
    'EAGG': ('iShares ESG Aware U.S. Aggregate Bond ETF', 'Renda Fixa'),  # Vol 0.4M
    'BUXX': ('Strive Enhanced Income Short Maturity ETF', 'Renda Fixa'),  # Vol 0.3M
    'CSHI': ('NEOS Enhanced Income 1-3 Month T-Bill ETF', 'Renda Fixa'),  # Vol 0.3M
    'EDGF': ('3EDGE Dynamic Fixed Income ETF', 'Renda Fixa'),  # Vol 0.3M
    'BHYB': ('Xtrackers USD High Yield BB-B ex Financial', 'Renda Fixa'),  # Vol 0.3M
    'CGSM': ('Capital Group Short Duration Municipal Inc', 'Renda Fixa'),  # Vol 0.3M
    'BKHY': ('BNY Mellon High Yield ETF', 'Renda Fixa'),  # Vol 0.2M
    'COYY': ('GraniteShares YieldBOOST COIN ETF', 'Renda Fixa'),  # Vol 0.2M
    'APLY': ('YieldMax AAPL Option Income Strategy ETF', 'Renda Fixa'),  # Vol 0.2M
    'FBY': ('YieldMax META Option Income Strategy ETF', 'Renda Fixa'),  # Vol 0.2M
    'AVIG': ('Avantis Core Fixed Income ETF', 'Renda Fixa'),  # Vol 0.2M

    # ── Novos: Commodities ──
    'FENY': ('Fidelity MSCI Energy Index ETF', 'Commodities'),  # Vol 4.9M
    'DBO': ('Invesco DB Oil Fund', 'Commodities'),  # Vol 2.5M
    'BCI': ('abrdn Bloomberg All Commodity Strategy K-1', 'Commodities'),  # Vol 2.2M
    'DBC': ('Invesco DB Commodity Index Tracking Fund', 'Commodities'),  # Vol 1.3M
    'FCG': ('First Trust Natural Gas ETF', 'Commodities'),  # Vol 1.2M
    'CPER': ('United States Copper Index Fund ETV', 'Commodities'),  # Vol 0.9M
    'CEF': ('Sprott Physical Gold and Silver Trust Unit', 'Commodities'),  # Vol 0.8M
    'COMT': ('iShares GSCI Commodity Dynamic Roll Strate', 'Commodities'),  # Vol 0.5M
    'DBB': ('Invesco DB Base Metals Fund', 'Commodities'),  # Vol 0.4M
    'EMLP': ('First Trust North American Energy Infrastr', 'Commodities'),  # Vol 0.3M
    'COPP': ('Sprott Copper Miners ETF', 'Commodities'),  # Vol 0.3M
    'CMDT': ('PIMCO Commodity Strategy Active Exchange-T', 'Commodities'),  # Vol 0.3M

    # ── Novos: Temático ──
    'ARKX': ('ARK Space & Defense Innovation ETF', 'Temático'),  # Vol 0.6M

    # ── Novos: Fator / Smart Beta ──
    'DYNF': ('iShares U.S. Equity Factor Rotation Active', 'Fator / Smart Beta'),  # Vol 8.3M
    'CGGR': ('Capital Group Growth ETF', 'Fator / Smart Beta'),  # Vol 4.3M
    'FELG': ('Fidelity Enhanced Large Cap Growth ETF', 'Fator / Smart Beta'),  # Vol 0.8M
    'FESM': ('Fidelity Enhanced Small Cap ETF', 'Fator / Smart Beta'),  # Vol 0.8M
    'COWG': ('Pacer US Large Cap Cash Cows Growth Leader', 'Fator / Smart Beta'),  # Vol 0.6M
    'DFUV': ('Dimensional US Marketwide Value ETF', 'Fator / Smart Beta'),  # Vol 0.6M
    'FBCG': ('Fidelity Blue Chip Growth ETF', 'Fator / Smart Beta'),  # Vol 0.5M
    'DFAT': ('Dimensional U.S. Targeted Value ETF', 'Fator / Smart Beta'),  # Vol 0.4M
    'BKDV': ('BNY Mellon Dynamic Value ETF', 'Fator / Smart Beta'),  # Vol 0.4M
    'FELV': ('Fidelity Enhanced Large Cap Value ETF', 'Fator / Smart Beta'),  # Vol 0.2M

    # ── Novos: Alavancado / Inverso ──
    'BMNU': ('T-REX 2X Long BMNR Daily Target ETF', 'Alavancado / Inverso'),  # Vol 105.8M
    'CRCG': ('Leverage Shares 2X Long CRCL Daily ETF', 'Alavancado / Inverso'),  # Vol 29.2M
    'BMNG': ('Leverage Shares 2X Long BMNR Daily ETF', 'Alavancado / Inverso'),  # Vol 25.0M
    'CRWG': ('Leverage Shares 2X Long CRWV Daily ETF', 'Alavancado / Inverso'),  # Vol 21.5M
    'ETHU': ('2x Ether ETF', 'Alavancado / Inverso'),  # Vol 7.3M
    'CCUP': ('T-REX 2X Long CRCL Daily Target ETF', 'Alavancado / Inverso'),  # Vol 4.7M
    'DXD': ('ProShares UltraShort Dow30', 'Alavancado / Inverso'),  # Vol 4.4M
    'CRCD': ('T-REX 2X Inverse CRCL Daily Target ETF', 'Alavancado / Inverso'),  # Vol 3.3M
    'ADBG': ('Leverage Shares 2X Long ADBE Daily ETF', 'Alavancado / Inverso'),  # Vol 2.6M
    'BULZ': ('MicroSectors FANG & Innovation 3x Leverage', 'Alavancado / Inverso'),  # Vol 2.3M
    'ETHT': ('ProShares Ultra Ether ETF', 'Alavancado / Inverso'),  # Vol 2.1M
    'ASTX': ('Tradr 2X Long ASTS Daily ETF', 'Alavancado / Inverso'),  # Vol 1.9M
    'CRCA': ('ProShares Ultra CRCL', 'Alavancado / Inverso'),  # Vol 1.8M
    'CWVX': ('Tradr 2X Long CRWV Daily ETF', 'Alavancado / Inverso'),  # Vol 1.8M
    'EOSU': ('T-REX 2X Long EOSE Daily Target ETF', 'Alavancado / Inverso'),  # Vol 1.8M
    'CRWU': ('T-REX 2X Long CRWV Daily Target ETF', 'Alavancado / Inverso'),  # Vol 1.6M
    'CRMG': ('Leverage Shares 2X Long CRM Daily ETF', 'Alavancado / Inverso'),  # Vol 1.5M
    'BMNZ': ('Defiance Daily Target 2X Short BMNR ETF', 'Alavancado / Inverso'),  # Vol 1.5M
    'APLX': ('Tradr 2X Long APLD Daily ETF', 'Alavancado / Inverso'),  # Vol 1.5M
    'CORD': ('T-REX 2X Inverse CRWV Daily Target ETF', 'Alavancado / Inverso'),  # Vol 1.5M
    'AVXX': ('Defiance Daily Target 2x Long AVAV ETF', 'Alavancado / Inverso'),  # Vol 1.4M
    'APPX': ('Tradr 2X Long APP Daily ETF', 'Alavancado / Inverso'),  # Vol 1.2M
    'AVS': ('Direxion Daily AVGO Bear 1X ETF', 'Alavancado / Inverso'),  # Vol 1.2M
    'BSCQ': ('Invesco BulletShares 2026 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 1.0M
    'DUOG': ('Leverage Shares 2X Long DUOL Daily ETF', 'Alavancado / Inverso'),  # Vol 1.0M
    'AVGX': ('Defiance Daily Target 2X Long AVGO ETF', 'Alavancado / Inverso'),  # Vol 1.0M
    'BEX': ('Tradr 2X Long BE Daily ETF', 'Alavancado / Inverso'),  # Vol 0.9M
    'BSCR': ('Invesco BulletShares 2027 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.9M
    'DPST': ('Direxion Daily Regional Banks Bull 3X ETF', 'Alavancado / Inverso'),  # Vol 0.9M
    'BSCS': ('Invesco BulletShares 2028 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.8M
    'BSCT': ('Invesco BulletShares 2029 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.7M
    'DJTU': ('T-REX 2X Long DJT Daily Target ETF', 'Alavancado / Inverso'),  # Vol 0.7M
    'ETHD': ('ProShares UltraShort Ether ETF', 'Alavancado / Inverso'),  # Vol 0.7M
    'BABX': ('GraniteShares 2x Long BABA Daily ETF', 'Alavancado / Inverso'),  # Vol 0.7M
    'DRN': ('Direxion Daily Real Estate Bull 3X ETF', 'Alavancado / Inverso'),  # Vol 0.7M
    'AVL': ('Direxion Daily AVGO Bull 2X ETF', 'Alavancado / Inverso'),  # Vol 0.6M
    'BSCU': ('Invesco BulletShares 2030 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.6M
    'CRDU': ('Tradr 2X Long CRDO Daily ETF', 'Alavancado / Inverso'),  # Vol 0.5M
    'ARMG': ('Leverage Shares 2X Long ARM Daily ETF', 'Alavancado / Inverso'),  # Vol 0.5M
    'CWEB': ('Direxion Daily CSI China Internet Index Bu', 'Alavancado / Inverso'),  # Vol 0.5M
    'BSCV': ('Invesco BulletShares 2031 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.5M
    'BAIG': ('Leverage Shares 2X Long BBAI Daily ETF', 'Alavancado / Inverso'),  # Vol 0.5M
    'BULG': ('Leverage Shares 2X Long BULL Daily ETF', 'Alavancado / Inverso'),  # Vol 0.5M
    'DFEN': ('Direxion Daily Aerospace & Defense Bull 3X', 'Alavancado / Inverso'),  # Vol 0.4M
    'CLSX': ('Tradr 2X Long CLSK Daily ETF', 'Alavancado / Inverso'),  # Vol 0.4M
    'BILZ': ('PIMCO Ultra Short Government Active Exchan', 'Alavancado / Inverso'),  # Vol 0.4M
    'COHX': ('Tradr 2X Long COHR Daily ETF', 'Alavancado / Inverso'),  # Vol 0.3M
    'DDM': ('ProShares Ultra Dow30', 'Alavancado / Inverso'),  # Vol 0.3M
    'BSCW': ('Invesco BulletShares 2032 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.3M
    'CIFU': ('T-REX 2X Long CIFR Daily Target ETF', 'Alavancado / Inverso'),  # Vol 0.3M
    'EDC': ('Direxion Emerging Markets Bull 3X ETF', 'Alavancado / Inverso'),  # Vol 0.3M
    'ASTN': ('Defiance Daily Target 2X Short ASTS ETF', 'Alavancado / Inverso'),  # Vol 0.3M
    'BRKU': ('Direxion Daily BRKB Bull 2X ETF', 'Alavancado / Inverso'),  # Vol 0.3M
    'BSJQ': ('Invesco BulletShares 2026 High Yield Corpo', 'Alavancado / Inverso'),  # Vol 0.2M
    'AVGG': ('Leverage Shares 2X Long AVGO Daily ETF', 'Alavancado / Inverso'),  # Vol 0.2M
    'BKUI': ('BNY Mellon Ultra Short Income ETF', 'Alavancado / Inverso'),  # Vol 0.2M
    'DUSB': ('Dimensional Ultrashort Fixed Income ETF', 'Alavancado / Inverso'),  # Vol 0.2M
    'APLZ': ('Tradr 2X Short APLD Daily ETF', 'Alavancado / Inverso'),  # Vol 0.2M
    'EDZ': ('Direxion Emerging Markets Bear 3X ETF', 'Alavancado / Inverso'),  # Vol 0.2M
    'BSCX': ('Invesco BulletShares 2033 Corporate Bond E', 'Alavancado / Inverso'),  # Vol 0.2M
    'ETU': ('T-Rex 2X Long Ether Daily Target ETF', 'Alavancado / Inverso'),  # Vol 0.2M

}

CATEGORIA_MAP = {tk: v[1] for tk, v in NOMAD_ETFS.items()}
NOME_MAP      = {tk: v[0] for tk, v in NOMAD_ETFS.items()}
PERIODO       = "1y"

# Volume médio 20 dias (fonte: CSV etfs_swing_trade.csv)
ETF_VOL_20D = {
    'AAAU': 2635857,
    'AAPD': 9880705,
    'AAPU': 1746077,
    'AAXJ': 1293142,
    'ACWI': 8288528,
    'ACWX': 3526269,
    'ADBG': 2635414,
    'AGG': 8634610,
    'AGQ': 5537940,
    'AIA': 616403,
    'AIPO': 372506,
    'AIQ': 2578273,
    'AIRR': 734492,
    'AKRE': 946832,
    'ALLW': 1075134,
    'AMDD': 15899600,
    'AMDL': 11196802,
    'AMLP': 1546233,
    'AMZD': 9712306,
    'AMZU': 3946235,
    'AMZY': 462104,
    'AMZZ': 318336,
    'ANGL': 1054634,
    'AOK': 212270,
    'AOR': 485033,
    'APLX': 1489756,
    'APLY': 240252,
    'APLZ': 217844,
    'APPX': 1224684,
    'ARKB': 6507974,
    'ARKF': 301554,
    'ARKG': 2598056,
    'ARKK': 10836831,
    'ARKX': 576451,
    'ARMG': 531371,
    'ARTY': 545574,
    'ASHR': 8721029,
    'ASTN': 271377,
    'ASTX': 1933840,
    'AVDE': 1355313,
    'AVDV': 803658,
    'AVEM': 2440110,
    'AVES': 221927,
    'AVGG': 236785,
    'AVGX': 963875,
    'AVIG': 204773,
    'AVL': 623164,
    'AVLV': 720563,
    'AVS': 1196129,
    'AVUS': 285390,
    'AVUV': 1126303,
    'AVXX': 1404962,
    'BABX': 658666,
    'BAI': 1915664,
    'BAIG': 489202,
    'BALT': 328829,
    'BBAX': 341843,
    'BBCA': 331104,
    'BBEU': 605875,
    'BBJP': 1990775,
    'BBUS': 265708,
    'BCGS': 359607,
    'BCI': 2154715,
    'BDRY': 313580,
    'BDVL': 470243,
    'BDYN': 426351,
    'BEX': 905192,
    'BHYB': 261953,
    'BIL': 8969970,
    'BILS': 495125,
    'BILZ': 359354,
    'BINC': 2957685,
    'BITB': 4234034,
    'BITI': 2426155,
    'BITO': 100809267,
    'BITU': 5480993,
    'BITX': 14353042,
    'BIV': 2161140,
    'BIZD': 4764572,
    'BKDV': 351108,
    'BKHY': 248372,
    'BKLN': 32785451,
    'BKUI': 235662,
    'BLCR': 4093662,
    'BLOK': 388314,
    'BLOX': 257347,
    'BLV': 1060621,
    'BMNG': 24999429,
    'BMNU': 105811636,
    'BMNZ': 1501596,
    'BND': 9196056,
    'BNDX': 5594551,
    'BNO': 5535567,
    'BOIL': 14291803,
    'BOND': 567495,
    'BOTZ': 1047367,
    'BOXX': 1827956,
    'BRKU': 258211,
    'BRRR': 347278,
    'BSCQ': 1017435,
    'BSCR': 904129,
    'BSCS': 845255,
    'BSCT': 689994,
    'BSCU': 589589,
    'BSCV': 505120,
    'BSCW': 288564,
    'BSCX': 204484,
    'BSJQ': 247180,
    'BSOL': 2481920,
    'BSV': 2620931,
    'BTAL': 1124241,
    'BTC': 5917206,
    'BTCI': 517029,
    'BTCZ': 18487679,
    'BUFD': 265316,
    'BUFR': 1391355,
    'BUG': 1589632,
    'BULG': 451563,
    'BULZ': 2340676,
    'BUXX': 346066,
    'BUYW': 424118,
    'BUZZ': 232592,
    'BWX': 1565288,
    'CAIE': 418556,
    'CALF': 996608,
    'CANE': 212929,
    'CARY': 495278,
    'CCUP': 4705919,
    'CEF': 761959,
    'CGBL': 1376647,
    'CGCB': 1489366,
    'CGCP': 1781556,
    'CGCV': 310851,
    'CGDG': 953029,
    'CGDV': 5092073,
    'CGGE': 1088414,
    'CGGO': 1299482,
    'CGGR': 4280186,
    'CGHM': 376910,
    'CGIC': 613091,
    'CGIE': 685578,
    'CGMM': 936616,
    'CGMS': 1066902,
    'CGMU': 1066080,
    'CGNG': 711149,
    'CGSD': 603064,
    'CGSM': 259365,
    'CGUS': 1229435,
    'CGXU': 1167757,
    'CHAT': 323658,
    'CHPY': 397291,
    'CIBR': 1909669,
    'CIFU': 286418,
    'CLIP': 293735,
    'CLOA': 441774,
    'CLOI': 222730,
    'CLOU': 219278,
    'CLOX': 294975,
    'CLOZ': 990011,
    'CLSX': 390824,
    'CMDT': 279741,
    'CMF': 464130,
    'CNEQ': 301232,
    'COHX': 337667,
    'COMT': 534172,
    'CONI': 373939,
    'CONL': 22600996,
    'CONY': 371489,
    'COPP': 287366,
    'COPX': 5058710,
    'CORD': 1468343,
    'CORN': 394991,
    'CORO': 2485446,
    'COWG': 630303,
    'COWZ': 1649897,
    'COYY': 244293,
    'CPER': 860262,
    'CQQQ': 1178642,
    'CRCA': 1844223,
    'CRCD': 3279359,
    'CRCG': 29236096,
    'CRDU': 531599,
    'CRMG': 1514531,
    'CRWG': 21538021,
    'CRWL': 458550,
    'CRWU': 1597463,
    'CSHI': 300941,
    'CTA': 538206,
    'CWB': 942277,
    'CWEB': 518417,
    'CWI': 275303,
    'CWVX': 1783078,
    'DAMD': 273303,
    'DAPP': 529573,
    'DBA': 1063683,
    'DBB': 377068,
    'DBC': 1293959,
    'DBEF': 795730,
    'DBMF': 2082956,
    'DBO': 2458966,
    'DDM': 300067,
    'DEM': 348584,
    'DFAC': 3563157,
    'DFAE': 1312182,
    'DFAI': 2462158,
    'DFAR': 1390056,
    'DFAS': 638912,
    'DFAT': 367584,
    'DFAU': 812299,
    'DFAX': 974689,
    'DFCF': 1020942,
    'DFEM': 1025825,
    'DFEN': 392158,
    'DFEV': 277797,
    'DFGR': 354192,
    'DFIC': 1309728,
    'DFIS': 523820,
    'DFIV': 1649146,
    'DFLV': 1186143,
    'DFSD': 478493,
    'DFSV': 1661341,
    'DFUS': 1156312,
    'DFUV': 553251,
    'DGRO': 2534082,
    'DGRW': 1273411,
    'DIA': 7205585,
    'DIHP': 600144,
    'DISV': 536955,
    'DIV': 324672,
    'DIVI': 286962,
    'DIVO': 869024,
    'DJTU': 670693,
    'DOG': 8578179,
    'DPST': 859868,
    'DRIP': 28519716,
    'DRN': 654420,
    'DTCR': 805389,
    'DUHP': 1581393,
    'DUOG': 969385,
    'DUSB': 219807,
    'DUST': 6021736,
    'DVY': 434252,
    'DVYE': 307837,
    'DXD': 4430656,
    'DXJ': 622319,
    'DYNF': 8322971,
    'EAGG': 357009,
    'EAGL': 391941,
    'EBND': 611237,
    'ECH': 1280723,
    'EDC': 272479,
    'EDGF': 293950,
    'EDIV': 231786,
    'EDV': 1131909,
    'EDZ': 214196,
    'EEM': 51301016,
    'EEMA': 553179,
    'EEMV': 416896,
    'EFA': 27456897,
    'EFAV': 650552,
    'EFG': 4683444,
    'EFV': 3951512,
    'EIDO': 789592,
    'EIS': 221029,
    'EMB': 12284387,
    'EMLC': 5741787,
    'EMLP': 303749,
    'EMXC': 4606172,
    'EOSU': 1764743,
    'EPHE': 232015,
    'EPI': 948869,
    'EPOL': 717822,
    'EPP': 611826,
    'ERX': 736699,
    'ERY': 1079781,
    'ESGD': 466997,
    'ESGE': 1733574,
    'ESGU': 546771,
    'ESGV': 245549,
    'ETH': 7427081,
    'ETHA': 37222347,
    'ETHB': 1736576,
    'ETHD': 659283,
    'ETHE': 5083308,
    'ETHT': 2082925,
    'ETHU': 7323269,
    'ETHV': 202799,
    'ETHW': 1693151,
    'ETU': 200567,
    'EUAD': 600463,
    'EUFN': 2665762,
    'EVTR': 540190,
    'EWA': 6593594,
    'EWC': 3263381,
    'EWG': 2211615,
    'EWH': 7017894,
    'EWI': 620499,
    'EWJ': 12839383,
    'EWJV': 308167,
    'EWL': 789294,
    'EWM': 517145,
    'EWP': 677435,
    'EWQ': 480979,
    'EWS': 1116554,
    'EWT': 7795892,
    'EWU': 2518379,
    'EWW': 2401638,
    'EWY': 31145013,
    'EWZ': 41100970,
    'EWZS': 999594,
    'EZA': 377968,
    'EZBC': 246786,
    'EZU': 2224336,
    'FALN': 1173086,
    'FAS': 1128426,
    'FAZ': 1118165,
    'FBCG': 489818,
    'FBL': 1026181,
    'FBND': 2961870,
    'FBTC': 5811354,
    'FBY': 208944,
    'FCG': 1237731,
    'FDD': 337973,
    'FDL': 1281767,
    'FDN': 916533,
    'FDVV': 1079502,
    'FEGE': 452076,
    'FELC': 1232084,
    'FELG': 827938,
    'FELV': 216486,
    'FENI': 1924976,
    'FENY': 4895094,
    'FEOE': 340854,
    'FESM': 751075,
    'FETH': 6474810,
    'FEZ': 2591064,
}

def get_liquidez_score(ticker, vol_yf=0):
    """Score 0-10 baseado no volume médio 20d do CSV. Fallback: yfinance."""
    vol = ETF_VOL_20D.get(ticker, vol_yf or 0)
    if   vol >= 50_000_000: return 10
    elif vol >= 20_000_000: return 9
    elif vol >= 10_000_000: return 8
    elif vol >=  5_000_000: return 7
    elif vol >=  2_000_000: return 6
    elif vol >=  1_000_000: return 5
    elif vol >=    500_000: return 4
    elif vol >=    100_000: return 3
    elif vol >=     50_000: return 2
    elif vol >           0: return 1
    return 1  # unknown — assume low


# =============================================================================
# EXPENSE RATIOS HARDCODED (yfinance não retorna esse campo de forma confiável)
# Fonte: sites oficiais dos fundos — atualizado 2025
# =============================================================================
ETF_EXPENSE_RATIO = {
    # Amplos EUA
    'SPY':0.0945,'VOO':0.03,'IVV':0.03,'QQQ':0.20,'QQQM':0.15,'VTI':0.03,
    'SCHB':0.03,'ITOT':0.03,'IWM':0.19,'IWV':0.20,'DIA':0.16,'MDY':0.23,
    'IJH':0.05,'IJR':0.06,'VB':0.05,'VO':0.04,'VV':0.04,'SCHX':0.03,
    'SCHA':0.04,'SCHM':0.04,'OEF':0.20,'RSP':0.20,
    # Setoriais SPDR
    'XLK':0.09,'XLF':0.09,'XLE':0.09,'XLV':0.09,'XLI':0.09,'XLB':0.09,
    'XLY':0.09,'XLP':0.09,'XLRE':0.09,'XLU':0.09,'XLC':0.09,
    # Vanguard setoriais
    'VGT':0.10,'VHT':0.10,'VFH':0.10,'VDE':0.10,'VAW':0.10,'VIS':0.10,
    'VCR':0.10,'VDC':0.10,'VOX':0.10,'VPU':0.10,'VNQ':0.12,
    # iShares setoriais
    'IYW':0.39,'IYF':0.39,'IYE':0.39,'IYH':0.39,'IYJ':0.39,'IYR':0.39,
    'IYC':0.39,'IYK':0.39,'IDU':0.39,
    # Financeiro / Bancos
    'KBWB':0.35,'KRE':0.35,'KBE':0.35,'IAI':0.39,
    # Saúde / Biotech
    'XBI':0.35,'IBB':0.44,'IHI':0.39,'IHF':0.39,'XPH':0.35,
    # Energia
    'XES':0.35,'XOP':0.35,'OIH':0.35,
    # Industrial / Defesa / Aéreo
    'JETS':0.60,'ITA':0.39,'PPA':0.58,
    # Imobiliário
    'XHB':0.35,'ITB':0.39,'SCHH':0.07,'REM':0.47,
    # Consumo
    'XRT':0.35,
    # Tech & IA
    'SOXX':0.35,'SMH':0.35,'SOXQ':0.19,'CIBR':0.60,'BUG':0.50,'HACK':0.60,
    'CLOU':0.68,'SKYY':0.60,'WCLD':0.45,'BOTZ':0.68,'ROBO':0.95,'AIQ':0.68,
    'ARKK':0.75,'ARKW':0.75,'ARKQ':0.75,'ARKF':0.75,'ARKG':0.75,
    'QQEW':0.58,'BKCH':0.50,'DRIV':0.68,'IDAT':0.47,'IGPT':0.35,'CHAT':0.75,
    # Cripto & Fintech
    'IBIT':0.25,'FBTC':0.25,'BITB':0.20,'ARKB':0.21,'HODL':0.20,'BRRR':0.25,
    'ETHA':0.25,'FETH':0.25,'GBTC':1.50,'BITO':0.95,'FINX':0.68,'BLOK':0.76,
    # Energia Limpa / ESG
    'ICLN':0.41,'QCLN':0.58,'TAN':0.69,'FAN':0.60,'ACES':0.55,'CNRG':0.45,
    'ESGU':0.15,'ESGE':0.25,'ESGD':0.20,'SNPE':0.10,'SUSL':0.10,
    # Internacional Desenvolvidos
    'EFA':0.32,'VEA':0.06,'SCHF':0.06,'IEFA':0.07,'EWJ':0.49,'EWG':0.49,
    'EWU':0.49,'EWL':0.49,'EWQ':0.49,'EWI':0.49,'EWP':0.49,'EWD':0.49,
    'EWN':0.49,'EWA':0.49,'EWC':0.49,'EWH':0.49,'EWS':0.49,'BBJP':0.19,
    'BBEU':0.09,'ACWX':0.32,'ACWI':0.32,'URTH':0.24,
    # Emergentes
    'EEM':0.70,'VWO':0.08,'IEMG':0.09,'SCHE':0.11,'FXI':0.74,'MCHI':0.59,
    'KWEB':0.76,'EWZ':0.59,'EWT':0.57,'EWY':0.57,'INDA':0.65,'INDY':0.90,
    'SMIN':0.74,'EWW':0.49,'ECH':0.57,'ILF':0.47,'GXG':0.57,'ARGT':0.59,
    'EZA':0.59,'EPHE':0.59,'THD':0.59,'EWM':0.49,'TUR':0.57,'EPOL':0.59,
    'GEM':0.45,
    # Dividendos
    'SCHD':0.06,'VIG':0.06,'VYM':0.06,'HDV':0.08,'DVY':0.38,'SDY':0.35,
    'NOBL':0.35,'DGRO':0.08,'DIVO':0.55,'SPHD':0.30,'SPYD':0.07,
    'JEPI':0.35,'JEPQ':0.35,'QYLD':0.61,'XYLD':0.60,'RYLD':0.60,
    'DGRW':0.28,'PFF':0.46,'PGX':0.52,
    # Renda Fixa
    'TLT':0.15,'TLH':0.15,'IEF':0.15,'IEI':0.15,'SHY':0.15,'SHV':0.15,
    'SGOV':0.05,'BIL':0.14,'USFR':0.15,'TFLO':0.15,
    'AGG':0.03,'BND':0.03,'SCHZ':0.03,'LQD':0.14,'VCIT':0.04,'VCSH':0.04,
    'VCLT':0.04,'HYG':0.49,'JNK':0.40,'FALN':0.25,'TIP':0.19,'SCHP':0.04,
    'STIP':0.03,'MBB':0.04,'EMB':0.39,'VWOB':0.20,'PCY':0.50,'BWX':0.35,
    'IGOV':0.35,'BNDX':0.07,'FLRN':0.15,'SPTI':0.06,'SPTS':0.03,'SPTL':0.06,
    'GOVT':0.05,'VGSH':0.04,'VGIT':0.04,'VGLT':0.04,'BSV':0.04,'BIV':0.04,
    'BLV':0.04,'IGSB':0.06,'IGIB':0.06,'IGLB':0.06,'USHY':0.08,'SHYG':0.30,
    'HYLB':0.05,'SJNK':0.40,'HYSA':0.29,
    # Commodities
    'GLD':0.40,'IAU':0.25,'GLDM':0.10,'BAR':0.17,'AAAU':0.18,'SLV':0.50,
    'SIVR':0.30,'PPLT':0.60,'PALL':0.60,'COPX':0.65,'URA':0.69,'LIT':0.75,
    'REMX':0.56,'SIL':0.65,'GDX':0.51,'GDXJ':0.52,'RING':0.39,'USO':0.73,
    'BNO':0.90,'UNG':0.60,'BOIL':1.21,'PDBC':0.59,'GSG':0.75,'DJP':0.75,
    'CORN':0.20,'WEAT':0.28,'SOYB':0.22,'CANE':0.28,
    # Temáticos
    'PAVE':0.47,'BETZ':0.45,'HERO':0.50,'ESPO':0.55,'SOCL':0.65,'AWAY':0.75,
    'NERD':0.50,'POTX':0.50,'MJ':0.75,'MSOS':0.74,'GNOM':0.50,'EDUT':0.50,
    'PINK':0.75,'NANC':0.75,'KRUZ':0.75,'DSPY':0.55,'SHLD':0.50,'PRNT':0.66,
    'LNGR':0.50,'SNSR':0.68,'CTEC':0.50,'BATT':0.59,'NXTG':0.70,'FIVG':0.30,
    'UFO':0.75,'ROKT':0.45,'MOO':0.53,'DIET':0.50,
    # Fator / Smart Beta
    'QUAL':0.15,'MTUM':0.15,'VLUE':0.15,'SIZE':0.15,'USMV':0.15,'ACWV':0.20,
    'EFAV':0.20,'EEMV':0.25,'SPLV':0.25,'SPHQ':0.15,'PRF':0.39,'COWZ':0.49,
    'CALF':0.59,'VFMO':0.13,'VFMV':0.13,'VFQY':0.13,'VFVA':0.13,
    'DFLV':0.22,'DFSV':0.31,'DFAC':0.19,'DFAS':0.26,'AVUV':0.25,'AVLV':0.15,
    'AVDV':0.36,'AVES':0.36,'XSVM':0.36,'QVAL':0.49,
    # Alavancados
    'TQQQ':0.95,'SQQQ':0.95,'QLD':0.95,'QID':0.95,'UPRO':0.92,'SPXU':0.91,
    'SSO':0.90,'SDS':0.89,'SPXL':0.91,'SPXS':0.91,'SOXL':0.97,'SOXS':0.97,
    'TECL':0.94,'TECS':0.94,'FAS':0.94,'FAZ':0.94,'TNA':0.94,'TZA':0.94,
    'LABU':0.94,'LABD':0.94,'NAIL':0.97,'CURE':0.97,'NUGT':1.24,'DUST':1.24,
    'GUSH':0.97,'DRIP':0.97,'ERX':0.97,'ERY':0.97,'TMF':1.06,'TMV':1.06,
    'TBT':0.90,'UBT':0.95,'SH':0.89,'PSQ':0.95,'DOG':0.95,'RWM':0.95,
    'UVXY':0.95,'SVXY':0.95,'VXX':0.89,'BITI':0.95,'UGL':0.95,'GLL':0.95,
    'AGQ':0.95,'ZSL':0.95,
    # Multi-Asset
    'AOR':0.15,'AOM':0.15,'AOA':0.15,'AOK':0.15,'GAL':0.25,'MDIV':0.68,
    'RPAR':0.23,'GDE':0.20,'NTSX':0.20,'SWAN':0.49,
}

# =============================================================================
# DESCRIÇÕES DETALHADAS DOS ETFs
# =============================================================================

# =============================================================================
# PROSPECTOS RESUMIDOS DOS ETFs
# Cada entrada: {'estrategia': str, 'composicao': str, 'riscos': str, 'resumo': str}
# =============================================================================
ETF_PROSPECTO = {

    # ── Amplos EUA ─────────────────────────────────────────────────────────────
    'SPY': {
        'resumo': 'O ETF mais negociado do mundo. Replica o S&P 500 — referência global de performance do mercado americano.',
        'estrategia': 'Replica passivamente o índice S&P 500, que representa as 500 maiores empresas americanas por capitalização de mercado. Rebalanceamento trimestral. Metodologia full replication — compra todas as ações do índice nas proporções exatas.',
        'composicao': 'Top 10 (~35% do fundo): Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet A/C, Berkshire Hathaway, Eli Lilly, JPMorgan. Setores dominantes: Tecnologia (~30%), Saúde (~13%), Financeiro (~13%), Consumo Discricionário (~11%). Total: 500 empresas.',
        'riscos': 'Alta concentração em Big Tech (~30%). Risco de mercado geral americano. Câmbio USD/BRL para investidores brasileiros. Pouca proteção em quedas do mercado — cai junto com o S&P 500.',
    },
    'VOO': {
        'resumo': 'Versão Vanguard do S&P 500 com custo ultra-baixo (0.03%/ano). Ideal para buy & hold de longo prazo.',
        'estrategia': 'Mesma metodologia do SPY: replica passivamente o S&P 500. Diferencial: custo 3x menor que o SPY (0.03% vs 0.09%). A Vanguard é uma cooperativa de fundos — os cotistas são os donos da gestora, o que alinha interesses e reduz taxas.',
        'composicao': 'Idêntica ao SPY: 500 maiores empresas americanas ponderadas por valor de mercado. Top holdings: Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet. Tecnologia ~30%, Saúde ~13%, Financeiro ~13%.',
        'riscos': 'Mesmos riscos do S&P 500. Concentração em mega-caps tech. Risco cambial USD/BRL. Para investidores de longo prazo, o principal risco é não ter disciplina para manter durante quedas.',
    },
    'QQQ': {
        'resumo': 'Replica o Nasdaq 100 — as 100 maiores empresas não-financeiras da Nasdaq. Alta exposição a tecnologia e crescimento.',
        'estrategia': 'Replica o Nasdaq-100 Index, que seleciona as 100 maiores empresas não-financeiras listadas na Nasdaq por capitalização de mercado. Exclui bancos e seguros. Rebalanceado anualmente. Muito mais concentrado em tech que o S&P 500.',
        'composicao': 'Top 10 (~50% do fundo): Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet, Tesla, Broadcom, Costco, AMD. Tecnologia (~60%), Consumo Discricionário (~15%), Saúde (~7%). Total: 100 empresas.',
        'riscos': 'Alta concentração — 10 empresas respondem por ~50% do fundo. Beta maior que 1: cai mais que o S&P 500 em bear markets. Sem exposição a setor financeiro. Muito sensível a taxas de juros (empresas growth sofrem mais com juros altos).',
    },
    'VTI': {
        'resumo': 'Cobre o mercado americano inteiro — mais de 3.600 ações (large, mid e small caps). Diversificação máxima.',
        'estrategia': 'Replica o CRSP US Total Market Index, que engloba praticamente todas as ações listadas nos EUA (~3.600 empresas). Inclui large caps, mid caps e small caps. A exposição a small caps (~9%) diferencia do S&P 500.',
        'composicao': 'Large caps (~72%), Mid caps (~19%), Small caps (~9%). Top holdings similares ao VOO, mas com maior diversificação. Tecnologia (~30%), Saúde (~13%), Financeiro (~13%), Industriais (~13%).',
        'riscos': 'Risco do mercado americano total. Small caps aumentam a volatilidade vs S&P 500 puro. Risco cambial. A diversificação extra vs VOO é marginal — correlação de ~0.99 com o S&P 500.',
    },
    'IWM': {
        'resumo': 'Principal ETF de small caps americanas (Russell 2000). Mais cíclico e volátil — tende a liderar em recuperações.',
        'estrategia': 'Replica o Russell 2000 Index, formado pelas 2.000 menores empresas do Russell 3000 (excluindo as 1.000 maiores). Empresas com market cap entre ~$300M e ~$2B. Rebalanceamento anual em junho.',
        'composicao': '~2.000 empresas de pequeno porte. Setores: Financeiro (~16%), Saúde (~15%), Industrial (~15%), Tecnologia (~13%), Consumo Discricionário (~11%). Maior diversificação setorial que large caps. Menos exposição a Big Tech.',
        'riscos': 'Alta volatilidade (~30-40% a mais que S&P 500). Menor liquidez das empresas componentes. Mais sensível ao ciclo econômico e crédito. Muitas empresas sem lucro consistente. Sofre mais em recessões e crises de crédito.',
    },
    'RSP': {
        'resumo': 'S&P 500 com pesos iguais — cada ação vale ~0.2%. Evita superponderação em mega-caps, historicamente supera no longo prazo.',
        'estrategia': 'Replica o S&P 500 Equal Weight Index. Ao contrário do SPY (ponderado por cap), cada uma das 500 ações recebe o mesmo peso (~0.2%). Rebalanceamento trimestral restaura os pesos iguais, forçando "comprar barato / vender caro" sistematicamente.',
        'composicao': 'As mesmas 500 empresas do S&P 500, mas com pesos iguais. Isso reduz a concentração em Apple/Microsoft/Nvidia de ~20% para ~0.6%. Maior exposição relativa a industriais, materiais e empresas menores do índice.',
        'riscos': 'Maior turnover = maior custo de transação implícito. Underperforma em bull markets dominados por mega-caps tech. Mais sensível ao ciclo econômico. Expense ratio de 0.20% vs 0.03% do VOO.',
    },

    # ── Setoriais ──────────────────────────────────────────────────────────────
    'XLK': {
        'resumo': 'Maior ETF de tecnologia dos EUA. Concentrado em Apple, Microsoft e Nvidia. Lidera em bull markets, cai mais em correções.',
        'estrategia': 'Replica o Technology Select Sector Index — ações do setor de tecnologia do S&P 500. Inclui semiconductores, software, hardware, serviços de TI e equipamentos. Rebalanceado trimestralmente.',
        'composicao': 'Top 3 respondem por ~47% do fundo: Apple (~20%), Microsoft (~19%), Nvidia (~8%). Outros: Broadcom, Salesforce, Oracle, AMD, Qualcomm, Texas Instruments, Applied Materials. Total: ~65 empresas.',
        'riscos': 'Extrema concentração — 3 empresas = quase metade do fundo. Beta ~1.2 vs S&P 500. Muito sensível a juros (empresas growth descontadas a taxas futuras). Risco regulatório de Big Tech. Valuation historicamente elevado.',
    },
    'XLF': {
        'resumo': 'Setor financeiro americano: bancos, seguros, gestoras de ativos. Beneficia de juros altos e curva positiva.',
        'estrategia': 'Replica o Financial Select Sector Index. Inclui bancos, seguradoras, gestoras de ativos, REITs de hipoteca e serviços financeiros do S&P 500. Sensível ao ciclo econômico e política monetária.',
        'composicao': 'Berkshire Hathaway (~13%), JPMorgan (~10%), Visa (~8%), Mastercard (~7%), Bank of America (~4%), Wells Fargo (~4%), Goldman Sachs (~3%), Morgan Stanley (~3%). ~70 empresas.',
        'riscos': 'Risco de crédito sistêmico (crises bancárias). Muito sensível à curva de juros — inversão penaliza margens bancárias. Risco regulatório crescente. Exposição a ciclos de crédito. Sofre muito em recessões.',
    },
    'XLE': {
        'resumo': 'Energia americana: petróleo, gás e serviços energéticos. Hedge natural contra inflação. Correlacionado ao preço do crude.',
        'estrategia': 'Replica o Energy Select Sector Index. Inclui empresas de exploração, produção, refino, transporte e serviços de energia do S&P 500. Dividendos históricos elevados.',
        'composicao': 'ExxonMobil (~23%), Chevron (~17%), ConocoPhillips (~8%), EOG Resources (~5%), Schlumberger (~5%), Pioneer Natural Resources, Marathon Petroleum, Phillips 66. ~25 empresas.',
        'riscos': 'Alta correlação ao preço do petróleo WTI. Risco de transição energética (longo prazo). Sensível a decisões da OPEP. Volatilidade em crises (COVID: petróleo negativo). Risco geopolítico. Regulação ambiental crescente.',
    },
    'XLV': {
        'resumo': 'Saúde americana: farmacêuticas, planos de saúde e devices médicos. Setor defensivo com crescimento secular.',
        'estrategia': 'Replica o Health Care Select Sector Index. Inclui farmacêuticas, biotecnologia, dispositivos médicos, planos de saúde e serviços de saúde do S&P 500. Considerado defensivo — demanda relativamente estável.',
        'composicao': 'Eli Lilly (~13%), UnitedHealth (~11%), Johnson & Johnson (~7%), AbbVie (~6%), Merck (~5%), Thermo Fisher (~4%), Abbott, Danaher, Boston Scientific. ~65 empresas.',
        'riscos': 'Risco regulatório e político (negociação de preços de medicamentos). Risco de patentes (cliffs de expiração). Ensaios clínicos podem fracassar. Pressão de margens em planos de saúde. Risco de reform de healthcare.',
    },
    'XLU': {
        'resumo': 'Utilities: energia elétrica, gás e água. O setor mais defensivo. Dividendos altos e estáveis. Inversamente correlacionado a juros.',
        'estrategia': 'Replica o Utilities Select Sector Index. Empresas reguladas de energia elétrica, gás natural, água e energia renovável. Receitas previsíveis por regulação governamental. Classificado como setor "bond proxy" — se comporta como renda fixa.',
        'composicao': 'NextEra Energy (~16%), Southern Company (~7%), Duke Energy (~7%), Sempra (~5%), Consolidated Edison (~4%), American Electric Power (~4%). ~30 empresas predominantemente de geração/distribuição elétrica.',
        'riscos': 'Inversamente correlacionado a taxas de juros — sobe quando juros caem, sofre com altas. Alta alavancagem (infraestrutura intensiva em capital). Transição para renováveis exige capex massivo. Risco regulatório de tarifas.',
    },
    'XLY': {
        'resumo': 'Consumo discricionário: varejo, automóveis, restaurantes, hotéis. Setor cíclico — reflete a confiança do consumidor americano.',
        'estrategia': 'Replica o Consumer Discretionary Select Sector Index. Empresas cujos produtos/serviços são compras não-essenciais. Alta sensibilidade ao ciclo econômico, emprego e confiança do consumidor.',
        'composicao': 'Amazon (~24%), Tesla (~15%), Home Depot (~9%), McDonald\'s (~4%), Lowe\'s (~4%), Nike (~3%), Starbucks (~3%), Booking Holdings. ~55 empresas. Amazon e Tesla respondem por ~40% do índice.',
        'riscos': 'Alta concentração em Amazon e Tesla. Muito cíclico — sofre muito em recessões. Sensível ao crédito ao consumidor e desemprego. Amazon distorce o índice pois é também tech/cloud. Tesla adiciona beta extremo.',
    },
    'XLP': {
        'resumo': 'Consumo básico: alimentos, bebidas, higiene. Setor defensivo que resiste bem em recessões. Dividendos estáveis.',
        'estrategia': 'Replica o Consumer Staples Select Sector Index. Empresas de bens essenciais do dia a dia — alimentação, bebidas, tabaco, higiene e supermercados. Demanda relativamente inelástica ao ciclo econômico.',
        'composicao': 'Procter & Gamble (~15%), Costco (~12%), Walmart (~11%), Coca-Cola (~10%), PepsiCo (~9%), Mondelez (~4%), Colgate, General Mills, Kimberly-Clark. ~35 empresas de marcas globais reconhecidas.',
        'riscos': 'Crescimento lento — não lidera em bull markets. Sensível a altas de custos (matérias-primas, energia, logística). Concorrência de marcas próprias. Risco cambial para receitas globais. Juros altos reduzem atratividade vs renda fixa.',
    },
    'XLRE': {
        'resumo': 'REITs americanos: shopping centers, galpões, data centers, torres de celular. Renda via dividendos. Sensível a juros.',
        'estrategia': 'Replica o Real Estate Select Sector Index. Inclui REITs (Real Estate Investment Trusts) do S&P 500 — obrigados por lei a distribuir 90%+ de sua renda tributável como dividendos. Exclui REITs hipotecários.',
        'composicao': 'Prologis (logística, ~13%), American Tower (torres celular, ~9%), Equinix (data centers, ~8%), Crown Castle, Public Storage, Simon Property Group, Digital Realty, Welltower. ~30 REITs diversificados.',
        'riscos': 'Altamente sensível a taxas de juros (dívida cara + competição com renda fixa). Alta alavancagem estrutural. Risco de vacância (escritórios sofreram muito pós-COVID). Risco de ciclo imobiliário. Setores específicos: e-commerce afeta varejo físico.',
    },
    'VNQ': {
        'resumo': 'REITs via Vanguard. Mais amplo e diversificado que XLRE, com custo baixo. Renda + valorização imobiliária.',
        'estrategia': 'Replica o MSCI US Investable Market Real Estate 25/50 Index. Inclui REITs de todas as capitalizações (não só do S&P 500 como o XLRE). Maior diversificação com ~160 REITs vs ~30 do XLRE.',
        'composicao': 'Prologis, Equinix, American Tower, Public Storage, Welltower, Simon Property, Crown Castle, Digital Realty, Alexandria Real Estate. Residencial, comercial, industrial, data centers, saúde, especializados.',
        'riscos': 'Mesmos riscos estruturais de REITs: sensibilidade a juros, alavancagem, ciclo imobiliário. Maior exposição a REITs menores e mid caps que podem ser menos líquidos.',
    },

    # ── Tecnologia & IA ────────────────────────────────────────────────────────
    'SOXX': {
        'resumo': 'Semicondutores via iShares. Inclui fabricantes, designers e equipamentos de chips. Altíssima volatilidade e retorno.',
        'estrategia': 'Replica o ICE Semiconductor Index. Inclui as 30 maiores empresas do ecossistema de semicondutores: design de chips, fabricação (foundries), equipamentos de litografia e testes. Setor considerado "commodities do século XXI".',
        'composicao': 'Broadcom (~8%), Nvidia (~8%), AMD (~8%), Intel (~5%), Qualcomm (~5%), Texas Instruments (~5%), Applied Materials (~5%), ASML (~5%), KLA (~5%), Lam Research (~5%). 30 empresas do ecossistema de chips.',
        'riscos': 'Extremamente cíclico — ciclos de inventário causam quedas de 50%+. Risco geopolítico Taiwan (TSMC). Concentração geográfica da produção. Capex massivo para novas fábricas. Risco de substituição tecnológica.',
    },
    'SMH': {
        'resumo': 'Semicondutores via VanEck. Mais concentrado nas top 25, com maior peso em TSMC. Diferente do SOXX na composição.',
        'estrategia': 'Replica o MVIS US Listed Semiconductor 25 Index. Seleciona as 25 maiores e mais líquidas empresas de semicondutores listadas nos EUA (incluindo ADRs como TSMC e ASML). Ponderação por capitalização com teto de 20%.',
        'composicao': 'TSMC (~14%), Nvidia (~12%), ASML (~7%), Broadcom (~6%), AMD (~6%), Qualcomm (~5%), Texas Instruments (~5%), Applied Materials (~5%), Intel (~4%), KLA (~4%). Inclui líderes globais via ADR.',
        'riscos': 'Maior concentração em TSMC (risco geopolítico Taiwan direto). Dependência de cadeia de suprimentos global. Ciclicidade da demanda por chips. Risco de sanções a empresas chinesas componentes.',
    },
    'ARKK': {
        'resumo': 'ETF flagship da Cathie Wood. Aposta em tecnologias disruptivas: IA, biotech, fintech, cripto. Altíssima volatilidade.',
        'estrategia': 'Gestão ativa — a equipe da ARK seleciona empresas com potencial de crescimento exponencial em 5 anos. Foco em inovação disruptiva: IA, edição genética, robótica, blockchain, armazenamento de energia. Concentrado: ~25-35 posições.',
        'composicao': 'Tesla, Coinbase, Roku, UiPath, Zoom, CRISPR Therapeutics, Pacific Biosciences, Twist Bioscience, Exact Sciences. Portfólio volátil — muda frequentemente baseado nas convicções da ARK.',
        'riscos': 'Gestão ativa com track record controverso (caiu ~75% em 2022). Empresas growth sem lucro atual. Beta muito alto. Alta concentração em empresas especulativas. Custo elevado (0.75%). Risco de saídas em massa (vicious cycle em quedas).',
    },
    'CIBR': {
        'resumo': 'Cibersegurança via First Trust. Setor de crescimento secular — gastos com segurança digital só aumentam independente do ciclo.',
        'estrategia': 'Replica o Nasdaq CEA Cybersecurity Index. Seleciona empresas diretamente envolvidas em proteger redes, sistemas e dados: firewall, endpoint security, cloud security, identity management, threat intelligence.',
        'composicao': 'Palo Alto Networks (~11%), CrowdStrike (~10%), Fortinet (~9%), Zscaler (~7%), Gen Digital (~6%), Broadcom (~6%), Cisco (~5%), Qualys, Rapid7, Varonis. ~40 empresas puras de cybersecurity.',
        'riscos': 'Valuation elevado (empresas SaaS de crescimento). Sensível a taxas de juros. Risco de consolidação do setor (M&A). Concorrência crescente com Microsoft e Google entrando no espaço. Ciclos de gastos corporativos.',
    },

    # ── Cripto & Fintech ───────────────────────────────────────────────────────
    'IBIT': {
        'resumo': 'Bitcoin spot ETF da BlackRock. O maior e mais líquido ETF de Bitcoin do mundo. Exposição direta ao preço do BTC.',
        'estrategia': 'Detém Bitcoin físico custodiado pela Coinbase. Cada cota representa uma fração de Bitcoin real. Aprovado pela SEC em janeiro de 2024. A BlackRock é o maior gestor de ativos do mundo (~$10T em AUM), trazendo credibilidade institucional.',
        'composicao': '100% Bitcoin físico. Sem derivativos, sem alavancagem. A BlackRock contrata a Coinbase como custodiante. Auditoria regular do Bitcoin detido. NAV calculado diariamente com base no preço spot do BTC.',
        'riscos': 'Volatilidade extrema do Bitcoin (pode cair 50-80% em bear markets). Risco regulatório (reversão de aprovação da SEC). Risco de custódia (Coinbase como ponto único de falha). Risco de hacking no protocolo Bitcoin. Risco de mercado 24/7.',
    },
    'FBTC': {
        'resumo': 'Bitcoin spot ETF da Fidelity. Diferencial: a própria Fidelity custodia o Bitcoin, sem terceirização.',
        'estrategia': 'Similar ao IBIT mas com custódia própria — a Fidelity Digital Assets faz a guarda do Bitcoin internamente, diferentemente dos concorrentes que terceirizam para Coinbase. A Fidelity opera no espaço de cripto desde 2018.',
        'composicao': '100% Bitcoin físico custodiado pela Fidelity Digital Assets. Mesmo conceito do IBIT com a vantagem da custódia integrada. Sem derivativos ou estratégias de hedge.',
        'riscos': 'Mesmos riscos de volatilidade do Bitcoin. Risco de custódia concentrado na Fidelity Digital Assets. Risco regulatório. A custódia própria é tanto vantagem (menos intermediários) quanto risco (concentração).',
    },
    'GBTC': {
        'resumo': 'O mais antigo veículo de Bitcoin listado (2013). Convertido para ETF em 2024. Custo alto (1.50%) penaliza retorno vs BTC.',
        'estrategia': 'Originalmente um trust fechado que negociava com desconto/prêmio ao NAV por anos. Convertido para ETF spot em janeiro de 2024 após decisão judicial contra a SEC. Gerido pela Grayscale Investments.',
        'composicao': '100% Bitcoin físico. Maior carência de saída vs concorrentes mais baratos — investidores têm migrado para IBIT e FBTC por custos menores. Ainda detém bilhões em Bitcoin.',
        'riscos': 'Custo 6x maior que IBIT (1.50% vs 0.25%) corrói retorno significativamente. Mesmos riscos de BTC. Risco de saída de capital para concorrentes mais baratos (pressão vendedora estrutural). Historicamente negociou com descontos enormes.',
    },
    'BITO': {
        'resumo': 'Primeiro ETF de Bitcoin nos EUA (2021), mas baseado em FUTUROS — não em Bitcoin spot. Custo de roll corrói retorno.',
        'estrategia': 'Investe em contratos futuros de Bitcoin na CME (Chicago Mercantile Exchange), não em Bitcoin real. Quando os contratos vencem, precisa "rolar" para o mês seguinte. Em mercados em contango (normal), esse roll tem custo.',
        'composicao': 'Contratos futuros de Bitcoin na CME. Mantém cash/Treasuries para margem. Sem Bitcoin físico. O retorno difere do BTC real pelo custo de roll (pode ser -5 a -20% ao ano em mercados normais).',
        'riscos': 'Custo de roll pode ser enorme em mercados aquecidos. Não replica o preço spot do BTC fielmente. Com ETFs spot aprovados (IBIT, FBTC), perdeu parte da razão de existir. Custo de 0.95% + custo de roll = retorno muito abaixo do BTC real.',
    },

    # ── Energia Limpa / ESG ────────────────────────────────────────────────────
    'ICLN': {
        'resumo': 'Energia limpa global: solar, eólica, hidráulica. Beneficia da transição energética. Sensível a juros e subsídios.',
        'estrategia': 'Replica o S&P Global Clean Energy Index. Seleciona empresas globais de geração de energia limpa e fornecedores de tecnologia/equipamentos para energia renovável. Rebalanceamento semestral. Exposição diversificada geograficamente.',
        'composicao': 'Enphase Energy, Vestas Wind, First Solar, SolarEdge, Orsted, Solaria Energía, EDP Renováveis, Plug Power. Mix de solar (~40%), eólica (~25%), outros renováveis (~35%). Cerca de 100 empresas globais.',
        'riscos': 'Muito sensível a taxas de juros (projetos intensivos em capital). Dependência de subsídios governamentais (IRA nos EUA, políticas europeias). Alta volatilidade. Concorrência com energia fóssil quando petróleo barato. Risco de execução de projetos.',
    },
    'TAN': {
        'resumo': 'Energia solar pura. Alta volatilidade — sobe muito quando subsídios aumentam, cai quando juros sobem ou políticas mudam.',
        'estrategia': 'Replica o MAC Global Solar Energy Index. Foca exclusivamente em empresas de energia solar: fabricantes de painéis fotovoltaicos, inversores, instaladores residenciais/comerciais e desenvolvedores de projetos solares.',
        'composicao': 'Enphase Energy (~12%), First Solar (~11%), SolarEdge (~8%), Sunrun (~6%), Shoals Technologies (~5%), Array Technologies, Canadian Solar, Daqo New Energy. ~25-30 empresas de solar puro.',
        'riscos': 'Concentração extrema em solar — muito sensível ao setor. Concorrência de fabricantes chineses de painéis. Risco de reversão de política (IRA, subsídios). Alta correlação a taxas de juros. Empresas pequenas com histórico de execução volátil.',
    },

    # ── Internacional ──────────────────────────────────────────────────────────
    'EFA': {
        'resumo': 'Mercados desenvolvidos ex-EUA: Europa, Japão, Austrália. Principal ETF de diversificação internacional fora dos EUA.',
        'estrategia': 'Replica o MSCI EAFE Index (Europe, Australasia, Far East). Cobre ~750 empresas de 21 países desenvolvidos excluindo EUA e Canadá. Ponderado por capitalização de mercado. Rebalanceamento trimestral.',
        'composicao': 'Japão (~24%), Reino Unido (~14%), França (~11%), Suíça (~10%), Alemanha (~9%), Austrália (~7%), Países Baixos (~5%). Top empresas: Nestlé, Novartis, ASML, Shell, Samsung, Toyota, LVMH.',
        'riscos': 'Risco cambial múltiplo (iene, euro, libra vs USD). Crescimento econômico estruturalmente menor vs EUA. Exposição a riscos políticos europeus. Japão: deflação histórica. Underperformou EUA por mais de uma década. Custo maior que ETFs americanos.',
    },
    'EWZ': {
        'resumo': 'Brasil via iShares. Concentrado em Petrobras, Vale e bancos. Alto dividend yield mas grande risco político-cambial.',
        'estrategia': 'Replica o MSCI Brazil 25/50 Index. Investe em ações brasileiras listadas na B3, denominadas em USD (via ADRs e ações ordinárias). Muito concentrado nos maiores conglomerados brasileiros. Alta volatilidade cambial (BRL/USD).',
        'composicao': 'Petrobras (~15%), Vale (~12%), Itaú Unibanco (~10%), Banco Bradesco (~7%), Nu Holdings (~6%), Ambev (~4%), Localiza, WEG, Embraer, B3. Top 10 respondem por ~65% do fundo. Alta concentração em commodities e bancos.',
        'riscos': 'Risco cambial BRL/USD elevado. Risco político elevado (interferência em Petrobras, Vale). Dependência de commodities (ferro, petróleo). Concentração extrema em poucos setores. Instabilidade fiscal brasileira. Liquidez menor que ETFs americanos.',
    },
    'KWEB': {
        'resumo': 'Internet chinesa: Alibaba, Tencent, Meituan. Alta volatilidade regulatória. Potencial enorme com risco político elevado.',
        'estrategia': 'Replica o CSI Overseas China Internet Index. Foca nas maiores empresas chinesas de internet, e-commerce, redes sociais e fintech. Investimento via H-shares de Hong Kong e ADRs. Acesso ao crescimento da classe média chinesa via digital.',
        'composicao': 'Tencent (~23%), Alibaba (~20%), Meituan (~8%), JD.com (~7%), Baidu (~6%), NetEase (~5%), Trip.com, Li Auto, Kuaishou, Pinduoduo. ~30 empresas de internet chinesa.',
        'riscos': 'Risco regulatório do governo chinês (crackdown de 2021 destruiu 70%+ do valor). Risco geopolítico (Taiwan, sanções EUA-China). Delisting de ADRs americanos possível. Estrutura VIE (não é propriedade direta). Risco de desaceleração econômica da China.',
    },
    'INDA': {
        'resumo': 'Índia via iShares. Exposição ao crescimento econômico indiano — um dos mais rápidos do mundo. Demograficamente favorável.',
        'estrategia': 'Replica o MSCI India Index. Investe nas maiores empresas indianas via mercado local (NSE/BSE) usando a estrutura FII (Foreign Institutional Investor). A Índia é a 5ª maior economia e deve superar o Japão e a Alemanha na próxima década.',
        'composicao': 'Reliance Industries (~9%), HDFC Bank (~8%), Infosys (~7%), ICICI Bank (~6%), Tata Consultancy (~5%), Bharti Airtel (~4%), Wipro, Larsen & Toubro, Asian Paints. ~85 empresas.',
        'riscos': 'Custo elevado (0.65%) para acesso ao mercado indiano. Valuation premium vs outros emergentes. Risco de mercado indiano específico (rupias, regulação). Monsoon/clima afeta setores agrícolas. Competição geopolítica com China.',
    },

    # ── Dividendos ─────────────────────────────────────────────────────────────
    'SCHD': {
        'resumo': 'O ETF de dividendos favorito para longo prazo. Qualidade + crescimento de dividendo + custo ultra-baixo (0.06%).',
        'estrategia': 'Replica o Dow Jones US Dividend 100 Index. Seleciona 100 ações do universo Dow Jones com: (1) 10+ anos de pagamento de dividendo, (2) alto FCF/Dívida, (3) alto ROE, (4) alto dividend yield. Rebalanceado anualmente. Foco em QUALIDADE e CRESCIMENTO do dividendo.',
        'composicao': 'Verizon (~4%), Home Depot (~4%), Cisco (~4%), Amgen (~4%), Pfizer (~4%), Texas Instruments (~4%), Broadcom (~4%), Lockheed Martin (~4%), Blackstone, Altria. ~100 empresas maduras e lucrativas. Setores: Financeiro (18%), Saúde (15%), Industriais (14%), TI (13%).',
        'riscos': 'Underperforma em bull markets de tech (exclui Apple, Microsoft, Nvidia por baixo yield). Exposição a setores tradicionais (telecom, energia, saúde). Risco de corte de dividendo em recessão. Sensível a taxas de juros (concorrência com renda fixa).',
    },
    'VIG': {
        'resumo': 'Dividend Appreciation: empresas que aumentaram dividendo por 10+ anos. Foco em crescimento do dividendo, não no yield atual.',
        'estrategia': 'Replica o S&P US Dividend Growers Index. Seleciona empresas do S&P que aumentaram dividendo por pelo menos 10 anos consecutivos, excluindo as de maior yield (que podem ser armadilhas). Crescimento do dividendo = qualidade empresarial.',
        'composicao': 'Microsoft (~5%), Apple (~5%), JPMorgan (~3%), Visa (~3%), UnitedHealth (~3%), Exxon Mobil (~3%), Broadcom (~3%), Costco (~3%), Johnson & Johnson (~3%). ~310 empresas de alta qualidade comprovada.',
        'riscos': 'Yield atual baixo (~2%) — mais focado em crescimento que renda imediata. Pode excluir empresas excelentes que reiniciam dividendo após corte. Concentração em mega-caps de qualidade. Underperforma setores mais cíclicos em bull markets.',
    },
    'JEPI': {
        'resumo': 'Income ETF da JPMorgan. Combina ações defensivas com covered calls para gerar renda mensal alta (~7-9%/ano). Upside limitado.',
        'estrategia': 'Gestão ativa. Estratégia em duas partes: (1) portfólio de ações defensivas do S&P 500 com baixa volatilidade, (2) venda de opções de compra (ELNs — Equity Linked Notes) sobre o S&P 500 para gerar renda adicional. O prêmio das opções vira distribuição mensal.',
        'composicao': 'Amazon (~2%), Microsoft (~2%), Meta (~2%), Visa (~2%), Progressive (~2%), Mastercard (~2%), AbbVie (~2%), Danaher, Honeywell... ~130 ações defensivas com baixo beta. Mais as ELNs de opções.',
        'riscos': 'Upside limitado em bull markets fortes (opções "queimam" o potencial de alta). Gestão ativa com custo de 0.35%. Risco de redução do dividendo se volatilidade do mercado cair. Não protege contra quedas severas da bolsa. Complexidade das ELNs.',
    },
    'QYLD': {
        'resumo': 'Covered calls no QQQ: vende calls ATM todo mês para gerar yield de ~11-12%. O NAV corrói com o tempo — "income trap".',
        'estrategia': 'Mensalmente vende opções de compra at-the-money sobre o QQQ inteiro. O prêmio coletado é distribuído como dividendo. Resultado: yield altíssimo mas praticamente zero de valorização de capital. Adequado apenas para quem precisa de renda mensal imediata.',
        'composicao': 'Replica o portfólio do QQQ (Nasdaq 100) + posição vendida em calls ATM do índice. A venda da call limita o ganho a zero em qualquer mês de alta. Em quedas, sofre igual ao Nasdaq sem benefício de proteção.',
        'riscos': 'Erosão estrutural do NAV (em bull markets, distribuições "vêm" da valorização que você não captura). Não repõe capital em mercados de alta. Distribuições incluem retorno de capital (não são lucro puro). Adequado apenas para necessidade de renda imediata sem preocupação com crescimento.',
    },
    'NOBL': {
        'resumo': 'Dividend Aristocrats do S&P 500: empresas que aumentaram dividendo por 25+ anos consecutivos. Qualidade máxima.',
        'estrategia': 'Replica o S&P 500 Dividend Aristocrats Index. Seleciona apenas empresas do S&P 500 que aumentaram dividendo por 25 anos ininterruptos (critério extremamente rigoroso — ~67 empresas). Equal-weight: cada empresa recebe peso similar, evitando concentração.',
        'composicao': 'Distribuição equal-weight entre ~67 aristocratas: Coca-Cola, J&J, Colgate-Palmolive, 3M, Caterpillar, Nucor, Essex Property, Consolidated Edison, Automatic Data Processing, T. Rowe Price. Setores: Industriais (~25%), Consumo Básico (~25%), Financeiro (~12%).',
        'riscos': 'Equal weight = maior exposição a industriais/staples, menor tech. Underperforma S&P 500 ponderado em bull markets de tech. Crescimento lento por natureza. Dividend aristocrat pode cortar dividendo em crise severa e sair do índice.',
    },

    # ── Renda Fixa ─────────────────────────────────────────────────────────────
    'TLT': {
        'resumo': 'Treasuries americanos de 20+ anos. O ETF mais usado para apostar em queda de juros. Duração ~17 anos — muito volátil.',
        'estrategia': 'Replica o ICE US Treasury 20+ Year Index. Investe em títulos do Tesouro americano com vencimento superior a 20 anos. Risco de crédito zero (governo americano), mas risco de duração muito alto. Cada 1% de variação de juros = ~17% de variação no preço.',
        'composicao': 'Apenas Treasuries americanos de longo prazo (20-30 anos). Considerado o ativo "livre de risco" mundial. Yield atual ~4.5-5%. Duração modificada de ~17 anos — o mais sensível ao nível de juros entre os ETFs de renda fixa.',
        'riscos': 'Risco de duração muito alto — em 2022 caiu ~36% com alta de juros. Custo de oportunidade quando juros sobem. Inflação destrói valor real. Para investidores brasileiros: dupla exposição a câmbio E juros americanos. Não é "seguro" no curto prazo.',
    },
    'IEF': {
        'resumo': 'Treasuries de 7-10 anos. Duração intermediária (~7.5 anos). Equilíbrio entre yield e sensibilidade a juros.',
        'estrategia': 'Replica o ICE US Treasury 7-10 Year Index. Ponto médio entre segurança de curto prazo (SHY) e potencial de ganho de longo prazo (TLT). Cada 1% de variação de juros = ~7.5% de variação no preço.',
        'composicao': 'Treasuries americanos com vencimento de 7 a 10 anos. Yield atual ~4.3-4.6%. Duração ~7.5 anos. Patrimônio de ~$30B. Liquidez excelente. Referência para o segmento de intermediate government bonds.',
        'riscos': 'Sensível a altas de juros (menos que TLT mas significativo). Yield menor que títulos de longo prazo. Inflação acima do yield corrói valor real. Para brasileiros: custo de hedging cambial pode superar o yield.',
    },
    'SGOV': {
        'resumo': 'T-Bills de 0-3 meses. Equivale a "dinheiro investindo no Fed". Risco mínimo, yield de mercado monetário (~4.5-5.3%).',
        'estrategia': 'Replica o ICE 0-3 Month US Treasury Securities Index. Investe em T-Bills (letras do Tesouro) de curtíssimo prazo — essencialmente a taxa do Federal Reserve. Distribuição mensal de juros. Duração quase zero — praticamente imune a variações de juros.',
        'composicao': 'T-Bills americanos com vencimento de 0 a 3 meses. Yield atual próximo à Fed Funds Rate (5.25-5.50% em 2024). Duração de ~0.08 anos. Mínima volatilidade. Expense ratio de 0.05% — um dos mais baratos.',
        'riscos': 'Yield cai imediatamente quando Fed corta juros. Não oferece apreciação de capital. Risco de reinvestimento (quando juros caem, novos T-Bills rendem menos). Para brasileiros, risco cambial ainda presente mesmo com baixo risco de juros.',
    },
    'AGG': {
        'resumo': 'O "S&P 500 dos bonds": replica toda a renda fixa investment grade americana. Governos, corporativos e hipotecas em uma posição.',
        'estrategia': 'Replica o Bloomberg US Aggregate Bond Index — o índice de referência de renda fixa americana. Cobre ~10.000 títulos investment grade: Treasuries (~40%), MBS (hipotecas, ~25%), corporativos IG (~25%), agências (~10%). Duração ~6 anos.',
        'composicao': 'Treasuries americanos (~40%), MBS/hipotecas (~25%), corporativos investment grade (~25%), bonds de agências (~10%). ~10.000 títulos individuais. Yield atual ~4.5-5%. Duração ~6 anos.',
        'riscos': 'Duração de ~6 anos — sensível a altas de juros (2022: caiu ~13%). MBS tem risco de pré-pagamento. Corporativos IG têm risco de crédito (pequeno). Yield frequentemente abaixo da inflação em períodos de juro real negativo.',
    },
    'HYG': {
        'resumo': 'High Yield americano: bonds corporativos com rating abaixo de BBB. Maior yield, maior risco de crédito. Correlacionado à bolsa.',
        'estrategia': 'Replica o Markit iBoxx USD Liquid High Yield Index. Seleciona bonds corporativos americanos com rating BB ou menor (abaixo de investment grade). Maior yield que AGG em troca de risco de crédito (risco de default). O mais líquido do segmento.',
        'composicao': '~1.000 bonds de empresas americanas com rating BB (46%), B (35%), CCC (12%) e outros. Diversificado por emissor (máx ~3% por empresa). Energia, consumo discricionário, saúde dominam. Yield atual ~7-8%.',
        'riscos': 'Alta correlação com ações (cai junto em recessões — "risco de crédito" e "risco de mercado" são a mesma coisa em crises). Em 2008 caiu ~35%. Default rate sobe em recessões. Menor liquidez dos bonds individuais. Menos diversificado que parece.',
    },
    'TIP': {
        'resumo': 'Títulos do Tesouro indexados ao CPI americano (TIPS). Proteção direta contra inflação. Principal no Brasil ainda em USD.',
        'estrategia': 'Replica o Bloomberg US TIPS Index. TIPS (Treasury Inflation-Protected Securities) têm seu principal ajustado pela inflação americana (CPI). O yield real é o retorno acima da inflação. Proteção direta contra inflação surpreendendo para cima.',
        'composicao': 'TIPS americanos com vencimentos de 5 a 30+ anos. Yield real atual ~2-2.5%. Quando inflação sobe, o principal sobe, aumentando tanto o preço quanto os cupons. Emitidos e garantidos pelo Tesouro americano.',
        'riscos': 'Protege contra inflação americana, não brasileira. Duração moderada (~7 anos) = sensível a juros reais. Em deflação, o principal não cai abaixo do valor face. Rendimento real pode ser negativo se juros reais subirem muito.',
    },

    # ── Commodities ────────────────────────────────────────────────────────────
    'GLD': {
        'resumo': 'O maior e mais líquido ETF de ouro do mundo. Cada cota = ~1/10 oz de ouro físico. Reserva de valor e hedge contra crise.',
        'estrategia': 'Detém ouro físico (lingotes) armazenado em cofres do HSBC em Londres. Cada ação representa 1/10 de onça troy de ouro. Sem renda (ouro não paga dividendos). Valor vem da valorização do preço do ouro.',
        'composicao': '100% ouro físico. Auditado 2x por ano pela KPMG. ~1.000 toneladas de ouro armazenadas. O ouro responde a: (1) taxa real de juros americana, (2) dólar americano, (3) demanda de bancos centrais, (4) stress geopolítico.',
        'riscos': 'Não gera renda (sem dividendos ou cupons). Custo de armazenamento embutido no expense ratio (0.40%). Pode underperformar por décadas em ambiente de juros reais positivos. Volatilidade de ~15-20% ao ano. Câmbio USD/BRL.',
    },
    'IAU': {
        'resumo': 'Ouro físico via iShares com custo menor (0.25% vs 0.40% do GLD). Preferido para alocação de longo prazo.',
        'estrategia': 'Mesmo modelo do GLD — detém ouro físico custodiado pela JPMorgan em NY e Toronto. Cota menor (1/100 oz vs 1/10 oz do GLD), tornando mais acessível para pequenos investidores. A diferença de custo de 0.15%/ano se acumula significativamente no longo prazo.',
        'composicao': '100% ouro físico. Cada cota = 1/100 de onça troy. Custodiado pelo JPMorgan. Auditado regularmente. Mesma exposição ao preço spot do ouro que o GLD, com apenas custo diferente.',
        'riscos': 'Mesmos riscos do GLD: sem renda, custo de armazenamento, volatilidade de preço do ouro. Menor liquidez intradiária que o GLD (diferença relevante apenas para traders de grande volume).',
    },
    'GDX': {
        'resumo': 'Mineradoras de ouro: Newmont, Barrick, Agnico Eagle. Alavancagem ao ouro (~2-3x). Sobe e cai mais que o metal físico.',
        'estrategia': 'Replica o NYSE Arca Gold Miners Index. Investe em empresas de mineração de ouro (não em ouro físico). As mineradoras têm alavancagem operacional ao preço do ouro — quando o ouro sobe 10%, as margens das mineradoras podem subir 30-50%, fazendo o GDX subir mais.',
        'composicao': 'Newmont (~25%), Barrick Gold (~13%), Agnico Eagle (~11%), Wheaton Precious Metals (~8%), Gold Fields (~5%), Kinross Gold, Pan American Silver, Hecla Mining. ~50 mineradoras globais.',
        'riscos': 'Alavancagem funciona nos dois sentidos: quando ouro cai, mineradoras caem mais. Riscos operacionais: custo de mineração, greves, licenças. Risco geopolítico dos países de operação (Africa, América Latina). Risco de gestão corporativa. Mais volátil que ouro físico.',
    },

    # ── Fator / Smart Beta ──────────────────────────────────────────────────────
    'QUAL': {
        'resumo': 'Quality factor: empresas com alto ROE, balanço sólido e lucros estáveis. Historicamente supera o mercado com menos risco.',
        'estrategia': 'Replica o MSCI USA Quality Factor Index. Seleciona ações do MSCI USA com maior pontuação em: (1) ROE alto, (2) Dívida/Equity baixo, (3) Variabilidade de lucros baixa. O fator quality tem prêmio histórico documentado academicamente.',
        'composicao': 'Apple (~8%), Microsoft (~8%), Nvidia (~7%), Meta (~4%), Alphabet (~4%), Visa (~3%), Mastercard (~3%), UnitedHealth (~3%), Broadcom (~3%). ~125 empresas de alta qualidade. Tecnologia domina (~40%) por ter ROEs elevados.',
        'riscos': 'Concentração em tech de alta qualidade — similar ao QQQ em períodos de bull market. Pode underperformar mercado quando value lidera. Quality pode ser "caro" (valuation premium). Fator quality foi intensamente explorado — prêmio pode ter diminuído.',
    },
    'USMV': {
        'resumo': 'Minimum Volatility EUA: ações com menor volatilidade histórica. Cai menos em bear markets. Ideal para investidores avessos a risco.',
        'estrategia': 'Replica o MSCI USA Minimum Volatility Index. Usa otimização quantitativa para selecionar o portfólio de menor volatilidade dentro do MSCI USA, com restrições setoriais para evitar concentração. Rebalanceado semestralmente.',
        'composicao': 'Visa (~3%), Waste Management (~3%), McDonald\'s (~3%), Accenture (~3%), Costco (~2.5%), Booking Holdings, Progressive, AutoZone, Republic Services. ~170 empresas de setores defensivos: saúde, utilities, consumo básico, financeiro.',
        'riscos': 'Underperforma significativamente em bull markets fortes. "Low volatility anomaly" pode ser explicada por risk factors (quality, value). Custo maior que ETFs simples (0.15%). Pode ter correlações inesperadas em crises sistêmicas.',
    },
    'COWZ': {
        'resumo': 'Cash Cows: 100 empresas com maior Free Cash Flow Yield do Russell 1000. Foco em geração de caixa real, não lucros contábeis.',
        'estrategia': 'Replica o Pacer US Cash Cows 100 Index. Seleciona as 100 empresas do Russell 1000 com maior FCF Yield (Free Cash Flow / Enterprise Value). Rebalanceado trimestralmente. Premissa: FCF é mais difícil de manipular contabilmente que lucro líquido.',
        'composicao': 'Tipicamente: Exxon, Chevron, Valero, Phillips 66, Marathon Petroleum, APA Corp, Coterra Energy — forte exposição a energia e value. ~100 empresas com FCF yields acima de 10%. Rotatividade trimestral significativa.',
        'riscos': 'Alta exposição a energia (ciclicidade). Equal-weight dentro do universo selecionado. Alto turnover = maiores custos de transação. Pode excluir empresas de crescimento excelente que reinvestem FCF (Amazon historicamente). Concentração setorial variável.',
    },
    'AVUV': {
        'resumo': 'Small Cap Value americano da Avantis (filha da Dimensional). Implementação superior de fatores acadêmicos: small + value + profitability.',
        'estrategia': 'Gestão ativa quantitativa baseada em pesquisa da Dimensional Fund Advisors. Seleciona small caps americanas com alto valor (baixo Price-to-Book) E alta lucratividade (ROE elevado). Exclui empresas com baixa lucratividade, evitando "value traps". Rebalanceamento contínuo.',
        'composicao': '~700 small caps americanas de value com lucratividade alta. Sem concentração individual — maior posição ~0.5%. Setores: Financeiro (~30%), Industrial (~15%), Consumo (~12%), Energia (~10%). Market cap médio ~$2-3B.',
        'riscos': 'Small cap value pode underperformar growth por longos períodos (2010-2020). Alta volatilidade de small caps. Prêmio de value pode ter se comprimido. Gestão ativa = risco de underperformance vs benchmark passivo. Menos diversificado que VTI.',
    },

    # ── Alavancados ────────────────────────────────────────────────────────────
    'TQQQ': {
        'resumo': 'Nasdaq 100 3x alavancado diário. Para cada 1% de alta do QQQ, TQQQ sobe ~3%. NUNCA adequado para longo prazo por decay.',
        'estrategia': 'Usa swaps e futuros para oferecer 3x o retorno DIÁRIO do Nasdaq-100. Rebalanceamento diário para manter a alavancagem. O "volatility decay" (beta slippage) corrói o valor em mercados laterais ou voláteis. Projetado exclusivamente para operações especulativas de curtíssimo prazo.',
        'composicao': 'Não detém ações diretamente. Usa swaps de retorno total sobre o QQQ com bancos (Goldman Sachs, Morgan Stanley, etc.) + T-Bills como colateral. Exposição nocional de 3x ao Nasdaq-100.',
        'riscos': 'Em 2022 caiu ~79%. Volatility decay: num mês que sobe 10% e cai 10%, o QQQ retorna -1%, o TQQQ retorna ~-9%. Adequado APENAS para day trade ou swing trade de no máximo alguns dias. Comprar e "esquecer" é virtualmente garantia de perda de longo prazo.',
    },
    'SQQQ': {
        'resumo': 'Nasdaq 100 inverso 3x. Lucra quando a Nasdaq cai. Perde em mercados de alta ou laterais. Exclusivo para hedge de curtíssimo prazo.',
        'estrategia': 'Oferece -3x o retorno diário do Nasdaq-100. Em dias de queda do QQQ, SQQQ sobe ~3x. Usado para: (1) hedge de posições compradas em tech, (2) especulação em quedas. O volatility decay é ainda mais severo no sentido inverso — em bull markets, perde rapidamente.',
        'composicao': 'Usa swaps inversos sobre o Nasdaq-100 + T-Bills como colateral. Estrutura similar ao TQQQ mas com sinal oposto. Rebalanceamento diário.',
        'riscos': 'Decay extremo — em 2023 (QQQ +55%), o SQQQ caiu >80%. Em mercados laterais, perde independentemente da direção. Adequado APENAS para hedges táticos de 1-5 dias. Manter posição por semanas/meses quase sempre resulta em perda catastrófica.',
    },
    'UPRO': {
        'resumo': 'S&P 500 3x alavancado diário. Similar ao TQQQ mas sobre o S&P 500. Em 2022 caiu ~75%. Altíssimo risco de ruína.',
        'estrategia': 'Oferece 3x o retorno diário do S&P 500. Mesmo mecanismo de swaps que o TQQQ. O S&P 500 tem menor volatilidade que o Nasdaq, o que reduz levemente o decay, mas continua inadequado para longo prazo.',
        'composicao': 'Swaps de retorno total sobre o S&P 500 com contrapartes bancárias + T-Bills como colateral. 3x de alavancagem diária sobre o SPY implicitamente.',
        'riscos': 'Queda de 34% no S&P 500 em 2020 (COVID) = queda de ~86% no UPRO no mesmo período (antes da recuperação). Em 2022 caiu ~75%. Volatility decay severo. Chamada de margem implícita se S&P cair >33% em um dia. APENAS para traders ativos e experientes.',
    },
    'TMF': {
        'resumo': 'Treasuries 20+ anos 3x alavancado. Em 2022 perdeu ~90% com alta de juros. Extremamente destrutivo se usado incorretamente.',
        'estrategia': 'Oferece 3x o retorno diário do TLT (Treasuries 20+ anos). Usado por alguns como hedge alavancado de risco de recessão (quando Fed corta juros, TLT sobe, TMF sobe 3x). A "HFEA strategy" (Hedgefundie\'s Excellent Adventure) popularizou o uso de UPRO + TMF.',
        'composicao': 'Swaps de retorno total sobre bonds do Tesouro americano de 20+ anos. Duração efetiva de ~51 anos (3x a duração do TLT de ~17 anos).',
        'riscos': 'Em 2022: TLT caiu 36% → TMF caiu ~90%. Duração efetiva absurda de ~51 anos. Decay em ambientes de volatilidade de juros. Só funciona em cenários de queda rápida de juros. A estratégia HFEA registrou perdas devastadoras em 2022.',
    },
    'UVXY': {
        'resumo': 'VIX de curto prazo 1.5x. O "índice do medo" alavancado. Sobe explosivamente em crashes, perde valor constantemente quando mercado calmo.',
        'estrategia': 'Oferece 1.5x a variação de índices de futuros de VIX de curto prazo (1 e 2 meses). O VIX mede a volatilidade implícita do S&P 500. Quando mercado cai abruptamente, VIX explode. O custo de roll de futuros de VIX é devastador — futuros de VIX normalmente estão em contango.',
        'composicao': 'Futuros de VIX de curto prazo (1º e 2º vencimentos) com alavancagem de 1.5x. Nenhuma ação ou bond. O custo de roll pode ser de -50 a -80% ao ano em mercados tranquilos.',
        'riscos': 'Perde virtualmente todo o valor em períodos de baixa volatilidade (pode perder 90%+ em 12 meses). O reverse split constante é necessário para manter o preço positivo. Adequado APENAS para hedges táticos de horas/dias. Manter por meses = perda quase certa.',
    },

    # ── Multi-Asset ─────────────────────────────────────────────────────────────
    'AOR': {
        'resumo': 'Portfólio completo 60% ações / 40% renda fixa em um único ETF. Diversificação global automática com rebalanceamento periódico.',
        'estrategia': 'ETF de ETFs da iShares. Investe em uma cesta de ETFs da própria BlackRock para atingir alocação de 60% em ações globais e 40% em renda fixa global. Rebalanceado periodicamente. Estratégia clássica de portfólio "60/40" num único produto.',
        'composicao': 'ETFs de renda variável (~60%): IVV (S&P 500), IEFA (desenvolvidos), IEMG (emergentes). ETFs de renda fixa (~40%): AGG (bonds EUA), IGOV (bonds internacionais). Total de ~15 ETFs subjacentes com diversificação global.',
        'riscos': 'Taxa dupla: 0.15% do AOR + taxas dos ETFs subjacentes (~0.05-0.07%). Em crises, ações e bonds podem cair juntos (2022). Alocação fixa pode não refletir necessidades individuais. Exposição cambial global.',
    },
    'NTSX': {
        'resumo': 'Portfólio eficiente: 90% S&P 500 + 60% bonds via futuros alavancados com apenas 100% de capital. Maximiza eficiência de capital.',
        'estrategia': 'Detém 90% do portfólio em ações do S&P 500 e usa os 10% restantes para comprar futuros de Treasuries com alavancagem de 6x, obtendo exposição de 60% a bonds. Resultado: exposição de 90/60 (ações/bonds) com 100% do capital — superior ao portfólio 60/40 tradicional em eficiência.',
        'composicao': '90% em ações do S&P 500 (similar ao VOO) + futuros de Treasuries de 2, 5 e 10 anos totalizando exposição equivalente a 60% em bonds. O caixa dos futuros rende T-Bills.',
        'riscos': 'Alavancagem nos bonds: se bonds caem (juros sobem), o portfólio sofre duplamente. Em 2022, tanto ações quanto bonds caíram = perda amplificada. Complexidade de estrutura — menor transparência. Adequado para investidores que entendem alavancagem em bonds.',
    },
}


PROSPECTOS_NOVOS = {

    # ══ ETF AÇÃO ÚNICA ALAVANCADO ══════════════════════════════════════════════
    'BMNU': {
        'resumo': 'T-REX 2X Long BMNR — ETF alavancado 2x de ação única. Amplifica diariamente os movimentos de BMNR.',
        'estrategia': 'Oferece 2x o retorno diário da ação-alvo via swaps. Rebalanceamento diário restaura a alavancagem. Projetado para operações intradiárias ou de poucos dias — o volatility decay destrói valor no longo prazo.',
        'composicao': 'Swaps de retorno total sobre a ação-alvo + T-Bills como colateral. Sem exposição diversificada — 100% dependente de uma única ação.',
        'riscos': '⚠️ ALTO RISCO. Volatility decay severo em mercados laterais ou voláteis. Adequado APENAS para day trade ou swing trade de 1-3 dias. Manter por semanas pode resultar em perda >50% mesmo com a ação lateral.',
    },
    'CRCG': {
        'resumo': 'Leverage Shares 2X Long CRCL — ETF 2x sobre Circle Internet Group (CRCL). Altíssima volatilidade.',
        'estrategia': '2x retorno diário de CRCL (Circle, emissora do USDC). Alavancagem diária via swaps. Circle é empresa de stablecoin e infraestrutura cripto — alta sensibilidade ao mercado de criptomoedas.',
        'composicao': 'Swaps 2x sobre CRCL + colateral em T-Bills. Exposição concentrada em uma única empresa de infraestrutura cripto.',
        'riscos': '⚠️ ALTO RISCO. Dupla exposição: alavancagem + setor cripto. Em quedas do BTC/cripto, CRCL cai e o 2x amplifica. Volatility decay. Apenas para operações táticas de curtíssimo prazo.',
    },
    'CONL': {
        'resumo': 'GraniteShares 2x Long COIN — ETF 2x sobre Coinbase (COIN). Amplifica movimentos da maior exchange de cripto dos EUA.',
        'estrategia': '2x retorno diário da Coinbase Global (COIN). A Coinbase tem alta correlação ao Bitcoin e ao mercado cripto em geral. Em bull markets de cripto, pode subir explosivamente. Em correções, cai dramaticamente.',
        'composicao': 'Swaps de retorno total 2x sobre COIN + T-Bills. Coinbase é proxy do mercado cripto — sobe/cai junto com BTC e ETH.',
        'riscos': '⚠️ EXTREMO RISCO. Coinbase é ação volátil (beta >3 vs S&P 500), e o 2x multiplica isso. Risco regulatório da Coinbase. Decay em mercados laterais. Apenas day trade.',
    },
    'CRWG': {
        'resumo': 'Leverage Shares 2X Long CRWV — ETF 2x sobre CoreWeave (CRWV). Exposição alavancada à infraestrutura de IA.',
        'estrategia': '2x retorno diário de CoreWeave (CRWV), empresa de computação em nuvem especializada em GPUs para IA. IPO recente (2024), alta volatilidade por ser empresa jovem em setor quente.',
        'composicao': 'Swaps 2x sobre CRWV + colateral. CoreWeave fornece infraestrutura de GPU cloud para treinamento de modelos de IA — exposição direta ao boom de IA.',
        'riscos': '⚠️ EXTREMO RISCO. Empresa de IPO recente sem histórico longo. Setor de IA com valuation elevado. 2x alavancagem sobre ação já volátil. Volatility decay. Apenas operações táticas.',
    },
    'BTCZ': {
        'resumo': 'T-Rex 2X Inverse Bitcoin — ETF INVERSO 2x do Bitcoin. Lucra quando BTC cai. Perde aceleradamente quando BTC sobe.',
        'estrategia': 'Oferece -2x o retorno diário do Bitcoin. Hedge de curtíssimo prazo para posições long em BTC. Em mercados em alta do BTC, perde valor rapidamente pelo decay inverso.',
        'composicao': 'Swaps inversos 2x sobre Bitcoin (via futuros CME ou spot) + T-Bills como colateral.',
        'riscos': '⚠️ EXTREMO RISCO. Em bull markets de Bitcoin, perde valor explosivamente. O decay inverso é devastador — Bitcoin subindo 10%/mês = BTCZ perdendo ~18%/mês. Apenas para hedges de horas/1-2 dias.',
    },
    'AMDD': {
        'resumo': 'Direxion Daily AMD Bear 1X — ETF INVERSO 1x de AMD. Sobe quando AMD cai. Hedge de semicondutores/IA.',
        'estrategia': 'Retorno inverso diário (-1x) da AMD. Usado como hedge para posições compradas em AMD ou para apostar em queda da empresa. AMD é líder em CPUs e GPUs — muito sensível ao ciclo de semicondutores.',
        'composicao': 'Swaps de retorno inverso 1x sobre AMD + T-Bills. Sem alavancagem mas com decay de mercados laterais por natureza dos swaps.',
        'riscos': '⚠️ ALTO RISCO. Mesmo sem alavancagem 2x, o ETF inverso tem decay estrutural. Em bull markets de AMD (IA/semicondutores), perde valor constantemente. Apenas para hedges táticos.',
    },
    'BITX': {
        'resumo': '2x Bitcoin Strategy ETF — ETF 2x sobre futuros de Bitcoin. Exposição alavancada ao BTC via mercado futuro.',
        'estrategia': 'Oferece 2x o retorno diário de índice de futuros de Bitcoin. Diferente dos ETFs spot (IBIT, FBTC), usa futuros da CME — o que adiciona custo de roll além do decay de alavancagem.',
        'composicao': 'Futuros de Bitcoin na CME com alavancagem de 2x + T-Bills como colateral. Dupla penalidade: custo de roll de futuros + decay de alavancagem.',
        'riscos': '⚠️ EXTREMO RISCO. Dois custos embutidos: roll de futuros (~5-15%/ano) + volatility decay do 2x. Retorno real muito abaixo de 2x BTC no médio/longo prazo. Apenas day trade.',
    },
    'AMDL': {
        'resumo': 'GraniteShares 2x Long AMD — ETF 2x sobre AMD. Amplifica retornos diários da AMD (semicondutores/IA).',
        'estrategia': '2x retorno diário de AMD (Advanced Micro Devices). AMD fabrica CPUs (Ryzen, EPYC) e GPUs (Radeon, Instinct). Alta correlação ao ciclo de semicondutores e ao boom de IA (GPUs para data centers).',
        'composicao': 'Swaps de retorno total 2x sobre AMD + T-Bills. AMD tem beta ~2 vs S&P 500, então o 2x eleva o beta efetivo para ~4.',
        'riscos': '⚠️ ALTO RISCO. AMD já é volátil — o 2x torna as oscilações extremas. Ciclicidade de semicondutores. Competição com Nvidia em GPUs de IA. Decay. Apenas swing trade de 1-5 dias.',
    },
    'AAPD': {
        'resumo': 'Direxion Daily AAPL Bear 1X — ETF INVERSO 1x de Apple. Hedge para posições em AAPL ou aposta em queda.',
        'estrategia': 'Retorno inverso diário (-1x) da Apple (AAPL). Apple é a maior empresa do mundo por capitalização — pouco volátil vs outras big caps. O ETF inverso permite apostar em correções da AAPL.',
        'composicao': 'Swaps de retorno inverso 1x sobre AAPL + T-Bills. Em dias que AAPL cai 2%, AAPD sobe ~2%.',
        'riscos': 'ALTO RISCO. Apple tem histórico de longo prazo de valorização — manter o inverso por muito tempo é estratégia perdedora. Adequado apenas para hedges táticos ou apostas em resultados negativos.',
    },
    'AMZD': {
        'resumo': 'Direxion Daily AMZN Bear 1X — ETF INVERSO 1x de Amazon. Sobe quando AMZN cai.',
        'estrategia': 'Retorno inverso diário (-1x) da Amazon (AMZN). Amazon é líder em e-commerce e AWS (cloud). O ETF inverso permite apostar em correções ou hedgear posições em AMZN.',
        'composicao': 'Swaps de retorno inverso 1x sobre AMZN + T-Bills.',
        'riscos': 'ALTO RISCO. Amazon tem forte tendência de valorização de longo prazo. Inverso tem decay estrutural. Apenas para hedges táticos de curto prazo.',
    },
    'ETHU': {
        'resumo': '2x Ether ETF — ETF 2x sobre Ethereum. Exposição alavancada ao segundo maior criptoativo.',
        'estrategia': 'Oferece 2x o retorno diário do Ethereum. ETH tem correlação alta com BTC mas com maior volatilidade. Exposição ao ecossistema DeFi, NFTs e contratos inteligentes — que impulsionam demanda por ETH.',
        'composicao': 'Swaps ou futuros 2x sobre Ethereum + T-Bills como colateral. Alta concentração de risco em ativo cripto já muito volátil.',
        'riscos': '⚠️ EXTREMO RISCO. Ethereum pode cair 70-90% em bear markets cripto. O 2x amplifica isso para perdas potenciais de 95%+. Volatility decay. Regulação cripto. Apenas day trade.',
    },
    'BITU': {
        'resumo': 'ProShares Ultra Bitcoin ETF — ETF 2x sobre Bitcoin spot. Exposição alavancada ao BTC com a marca ProShares.',
        'estrategia': '2x retorno diário do Bitcoin via swaps sobre o preço spot. ProShares é uma das maiores emissoras de ETFs alavancados dos EUA. Similar ao BITX mas pode usar estrutura diferente de colateral.',
        'composicao': 'Swaps 2x sobre Bitcoin spot + T-Bills. Sem posse direta de BTC. Rebalanceamento diário para manter a alavancagem.',
        'riscos': '⚠️ EXTREMO RISCO. Mesmos riscos do BITX: volatility decay + volatilidade extrema do BTC. Apenas day trade. Em 2022, BTC caiu ~65% — BITU teria caído ~90%+.',
    },
    'BMNG': {
        'resumo': 'Leverage Shares 2X Long BMNR — ETF 2x sobre ação alvo BMNR. Alta volatilidade intradiária.',
        'estrategia': '2x retorno diário da ação-alvo via swaps. Série de ETFs de ação única da Leverage Shares, emissora europeia que expandiu para o mercado americano.',
        'composicao': 'Swaps 2x sobre ação-alvo + colateral em T-Bills. Alta rotatividade típica de traders de alta frequência.',
        'riscos': '⚠️ ALTO RISCO. Volatility decay. Liquidez concentrada em horários específicos. Apenas day trade.',
    },
    'CCUP': {
        'resumo': 'T-REX 2X Long CRCL — ETF 2x sobre Circle (CRCL). Similar ao CRCG com mesma exposição alavancada.',
        'estrategia': '2x retorno diário de Circle Internet Group via estrutura T-REX (emissora americana). Circle é a empresa por trás do USDC — stablecoin de $40B+ de capitalização.',
        'composicao': 'Swaps 2x sobre CRCL + T-Bills como colateral.',
        'riscos': '⚠️ EXTREMO RISCO. Setor cripto + alavancagem + empresa de IPO recente. Apenas day trade de horas.',
    },
    'DXD': {
        'resumo': 'ProShares UltraShort Dow30 — ETF 2x INVERSO do Dow Jones. Lucra quando o DJIA cai 2x.',
        'estrategia': 'Oferece -2x o retorno diário do Dow Jones Industrial Average. Hedge alavancado contra quedas do mercado americano de large caps. Em bear markets, pode subir significativamente.',
        'composicao': 'Swaps de retorno inverso 2x sobre o DJIA + T-Bills.',
        'riscos': 'ALTO RISCO. Volatility decay severo. Em mercados de alta (como 2023-2024), perde valor rapidamente. Apenas para hedges táticos de dias.',
    },

    # ══ AMPLO EUA — NOVOS ═════════════════════════════════════════════════════
    'SCHD': {
        'resumo': 'Schwab US Dividend Equity ETF — referência em dividendos de qualidade com custo ultra-baixo (0.06%).',
        'estrategia': 'Seleciona 100 ações do Dow Jones US Dividend 100 Index com: 10+ anos de dividendo consistente, alto FCF/Dívida, alto ROE e yield acima da média. Rebalanceamento anual. Foco em qualidade E crescimento do dividendo.',
        'composicao': 'Verizon, Cisco, Home Depot, Amgen, Pfizer, Texas Instruments, Broadcom, Lockheed Martin. ~100 empresas maduras. Setores: Financeiro (18%), Saúde (15%), Industriais (14%), TI (13%).',
        'riscos': 'Underperforma tech em bull markets. Sensível a juros. Pode cortar dividendos em recessão severa.',
    },
    'SPLG': {
        'resumo': 'SPDR Portfolio S&P 500 ETF — S&P 500 com custo de apenas 0.02%/ano. Um dos mais baratos disponíveis.',
        'estrategia': 'Replica o S&P 500 com expense ratio de 0.02% — menor que VOO (0.03%) e muito menor que SPY (0.09%). Menos líquido que SPY mas ideal para investidores de longo prazo. Da mesma gestora que o SPY (State Street).',
        'composicao': 'Idêntica ao SPY: 500 maiores empresas americanas. Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet dominam (~30% do fundo).',
        'riscos': 'Menos liquidez intradiária que SPY (irrelevante para longo prazo). Mesmos riscos do S&P 500.',
    },
    'FNGS': {
        'resumo': 'MicroSectors FANG+ ETN — exposição às 10 maiores empresas de tecnologia e internet (FANG+).',
        'estrategia': 'ETN (Exchange Traded Note, não ETF) da Bank of Montreal que replica o NYSE FANG+ Index: as 10 maiores empresas de tecnologia e plataformas digitais. Ponderação igual — cada empresa vale ~10%.',
        'composicao': 'Meta, Apple, Amazon, Netflix, Alphabet, Microsoft, Nvidia, Tesla, Snowflake, Spotify (composição varia). 10 empresas com peso igual de ~10% cada.',
        'riscos': 'ETN = risco de crédito da emissora (BMO). Concentração extrema em 10 empresas de tech. Alta volatilidade. Custo elevado.',
    },
    'IUSG': {
        'resumo': 'iShares Core S&P US Growth ETF — metade de crescimento do S&P 1500. Focado em empresas de alto crescimento.',
        'estrategia': 'Replica o S&P 900 Growth Index — ações de crescimento do S&P 500/400/600 combinados, selecionadas por P/B, crescimento de vendas e momentum. Mais diversificado que QQQ por incluir mid e small caps de growth.',
        'composicao': 'Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet no topo. ~450 ações de crescimento de todas as capitalizações. Tecnologia domina (~40%).',
        'riscos': 'Muito sensível a juros (growth sofre com taxas altas). Valuation elevado. Concentração em tech. Alta volatilidade em ciclos de aversão a risco.',
    },
    'IUSV': {
        'resumo': 'iShares Core S&P US Value ETF — metade de value do S&P 1500. Contraste com IUSG.',
        'estrategia': 'Replica o S&P 900 Value Index — ações de valor selecionadas por baixo P/B, baixo P/E e alta distribuição de dividendos. Inclui large, mid e small caps de value. Complementar ao IUSG em alocação estilo.',
        'composicao': 'Berkshire Hathaway, JPMorgan, Exxon Mobil, Johnson & Johnson, UnitedHealth. Setor Financeiro (~25%), Saúde (~15%), Energia (~10%), Industriais (~10%). ~450 ações.',
        'riscos': 'Underperforma growth em bull markets tecnológicos. Exposição a setores tradicionais (financeiro, energia). Pode incluir "value traps".',
    },
    'MGC': {
        'resumo': 'Vanguard Mega Cap ETF — as ~230 maiores empresas americanas. Mais concentrado que VOO.',
        'estrategia': 'Replica o CRSP US Mega Cap Index — empresas acima do 70º percentil do mercado americano total por capitalização. Foco nas verdadeiras mega-caps com market cap típico de $100B+.',
        'composicao': '~230 mega-caps. Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet formam >35% do fundo. Tecnologia domina fortemente por ter as maiores capitalizações do mundo.',
        'riscos': 'Alta concentração em Big Tech. Muito sensível ao desempenho das 10 maiores empresas. Câmbio USD/BRL.',
    },
    'MGK': {
        'resumo': 'Vanguard Mega Cap Growth ETF — mega-caps de crescimento. As maiores empresas de alto crescimento dos EUA.',
        'estrategia': 'Replica o CRSP US Mega Cap Growth Index — subset de crescimento do MGC. Seleciona mega-caps com características de growth: alto P/B, alto crescimento de EPS/vendas. Ainda mais concentrado em tech que o MGC.',
        'composicao': 'Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet: ~50%+ do fundo. Apenas ~140 empresas de mega crescimento. O ETF mais puro de "Big Tech" da Vanguard.',
        'riscos': 'Concentração extrema em tech mega-caps. Beta elevado. Muito sensível a juros e ciclos de risk-off. Valuation persistentemente alto.',
    },

    # ══ RENDA FIXA — NOVOS ════════════════════════════════════════════════════
    'BKLN': {
        'resumo': 'Invesco Senior Loan ETF — empréstimos sênior de taxa flutuante. Yield alto + proteção parcial contra alta de juros.',
        'estrategia': 'Replica o Morningstar LSTA US Leveraged Loan 100 Index. Investe em empréstimos bancários sênior a empresas com rating abaixo de investment grade (leveraged loans). Taxa de juros FLUTUANTE (atrelada ao SOFR) — não sofre com alta de juros como bonds de taxa fixa.',
        'composicao': '~100 empréstimos sênior das maiores empresas com leveraged loans. Diversificado por setor. Taxa SOFR + spread (~4-5%). Yield atual ~8-9%. Garantia: ativos da empresa (sênior na estrutura de capital).',
        'riscos': 'Risco de crédito alto (empresas abaixo de investment grade). Em recessão, default rates sobem. Menor liquidez que bonds tradicionais. Recuperação em caso de default pode ser longa. Custo elevado (0.65%).',
    },
    'EMLC': {
        'resumo': 'VanEck EM Local Currency Bond ETF — bonds soberanos de emergentes em MOEDA LOCAL (não em USD).',
        'estrategia': 'Replica o J.P. Morgan GBI-EMG Core Index. Investe em bonds governamentais de mercados emergentes denominados em moedas locais (real, peso, rupia, etc.). Combina yield alto com aposta em valorização das moedas emergentes vs dólar.',
        'composicao': 'Brasil (~10%), México (~9%), Indonésia (~9%), África do Sul (~8%), Tailândia (~7%), China, Polônia, Colômbia. ~20 países. Yield local alto (5-10% dependendo do país).',
        'riscos': 'Risco cambial DUPLO: variação das moedas locais vs USD E variação USD vs BRL para investidor brasileiro. Risco político de emergentes. Inflação local pode erodir yield real. Alta volatilidade.',
    },
    'FBND': {
        'resumo': 'Fidelity Total Bond ETF — gestão ativa de renda fixa diversificada. Alternativa ao AGG com alpha potencial.',
        'estrategia': 'Gestão ativa pela equipe de renda fixa da Fidelity. Benchmarkado contra o Bloomberg US Aggregate, mas com liberdade para desviar. Pode incluir bonds fora do investimento grade para gerar alpha. Custo de 0.36%.',
        'composicao': 'Treasuries (~30%), MBS (~25%), corporativos IG (~25%), high yield selecionado (~5-10%), bonds internacionais. Mix dinâmico ajustado pela equipe Fidelity.',
        'riscos': 'Gestão ativa = risco de underperformance vs AGG. Custo maior que ETFs passivos (0.36% vs 0.03% do AGG). Exposição a high yield aumenta risco de crédito.',
    },
    'BINC': {
        'resumo': 'iShares Flexible Income Active ETF — renda fixa ativa da BlackRock. Busca maximizar renda dentro de parâmetros de risco.',
        'estrategia': 'Gestão ativa pela BlackRock com mandato flexível de renda fixa — pode investir em qualquer segmento de bonds (governo, corporativo, high yield, internacional, TIPS) conforme a visão da equipe sobre ciclo econômico e juros.',
        'composicao': 'Mix dinâmico ajustado mensalmente. Pode incluir: Treasuries, MBS, corporativos IG/HY, bonds emergentes, TIPS. Diversificação máxima de renda fixa global.',
        'riscos': 'Gestão ativa com custo de 0.40%. Risco de underperformance. Exposição a múltiplos riscos de crédito e duração simultaneamente. Câmbio se incluir bonds internacionais.',
    },
    'HYSA': {
        'resumo': 'PGIM Short Duration High Yield Bond ETF — high yield de curta duração. Yield alto com menor sensibilidade a juros.',
        'estrategia': 'Gestão ativa pela PGIM (Prudential). Foca em bonds de alto yield com vencimento curto (1-3 anos). Combinação de alto yield (~7-8%) com menor risco de duração que HYG/JNK. Ideal para ambiente de juros altos.',
        'composicao': 'Bonds corporativos HY com vencimento de 1-3 anos. Rating médio: BB/B. Diversificado por setor — energia, consumo, saúde, serviços. ~200-300 posições.',
        'riscos': 'Risco de crédito elevado (HY). Em recessão, defaults sobem mesmo para vencimentos curtos. Gestão ativa = custo maior. Menor liquidez que HYG.',
    },
    'FLRN': {
        'resumo': 'SPDR Bloomberg Investment Grade Float Rate ETF — bonds investment grade de taxa FLUTUANTE. Proteção contra alta de juros.',
        'estrategia': 'Bonds corporativos investment grade com taxa flutuante (atrelada ao SOFR/LIBOR). Em ambiente de juros altos ou crescentes, supera bonds de taxa fixa. Duração próxima de zero mesmo com vencimentos longos.',
        'composicao': 'Bonds corporativos IG de taxa flutuante: bancos, utilities, industriais. Vencimentos de 1-5 anos tipicamente. Taxa atual: SOFR + spread (~4.5-5.5%). ~200 posições.',
        'riscos': 'Yield cai quando Fed corta juros. Risco de crédito corporativo. Menor diversificação que AGG. Menos transparência de preços que bonds de taxa fixa.',
    },
    'SPTI': {
        'resumo': 'SPDR Portfolio Intermediate Term Treasury ETF — Treasuries de 3-10 anos com custo ultra-baixo (0.06%).',
        'estrategia': 'Replica o Bloomberg 3-10 Year US Treasury Bond Index. Faixa intermediária do Tesouro americano — mais yield que curto prazo (SHY), menos duração que longo prazo (IEF/TLT). Custo muito baixo vs iShares equivalentes.',
        'composicao': 'Treasuries americanos de 3 a 10 anos. Duração ~5-6 anos. Yield atual ~4.3-4.5%. Patrimônio de ~$5B. Portfólio completamente livre de risco de crédito (governo americano).',
        'riscos': 'Sensível a altas de juros (duração ~5-6 anos). Menor yield que longo prazo. Para brasileiros: câmbio USD/BRL ainda presente.',
    },
    'SPTS': {
        'resumo': 'SPDR Portfolio Short Term Treasury ETF — Treasuries de 1-3 anos. Segurança máxima com yield de curto prazo.',
        'estrategia': 'Replica o Bloomberg 1-3 Year US Treasury Bond Index. Equivalente ao SHY mas da SPDR com custo menor. Maturidade curta = mínima sensibilidade a juros + máxima segurança de crédito (Tesouro americano).',
        'composicao': 'Treasuries americanos de 1 a 3 anos. Duração ~1.8 anos. Yield atual ~4.5-5%. Custo de 0.03%. Zero risco de crédito.',
        'riscos': 'Yield menor que intermediate/long. Em cortes de juros pelo Fed, yield cai imediatamente com o roll dos títulos. Inflação pode superar o yield.',
    },
    'SPTL': {
        'resumo': 'SPDR Portfolio Long Term Treasury ETF — Treasuries de 10+ anos. Alta sensibilidade a juros com custo baixo (0.06%).',
        'estrategia': 'Replica o Bloomberg Long US Treasury Bond Index. Bonds do Tesouro americano de longo prazo (10-30 anos). Similar ao TLT mas com custo menor (0.06% vs 0.15%). Duração ~16 anos — sensível a ciclos de juros.',
        'composicao': 'Treasuries americanos de 10+ anos. Duração ~16 anos. Cada 1% de variação em juros = ~16% de variação no preço. Yield atual ~4.5-5%. Patrimônio menor que TLT mas mesmo exposição.',
        'riscos': 'Em 2022 caiu ~30% com alta de juros. Alta sensibilidade a política monetária do Fed. Longo prazo implica alto risco de duração.',
    },
    'GOVT': {
        'resumo': 'iShares US Treasury Bond ETF — Treasuries americanos de todos os vencimentos em um único ETF.',
        'estrategia': 'Replica o ICE US Treasury Core Bond Index — cobertura completa da curva de Treasuries americanos: curto, intermediário e longo prazo. Duração média ponderada ~7 anos. Diversificação de vencimentos em um único produto.',
        'composicao': 'Tesouros americanos de 1 a 30 anos. Distribuição balanceada por vencimento: curto ~30%, intermediário ~40%, longo ~30%. Yield médio atual ~4.4%.',
        'riscos': 'Duração de ~7 anos = sensível a variações de juros. Sem risco de crédito. Para brasileiros: exposição cambial USD/BRL.',
    },
    'VGSH': {
        'resumo': 'Vanguard Short-Term Government Bond ETF — Treasuries e agências de 1-3 anos. Custo de 0.04%/ano.',
        'estrategia': 'Replica o Bloomberg US 1-3 Year Government Float Adjusted Index. Inclui Treasuries e bonds de agências americanas (Fannie Mae, Freddie Mac) de curto prazo. Mínimo risco de duração e crédito quasi-zero.',
        'composicao': 'Treasuries e bonds de agências de 1-3 anos. Duração ~1.9 anos. Yield atual ~4.5-5%. Agências adicionam pequeno prêmio vs Treasuries puros.',
        'riscos': 'Yield menor que intermediate/long. Bonds de agências têm risco implícito do governo americano (não explícito). Câmbio.',
    },
    'VGIT': {
        'resumo': 'Vanguard Intermediate-Term Government Bond ETF — Treasuries e agências de 3-10 anos. Custo de 0.04%/ano.',
        'estrategia': 'Replica o Bloomberg US 3-10 Year Government Float Adjusted Index. Inclui Treasuries e bonds de agências de prazo intermediário. Equilíbrio entre yield e sensibilidade a juros.',
        'composicao': 'Treasuries e bonds de agências de 3-10 anos. Duração ~5.5 anos. Yield atual ~4.3-4.5%. Mix de vencimentos para capturar curva de juros intermediária.',
        'riscos': 'Sensível a movimentos na parte intermediária da curva de juros. Menos risco que VGLT mas mais que VGSH.',
    },
    'VGLT': {
        'resumo': 'Vanguard Long-Term Government Bond ETF — Treasuries e agências de 10+ anos. Alta duração com custo de 0.04%.',
        'estrategia': 'Replica o Bloomberg US Long Government Float Adjusted Index. Foco em longa duração para máxima sensibilidade a ciclos de juros. Alternativa ao TLT com custo menor (0.04% vs 0.15%).',
        'composicao': 'Treasuries e bonds de agências de 10-30 anos. Duração ~16 anos. Yield atual ~4.5-5%. Mix de Treasuries puros e agências de longo prazo.',
        'riscos': 'Alta sensibilidade a juros (duração ~16 anos). Em 2022 caiu ~30%. Risco de inflação. Câmbio.',
    },
    'BSV': {
        'resumo': 'Vanguard Short-Term Bond ETF — renda fixa diversificada de curto prazo (governo + corporativo). Custo de 0.04%.',
        'estrategia': 'Replica o Bloomberg US 1-5 Year Government/Credit Float Adjusted Index. Combinação de Treasuries, agências e bonds corporativos investment grade de 1-5 anos. Mais yield que apenas Treasuries com risco moderado.',
        'composicao': 'Treasuries e agências (~70%) + corporativos IG de curto prazo (~30%). Duração ~2.7 anos. Yield atual ~4.5-5%. ~2.500 títulos.',
        'riscos': 'Mínima sensibilidade a juros. Pequeno risco de crédito dos corporativos. Para brasileiros: câmbio USD/BRL.',
    },
    'BIV': {
        'resumo': 'Vanguard Intermediate-Term Bond ETF — renda fixa diversificada de prazo intermediário. Custo de 0.04%.',
        'estrategia': 'Replica o Bloomberg US 5-10 Year Government/Credit Float Adjusted Index. Governo + corporativo IG de prazo intermediário. Ponto de equilíbrio entre yield e sensibilidade a juros. Popular em portfólios balanceados.',
        'composicao': 'Treasuries/agências (~50%) + corporativos IG (~50%) de 5-10 anos. Duração ~6.5 anos. Yield atual ~4.5-5%. ~2.000 títulos.',
        'riscos': 'Sensível a variações de juros (duração ~6.5 anos). Risco de crédito corporativo moderado. Em 2022 caiu ~12%.',
    },
    'BLV': {
        'resumo': 'Vanguard Long-Term Bond ETF — renda fixa de longo prazo diversificada. Alta duração. Custo de 0.04%.',
        'estrategia': 'Replica o Bloomberg US Long Government/Credit Float Adjusted Index. Governo + corporativo IG de longo prazo (10-25 anos). Máxima exposição a variações de juros dentro do universo investment grade.',
        'composicao': 'Treasuries/agências (~50%) + corporativos IG de longo prazo (~50%). Duração ~15 anos. Yield atual ~5-5.5%. ~2.000 títulos de longo prazo.',
        'riscos': 'Muito sensível a juros (duração ~15 anos). Em 2022 caiu ~27%. Risco de crédito corporativo de longo prazo. Não adequado para horizontes curtos.',
    },
    'IGSB': {
        'resumo': 'iShares Short-Term Corporate Bond ETF — corporativos investment grade de 1-5 anos. Yield adicional vs Treasuries.',
        'estrategia': 'Replica o ICE BofA 1-5 Year US Corporate Index. Bonds de empresas americanas com rating de BBB a AAA e vencimento de 1-5 anos. Yield adicional de ~0.5-1% vs Treasuries de mesmo prazo como compensação pelo risco de crédito.',
        'composicao': '~3.200 bonds de empresas americanas de alta qualidade: bancos (JPMorgan, Goldman), industriais (Apple, Microsoft), utilities, saúde. Rating médio: A. Duração ~2.7 anos.',
        'riscos': 'Risco de crédito corporativo (pequeno para IG). Em recessão severa, spreads abrem e preço cai. Spread pode comprimir em mercados aquecidos reduzindo atratividade relativa.',
    },
    'IGIB': {
        'resumo': 'iShares Intermediate-Term Corporate Bond ETF — corporativos IG de 5-10 anos. Custo de 0.06%.',
        'estrategia': 'Replica o ICE BofA 5-10 Year US Corporate Index. Bonds de empresas investment grade de prazo intermediário. Yield ~4.8-5.5% com risco moderado de crédito e duração.',
        'composicao': '~3.000 bonds corporativos IG de 5-10 anos. Bancos, utilities, healthcare, telecom dominam. Rating médio: A/BBB+. Duração ~6.5 anos.',
        'riscos': 'Risco de crédito e duração combinados (~6.5 anos). Em recessão: tanto juros caem (ajuda) quanto spreads abrem (prejudica). Em 2022 caiu ~14%.',
    },
    'IGLB': {
        'resumo': 'iShares Long-Term Corporate Bond ETF — corporativos IG de 10+ anos. Máximo yield IG com máxima duração.',
        'estrategia': 'Replica o ICE BofA 10+ Year US Corporate Index. Longo prazo de corporativos investment grade. Yield adicional vs Treasuries de longo prazo compensa risco de crédito. Usado por gestores de pensão por imunização de passivos de longo prazo.',
        'composicao': '~1.500 bonds corporativos IG de 10-30 anos. Utilities, bancos, healthcare, telecom. Rating médio: A/BBB. Duração ~14 anos. Yield atual ~5.5%.',
        'riscos': 'Combinação de alto risco de crédito E alta duração. Em recessão com alta de spreads E juros altos: queda dupla. Em 2022 caiu ~26%.',
    },
    'USHY': {
        'resumo': 'iShares Broad USD High Yield Corporate Bond ETF — high yield americano amplo com custo de apenas 0.08%.',
        'estrategia': 'Replica o ICE BofA US High Yield Constrained Index. Mais amplo que HYG (~2.000 bonds vs ~1.000 do HYG) com custo menor (0.08% vs 0.49%). Inclui bonds de menor capitalização para maior diversificação.',
        'composicao': '~2.000 bonds HY americanos. Rating médio: BB/B. Mais diversificado que HYG/JNK. Energia, consumo, saúde, industriais. Yield atual ~7-8%.',
        'riscos': 'Risco de crédito alto (HY). Correlação com ações em crises. Em recessão, defaults sobem. Menor liquidez individual dos bonds vs HYG.',
    },
    'HYLB': {
        'resumo': 'Xtrackers USD High Yield Corporate Bond ETF — high yield com custo de apenas 0.05%. Um dos mais baratos do segmento.',
        'estrategia': 'Replica o Solactive USD High Yield Corporates Total Market Index. Cobertura ampla do mercado de high yield americano com custo muito abaixo dos concorrentes (0.05% vs 0.49% do HYG). Criado pela DWS/Xtrackers.',
        'composicao': '~2.000+ bonds HY americanos. Similar ao USHY em composição. Ampla diversificação por emissor e setor. Rating médio: BB/B. Yield atual ~7-8%.',
        'riscos': 'Mesmos riscos de HY: crédito, correlação com ações, recessão. Menor liquidez intradiária que HYG/JNK apesar do custo menor.',
    },
    'SJNK': {
        'resumo': 'SPDR Bloomberg Short-Term High Yield Bond ETF — high yield de 1-5 anos. Yield alto com menor duração que HYG.',
        'estrategia': 'Foco em bonds HY de vencimento de 1-5 anos. Reduz o risco de duração vs HYG/JNK (que incluem bonds mais longos) mantendo yield elevado. Em ambientes de juros incertos, preferível ao HY de longo prazo.',
        'composicao': 'Bonds corporativos HY de 1-5 anos. ~500-700 bonds. Rating BB/B. Yield atual ~7-8%. Duração ~2.5 anos vs ~3.5 anos do HYG.',
        'riscos': 'Risco de crédito HY presente mesmo em prazos curtos. Em recessão, defaults sobem em todos os vencimentos. Menor diversificação que HYG por restringir ao curto prazo.',
    },
    'FALN': {
        'resumo': 'iShares Fallen Angels USD Bond ETF — bonds que foram rebaixados de IG para HY. Yield alto + potencial de recuperação.',
        'estrategia': 'Replica o Bloomberg US HY Fallen Angel 3% Capped Index. "Fallen angels" são bonds que foram investment grade e foram rebaixados para HY. Pesquisas mostram que fallen angels têm performance melhor que HY nativo por qualidade superior e precificação defensiva no momento de entrada.',
        'composicao': '~200 bonds fallen angel. Incluem ex-investment grade de empresas reconhecidas: Ford, Occidental, Kraft Heinz, Macy\'s, Delta Air Lines. Rating médio: BB+/BB — melhor que HY nativo.',
        'riscos': 'Concentração em setores que sofreram rebaixamentos (energia, varejo, automotivo). Pode incluir empresas em dificuldade real. Menor diversificação que HYG.',
    },
    'STIP': {
        'resumo': 'iShares 0-5 Year TIPS Bond ETF — TIPS de curto prazo. Proteção contra inflação com mínima duração.',
        'estrategia': 'Foco em TIPS (Treasury Inflation-Protected Securities) com vencimento de 0-5 anos. Menor duração que TIP (~7 anos) = menos sensível a variações de juros reais. Proteção inflacionária mais imediata para o portfólio.',
        'composicao': 'TIPS americanos de 0-5 anos. Duração ~2.5 anos. Principal ajustado mensalmente pelo CPI. Yield real atual ~2-2.5%. Patrimônio de ~$15B.',
        'riscos': 'Yield real pode ser negativo se inflação cair abaixo do esperado. Menor yield que TIPS de longo prazo. Em deflação, o principal não cai abaixo do valor face (proteção).',
    },
    'MBB': {
        'resumo': 'iShares MBS ETF — títulos lastreados em hipotecas americanas (Mortgage-Backed Securities). Componente do AGG.',
        'estrategia': 'Replica o Bloomberg US MBS Float Adjusted Index. MBS são pools de hipotecas americanas securitizadas por Fannie Mae, Freddie Mac e Ginnie Mae (implicitamente garantidas pelo governo). Yield adicional vs Treasuries de mesmo prazo.',
        'composicao': 'Apenas MBS de agências americanas. Hipotecas residenciais de 15-30 anos securitizadas. Yield atual ~5-5.5%. Duração ~6 anos mas com risco de pré-pagamento.',
        'riscos': 'Risco de pré-pagamento (quando juros caem, hipotecas são quitadas antecipadamente — recebe principal quando reinvestimento é desfavorável). Risco de extensão (quando juros sobem, duração aumenta). Complexidade do produto.',
    },
    'PCY': {
        'resumo': 'Invesco Emerging Markets Sovereign Debt ETF — bonds soberanos de emergentes em USD. Yield alto + risco político.',
        'estrategia': 'Replica o DB Emerging Market USD Liquid Balanced Index. Bonds governamentais de países emergentes denominados em dólares americanos. Em USD, elimina o risco cambial das moedas locais (mas mantém risco político/econômico dos países).',
        'composicao': 'Bonds soberanos de ~50 países emergentes: Indonésia, México, Brasil, Argentina, Filipinas, Colômbia, Peru. Balanceado para diversificação regional. Yield atual ~6-7%.',
        'riscos': 'Risco de default soberano (Argentina, Equador, Sri Lanka já defaultaram). Risco político. Sensível ao ciclo do dólar (dólar forte = emergentes sofrem). Duração ~8 anos.',
    },
    'BWX': {
        'resumo': 'SPDR Bloomberg International Treasury Bond ETF — bonds soberanos de países desenvolvidos em MOEDAS LOCAIS.',
        'estrategia': 'Replica o Bloomberg Global Treasury ex-US Capped Index. Bonds governamentais de países desenvolvidos ex-EUA (Japão, Alemanha, Reino Unido, França, etc.) em suas moedas locais. Diversificação geográfica de renda fixa com exposição cambial múltipla.',
        'composicao': 'Japão (~25%), Alemanha (~10%), França (~10%), UK (~8%), Itália (~8%), Espanha (~7%), Canadá (~5%). ~1.000 bonds soberanos de ~20 países desenvolvidos. Yield baixo (~1-2% em termos de USD hedged).',
        'riscos': 'Risco cambial múltiplo (iene, euro, libra vs USD). Yield muito baixo para o risco. Japão com yield próximo de zero distorce o índice. Para brasileiros: câmbio adicional BRL/USD.',
    },
    'IGOV': {
        'resumo': 'iShares International Treasury Bond ETF — bonds soberanos internacionais desenvolvidos. Similar ao BWX.',
        'estrategia': 'Replica o S&P/Citigroup International Treasury Bond ex-US Index. Similar ao BWX mas com metodologia diferente. Exposição a bonds governamentais de países desenvolvidos ex-EUA. Yields baixos em moedas locais.',
        'composicao': 'Japão, Europa, Austrália, Canadá. Mix similar ao BWX em composição geográfica. ~900 bonds soberanos de países com alta qualidade de crédito.',
        'riscos': 'Risco cambial múltiplo. Yield estruturalmente baixo. Japão com yield próximo de zero. Menos relevante para geração de renda.',
    },
    'BNDX': {
        'resumo': 'Vanguard Total International Bond ETF — renda fixa internacional completa (governo + corporativo). Custo de 0.07%.',
        'estrategia': 'Replica o Bloomberg Global Aggregate ex-USD Float Adjusted RIC Capped Index com hedge cambial para USD. Cobertura global de renda fixa ex-EUA com proteção cambial — isola o retorno do bond sem o risco de câmbio.',
        'composicao': 'Bonds governamentais e corporativos IG de países desenvolvidos E emergentes ex-EUA. ~7.000 títulos. Japão, Alemanha, França dominam. Hedge para USD reduz mas não elimina riscos cambiais residuais.',
        'riscos': 'Custo do hedge cambial (~1-2%/ano) corrói yield. Yields internacionais baixos vs EUA. Risco de contraparte no hedge. Exposição a qualidade variável de crédito global.',
    },
    'VWOB': {
        'resumo': 'Vanguard Emerging Markets Government Bond ETF — bonds soberanos de emergentes em USD com custo baixo (0.20%).',
        'estrategia': 'Replica o Bloomberg USD Emerging Markets Government RIC Capped Index. Alternativa mais barata ao EMB (0.20% vs 0.39%) com cobertura similar de bonds soberanos de emergentes em dólares. Mais de 50 países.',
        'composicao': 'Bonds soberanos de emergentes em USD: China, Indonésia, México, Brasil, Arábia Saudita, Qatar. ~700 bonds de ~50 países. Yield atual ~6-7%. Duração ~8 anos.',
        'riscos': 'Risco de default soberano. Risco político de países individuais. Sensível ao dólar forte. Duração de ~8 anos = sensível a juros americanos também.',
    },

    # ══ INTERNACIONAL DESENVOLVIDOS — NOVOS ══════════════════════════════════
    'IEFA': {
        'resumo': 'iShares Core MSCI EAFE ETF — desenvolvidos ex-EUA com custo de 0.07%. Alternativa barata ao EFA (0.32%).',
        'estrategia': 'Replica o MSCI EAFE IMI Index (~3.000 empresas, incluindo small e mid caps vs ~750 do EFA). Custo 4.5x menor que EFA. Preferido para exposição de longo prazo a mercados desenvolvidos internacionais.',
        'composicao': 'Japão (~24%), UK (~14%), França (~10%), Suíça (~9%), Alemanha (~9%). ~3.000 empresas incluindo small/mid caps além das large caps do EFA. Nestlé, ASML, Samsung, Toyota, LVMH.',
        'riscos': 'Risco cambial múltiplo. Crescimento econômico menor vs EUA. Underperformou EUA por mais de uma década. Exposição a riscos políticos europeus.',
    },
    'SCHF': {
        'resumo': 'Schwab International Equity ETF — desenvolvidos ex-EUA via Schwab. Custo ultra-baixo de 0.06%/ano.',
        'estrategia': 'Replica o FTSE Developed ex US Index (~1.500 empresas). Custo idêntico ao IEFA mas com metodologia FTSE. Schwab oferece comissão zero para clientes. Cobertura de países desenvolvidos sem EUA e sem Canadá (diferença vs IEFA).',
        'composicao': 'Japão (~24%), UK (~14%), França (~10%), Suíça (~10%), Alemanha (~9%). ~1.500 empresas large e mid cap. Top: Nestlé, ASML, Novo Nordisk, LVMH, TotalEnergies.',
        'riscos': 'Mesmos do EFA/IEFA. Não inclui Canada (diferença vs IEFA). Risco cambial múltiplo. Dependência do ciclo econômico global.',
    },
    'VEA': {
        'resumo': 'Vanguard FTSE Developed Markets ETF — desenvolvidos ex-EUA via Vanguard com custo de 0.06%/ano.',
        'estrategia': 'Replica o FTSE Developed All Cap ex US Index. Similar ao SCHF mas inclui Canada (~9%) e ~4.000 empresas (large, mid, small caps). A Vanguard como cooperativa alinha interesses com cotistas.',
        'composicao': 'Japão (~21%), UK (~13%), Canada (~9%), França (~9%), Suíça (~9%). ~4.000 empresas de todos os tamanhos. Maior diversificação que EFA/SCHF.',
        'riscos': 'Risco cambial de múltiplas moedas. Inclui Canada diferente do EFA padrão. Underperformou EUA historicamente. Volatilidade dos mercados locais.',
    },
    'EWJ': {
        'resumo': 'iShares MSCI Japan ETF — exposição direta à bolsa japonesa. Afetado pelo iene e pela política do Bank of Japan.',
        'estrategia': 'Replica o MSCI Japan Index (~250 empresas). Acesso ao mercado japonês: empresas de exportação (Toyota, Sony, Canon) e domésticas (bancos, varejo). O iene é determinante — iene fraco beneficia exportadores mas reduz retorno em USD.',
        'composicao': 'Toyota (~4%), Sony (~3%), Mitsubishi UFJ (~3%), Keyence (~2%), Softbank (~2%), Shin-Etsu Chemical, Nintendo, Honda. Setores: Industrial (~20%), Consumo (~16%), TI (~13%), Financeiro (~12%).',
        'riscos': 'Risco do iene JPY/USD. Deflação histórica japonesa. Envelhecimento populacional severo. Política ultra-dovish do Bank of Japan pode mudar abruptamente. Crescimento econômico estruturalmente baixo.',
    },
    'EWG': {
        'resumo': 'iShares MSCI Germany ETF — exposição à maior economia da Europa. Muito dependente de exportações e energia.',
        'estrategia': 'Replica o MSCI Germany Index (~60 empresas). Alemanha é hub industrial da Europa: automóveis (Volkswagen, BMW, Mercedes), químicos (BASF, Bayer), engenharia (Siemens, SAP). Muito sensível ao ciclo econômico global.',
        'composicao': 'SAP (~14%), Siemens (~8%), Allianz (~8%), Deutsche Telekom (~6%), Volkswagen (~5%), BASF (~4%), BMW, Bayer, Adidas, Munich Re. ~60 empresas. Industrial (~25%), Financeiro (~18%), TI (~15%).',
        'riscos': 'Dependência de exportações (China como maior parceiro). Crise energética pós-Ucrânia. Transição automotiva para elétrico. Desindustrialização gradual. Risco euro/USD.',
    },
    'EWU': {
        'resumo': 'iShares MSCI United Kingdom ETF — bolsa britânica com alto dividend yield. Impactado pelo Brexit.',
        'estrategia': 'Replica o MSCI United Kingdom Index (~85 empresas). A bolsa britânica é rica em empresas de energia (Shell, BP), mineração (Rio Tinto, BHP), financeiro (HSBC, Barclays) e consumo global (Unilever, Diageo). Alto dividend yield histórico.',
        'composicao': 'Shell (~10%), AstraZeneca (~9%), HSBC (~7%), Unilever (~5%), BP (~4%), Rio Tinto (~4%), GSK, Diageo, BAE Systems. Financeiro (~24%), Energia (~18%), Saúde (~12%), Mineração (~10%).',
        'riscos': 'Impacto econômico do Brexit (incerteza regulatória, restrições comerciais). Risco da libra GBP. Concentração em setores "velha economia". Menor crescimento vs EUA.',
    },
    'BBJP': {
        'resumo': 'JPMorgan BetaBuilders Japan ETF — Japão com custo de 0.19%. Alternativa barata ao EWJ (0.49%).',
        'estrategia': 'Replica o Morningstar Japan Target Market Exposure Index. Similar ao EWJ mas com custo menor (~0.19% vs 0.49%). JPMorgan série BetaBuilders oferece acesso a países individuais com custo competitivo.',
        'composicao': 'Toyota, Sony, Mitsubishi UFJ, Keyence, Softbank. Similar ao EWJ em composição com mesma exposição ao mercado japonês e ao iene.',
        'riscos': 'Mesmos do EWJ: risco do iene, deflação japonesa, envelhecimento populacional, política do BoJ.',
    },
    'BBEU': {
        'resumo': 'JPMorgan BetaBuilders Europe ETF — Europa com custo de 0.09%. Cobertura ampla dos mercados desenvolvidos europeus.',
        'estrategia': 'Replica o Morningstar Developed Europe Target Market Exposure Index. Cobertura de UK, Alemanha, França, Suíça, Países Baixos e outros países europeus desenvolvidos. Alternativa barata ao EFA limitado à Europa.',
        'composicao': 'UK (~28%), França (~15%), Suíça (~13%), Alemanha (~13%), Países Baixos (~8%), Suécia (~6%). Nestlé, ASML, Shell, Novo Nordisk, LVMH, Roche entre os maiores.',
        'riscos': 'Risco euro/GBP vs USD. Desafios estruturais da economia europeia. Riscos políticos (partidos populistas). Dependência energética. Crescimento mais lento que EUA.',
    },
    'ACWI': {
        'resumo': 'iShares MSCI ACWI ETF — mercado global completo: EUA + desenvolvidos + emergentes em uma posição.',
        'estrategia': 'Replica o MSCI ACWI (All Country World Index) — cobertura de ~50 países desenvolvidos e emergentes. EUA representa ~60%, desenvolvidos ex-EUA ~28%, emergentes ~12%. Uma única posição para diversificação mundial máxima.',
        'composicao': 'EUA (~60%): Apple, Microsoft, Nvidia. Desenvolvidos ex-EUA (~28%): ASML, Nestlé, Toyota. Emergentes (~12%): Samsung, Tencent, Alibaba. ~2.800 empresas globais.',
        'riscos': 'Dominância americana (~60%) — não é tão "global" quanto parece. Custo de 0.32% relativamente alto. Risco cambial múltiplo. Exposição a todos os riscos de mercado globais.',
    },
    'ACWX': {
        'resumo': 'iShares MSCI ACWI ex US ETF — mercado global excluindo EUA. Diversificação pura fora dos EUA.',
        'estrategia': 'Replica o MSCI ACWI ex USA Index — todos os países desenvolvidos e emergentes excluindo os EUA. Complemento natural para investidores que já têm exposição doméstica americana via SPY/VOO. ~2.300 empresas de ~45 países.',
        'composicao': 'Japão (~14%), UK (~9%), China (~8%), França (~7%), Canada (~7%), Índia (~5%), Alemanha (~5%), Austrália (~5%). Samsung, Shell, Nestle, Tencent, Toyota.',
        'riscos': 'Risco cambial múltiplo. Menor liquidez que ACWI completo. Exposição a riscos políticos de emergentes. Historicamente underperforma EUA no longo prazo.',
    },
    'URTH': {
        'resumo': 'iShares MSCI World ETF — apenas países DESENVOLVIDOS (~23 países). Exclui emergentes do ACWI.',
        'estrategia': 'Replica o MSCI World Index — cobertura dos mercados desenvolvidos globais sem emergentes. EUA (~68%), Japão (~6%), UK (~4%), França (~3%), Canada (~3%). Menos volátil que ACWI por excluir emergentes mais arriscados.',
        'composicao': 'EUA (~68%): Apple, Microsoft, Nvidia. Japão (~6%), UK (~4%), França (~3%). ~1.500 empresas de 23 países desenvolvidos. Custo de 0.24%.',
        'riscos': 'Ainda muito concentrado em EUA (~68%). Risco cambial de múltiplas moedas desenvolvidas. Exclui China e Índia — mercados de alto crescimento. Custo maior que ETFs americanos puros.',
    },
    'EWL': {
        'resumo': 'iShares MSCI Switzerland ETF — Suíça: mercado farmacêutico, financeiro e de bens de luxo. Franco suíço como reserva de valor.',
        'estrategia': 'Replica o MSCI Switzerland 25/50 Index (~30 empresas). Suíça é sede de empresas globais: Nestlé (alimentos), Novartis/Roche (farmácia), UBS/Credit Suisse (finanças), Richemont (luxo). Franc suíço é moeda de reserva histórica.',
        'composicao': 'Nestlé (~15%), Novartis (~14%), Roche (~13%), UBS (~8%), ABB (~5%), Zurich Insurance (~5%), Richemont (~5%). ~30 empresas. Saúde (~35%), Consumo Básico (~20%), Financeiro (~15%).',
        'riscos': 'Concentração em poucas empresas (~30). Franco suíço pode valorizar vs USD (reduz retorno). Custo de 0.49%. Risco de eventos específicos (UBS/Credit Suisse em 2023).',
    },
    'EWQ': {
        'resumo': 'iShares MSCI France ETF — França: luxo, energia e finanças. Exposição ao euro e à economia francesa.',
        'estrategia': 'Replica o MSCI France Index (~70 empresas). França é lar de líderes globais em luxo (LVMH, Hermès, Kering), energia (TotalEnergies), finanças (BNP Paribas) e serviços (Airbus, Schneider Electric).',
        'composicao': 'LVMH (~18%), TotalEnergies (~8%), Sanofi (~7%), Airbus (~6%), BNP Paribas (~5%), Schneider Electric (~5%), Hermès (~5%). Consumo Discricionário/Luxo (~30%), Energia (~10%), Saúde (~12%).',
        'riscos': 'Risco euro/USD. Concentração em luxo — sensível a consumo da classe alta chinesa. Risco político francês (instabilidade do governo). Crescimento econômico europeu lento.',
    },
    'EWI': {
        'resumo': 'iShares MSCI Italy ETF — Itália: financeiro, energia e consumo. Alta dívida pública cria risco de crédito soberano.',
        'estrategia': 'Replica o MSCI Italy Index (~30 empresas). Itália tem maior razão dívida/PIB da Europa depois da Grécia. Empresas: ENI (petróleo), Enel (energia), Stellantis (automóveis), Intesa Sanpaolo, UniCredit.',
        'composicao': 'ENI (~12%), Enel (~11%), Intesa Sanpaolo (~10%), UniCredit (~9%), Stellantis (~8%), Mediobanca, Prysmian, Ferrari. Financeiro (~27%), Energia (~20%), Industrial (~15%).',
        'riscos': 'Risco soberano italiano (dívida/PIB ~140%). Risco euro/USD. Vulnerabilidade bancária sistêmica. Crescimento econômico historicamente fraco. Concentração em setores tradicionais.',
    },
    'EWP': {
        'resumo': 'iShares MSCI Spain ETF — Espanha: financeiro, utilities e telecom. Exposição à América Latina via Santander/Telefónica.',
        'estrategia': 'Replica o MSCI Spain Index (~25 empresas). Espanha tem empresas com grande exposição à América Latina: Banco Santander, Telefónica, BBVA — o que cria correlação indireta com emergentes latino-americanos.',
        'composicao': 'Inditex (Zara) (~25%), Banco Santander (~14%), BBVA (~11%), Iberdrola (~10%), Telefónica (~7%), Repsol, Cellnex. Financeiro (~30%), Consumo (~25%), Utilities (~15%).',
        'riscos': 'Risco euro/USD. Exposição à América Latina via grandes bancos. Alta dívida histórica (embora reduzida). Dependência do turismo. Mercado relativamente pequeno.',
    },
    'EWD': {
        'resumo': 'iShares MSCI Sweden ETF — Suécia: inovação, industriais de qualidade e coroa sueca.',
        'estrategia': 'Replica o MSCI Sweden Index (~35 empresas). Suécia é sede de empresas globais de qualidade: Atlas Copco (engenharia), Volvo (caminhões), Ericsson (telecom), Swedbank/Handelsbanken (finanças), H&M (varejo).',
        'composicao': 'Atlas Copco (~13%), Investor AB (~10%), Volvo (~7%), Ericsson (~5%), H&M (~5%), Swedbank, Hexagon, SKF, Sandvik. Industrial (~30%), Financeiro (~25%), TI (~10%).',
        'riscos': 'Risco corona sueca SEK/USD. Mercado pequeno (~35 empresas). Alta sensibilidade ao ciclo industrial global. Custo de 0.49%.',
    },
    'EWN': {
        'resumo': 'iShares MSCI Netherlands ETF — Países Baixos: ASML, Shell, Heineken. Bolsa com algumas das melhores empresas europeias.',
        'estrategia': 'Replica o MSCI Netherlands Index (~20 empresas). Amsterdã é sede de gigantes globais: ASML (líder mundial em litografia para chips), Shell (energia), Heineken (cervejas), ING (finanças), ASML responde por ~30%+ do índice.',
        'composicao': 'ASML (~33%), Shell (~17%), ING (~8%), Heineken (~7%), NN Group (~5%), Wolters Kluwer, Akzo Nobel. TI (~33%), Energia (~17%), Financeiro (~15%). ~20 empresas.',
        'riscos': 'Concentração extrema em ASML — risco geopolítico Taiwan + regulação exportação de chips. Mercado pequeno. Risco euro/USD. Custo de 0.49%.',
    },
    'EWA': {
        'resumo': 'iShares MSCI Australia ETF — Austrália: mineração, bancos e energia. Alta exposição à demanda da China por commodities.',
        'estrategia': 'Replica o MSCI Australia Index (~60 empresas). Economia australiana muito ligada à demanda chinesa por minérios (ferro, carvão) e energia. Dólar australiano correlacionado ao ciclo de commodities.',
        'composicao': 'BHP (~20%), Commonwealth Bank (~10%), CSL (~8%), NAB (~6%), Westpac (~5%), ANZ, Rio Tinto, Macquarie. Financeiro (~30%), Materiais (~25%), Saúde (~10%). ~60 empresas.',
        'riscos': 'Alta dependência da China (maior parceiro comercial). Risco do dólar australiano AUD/USD. Concentração em materiais básicos. Sensível ao ciclo de commodities.',
    },
    'EWC': {
        'resumo': 'iShares MSCI Canada ETF — Canadá: finanças, energia e materiais. Economia muito ligada ao petróleo e ao mercado americano.',
        'estrategia': 'Replica o MSCI Canada Index (~70 empresas). Canadá tem economia integrada com os EUA (maior parceiro comercial). Bolsa concentrada em: bancos grandes (Royal Bank, TD), energia (Suncor, Enbridge) e mineração (Barrick, Agnico Eagle).',
        'composicao': 'Royal Bank of Canada (~10%), Toronto-Dominion Bank (~9%), Enbridge (~7%), Canadian Pacific (~5%), Suncor (~4%), Bank of Montreal, Brookfield. Financeiro (~35%), Energia (~18%), Materiais (~12%).',
        'riscos': 'Risco do dólar canadense CAD/USD. Alta dependência do preço do petróleo. Concentração em financeiro e energia. Exposição ao mercado imobiliário canadense (bolha histórica).',
    },
    'EWH': {
        'resumo': 'iShares MSCI Hong Kong ETF — Hong Kong: bancos e imobiliário. Risco crescente de influência política da China.',
        'estrategia': 'Replica o MSCI Hong Kong Index (~30 empresas). HK é hub financeiro asiático, mas com crescente influência política de Pequim após as leis de segurança nacional de 2020. Imobiliário e bancos dominam.',
        'composicao': 'AIA Group (~28%), Hong Kong Exchanges (~15%), CK Hutchison (~6%), Hang Lung Properties (~5%), New World Development. Financeiro (~50%), Imobiliário (~30%). ~30 empresas.',
        'riscos': 'Risco político crescente (influência de Pequim). HKD atrelado ao USD mas com riscos de desvinculação. Crise imobiliária chinesa afeta HK. Fuga de capital e talentos pós-2020.',
    },
    'EWS': {
        'resumo': 'iShares MSCI Singapore ETF — Cingapura: hub financeiro asiático. Bancos, REITs e industriais.',
        'estrategia': 'Replica o MSCI Singapore Index (~25 empresas). Cingapura é um dos maiores centros financeiros da Ásia: DBS, OCBC, UOB (grandes bancos). REITs de alta qualidade listados na SGX. Porta de entrada para Sudeste Asiático.',
        'composicao': 'DBS Group (~30%), Oversea-Chinese Banking (~17%), United Overseas Bank (~14%), Singapore Telecom (~8%), CapitaLand (~5%). Financeiro (~55%), Imobiliário (~20%), Industrial (~10%).',
        'riscos': 'Concentração extrema em 3 bancos (~60%). Risco do dólar de Cingapura SGD/USD. Exposição ao ciclo econômico da Ásia. Mercado pequeno.',
    },

    # ══ MERCADOS EMERGENTES — NOVOS ═══════════════════════════════════════════
    'IEMG': {
        'resumo': 'iShares Core MSCI Emerging Markets ETF — emergentes com custo de 0.09%. Alternativa barata ao EEM (0.70%).',
        'estrategia': 'Replica o MSCI Emerging Markets IMI Index (~3.000 empresas). Cobre grande, médio e pequeno cap de emergentes. Custo 8x menor que EEM com exposição similar. Preferido para posições de longo prazo em emergentes.',
        'composicao': 'China (~27%), Taiwan (~15%), Índia (~20%), Coreia (~12%), Brasil (~5%), Arábia Saudita (~4%). Top: Samsung, Taiwan Semi, Alibaba, Tencent, Reliance. ~3.000 empresas.',
        'riscos': 'Mesmos riscos de emergentes: câmbio, política, regulação. Alta concentração em China/Taiwan com risco geopolítico. Índia com valuation premium.',
    },
    'SCHE': {
        'resumo': 'Schwab Emerging Markets Equity ETF — emergentes via Schwab com custo de 0.11%. Excelente custo-benefício.',
        'estrategia': 'Replica o FTSE Emerging Index (~1.300 empresas). Similar ao IEMG mas com metodologia FTSE. Diferença: inclui Coreia do Sul como emergente (FTSE) vs desenvolvido (MSCI). Comissão zero para clientes Schwab.',
        'composicao': 'China (~28%), Taiwan (~17%), Índia (~21%), Brasil (~5%), Arábia Saudita (~4%), Coreia do Sul (~3% — diferença vs MSCI). Top: Samsung, TSMC, Alibaba, Tencent, Reliance.',
        'riscos': 'Mesmos de IEMG. Tratamento diferente da Coreia vs MSCI pode causar divergência. Concentração em Ásia.',
    },
    'MCHI': {
        'resumo': 'iShares MSCI China ETF — ações chinesas amplas: H-shares HK + ADRs EUA + A-shares. Maior exposição à China.',
        'estrategia': 'Replica o MSCI China All Shares Index. Cobre ações de empresas chinesas listadas em múltiplas bolsas: Hong Kong (H-shares), EUA (ADRs), e acesso às A-shares via Stock Connect. Mais amplo que FXI.',
        'composicao': 'Tencent (~15%), Alibaba (~8%), Meituan (~5%), JD.com (~4%), Baidu (~4%), PDD Holdings, Xiaomi, NetEase, China Construction Bank. ~600 empresas de todos os setores.',
        'riscos': 'Risco regulatório do governo chinês. Estrutura VIE para internet. Risco de delisting de ADRs. Desaceleração econômica chinesa. Geopolítica Taiwan. Setor imobiliário em crise.',
    },
    'EWT': {
        'resumo': 'iShares MSCI Taiwan ETF — Taiwan: TSMC domina (~25%). Exposição central ao mercado de semicondutores globais.',
        'estrategia': 'Replica o MSCI Taiwan 25/50 Index (~100 empresas). Taiwan é o coração da indústria de semicondutores global: TSMC fabrica chips para Apple, Nvidia, AMD, Qualcomm. Qualquer ETF de Taiwan é essencialmente uma aposta em TSMC.',
        'composicao': 'TSMC (~25%), Hon Hai (Foxconn, ~5%), MediaTek (~5%), Cathay Financial (~3%), Delta Electronics (~2%). TI (~68%), Financeiro (~11%), Industrial (~8%). ~100 empresas.',
        'riscos': 'RISCO GEOPOLÍTICO EXTREMO: China reivindica Taiwan — invasão militar seria catastrófica para o ETF. TSMC representa 25% do índice. Custo de 0.57%.',
    },
    'EWY': {
        'resumo': 'iShares MSCI South Korea ETF — Coreia do Sul: Samsung, SK Hynix, POSCO. Hub de tecnologia e indústria pesada.',
        'estrategia': 'Replica o MSCI Korea 25/50 Index (~100 empresas). Coreia é potência industrial: eletrônicos (Samsung), chips de memória (SK Hynix), aço (POSCO), químicos (LG Chem), automóveis (Hyundai). Alta dependência de exportações.',
        'composicao': 'Samsung Electronics (~25%), SK Hynix (~6%), Hyundai Motor (~4%), LG Energy Solution (~4%), Celltrion (~3%), Kakao, KB Financial, POSCO. TI (~40%), Financeiro (~13%), Consumo (~11%). ~100 empresas.',
        'riscos': 'Risco geopolítico da Coreia do Norte. Risco won KRW/USD. Concentração em chaebol (conglomerados familiares com governança questionável). Alta dependência de ciclos de semicondutores.',
    },
    'INDY': {
        'resumo': 'iShares India 50 ETF — as 50 maiores empresas indianas. Mais concentrado que INDA.',
        'estrategia': 'Replica o Nifty 50 Index — as 50 maiores empresas da NSE (National Stock Exchange da Índia). Mais concentrado que INDA mas com maior liquidez das holdings individuais. Índia é a economia de maior crescimento entre os países grandes.',
        'composicao': 'Reliance Industries (~11%), HDFC Bank (~13%), Infosys (~7%), ICICI Bank (~7%), TCS (~5%), Bajaj Finance, Axis Bank, Larsen & Toubro, Hindustan Unilever. 50 empresas líderes setoriais.',
        'riscos': 'Valuation premium persistente (P/E ~25-30x vs EM médio ~12x). Custo alto (0.90%). Risco da rupia indiana INR/USD. Riscos políticos (eleições). Menor diversificação que INDA (50 vs 85 empresas).',
    },
    'SMIN': {
        'resumo': 'iShares MSCI India Small-Cap ETF — small caps indianas. Exposição ao crescimento doméstico da Índia.',
        'estrategia': 'Replica o MSCI India Small Cap Index. Small caps indianas têm maior exposição ao consumo doméstico e crescimento interno vs large caps (mais exportação). Alta volatilidade mas potencial de crescimento maior.',
        'composicao': '~400 small caps indianas. Setores: Industrial (~17%), Financeiro (~15%), Consumo Discricionário (~14%), Materiais (~12%), Saúde (~10%). Market cap médio ~$1-3B.',
        'riscos': 'Alta volatilidade de small caps em emergentes. Liquidez limitada. Custo alto (0.74%). Risco cambial INR/USD. Valuation ainda premium vs outros emergentes.',
    },
    'EWW': {
        'resumo': 'iShares MSCI Mexico ETF — México: bancos, indústria e nearshoring. Peso forte por fluxo comercial com EUA.',
        'estrategia': 'Replica o MSCI Mexico IMI 25/50 Index (~50 empresas). México beneficia do nearshoring (empresas relocando fábricas próximas ao EUA) e do USMCA. Peso mexicano forte historicamente mas volátil com eventos políticos.',
        'composicao': 'Grupo Mexico (~18%), Walmart Mexico (~14%), FEMSA (~9%), Grupo Financiero Banorte (~8%), America Movil (~7%), Televisa, Cemex. Materiais (~22%), Consumo Básico (~20%), Financeiro (~18%).',
        'riscos': 'Risco político (AMLO/Sheinbaum — intervencionismo). Risco peso MXN/USD. Dependência da economia americana. Cartel/violência como risco operacional. Incerteza sobre investimento estrangeiro.',
    },
    'ECH': {
        'resumo': 'iShares MSCI Chile ETF — Chile: cobre, lithium e finanças. Exposto ao ciclo de commodities da transição energética.',
        'estrategia': 'Replica o MSCI Chile IMI 25/50 Index (~25 empresas). Chile é o maior produtor mundial de cobre e segundo de lítio — materiais críticos para transição energética (EVs, baterias, energia solar). Mercado pequeno mas com recursos naturais estratégicos.',
        'composicao': 'SQM (lítio, ~15%), Banco Santander Chile (~10%), Empresas Copec (~8%), Falabella (~7%), Engie Chile (~6%), Colbún, Banco de Chile. Materiais (~30%), Financeiro (~25%), Utilities (~15%).',
        'riscos': 'Alta exposição a preço do cobre e lítio. Risco político (tentativa de nova constituição). Risco peso chileno CLP/USD. Mercado muito pequeno (~25 empresas). Concentração em SQM.',
    },
    'ILF': {
        'resumo': 'iShares Latin America 40 ETF — as 40 maiores empresas da América Latina. Brasil + México respondem por ~80%.',
        'estrategia': 'Replica o S&P Latin America 40 Index. Cobertura das maiores empresas da região: Brasil (~58%), México (~22%), Chile (~10%), Colômbia (~6%), Peru (~4%). Concentrado em commodities, bancos e telecomunicações.',
        'composicao': 'Petrobras (~11%), Vale (~8%), Itaú Unibanco (~7%), Bradesco (~6%), FEMSA (~5%), Grupo Mexico (~5%), America Movil (~4%). 40 empresas. Materiais (~22%), Financeiro (~20%), Energia (~18%).',
        'riscos': 'Alta exposição ao Brasil (58%) com todos seus riscos político-cambiais. Concentração em commodities. Risco cambial múltiplo (BRL + MXN). Instabilidade política regional histórica.',
    },
    'GXG': {
        'resumo': 'Global X MSCI Colombia ETF — Colômbia: energia, financeiro e telecom. Mercado pequeno com alto risco político.',
        'estrategia': 'Replica o MSCI Colombia IMI 25/50 Index. Colômbia é importante produtor de petróleo (Ecopetrol) e tem mercado financeiro em desenvolvimento. Peso colombiano sujeito a alta volatilidade política.',
        'composicao': 'Ecopetrol (~35%), Bancolombia (~18%), GrupoSura (~9%), Grupo Argos (~7%), Celsia (~6%). Energia (~40%), Financeiro (~30%), Industrial (~15%). ~15 empresas. Muito concentrado.',
        'riscos': 'Mercado extremamente pequeno (~15 empresas). Alta concentração em Ecopetrol. Risco político elevado (presidente Petro). Risco peso colombiano COP/USD. Guerrilha/narcotráfico como risco operacional.',
    },
    'ARGT': {
        'resumo': 'Global X MSCI Argentina ETF — Argentina: MercadoLibre domina. Altíssimo risco político e cambial histórico.',
        'estrategia': 'Replica o MSCI Argentina IMI 25/50 Index. Argentina tem histórico de defaults soberanos (2001, 2020). MercadoLibre (~50% do índice) cresceu tanto que o ETF é largamente um proxy do MELI com alguma diversificação local.',
        'composicao': 'MercadoLibre (~50%), Loma Negra (~8%), Grupo Supervielle (~7%), Banco Macro (~7%), Transportadora de Gas del Norte. Financeiro e MELI dominam.',
        'riscos': 'RISCO EXTREMO. Argentina tem histórico de hiperinflação e defaults. Peso argentino ARS despencando historicamente. MercadoLibre responde por metade — se MELI cair, o ETF cai junto. Controles de capital.',
    },
    'EZA': {
        'resumo': 'iShares MSCI South Africa ETF — África do Sul: mineração, finanças e varejo. Rand volátil e risco político crescente.',
        'estrategia': 'Replica o MSCI South Africa IMI 25/50 Index (~50 empresas). África do Sul é a maior economia da África. Rica em minerais (ouro, platina, diamantes). Naspers (maior empresa) domina por ser acionista do Tencent.',
        'composicao': 'Naspers/Prosus (~24%), FirstRand (~8%), Standard Bank (~7%), Gold Fields (~5%), Anglo American (~5%), MTN Group, AngloGold. Financeiro (~25%), Materiais (~20%), Consumo (~15%).',
        'riscos': 'Risco do rand ZAR/USD (uma das moedas mais voláteis de emergentes). Instabilidade elétrica (load shedding). Risco político crescente (ANC perde maioria). Violência e criminalidade. Alta desigualdade social.',
    },
    'EPHE': {
        'resumo': 'iShares MSCI Philippines ETF — Filipinas: bancos, imobiliário e conglomerados familiares. Crescimento demográfico forte.',
        'estrategia': 'Replica o MSCI Philippines IMI 25/50 Index (~30 empresas). Filipinas tem crescimento demográfico favorável, alta penetração de remessas (OFW — trabalhadores no exterior) e economia de serviços em ascensão.',
        'composicao': 'SM Investments (~18%), Ayala Corp (~12%), BDO Unibank (~10%), Bank of the Philippine Islands (~8%), JG Summit (~7%). Financeiro (~30%), Imobiliário (~20%), Conglomerados (~25%).',
        'riscos': 'Governança corporativa fraca (conglomerados familiares dominam). Risco peso filipino PHP/USD. Vulnerabilidade a tufões/desastres naturais. Corrupção política. Mercado pequeno (~30 empresas).',
    },
    'THD': {
        'resumo': 'iShares MSCI Thailand ETF — Tailândia: exportações, turismo e manufatura. Exposição ao ciclo econômico asiático.',
        'estrategia': 'Replica o MSCI Thailand IMI 25/50 Index (~60 empresas). Tailândia é hub de manufatura (automóveis, eletrônicos) e turismo (Bangkok, Phuket). Economia de renda média em transição para mais serviços.',
        'composicao': 'PTT (~10%), Bangkok Bank (~8%), Kasikornbank (~8%), Siam Cement (~7%), CP ALL (~6%), Advanced Info Service, Central Group. Financeiro (~30%), Energia (~18%), Industrial (~15%).',
        'riscos': 'Instabilidade política (golpes militares históricos). Risco baht tailandês THB/USD. Dependência do turismo. Envelhecimento populacional acelerado. Exposição ao ciclo econômico da China.',
    },
    'EWM': {
        'resumo': 'iShares MSCI Malaysia ETF — Malásia: petróleo, finanças e palmiste. Exposição ao Sudeste Asiático.',
        'estrategia': 'Replica o MSCI Malaysia IMI 25/50 Index (~50 empresas). Malásia tem economia diversificada: petróleo (Petronas), eletrônicos (penhaur elétrico), finanças islâmicas e agrícola (palma). Hub para investimento em Sudeste Asiático.',
        'composicao': 'Public Bank (~10%), Malayan Banking (~9%), CIMB Group (~8%), Petronas (~7%), IHH Healthcare (~5%), Axiata, Tenaga Nasional. Financeiro (~30%), Energia (~15%), Saúde (~10%).',
        'riscos': 'Risco ringgit MYR/USD (afetado pelo dólar forte e preço do petróleo). Governança corporativa questionável. Dependência de commodities. Risco político (korupsi histórica). Mercado relativamente ilíquido.',
    },
    'TUR': {
        'resumo': 'iShares MSCI Turkey ETF — Turquia: alta inflação, lira devastada, mas valuation extremamente barato.',
        'estrategia': 'Replica o MSCI Turkey IMI 25/50 Index (~25 empresas). Turquia passou por crise cambial severa (lira perdeu 90%+ vs USD em 10 anos). Bolsa em liras sobe muito em termos nominais mas retorno em USD é desastroso historicamente.',
        'composicao': 'Akbank (~10%), Garanti BBVA (~9%), Isbank (~8%), Türk Hava Yollari (THY, ~7%), Koc Holding (~7%), Eregli Demir, Haci Omer Sabanci. Financeiro (~35%), Industrial (~15%), Energia (~12%).',
        'riscos': 'Risco lira TRY/USD extremo (inflação >50% histórica). Política econômica heterodoxa do presidente Erdogan. Risco geopolítico (fronteira com Síria/Iraque). Imprevisibilidade regulatória. Valuation barato pode ser "armadilha".',
    },
    'EPOL': {
        'resumo': 'iShares MSCI Poland ETF — Polônia: economias da Europa Central em crescimento, próxima à guerra na Ucrânia.',
        'estrategia': 'Replica o MSCI Poland IMI 25/50 Index (~25 empresas). Polônia é a maior economia da Europa Central: bancária, energia e varejo. Membro da UE mas não do euro (zloty próprio). Proximidade com Ucrânia é risco geopolítico.',
        'composicao': 'PKO Bank Polski (~16%), PKN Orlen (~14%), Bank Pekao (~10%), PZU (~9%), Allegro (~8%), mBank, Dino Polska. Financeiro (~35%), Energia (~15%), Consumo (~15%). ~25 empresas.',
        'riscos': 'Risco geopolítico da guerra na Ucrânia (fronteira direta). Risco zloty PLN/USD. Tensões com UE sobre estado de direito. Dependência de energia russa historicamente.',
    },
    'GEM': {
        'resumo': 'Goldman Sachs ActiveBeta Emerging Markets ETF — emergentes com factor tilts da Goldman Sachs. Custo de 0.45%.',
        'estrategia': 'Gestão semi-ativa (factor investing) pela Goldman Sachs. Seleciona ações de emergentes com scores positivos nos quatro fatores: Value, Momentum, Quality e Low Volatility. Rebalanceamento trimestral.',
        'composicao': 'China (~25%), Taiwan (~15%), Índia (~18%), Coreia (~12%), Brasil (~5%). Similar ao EEM/IEMG mas com tilts de factor. ~500 ações de emergentes.',
        'riscos': 'Gestão ativa pode underperformar índice passivo (EEM/IEMG). Custo maior que IEMG (0.45% vs 0.09%). Mesmos riscos estruturais de mercados emergentes.',
    },
    'ASHR': {
        'resumo': 'Xtrackers Harvest CSI 300 China A-Shares ETF — acesso direto às ações A da bolsa continental chinesa (Shanghai/Shenzhen).',
        'estrategia': 'Replica o CSI 300 Index — as 300 maiores ações A listadas em Shanghai e Shenzhen. Acesso ao mercado DOMÉSTICO chinês (não as H-shares de Hong Kong ou ADRs). As A-shares são onde o investidor local chinês investe.',
        'composicao': 'Top empresas da bolsa continental: Kweichow Moutai (destilaria premium, ~5%), CATL (baterias EV, ~4%), Ping An Insurance (~4%), BYD (~3%), China Merchants Bank (~3%). ~300 empresas. Financeiro (~30%), Consumo (~20%), Industrial (~12%).',
        'riscos': 'Risco regulatório e político do governo chinês direto (mais que ETFs de H-shares). Risco yuan CNY/USD. Mercado dominado por investidores de varejo (alta volatilidade). Acesso via Stock Connect pode ter restrições.',
    },

    # ══ DIVIDENDOS — NOVOS ════════════════════════════════════════════════════
    'SPHD': {
        'resumo': 'Invesco S&P 500 High Dividend Low Volatility ETF — alto yield + baixa volatilidade entre as ações do S&P 500.',
        'estrategia': 'Seleciona as 50 ações do S&P 500 com maior dividend yield E menor volatilidade nos últimos 12 meses. Rebalanceado semestralmente. Combina renda com estabilidade — setor Utilities, Saúde e Consumo Básico dominam.',
        'composicao': '50 ações: Altria, AT&T, Verizon, Kinder Morgan, PPL Corp, Leggett & Platt, Seagate Technology. Utilities (~20%), Financeiro (~17%), Consumo Básico (~17%), Saúde (~15%). Dividend yield atual ~4%.',
        'riscos': 'Concentração em setores defensivos — underperforma em bull markets de tech. Alta sensibilidade a juros ("bond proxy"). Empresas de alto yield podem cortar dividendo. Custo de 0.30%.',
    },
    'DGRW': {
        'resumo': 'WisdomTree US Quality Dividend Growth ETF — ações com crescimento de dividendo + qualidade fundamentalista.',
        'estrategia': 'Seleciona ações com: (1) histórico de crescimento de dividendo, (2) altas previsões de crescimento de EPS, (3) alto ROE e ROA. Gestão ativa quantitativa pela WisdomTree. Rebalanceado anualmente.',
        'composicao': 'Microsoft (~6%), Apple (~5%), Broadcom (~4%), Nvidia (~4%), Cisco (~3%), Home Depot (~3%), UnitedHealth, Texas Instruments. ~300 ações. Tecnologia (~25%), Saúde (~15%), Consumo Básico (~12%).',
        'riscos': 'Exposição significativa a tech (similar ao QQQ em peso). Custo de 0.28%. Gestão ativa pode underperformar. Foco em crescimento de EPS pode incluir empresas com dividendo baixo atual.',
    },
    'DIVO': {
        'resumo': 'Amplify CWP Enhanced Dividend Income ETF — dividendos + covered calls selecionadas em ações individuais.',
        'estrategia': 'Gestão ativa: portfólio de ~25 ações de dividendo de qualidade + venda seletiva de covered calls sobre posições individuais (não no índice todo, como JEPI/JEPQ). Seletividade maior na escolha de quando vender calls vs JEPI.',
        'composicao': '~25 posições concentradas: UnitedHealth, Visa, Microsoft, JPMorgan, Home Depot, Broadcom, Apple, Exxon Mobil. Portfólio muito concentrado vs JEPI (~130 ações). Covered calls sobre posições selecionadas.',
        'riscos': 'Alta concentração (25 posições vs 130 do JEPI). Gestão ativa subjetiva. Custo de 0.55%. Upside potencialmente mais limitado que mercado amplo. Risco de seleção na escolha das calls.',
    },
    'SPYD': {
        'resumo': 'SPDR Portfolio S&P 500 High Dividend ETF — as 80 ações de maior yield do S&P 500. Custo ultra-baixo de 0.07%.',
        'estrategia': 'Seleciona as 80 ações do S&P 500 com maior dividend yield. Equal-weight entre as 80 — cada ação recebe ~1.25% do portfólio. Rebalanceado semestralmente. Dividend yield atual ~4-5%.',
        'composicao': '80 ações do S&P 500 de alto yield, equal-weight. Utilities, Energia, Financeiro, Real Estate dominam. Altria, AT&T, Iron Mountain, Philip Morris, Devon Energy entre os maiores por yield.',
        'riscos': 'Equal-weight em alto yield = concentração em setores defensivos/energia. Empresas de alto yield podem cortar dividendo. Underperforma S&P 500 total em bull markets de crescimento.',
    },
    'JEPQ': {
        'resumo': 'JPMorgan Nasdaq Equity Premium Income ETF — covered calls no Nasdaq para gerar renda mensal (~9-11%/ano).',
        'estrategia': 'Versão Nasdaq do JEPI. Portfólio de ações do Nasdaq 100 + venda de ELNs (Equity Linked Notes) baseadas em calls do QQQ. Maior exposição a tech que o JEPI (S&P 500). Distribuição mensal de renda.',
        'composicao': 'Apple, Microsoft, Nvidia, Meta, Amazon, Alphabet (~5% cada) + ~50 outras ações do Nasdaq. Mais pesado em tech que JEPI. Covered calls sobre o índice via ELNs.',
        'riscos': 'Upside fortemente limitado em bull markets de tech — em 2023 (QQQ +55%), JEPQ subiu apenas ~30%. Gestão ativa. Custo de 0.35%. Risco de redução de distribuição em baixa volatilidade.',
    },
    'DVY': {
        'resumo': 'iShares Select Dividend ETF — 100 ações americanas de alto yield com histórico de pagamento. Foco em renda atual.',
        'estrategia': 'Replica o Dow Jones US Select Dividend Index. Seleciona 100 ações com: (1) alto dividend yield, (2) histórico de 5 anos sem corte, (3) payout ratio sustentável, (4) liquidez adequada. Ponderado por yield (maiores yields = maior peso).',
        'composicao': '100 ações de alto yield: Altria, AT&T, Verizon, Unilateral Corp, Exxon Mobil, Phillips 66. Financeiro (~25%), Utilities (~20%), Energia (~15%), Consumo Básico (~12%). Yield atual ~4-5%.',
        'riscos': 'Concentração em setores tradicionais. Ponderação por yield = mais peso em empresas mais arriscadas. Sensível a juros. Custo de 0.38%. Underperforma S&P 500 total historicamente.',
    },
    'SDY': {
        'resumo': 'SPDR S&P Dividend ETF — ações que aumentaram dividendo por 20+ anos consecutivos. Qualidade histórica.',
        'estrategia': 'Replica o S&P High Yield Dividend Aristocrats Index — empresas do S&P Composite 1500 (large+mid+small cap) que aumentaram dividendo por 20+ anos consecutivos. Menos rigoroso que NOBL (25 anos) mas mais amplo.',
        'composicao': '~135 ações. IBM, AT&T, Realty Income, Leggett & Platt, Kimberly-Clark, Consolidated Edison, Prologis, National Retail Properties. Financeiro (~18%), Utilities (~14%), Consumo Básico (~13%), Industrial (~12%).',
        'riscos': 'Equal-weight = mais exposição a mid caps vs large caps. Inclui setores madures/defasados. Algumas empresas com histórico de crescimento mas lento. Custo de 0.35%.',
    },
    'DGRO': {
        'resumo': 'iShares Core Dividend Growth ETF — ações com crescimento de dividendo sustentável. Custo de 0.08%.',
        'estrategia': 'Replica o Morningstar US Dividend Growth Index. Seleciona ações com: (1) crescimento de dividendo por 5+ anos, (2) payout ratio < 75% (sustentável), (3) crescimento de dividendo esperado positivo. Excluí os de maior yield (mais arriscados).',
        'composicao': 'Microsoft (~4%), JPMorgan (~4%), Apple (~3%), Broadcom (~3%), Exxon Mobil (~3%), UnitedHealth (~3%), Johnson & Johnson (~3%). ~400 ações. Tecnologia (~20%), Financeiro (~20%), Saúde (~15%).',
        'riscos': 'Yield atual baixo (~2%) — foco em crescimento, não renda imediata. Exposição a tech significativa. Underperforma SCHD em alguns períodos. Muito similar ao VIG.',
    },
    'XYLD': {
        'resumo': 'Global X S&P 500 Covered Call ETF — covered calls AT/M mensais no SPY para yield de ~10-12%/ano.',
        'estrategia': 'Replica o CBOE S&P 500 BuyWrite Index. Detém S&P 500 (via SPY) e vende call at-the-money mensalmente. Similar ao QYLD mas sobre S&P 500 (menor volatilidade = menor prêmio = menor yield). Distribuição mensal.',
        'composicao': 'S&P 500 inteiro (via SPY) + short call ATM mensal sobre o índice. O prêmio coletado é distribuído como renda. Em mercados de alta, a valorização é "queimada" pela call vendida.',
        'riscos': 'Erosão de NAV em bull markets (valorização vai para a call, não para o cotista). Yield menor que QYLD (~10% vs ~12%). Em quedas, perde igual ao S&P 500 sem proteção. Apenas para geração de renda sem expectativa de crescimento de capital.',
    },
    'RYLD': {
        'resumo': 'Global X Russell 2000 Covered Call ETF — covered calls no Russell 2000 para yield de ~12-14%/ano.',
        'estrategia': 'Detém Russell 2000 (via IWM) e vende calls ATM mensais. Small caps têm maior volatilidade → maior prêmio das opções → yield mais alto que XYLD/QYLD. Distribuição mensal de renda.',
        'composicao': 'Russell 2000 inteiro + short call ATM mensal sobre o índice. Máxima renda, mínimo crescimento de capital. Yield atual ~12-14%.',
        'riscos': 'Small caps são mais voláteis — em quedas, perde mais que XYLD. Erosão de NAV ainda mais severa em bull markets de small caps. Apenas para quem precisa de renda mensal máxima sem crescimento de capital.',
    },
    'PFF': {
        'resumo': 'iShares Preferred and Income Securities ETF — ações preferenciais americanas. Yield alto (~6%), entre bond e ação.',
        'estrategia': 'Replica o ICE Exchange-Listed Preferred & Hybrid Securities Index. Ações preferenciais pagam dividendo fixo antes das ações ordinárias, com prioridade sobre ordinários mas após bonds. Híbrido entre renda fixa e variável.',
        'composicao': '~450 ações preferenciais americanas. Bancos (JPMorgan, Wells Fargo, Bank of America, Goldman) respondem por ~50% do fundo por serem os maiores emissores. Financeiro extremamente concentrado.',
        'riscos': 'Alta concentração em setor financeiro. Sensível a juros (duração longa). Em crise bancária, preferenciais sofrem. Menor proteção que bonds na estrutura de capital. Custo de 0.46%.',
    },
    'PGX': {
        'resumo': 'Invesco Preferred ETF — ações preferenciais com gestão ativa. Yield atual ~6-7%/ano.',
        'estrategia': 'Similar ao PFF mas com gestão ativa — a Invesco faz seleção mais rigorosa de preferenciais por qualidade de crédito e yield ajustado ao risco. Rebalanceamento mensal.',
        'composicao': '~200 preferenciais. Bancos americanos e europeus dominam. Yield ligeiramente maior que PFF por gestão ativa e seleção. Diversificação geográfica inclui emissores canadenses e europeus listados nos EUA.',
        'riscos': 'Mesmos do PFF: concentração em financeiro, sensibilidade a juros, risco de crédito de preferenciais. Custo de 0.52% acima do PFF (0.46%). Gestão ativa não garante outperformance.',
    },

    # ══ COMMODITIES — NOVOS ═══════════════════════════════════════════════════
    'GLDM': {
        'resumo': 'SPDR Gold MiniShares ETF — ouro físico com o MENOR custo entre os grandes (0.10%/ano). Lançado pela SPDR em 2018.',
        'estrategia': 'Detém ouro físico em barras. Cota representa 1/100 oz (menor que GLD = 1/10 oz). Lançado para competir diretamente com IAU (0.25%) e atrair investidores de longo prazo com foco em custo. Custódia HSBC.',
        'composicao': '100% ouro físico. Cota = 1/100 onça troy de ouro. Auditado regularmente. Sem renda. Valor = preço spot do ouro / 100.',
        'riscos': 'Menor liquidez intradiária que GLD e IAU. Sem renda (sem dividendos). Câmbio USD/BRL. Ouro pode underperformar em ambientes de juros reais positivos.',
    },
    'BAR': {
        'resumo': 'GraniteShares Gold Trust ETF — ouro físico com custo de 0.17%/ano. Emissora independente com custódia ICBC Standard.',
        'estrategia': 'Detém ouro físico na ICBC Standard Bank. Cota = 1/100 oz. A GraniteShares é uma emissora independente menor — risco de liquidez de negociação maior que os ETFs tradicionais (GLD, IAU, GLDM).',
        'composicao': '100% ouro físico. Sem alavancagem. Custo entre GLDM (0.10%) e IAU (0.25%). Menos popular que concorrentes.',
        'riscos': 'Menor liquidez e volume que GLD/IAU/GLDM — spreads bid-ask maiores. Emissora menor sem o respaldo da BlackRock/State Street/Vanguard. Risco de descontinuação do fundo.',
    },
    'AAAU': {
        'resumo': 'Goldman Sachs Physical Gold ETF — ouro físico com custo de 0.18%/ano e custódia da JPMorgan.',
        'estrategia': 'Detém ouro físico custodiado pelo JPMorgan Chase. Lançado em 2018 pela Goldman Sachs. Custo entre GLDM e IAU. Respaldo do maior banco de investimento do mundo pode dar segurança institucional.',
        'composicao': '100% ouro físico custodiado em cofres do JPMorgan. Cota = 1/100 oz. AUM menor que GLD/IAU — menor liquidez intradiária.',
        'riscos': 'Menor volume e liquidez que GLD/IAU. Emissora Goldman tem respaldo, mas fundo é menor. Mesmo risco estrutural de todos os ETFs de ouro físico.',
    },
    'SIVR': {
        'resumo': 'abrdn Physical Silver Shares ETF — prata física com custo de 0.30%/ano. Alternativa ao SLV (Aberdeen vs BlackRock).',
        'estrategia': 'Detém prata física em cofres. Alternativa ao SLV da iShares com gestora diferente (abrdn, ex-Aberdeen). Custo similar ao SLV (0.30%). Prata combina uso industrial (solar, eletrônicos) com aspecto monetário.',
        'composicao': '100% prata física. Menor liquidez que SLV por ser menos popular. Prata é mais volátil que ouro por ter maior uso industrial (demanda oscila com ciclo econômico).',
        'riscos': 'Maior volatilidade que ouro. Menor liquidez que SLV. Sem renda. Câmbio. Preço da prata muito sensível ao ciclo industrial e à demanda de energia solar.',
    },
    'PPLT': {
        'resumo': 'abrdn Physical Platinum Shares ETF — platina física. Metal de transição: uso em catalisadores, joias e células de hidrogênio.',
        'estrategia': 'Detém platina física. Platina é usada principalmente em catalisadores de automóveis (veículos a gasolina), joalheria e potencialmente em células de combustível de hidrogênio. Produção concentrada na África do Sul (>70%).',
        'composicao': '100% platina física em cofres seguros. Produção mundial muito concentrada (África do Sul ~70%, Zimbábue ~10%). Raridade extrema — estoque acima do solo menor que ouro.',
        'riscos': 'Transição para EVs (elétricos) reduz demanda por catalisadores de motores a combustão. Risco de produção concentrado em África do Sul. Alta volatilidade por mercado pequeno. Menor liquidez.',
    },
    'PALL': {
        'resumo': 'abrdn Physical Palladium Shares ETF — paládio físico. Usado em catalisadores. Dependente da produção russa.',
        'estrategia': 'Detém paládio físico. Paládio é usado principalmente em catalisadores de veículos à gasolina e diesel. Rússia produz ~40% do paládio mundial — sanções pós-Ucrânia criaram volatilidade extrema.',
        'composicao': '100% paládio físico. Mercado muito menor que ouro ou prata. Rússia (~40%) + África do Sul (~37%) = ~77% da produção mundial.',
        'riscos': 'Alta dependência da Rússia para produção. Transição para EVs reduz demanda. Mercado muito pequeno e ilíquido. Volatilidade extrema. Sanções a exportações russas criam choques de oferta.',
    },
    'REMX': {
        'resumo': 'VanEck Rare Earth/Strategic Metals ETF — terras raras e metais estratégicos. Críticos para tecnologia e defesa.',
        'estrategia': 'Replica o MVIS Global Rare Earth/Strategic Metals Index. Terras raras são essenciais para motores elétricos, turbinas eólicas, eletrônicos e sistemas de guia de mísseis. China controla ~85% da produção/processamento mundial.',
        'composicao': 'MP Materials (EUA), Lynas Rare Earths (Austrália), Pilbara Minerals, Sigma Lithium, Lithium Americas. ~25 empresas de mineração de terras raras e metais estratégicos globais.',
        'riscos': 'China domina processamento (~85%) — risco de restrições de exportação. Empresas pequenas e voláteis. Custo de 0.56%. Projetos de mineração têm riscos operacionais e licenciamento. Liquidez reduzida.',
    },
    'SIL': {
        'resumo': 'Global X Silver Miners ETF — mineradoras de prata. Alavancagem ao preço da prata (~2-3x), similar ao GDX para ouro.',
        'estrategia': 'Replica o Solactive Global Silver Miners Total Return Index. Investe em mineradoras de prata (não prata física). As mineradoras têm alavancagem operacional ao preço da prata: quando prata sobe 10%, margens das mineradoras podem subir 30%.',
        'composicao': 'Wheaton Precious Metals (~23%), Pan American Silver (~12%), First Majestic Silver (~10%), Coeur Mining (~7%), Hecla Mining (~6%). ~25-30 mineradoras globais de prata.',
        'riscos': 'Alavancagem dupla em quedas: quando prata cai, mineradoras caem mais. Riscos operacionais (custos de mineração, segurança, licenças). Geopolítico (México, Peru, Argentina são produtores principais). Custo de 0.65%.',
    },
    'GDXJ': {
        'resumo': 'VanEck Junior Gold Miners ETF — mineradoras de ouro JUNIOR (menores). Maior potencial e maior risco que GDX.',
        'estrategia': 'Replica o MVIS Global Junior Gold Miners Index. Investe em mineradoras de ouro menores ("juniors") em fase de desenvolvimento ou produção inicial. Maior potencial de retorno que GDX em bull markets de ouro, mas muito mais volátil.',
        'composicao': 'Sibanye Stillwater, Pan American Silver, Kinross Gold, Gold Fields, Evolution Mining, Harmony Gold, Alamos Gold. ~80 mineradoras junior e mid-tier. Menor que GDX mas maior AUM.',
        'riscos': 'Volatilidade muito mais alta que GDX. Risco de financiamento (juniors podem precisar de capital). Projetos podem falhar. Geopolítico (África, Américas). Custo de 0.52%.',
    },
    'RING': {
        'resumo': 'iShares MSCI Global Gold Miners ETF — mineradoras de ouro globais. Similar ao GDX com metodologia MSCI.',
        'estrategia': 'Replica o MSCI ACWI Select Gold Miners Investable Market Index. Similar ao GDX mas com metodologia MSCI e cobertura potencialmente mais ampla de mineradoras globais.',
        'composicao': 'Newmont, Barrick Gold, Agnico Eagle, Kinross, Gold Fields, Harmony Gold, B2Gold. ~25-30 mineradoras globais de ouro. Similar ao GDX na composição.',
        'riscos': 'Mesmos do GDX: alavancagem ao ouro, riscos operacionais, geopolítico. Menor AUM e liquidez que GDX. Custo de 0.39% — menor que GDX (0.51%).',
    },
    'USO': {
        'resumo': 'United States Oil Fund — petróleo WTI via futuros. Custo de roll corrói retorno. Adequado para trades de curto prazo.',
        'estrategia': 'Investe em contratos futuros de crude WTI (West Texas Intermediate). Rola mensalmente para o próximo contrato, incorrendo em custo de roll quando futuros estão em contango. Em situações extremas, petróleo ficou negativo (COVID 2020).',
        'composicao': 'Futuros de crude WTI na NYMEX + T-Bills como colateral. Rola para o próximo mês antes do vencimento. Após COVID, mudou metodologia para diversificar os vencimentos e reduzir risco de roll.',
        'riscos': 'Custo de roll em contango pode ser -10 a -30% ao ano. Petróleo chegou a ser NEGATIVO em abril 2020. Não replica fielmente o preço spot do crude. Adequado apenas para apostas táticas de dias/semanas.',
    },
    'BNO': {
        'resumo': 'United States Brent Oil Fund — petróleo Brent via futuros. Brent é referência para mercados europeus e asiáticos.',
        'estrategia': 'Similar ao USO mas sobre petróleo Brent (produzido no Mar do Norte), que é referência para precificação de ~60% do petróleo mundial (vs WTI que é referência americana). Futuros Brent na ICE (London).',
        'composicao': 'Futuros de Brent crude na ICE + T-Bills. Estrutura similar ao USO. Rola mensalmente com custo de roll em contango.',
        'riscos': 'Mesmos do USO: custo de roll, não replica spot fielmente, alta volatilidade do petróleo. Brent é normalmente precificado acima do WTI (Brent premium). Adequado apenas para curto prazo.',
    },
    'UNG': {
        'resumo': 'United States Natural Gas Fund — gás natural via futuros. Extremamente volátil por sazonalidade e clima.',
        'estrategia': 'Investe em futuros de gás natural na NYMEX. O gás natural é influenciado por: temperatura, produção de xisto, exportações de GNL, geopolítica (Ucrânia/Rússia). Alta sazonalidade (inverno = pico de demanda).',
        'composicao': 'Futuros de gás natural Henry Hub + T-Bills. Custo de roll em contango é ainda mais severo que petróleo — mercados de gás frequentemente em super-contango.',
        'riscos': 'Volatilidade extrema (pode subir ou cair 50%+ em semanas). Custo de roll devastador em contango — BOIL 2x amplifica isso. Altamente dependente de clima. Gás natural chegou a mínimas históricas em 2023.',
    },
    'PDBC': {
        'resumo': 'Invesco DB Optimum Yield Diversified Commodity Strategy ETF — commodities diversificadas com estratégia de roll otimizada.',
        'estrategia': 'Replica o DBIQ Optimum Yield Diversified Commodity Index. Investe em futuros de 14 commodities: energia (~55%), metais (~23%), agrícolas (~22%). Diferencial: usa algoritmo de roll otimizado para minimizar custo de contango.',
        'composicao': 'WTI (~20%), Brent (~17%), Gasolina RBOB (~8%), Gold (~8%), Silver (~5%), Corn (~5%), Wheat (~5%), Soybeans (~4%), Natural Gas (~4%), Copper, Aluminum. Diversificação ampla.',
        'riscos': 'Ainda tem custo de roll mesmo com otimização. Tributação especial (K-1 form nos EUA). Alta exposição a energia. Custo de 0.59%. Mais complexo que ETFs de commodity única.',
    },
    'GSG': {
        'resumo': 'iShares S&P GSCI Commodity-Indexed Trust ETF — índice de commodities Goldman Sachs. Alta concentração em energia.',
        'estrategia': 'Replica o S&P GSCI Index — índice de commodities ponderado por produção. Por isso, energia domina (~60% do índice, vs metais ~15%, agrícolas ~25%). Alta exposição ao ciclo de petróleo/gás natural.',
        'composicao': 'WTI (~25%), Brent (~18%), Gasolina RBOB (~10%), Gás Natural (~7%) — energia total ~60%. Ouro (~4%), Prata (~1%), Cobre (~3%). Grãos (~15%), Açúcar (~4%).',
        'riscos': 'Alta concentração em energia (~60%) — volatilidade extrema. Custo de roll de futuros. Taxado como commodity pool (K-1). Custo de 0.75%. Não é ETF puro (ETP de diferente estrutura).',
    },
    'DJP': {
        'resumo': 'iPath Bloomberg Commodity Index Total Return ETN — índice diversificado de commodities via estrutura ETN.',
        'estrategia': 'ETN (não ETF) que replica o Bloomberg Commodity Index Total Return — 23 commodities com limites de concentração (máximo 15% por commodity, 33% por setor). Mais balanceado que GSG. Emitido pelo Barclays.',
        'composicao': 'Energia (~30%), Metais (~25%), Grãos (~20%), Soft commodities (açúcar, café, algodão, ~15%), Proteína animal (~10%). Melhor diversificação que GSG.',
        'riscos': 'ETN = risco de crédito do emissor (Barclays). Custo de roll de futuros. Tributação especial. Custo de 0.75%. Estrutura mais complexa que ETF traditional.',
    },
    'SOYB': {
        'resumo': 'Teucrium Soybean Fund ETF — futuros de soja. Exposição direta ao agronegócio e demanda da China.',
        'estrategia': 'Investe em futuros de soja do CBOT (Chicago Board of Trade) com 3 vencimentos diferentes para reduzir custo de roll. Soja é uma das principais commodities agrícolas — EUA e Brasil respondem por ~80% das exportações mundiais.',
        'composicao': 'Contratos futuros de soja: CBOT JAN (~35%), CBOT MAR (~30%), CBOT NOV (~35%). Estrutura de 3 vencimentos reduz exposição ao custo de roll de um único contrato.',
        'riscos': 'Custo de roll presente (menor que petróleo mas existe). Clima é principal driver de preço (seca no Brasil/EUA). Demanda da China como maior importador. Câmbio. Custo de 0.22%.',
    },
    'CANE': {
        'resumo': 'Teucrium Sugar Fund ETF — futuros de açúcar bruto. Exposição ao agronegócio e ao etanol.',
        'estrategia': 'Investe em futuros de açúcar bruto (raw sugar) da ICE. Brasil é o maior exportador mundial de açúcar e etanol — o preço do açúcar está correlacionado ao preço do petróleo (quando petróleo sobe, usinas preferem produzir etanol).',
        'composicao': 'Contratos futuros de açúcar bruto Sugar #11 da ICE com 3 vencimentos. Estrutura da Teucrium para reduzir custo de roll.',
        'riscos': 'Alta correlação com o petróleo (etanol/açúcar). Clima nos trópicos (Brasil, Índia, Tailândia). Políticas de subsídio a etanol. Custo de roll. Mercado altamente especulativo com grandes fundos.',
    },

    # ══ TEMÁTICOS — NOVOS ════════════════════════════════════════════════════
    'PAVE': {
        'resumo': 'Global X US Infrastructure Development ETF — empresas que se beneficiam da renovação da infraestrutura americana.',
        'estrategia': 'Replica o INDXX US Infrastructure Development Index. Seleciona empresas americanas que fornecem materiais, equipamentos e serviços para infraestrutura: aço, cimento, engenharia, construção, utilities. Beneficia do Infrastructure Investment & Jobs Act (2021).',
        'composicao': 'Caterpillar, Vulcan Materials, Martin Marietta, Nucor, Eaton, Parker Hannifin, Aecom, IDEX, Quanta Services. ~100 empresas. Industrial (~40%), Materiais (~25%), Utilities (~10%).',
        'riscos': 'Dependência de gastos governamentais em infraestrutura. Alta ciclicidade (industrial/materiais). Inflação de custos (aço, cimento). Risco de atraso em projetos de infraestrutura pública.',
    },
    'BETZ': {
        'resumo': 'Roundhill Sports Betting & iGaming ETF — empresas de apostas esportivas e cassinos online. Setor em expansão nos EUA.',
        'estrategia': 'Replica o Roundhill Sports Betting & iGaming Index. Exposição a empresas de apostas esportivas legalizadas (DraftKings, FanDuel/Flutter), cassinos online e fornecedores de tecnologia para o setor. Legalização nos EUA está expandindo.',
        'composicao': 'Flutter Entertainment (FanDuel, ~20%), DraftKings (~15%), Penn Entertainment (~8%), Entain (~8%), IGT (~6%), Scientific Games, GAN Limited. ~30-40 empresas globais.',
        'riscos': 'Setor ainda não lucrativo em escala (gastos enormes em marketing e bônus). Regulação estadual variável nos EUA. Concorrência intensa. Alto custo de aquisição de clientes. Dependência de aprovações regulatórias.',
    },
    'ESPO': {
        'resumo': 'VanEck Video Gaming & eSports ETF — empresas de jogos eletrônicos e esports. Setor de entretenimento digital global.',
        'estrategia': 'Replica o MVIS Global Video Gaming & eSports Index. Seleciona empresas com 50%+ da receita de videogames, esports e transmissão ao vivo. Inclui desenvolvedores, publishers, hardware e plataformas. Exposição global com forte componente asiático.',
        'composicao': 'Nvidia (~11%), Tencent (~10%), Nintendo (~8%), Sea Limited (~6%), Electronic Arts (~5%), Take-Two Interactive (~5%), Roblox, Activision, NetEase. ~25 empresas.',
        'riscos': 'Alta concentração em Ásia (Tencent, Nintendo, NetEase = ~30%). Risco regulatório chinês em jogos. Ciclicidade — vendas de jogos caem em recessão. Custo de 0.55%.',
    },
    'SOCL': {
        'resumo': 'Global X Social Media ETF — redes sociais globais: Meta, Snap, Pinterest, TikTok parent. Alto beta, alta volatilidade.',
        'estrategia': 'Replica o Solactive Social Media Total Return Index. Seleciona empresas com 50%+ da receita de social media/user-generated content. Inclui tanto empresas americanas quanto chinesas.',
        'composicao': 'Meta (~22%), Alphabet (~12%), Snap (~8%), Pinterest (~7%), Twitter (pré-aquisição), Kuaishou, Weibo, Baidu. Mix americano e chinês. ~25-30 empresas.',
        'riscos': 'Alta concentração em Meta. Risco regulatório (privacidade, GDPR, antitruste). Risco geopolítico pela exposição chinesa. Publicidade digital cíclica. Custo de 0.65%.',
    },
    'GNOM': {
        'resumo': 'Global X Genomics & Biotechnology ETF — edição genética, CRISPR, terapias genéticas. Setor de vanguarda da medicina.',
        'estrategia': 'Replica o Solactive Genomics Index. Empresas envolvidas em: sequenciamento de DNA, edição genética (CRISPR), terapias gênicas, bioinformática e diagnósticos moleculares. Alto risco, alto potencial transformador.',
        'composicao': 'Illumina (~11%), Pacific Biosciences (~8%), CRISPR Therapeutics (~7%), Beam Therapeutics (~6%), Invitae (~6%), Twist Bioscience, Editas Medicine, Intellia Therapeutics. ~40 empresas.',
        'riscos': 'Maioria das empresas pré-lucratividade (queima de caixa). Aprovação da FDA pode demorar anos. Alta volatilidade por dados clínicos. Custo de 0.50%. Risco de execução tecnológica muito alto.',
    },
    'NANC': {
        'resumo': 'Unusual Whales Subversive Democratic Trading ETF — replica as trades de congressistas democratas. Transparência política.',
        'estrategia': 'Gestão ativa baseada nas divulgações obrigatórias de trades de congressistas democratas americanos (STOCK Act). Compra as mesmas ações que democratas do Congresso declararam comprar. Conceito controverso mas legal.',
        'composicao': 'Varia dinamicamente com os trades dos congressistas. Historicamente: Microsoft, Nvidia, Apple, Broadcom (trades de Nancy Pelosi foram muito lucrativos). Portfólio muito diferente de índices tradicionais.',
        'riscos': 'Atraso nos relatórios (congressistas têm 45 dias para declarar). Estratégia não validada academicamente. Alta rotatividade. Custo de 0.75%. Pode ter trades de baixa qualidade de congressistas menos sofisticados.',
    },
    'KRUZ': {
        'resumo': 'Unusual Whales Subversive Republican Trading ETF — replica as trades de congressistas republicanos.',
        'estrategia': 'Similar ao NANC mas focado nas declarações de trades de congressistas republicanos. Complemento ao NANC para quem quer diversificar por orientação política.',
        'composicao': 'Energia, defesa, financeiro (setores favorecidos por políticas republicanas historicamente). Portfólio varia com declarações dos congressistas. Menos concentrado que NANC.',
        'riscos': 'Mesmos do NANC: atraso nas declarações, qualidade variável dos trades, alta rotatividade, custo de 0.75%.',
    },
    'DSPY': {
        'resumo': 'VanEck Defense ETF — setor de defesa americano e global. Beneficia de aumento de gastos militares mundiais.',
        'estrategia': 'Replica o MarketVector US Listed Defense Industry Index. Empresas de aeroespacial e defesa: fabricantes de aviões militares, sistemas de mísseis, cibersegurança militar, navios e veículos blindados.',
        'composicao': 'Lockheed Martin (~15%), RTX (~13%), Northrop Grumman (~12%), Boeing (defesa, ~10%), General Dynamics (~9%), L3 Technologies, Leidos, Booz Allen Hamilton. ~25-30 empresas.',
        'riscos': 'Dependência de contratos governamentais. Pressão política para reduzir gastos militares. Risco reputacional (setor controverso). Concentração em poucas grandes contratantes.',
    },
    'SHLD': {
        'resumo': 'Global X Defense Tech ETF — tecnologia de defesa: IA militar, drones, cibersegurança nacional.',
        'estrategia': 'Foca em empresas de tecnologia de defesa de próxima geração: drones, IA para defesa, comunicações militares, eletrônica de combate. Diferente do DSPY (hardware tradicional), mais focado em tech de defesa.',
        'composicao': 'Palantir (~10%), Booz Allen Hamilton (~8%), Leidos (~7%), CACI International (~6%), Science Applications (~5%), Kratos Defense, AeroVironment. ~40 empresas de tech-defense.',
        'riscos': 'Setor emergente com regulação específica. Dependência de aprovações governamentais. Palantir tem alta participação mas é controverso. Custo de 0.50%.',
    },
    'SNSR': {
        'resumo': 'Global X Internet of Things ETF — IoT: sensores, conectividade, automação industrial e smart homes.',
        'estrategia': 'Replica o Indxx Global Internet of Things Thematic Index. Empresas que desenvolvem sensores, chips de conectividade (Bluetooth/WiFi/5G), plataformas IoT industriais e automação inteligente.',
        'composicao': 'NXP Semiconductors (~9%), Skyworks Solutions (~8%), Qualcomm (~7%), Amphenol (~6%), Zebra Technologies (~6%), Keysight Technologies, FLIR Systems. ~50 empresas globais.',
        'riscos': 'Setor amplo com múltiplas definições — portfólio pode não focar no que se espera. Segurança IoT é problema crescente. Custo de 0.68%. Alta diversificação dilui potencial de alpha.',
    },
    'FIVG': {
        'resumo': 'Defiance Next Gen Connectivity ETF — infraestrutura 5G: torres, equipamentos, chips e operadoras.',
        'estrategia': 'Replica o BlueStar 5G Communications Index. Empresas que constroem e lucram com a infraestrutura 5G: fabricantes de equipamentos de rede, torres, chips de rádio-frequência e operadoras que investem em 5G.',
        'composicao': 'Qualcomm (~9%), Nokia (~7%), Ericsson (~7%), Marvell Technology (~6%), Crown Castle (~6%), American Tower, Qorvo, Skyworks. ~100 empresas globais de conectividade 5G.',
        'riscos': 'Roll-out do 5G mais lento que o esperado. Concorrência com Huawei em equipamentos (questão geopolítica). Operadoras com alto endividamento. Custo de 0.30%.',
    },
    'UFO': {
        'resumo': 'Procure Space ETF — indústria espacial: satélites, lançadores, exploração espacial e defesa militar no espaço.',
        'estrategia': 'Replica o S-Network Space Index. Exposição à economia espacial emergente: fabricantes de satélites, operadores de constelações (SpaceX não listado mas Starlink indiretamente), sistemas de lançamento, comunicação via satélite.',
        'composicao': 'Maxar Technologies, Iridium Communications, DigitalBridge, Planet Labs, Rocket Lab, Trimble, ViaSat, Garmin. ~30-35 empresas de espaço puro ou significativo.',
        'riscos': 'Setor emergente com poucas empresas puras listadas. SpaceX (líder do setor) não está listada na bolsa. Custo de 0.75%. Alta volatilidade. Dependência de contratos governamentais e militares.',
    },
    'MOO': {
        'resumo': 'VanEck Agribusiness ETF — agronegócio global: fertilizantes, sementes, maquinário agrícola e processamento.',
        'estrategia': 'Replica o MVIS Global Agribusiness Index. Empresas da cadeia de valor agrícola: fertilizantes (Mosaic, Nutrien), sementes (Corteva), maquinário (Deere, AGCO), processamento (Archer Daniels, Bunge, Tyson Foods).',
        'composicao': 'Deere (~10%), Mosaic (~8%), Nutrien (~8%), Corteva (~7%), Archer Daniels Midland (~7%), Bunge, AGCO, Tyson Foods. ~50 empresas. Fertilizantes (~25%), Maquinário (~20%), Processamento (~25%).',
        'riscos': 'Dependência de clima e safras. Preço de matérias-primas (potassa, fosfato, nitrogênio). Regulação ambiental. Guerra Ucrânia-Rússia afetou fertilizantes e grãos. Custo de 0.53%.',
    },

    # ══ FATOR / SMART BETA — NOVOS ════════════════════════════════════════════
    'VLUE': {
        'resumo': 'iShares MSCI USA Value Factor ETF — ações de value: baixo P/B, baixo P/E, alto dividendo. Contrária ao growth.',
        'estrategia': 'Replica o MSCI USA Enhanced Value Index. Seleciona as ações do MSCI USA com maior pontuação de value usando 3 métricas: Price-to-Book, Price-to-Forward-Earnings e Enterprise Value/Cash Flow Operacional. Rebalanceamento semestral.',
        'composicao': 'Berkshire Hathaway, JPMorgan, Exxon Mobil, Johnson & Johnson, Pfizer, Bank of America, Wells Fargo, Chevron. Financeiro (~25%), Saúde (~15%), Energia (~12%), Industrial (~10%).',
        'riscos': 'Historicamente underperformou growth por longo período (2010-2020). "Value trap" — empresas baratas podem ser baratas por bons motivos. Concentração em setores tradicionais. Custo de 0.15%.',
    },
    'SPLV': {
        'resumo': 'Invesco S&P 500 Low Volatility ETF — as 100 ações do S&P 500 com MENOR volatilidade. Proteção em quedas.',
        'estrategia': 'Seleciona as 100 ações do S&P 500 com menor volatilidade realizada nos últimos 12 meses, ponderadas inversamente pela volatilidade. Rebalanceamento trimestral. Defesa máxima dentro do universo S&P 500.',
        'composicao': 'Utilities (~20%), Financeiro (~19%), Consumo Básico (~17%), Saúde (~15%), Real Estate (~10%). Ações como Berkshire, Visa, McDonald\'s, Walmart predominam. Quase zero em tech volátil.',
        'riscos': 'Underperforma fortemente em bull markets de tech/growth. "Low volatility anomaly" pode ser parcialmente capturada pelo mercado. Sensível a juros (muitas "bond proxies"). Custo de 0.25%.',
    },
    'SPHQ': {
        'resumo': 'Invesco S&P 500 Quality ETF — ações do S&P 500 com maior qualidade fundamentalista (ROE, accruals, alavancagem).',
        'estrategia': 'Replica o S&P 500 Quality Index. Seleciona as 100 ações do S&P 500 com maior score de qualidade baseado em 3 fatores: (1) ROE alto, (2) Razão accruals baixa (lucros de alta qualidade), (3) Índice de alavancagem financeira baixo.',
        'composicao': 'Apple (~9%), Microsoft (~8%), Visa (~5%), Mastercard (~5%), Broadcom (~4%), Accenture (~4%), Alphabet, UnitedHealth. ~100 ações. TI (~35%), Saúde (~15%), Financeiro (~14%).',
        'riscos': 'Alta sobreposição com XLK/QQQ em tech de qualidade. Custo de 0.15%. O fator quality foi muito explorado — prêmio pode ter diminuído. Concentração em mega-caps tech de qualidade.',
    },
    'PRF': {
        'resumo': 'Invesco FTSE RAFI US 1000 ETF — S&P 500 ponderado por FUNDAMENTOS (vendas, fluxo de caixa, dividendos, book value).',
        'estrategia': 'Replica o FTSE RAFI US 1000 Index (Research Affiliates Fundamental Index). Pondera as 1.000 maiores empresas americanas por métricas fundamentalistas (não por capitalização de mercado). Resultado: mais value, menos tech vs S&P 500.',
        'composicao': 'Exxon Mobil, JPMorgan, Apple, Microsoft, Berkshire, Walmart, Chevron. Mix mais equilibrado entre value e growth. Financeiro (~17%), TI (~16%), Saúde (~14%), Energia (~9%).',
        'riscos': 'Underperformou S&P 500 ponderado por cap em mercados de bull de tech. Custo de 0.39% — caro vs VOO (0.03%). Metodologia proprietária da Research Affiliates.',
    },
    'CALF': {
        'resumo': 'Pacer US Small Cap Cash Cows ETF — small caps americanas com maior FCF Yield. Versão small do COWZ.',
        'estrategia': 'Replica o Pacer US Small Cap Cash Cows 100 Index. Seleciona as 100 small caps do Russell 2000 com maior FCF Yield. Equal-weight. Rebalanceamento trimestral. FCF Yield é difícil de manipular contabilmente.',
        'composicao': '100 small caps americanas com FCF yield elevado. Alta exposição a energia (E&P, serviços), financeiro e industrial. Rotatividade alta por rebalanceamento trimestral.',
        'riscos': 'Alta concentração em energia (ciclicidade). Small caps + value = maior volatilidade. Alto turnover = maiores custos implícitos. Custo de 0.59%.',
    },
    'VFMO': {
        'resumo': 'Vanguard US Momentum Factor ETF — ações com maior momentum (as que mais subiram recentemente). Custo de 0.13%.',
        'estrategia': 'Replica o Russell 3000 Momentum Focused Factor Index. Seleciona ações do Russell 3000 com maior momentum ajustado ao risco nos últimos 12 meses (excluindo o último mês). Rebalanceamento semestral.',
        'composicao': 'Portfólio dinâmico — muda significativamente a cada rebalanceamento. Em bull markets de tech, concentra em tech. Em rotações setoriais, muda para líderes do momento. Maior rotatividade que outros fatores.',
        'riscos': 'Alto momentum pode reverter abruptamente (momentum crash). Alta rotatividade = custo de transação implícito. Underperforma fortemente em reversões de mercado. "Comprar caro" é inerente à estratégia.',
    },
    'VFMV': {
        'resumo': 'Vanguard US Min Volatility ETF — ações americanas de menor volatilidade histórica. Versão Vanguard do USMV.',
        'estrategia': 'Replica o Russell 3000 Volatility Focused Factor Index. Seleciona as ações do Russell 3000 (não só S&P 500) com menor volatilidade histórica. Inclui mid e small caps de baixa volatilidade além das large caps.',
        'composicao': 'Visa, Waste Management, Berkshire, Automatic Data Processing, Accenture. Mix de large e mid caps defensivas. Setores: Saúde, Consumo Básico, Financeiro, Utilities dominam.',
        'riscos': 'Underperforma significativamente em bull markets. Risco de "crowded trade" — todos compram min vol ao mesmo tempo. Custo de 0.13%. Inclui mid caps que podem ser menos líquidas.',
    },
    'VFQY': {
        'resumo': 'Vanguard US Quality Factor ETF — ações americanas com alta rentabilidade, crescimento estável e baixa alavancagem.',
        'estrategia': 'Replica o Russell 3000 Quality Focused Factor Index. Pondera ações do Russell 3000 por score de quality: (1) Retorno sobre o Equity, (2) Mudança em ativos líquidos, (3) Alavancagem operacional. Inclui todas as caps.',
        'composicao': 'Microsoft, Apple, Visa, UnitedHealth, Mastercard, Alphabet — similares ao QUAL da iShares. Tecnologia domina por ter alto ROE e baixa alavancagem estrutural.',
        'riscos': 'Alta sobreposição com tech mega-cap. Custo de 0.13%. Prêmio de quality pode ter sido parcialmente eliminado. Concentração em tech com valuation elevado.',
    },
    'VFVA': {
        'resumo': 'Vanguard US Value Factor ETF — ações americanas baratas por múltiplos (P/B, P/E, P/S). Versão Vanguard do VLUE.',
        'estrategia': 'Replica o Russell 3000 Value Focused Factor Index. Seleciona ações do Russell 3000 com maior score de value usando P/B, P/E e P/S. Cobre todas as capitalizações (large, mid, small cap value).',
        'composicao': 'Berkshire, JPMorgan, Exxon, Johnson & Johnson, Chevron. Financeiro, Energia, Saúde e Industrial dominam. Menor exposição a tech que ETFs de growth.',
        'riscos': 'Historicamente underperformou growth (2010-2020). Value traps. Concentração em setores tradicionais "velha economia". Custo de 0.13%.',
    },
    'DFLV': {
        'resumo': 'Dimensional US Large Value ETF — large caps americanas de value com metodologia Dimensional. Custo de 0.22%.',
        'estrategia': 'Gestão ativa quantitativa baseada em pesquisa académica da Dimensional Fund Advisors (fundada por Eugene Fama). Compra systematicamente large caps americanas com baixo Price-to-Book e alta lucratividade. Rebalanceamento contínuo, sem índice fixo.',
        'composicao': 'JPMorgan, Berkshire, Exxon, Chevron, Johnson & Johnson, Wells Fargo, Bank of America. Financeiro (~30%), Saúde (~15%), Energia (~12%), Industrial (~10%). ~500 large caps de value.',
        'riscos': 'Gestão ativa com risco de underperformance vs benchmark passivo. Custo de 0.22% vs 0.04% do VLUE/VV. Prêmio de value pode ser persistentemente baixo. Concentração em setores tradicionais.',
    },
    'DFSV': {
        'resumo': 'Dimensional US Small Value ETF — small caps americanas de value com lucratividade. O melhor da classe acadêmica.',
        'estrategia': 'Gestão ativa quantitativa da Dimensional. Seleciona small caps americanas com baixo P/B E alta lucratividade (elimina value traps). Implementação superior ao Russell 2000 Value por usar também o filtro de profitability.',
        'composicao': '~500 small caps de value e lucrativas. Setores: Financeiro (~35%), Industrial (~15%), Consumo (~12%), Energia (~10%). Market cap médio ~$2-3B. Similar ao AVUV em filosofia.',
        'riscos': 'Small cap value pode underperformar growth por longo período. Alta volatilidade. Gestão ativa (risco de underperformance). Custo de 0.31%.',
    },
    'DFAC': {
        'resumo': 'Dimensional US Core Equity 2 ETF — mercado americano amplo com tilts de fator (value + profitability + small cap).',
        'estrategia': 'Gestão ativa quantitativa da Dimensional. Cobre todo o mercado americano mas com sobreposição sistemática em ações de menor P/B (value) e maior rentabilidade. Alternativa ao VTI com factor tilts incorporados.',
        'composicao': 'Mercado americano amplo (~2.000 ações) com mais peso em value e profitable. Top: Apple, Microsoft, Nvidia (por tamanho) mas com mais exposição a mid/small value que VTI.',
        'riscos': 'Gestão ativa com custo de 0.19% vs 0.03% do VTI. Factor tilts podem underperformar em mercados dominados por growth. Complexity desnecessária para investidores simples.',
    },
    'DFAS': {
        'resumo': 'Dimensional US Small Cap ETF — small caps americanas amplas com tilt de profitability. Alternativa ao VB/IWM.',
        'estrategia': 'Gestão ativa quantitativa da Dimensional. Investe em small caps americanas mas com overweight em empresas lucrativas e underweight em não-lucrativas. Melhora vs Russell 2000 por excluir empresas "zumbi".',
        'composicao': '~2.000 small caps americanas. Setores: Financeiro, Industrial, Saúde, Consumo. Similar ao VB mas com viés de lucratividade.',
        'riscos': 'Gestão ativa com custo de 0.26% vs 0.05% do VB. Small cap volatilidade. Ciclicidade. Factor premium pode ser pequeno.',
    },
    'AVLV': {
        'resumo': 'Avantis US Large Cap Value ETF — large caps americanas de value + profitability. Versão large cap do AVUV.',
        'estrategia': 'Gestão ativa quantitativa da Avantis (filha da Dimensional). Seleciona large caps americanas com baixo Price-to-Book E alta lucratividade. Complemento ao AVUV para portfolio factor completo.',
        'composicao': '~300 large caps americanas de value lucrativas. JPMorgan, Berkshire, Exxon, Chevron, UnitedHealth, Johnson & Johnson. Financeiro, Energia, Saúde dominam.',
        'riscos': 'Custo de 0.15%. Factor value pode underperformar. Concentração em setores tradicionais. Gestão ativa vs benchmark passivo de value (VLUE 0.15%).',
    },
    'AVDV': {
        'resumo': 'Avantis International Small Cap Value ETF — small caps internacionais de value + profitability. Alta diversificação global.',
        'estrategia': 'Gestão ativa quantitativa da Avantis. Aplica mesma filosofia do AVUV em small caps de países desenvolvidos ex-EUA. Mercado internacional de small value é menos eficiente — maior prêmio potencial.',
        'composicao': '~500 small caps internacionais value+profitable. Japão (~22%), UK (~12%), Alemanha (~8%), Austrália (~8%), Canada (~7%), Suécia, Holanda, Suíça. Financeiro, Industrial dominam.',
        'riscos': 'Risco cambial múltiplo. Menor liquidez de small caps internacionais. Gestão ativa com custo de 0.36%. Mercados internacionais menos transparentes.',
    },
    'AVES': {
        'resumo': 'Avantis Emerging Markets Value ETF — emergentes de value + profitability. Fator investing em mercados emergentes.',
        'estrategia': 'Gestão ativa quantitativa da Avantis em mercados emergentes. Seleciona ações de emergentes com baixo P/B e alta lucratividade. O prêmio de value em emergentes é historicamente maior que em desenvolvidos.',
        'composicao': '~500 ações de emergentes value+profitable. China (~25%), Taiwan (~15%), Índia (~12%), Coreia (~10%), Brasil (~7%). Financeiro, Energia, Materiais dominam.',
        'riscos': 'Todos os riscos de mercados emergentes + fator value. Gestão ativa. Custo de 0.36%. Concentração em países com risco político.',
    },
    'XSVM': {
        'resumo': 'Invesco S&P SmallCap Value with Momentum ETF — small caps americanas com DUPLO fator: value E momentum.',
        'estrategia': 'Replica o S&P 600 High Momentum Value Index. Combina os fatores value e momentum no universo de small caps do S&P 600. Seleciona as ações com maior score combinado de baixo valuation + forte momentum recente.',
        'composicao': '~120 small caps do S&P 600 com alto score de value E momentum simultaneamente. Rotatividade maior que ETFs de fator único. Energia e financeiro frequentemente dominam.',
        'riscos': 'Combinação de fatores pode se cancelar em alguns ciclos. Alta rotatividade. Custo de 0.36%. Small caps + double factor = volatilidade elevada.',
    },
    'QVAL': {
        'resumo': 'Alpha Architect US Quantitative Value ETF — value com screening quantitativo rigoroso para evitar value traps.',
        'estrategia': 'Gestão ativa quantitativa pela Alpha Architect. Processo de 5 etapas: (1) universo quality (excluir baixa qualidade), (2) cheap (baixo EBIT/EV), (3) avoid financial distress, (4) avoid manipulation, (5) momentum filter. Apenas ~40-50 posições = alta convicção.',
        'composicao': '~40-50 ações americanas de value de alta qualidade. Alta concentração = cada posição ~2-3%. Setores variam muito por rebalanceamento. Empresas industriais, financeiras e de consumo frequentemente dominam.',
        'riscos': 'Alta concentração (40-50 posições) = risco idiossincrático. Gestão ativa com custo de 0.49%. High conviction pode ser errado. Factor value em períodos longos de underperformance.',
    },

    # ══ ALAVANCADOS — NOVOS ═══════════════════════════════════════════════════
    'QLD': {
        'resumo': 'ProShares Ultra QQQ 2x — Nasdaq 100 2x alavancado diário. Menos extremo que TQQQ mas ainda muito arriscado.',
        'estrategia': '2x retorno diário do Nasdaq-100. Mesmo mecanismo do TQQQ mas com alavancagem de 2x (vs 3x). O decay é menor que o TQQQ mas ainda significativo em mercados voláteis. Alguns investidores usam como alternativa "mais segura" ao TQQQ.',
        'composicao': 'Swaps de retorno total 2x sobre QQQ/Nasdaq-100 + T-Bills. Em 2022, Nasdaq caiu ~33% → QLD caiu ~55% (vs TQQQ que caiu ~79%).',
        'riscos': 'ALTO RISCO. Volatility decay presente. Em 2022 caiu ~55%. Apenas para swing trades de dias. O decay de 2x é menor que 3x mas ainda destrói valor no longo prazo.',
    },
    'QID': {
        'resumo': 'ProShares UltraShort QQQ 2x inverso — lucra quando Nasdaq cai 2x. Hedge de tech de médio prazo.',
        'estrategia': '-2x retorno diário do Nasdaq-100. Em mercados de queda de tech, amplifica os ganhos. Em bull markets de tech (como 2023), perde valor rapidamente pelo decay inverso.',
        'composicao': 'Swaps inversos -2x sobre QQQ + T-Bills. Menos extremo que SQQQ (-3x) mas ainda inadequado para longo prazo.',
        'riscos': 'ALTO RISCO. Decay inverso severo em mercados de alta. Em 2023 (QQQ +55%), QID teria caído ~75%+. Apenas para hedges táticos de dias/semanas.',
    },
    'SPXU': {
        'resumo': 'ProShares UltraPro Short S&P 500 3x inverso — lucra quando S&P 500 cai 3x. Hedge extremo de mercado.',
        'estrategia': '-3x retorno diário do S&P 500. Especulação em quedas do mercado americano ou hedge extremo. Idêntico ao SPXS da Direxion em estrutura. Em bull markets, perde valor explosivamente.',
        'composicao': 'Swaps inversos -3x sobre S&P 500 + T-Bills. Em 2023 (S&P +26%), SPXU teria caído ~55%+. Decay extremo.',
        'riscos': 'EXTREMO RISCO. Decay inverso devastador em bull markets. Apenas para hedges de 1-5 dias em momentos de alto risco percebido.',
    },
    'SSO': {
        'resumo': 'ProShares Ultra S&P 500 2x — S&P 500 2x alavancado diário. Menos extremo que UPRO/SPXL.',
        'estrategia': '2x retorno diário do S&P 500. Alternativa "menos extrema" ao UPRO (3x). Alguns gestores usam SSO como parte de portfólio alavancado diversificado. O decay de 2x é menor que 3x.',
        'composicao': 'Swaps 2x sobre S&P 500 + T-Bills. Em 2022 (S&P -18%), SSO caiu ~35% vs UPRO que caiu ~75%.',
        'riscos': 'ALTO RISCO. Volatility decay presente. Em 2022 caiu ~35%. Apenas para swing trades. Não adequado para buy & hold.',
    },
    'SDS': {
        'resumo': 'ProShares UltraShort S&P 500 2x inverso — lucra quando S&P 500 cai 2x.',
        'estrategia': '-2x retorno diário do S&P 500. Alternativa menos extrema ao SPXU (-3x) para hedgear posições ou apostar em quedas do mercado americano.',
        'composicao': 'Swaps inversos -2x sobre S&P 500 + T-Bills. Decay menor que SPXU mas ainda significativo.',
        'riscos': 'ALTO RISCO. Em 2023 (S&P +26%), SDS teria caído ~40%+. Apenas para hedges táticos de curto prazo.',
    },
    'SPXS': {
        'resumo': 'Direxion Daily S&P 500 Bear 3x — idêntico ao SPXU mas da Direxion. Lucra quando S&P cai 3x.',
        'estrategia': 'Mesmo mecanismo do SPXU (ProShares). Direxion e ProShares competem diretamente com produtos idênticos. SPXS pode ter diferenças marginais de custo e spread. -3x do S&P 500 diário.',
        'composicao': 'Swaps inversos -3x sobre S&P 500 + T-Bills. Rebalanceamento diário.',
        'riscos': 'EXTREMO RISCO. Idênticos ao SPXU. Apenas hedges de 1-5 dias máximo.',
    },
    'SOXS': {
        'resumo': 'Direxion Daily Semiconductor Bear 3x — lucra quando semicondutores caem 3x. Oposto do SOXL.',
        'estrategia': '-3x retorno diário do índice de semicondutores da Direxion. Usado como hedge para posições compradas em SOXX/SMH ou como aposta em queda do setor de chips.',
        'composicao': 'Swaps inversos -3x sobre o índice de semicondutores + T-Bills. Extremamente volátil — semicondutores já têm beta alto.',
        'riscos': 'EXTREMO RISCO. Semicondutores são muito voláteis — o 3x inverso é devastador em bull markets de chips. Em 2023 (semicondutores +60%+), SOXS teria perdido ~90%+.',
    },
    'TECL': {
        'resumo': 'Direxion Daily Technology Bull 3x — tecnologia 3x alavancado. Similar ao TQQQ mas sobre o setor XLK.',
        'estrategia': '3x retorno diário do Technology Select Sector Index (XLK). Similar ao TQQQ mas o XLK inclui apenas ações de tecnologia (sem Amazon, Netflix que estão no QQQ). Apple e Microsoft respondem por ~50% do XLK.',
        'composicao': 'Swaps 3x sobre XLK + T-Bills. Alta concentração em Apple e Microsoft. Menos diversificado que TQQQ por excluir Amazon, Meta, Netflix.',
        'riscos': 'EXTREMO RISCO. 3x de um índice já concentrado em 2 ações. Volatility decay. Apenas day trade. Em 2022 caiu ~80%+.',
    },
    'TECS': {
        'resumo': 'Direxion Daily Technology Bear 3x — tecnologia 3x inverso. Lucra quando setor de tech cai.',
        'estrategia': '-3x retorno diário do XLK (Technology Select Sector). Hedge de posições compradas em tech ou aposta em queda do setor. Em bull markets de tech, perde valor extremamente rápido.',
        'composicao': 'Swaps inversos -3x sobre XLK + T-Bills.',
        'riscos': 'EXTREMO RISCO. Em 2023 (tech subiu muito), TECS teria caído >90%. Apenas hedges de horas/1-2 dias.',
    },
    'FAS': {
        'resumo': 'Direxion Daily Financial Bull 3x — setor financeiro 3x alavancado. Bancos em bull market amplificado.',
        'estrategia': '3x retorno diário do Russell 1000 Financial Services Index. Bancos, seguradoras, gestoras de ativos todos 3x alavancados. Beneficia de alta de juros e ciclo econômico positivo de forma amplificada.',
        'composicao': 'Swaps 3x sobre índice financeiro Russell 1000 + T-Bills. JPMorgan, Berkshire, Bank of America, Wells Fargo como principais exposições implícitas.',
        'riscos': 'EXTREMO RISCO. Em crises bancárias (Silicon Valley Bank 2023), setor financeiro pode cair 20%+ em dias — 3x isso = >50% de perda. Apenas day trade.',
    },
    'FAZ': {
        'resumo': 'Direxion Daily Financial Bear 3x — setor financeiro 3x inverso. Hedge de portfólios bancários.',
        'estrategia': '-3x retorno diário do Russell 1000 Financial Services Index. Útil como hedge em períodos de estresse bancário (SVB, Credit Suisse, 2023). Em bull markets de financeiro, perde explosivamente.',
        'composicao': 'Swaps inversos -3x sobre índice financeiro + T-Bills.',
        'riscos': 'EXTREMO RISCO. Em mercados de alta para bancos, decay e queda são devastadores. Apenas hedges táticos de 1-5 dias.',
    },
    'TNA': {
        'resumo': 'Direxion Daily Small Cap Bull 3x — Russell 2000 3x alavancado. Small caps com máxima alavancagem.',
        'estrategia': '3x retorno diário do Russell 2000 Index. Small caps já são mais voláteis que large caps — o 3x eleva o risco a níveis extremos. Beneficia fortemente em rally de small caps e ciclos de corte de juros.',
        'composicao': 'Swaps 3x sobre Russell 2000 + T-Bills. Em recuperações econômicas com cortes de juros, TNA pode subir 100%+ rapidamente.',
        'riscos': 'EXTREMO RISCO. Small caps + 3x alavancagem = volatilidade extrema. Em 2022 caiu >80%. Decay severo. Apenas day/swing trade de 1-5 dias.',
    },
    'TZA': {
        'resumo': 'Direxion Daily Small Cap Bear 3x — Russell 2000 3x inverso. Hedge de small caps.',
        'estrategia': '-3x retorno diário do Russell 2000. Small caps são mais sensíveis a recessão e credit crunch — TZA protege intensamente contra esses cenários. Em recoveries, perde explosivamente.',
        'composicao': 'Swaps inversos -3x sobre Russell 2000 + T-Bills.',
        'riscos': 'EXTREMO RISCO. Em bull markets de small caps, perda catastrófica. Apenas hedges táticos.',
    },
    'LABU': {
        'resumo': 'Direxion Daily Biotech Bull 3x — biotecnologia 3x alavancado. O mais volátil dos ETFs alavancados líquidos.',
        'estrategia': '3x retorno diário do S&P Biotechnology Select Industry Index. Biotech já é o setor mais volátil do mercado (dados clínicos podem mover ações 50%+ em um dia). 3x alavancagem sobre isso é exponencialmente arriscado.',
        'composicao': 'Swaps 3x sobre XBI/biotech index + T-Bills. Principais exposições implícitas: Moderna, BioNTech, CRISPR Therapeutics, Regeneron.',
        'riscos': 'RISCO EXTREMO. Biotech + 3x = perdas potenciais de >90% em semanas. Dados negativos de ensaios clínicos podem destruir valor instantaneamente. APENAS day trade de horas.',
    },
    'LABD': {
        'resumo': 'Direxion Daily Biotech Bear 3x — biotecnologia 3x inverso. Hedge extremo de posições long em biotech.',
        'estrategia': '-3x retorno diário do índice de biotecnologia. Usado para apostar em quedas de biotech (FDA rejeições, dados negativos, valuation excessivo).',
        'composicao': 'Swaps inversos -3x sobre XBI/biotech + T-Bills.',
        'riscos': 'RISCO EXTREMO. Biotech pode subir explosivamente com dados positivos — LABD perderia tanto quanto LABU ganharia. Apenas para hedges táticos de horas.',
    },
    'NAIL': {
        'resumo': 'Direxion Daily Homebuilders Bull 3x — construtoras residenciais 3x alavancado.',
        'estrategia': '3x retorno diário do Dow Jones US Select Home Construction Index. Beneficia de quedas nas taxas hipotecárias que estimulam compra de imóveis. Quando Fed corta juros, NAIL pode subir explosivamente.',
        'composicao': 'Swaps 3x sobre ITB/homebuilders index + T-Bills. D.R. Horton, Lennar, PulteGroup são exposições implícitas.',
        'riscos': 'ALTO RISCO. Setor imobiliário sensível a juros hipotecários. Com juros altos (2022-2024), construtoras sofrem — NAIL amplifica 3x. Apenas swing trade.',
    },
    'CURE': {
        'resumo': 'Direxion Daily Healthcare Bull 3x — saúde americana 3x alavancado. Setor defensivo com alavancagem agressiva.',
        'estrategia': '3x retorno diário do Health Care Select Sector Index (XLV). Saúde é setor "defensivo" mas o 3x adiciona agressividade. Beneficia de ciclo positivo de aprovações FDA, resultados de ensaios clínicos.',
        'composicao': 'Swaps 3x sobre XLV + T-Bills. Eli Lilly, UnitedHealth, J&J, Merck como exposições implícitas.',
        'riscos': 'ALTO RISCO. Mesmo em setor defensivo, 3x alavancagem é perigoso. Risco regulatório (regulação de preços de medicamentos). Decay. Apenas swing trade.',
    },
    'NUGT': {
        'resumo': 'Direxion Daily Gold Miners Bull 2x — mineradoras de ouro 2x alavancado. Beta ao ouro amplificado.',
        'estrategia': '2x retorno diário do NYSE Arca Gold Miners Index (GDX). Mineradoras de ouro já têm alavancagem operacional ao ouro (~2-3x). O ETF adiciona alavancagem financeira de 2x → exposição efetiva ao ouro de ~4-6x.',
        'composicao': 'Swaps 2x sobre GDX + T-Bills. Newmont, Barrick, Agnico Eagle implicitamente.',
        'riscos': 'ALTO RISCO. 4-6x de exposição efetiva ao ouro. Em quedas do ouro, NUGT pode cair 3x mais que o metal. Decay presente. Swing trade de 1-5 dias máximo.',
    },
    'DUST': {
        'resumo': 'Direxion Daily Gold Miners Bear 2x — mineradoras de ouro 2x inverso. Hedge de posições compradas em GDX/GDXJ.',
        'estrategia': '-2x retorno diário do NYSE Arca Gold Miners Index. Usado para apostar em queda das mineradoras de ouro ou hedgear posições long em GDX.',
        'composicao': 'Swaps inversos -2x sobre GDX + T-Bills.',
        'riscos': 'ALTO RISCO. Em bull markets de ouro/mineradoras, DUST perde explosivamente. Decay inverso. Apenas hedges táticos.',
    },
    'GUSH': {
        'resumo': 'Direxion Daily S&P Oil & Gas Bull 2x — empresas de oil & gas 2x alavancado.',
        'estrategia': '2x retorno diário do S&P Oil & Gas Exploration & Production Select Industry Index. Empresas de E&P de petróleo e gás amplificadas 2x. Beneficia de ciclos de alta do crude.',
        'composicao': 'Swaps 2x sobre XOP/oil&gas E&P index + T-Bills. Devon Energy, Pioneer, EOG Resources, ConocoPhillips implicitamente.',
        'riscos': 'ALTO RISCO. Petróleo é muito volátil. Quando crude cai, GUSH cai 2x. Decay em mercados laterais. Apenas swing trade em tendências claras de petróleo.',
    },
    'DRIP': {
        'resumo': 'Direxion Daily S&P Oil & Gas Bear 2x — empresas de oil & gas 2x inverso.',
        'estrategia': '-2x retorno diário do S&P Oil & Gas E&P Select Industry Index. Hedge contra quedas do petróleo ou aposta em transição energética que prejudica E&P.',
        'composicao': 'Swaps inversos -2x sobre XOP + T-Bills.',
        'riscos': 'ALTO RISCO. Em ciclos de alta do petróleo, DRIP perde explosivamente. Apenas hedges táticos.',
    },
    'ERX': {
        'resumo': 'Direxion Daily Energy Bull 2x — setor de energia americano 2x alavancado.',
        'estrategia': '2x retorno diário do Energy Select Sector Index (XLE). Diferente do GUSH (só E&P), ERX inclui o setor de energia completo: integradas (Exxon, Chevron), E&P, serviços.',
        'composicao': 'Swaps 2x sobre XLE + T-Bills. Exxon Mobil, Chevron, ConocoPhillips como maiores exposições implícitas.',
        'riscos': 'ALTO RISCO. Correlação ao preço do petróleo. Decay de alavancagem. Apenas swing trade em tendências definidas de energia.',
    },
    'ERY': {
        'resumo': 'Direxion Daily Energy Bear 2x — setor de energia americano 2x inverso.',
        'estrategia': '-2x retorno diário do XLE (Energy Select Sector). Hedge de posições long em energia ou aposta em queda do petróleo.',
        'composicao': 'Swaps inversos -2x sobre XLE + T-Bills.',
        'riscos': 'ALTO RISCO. Em bull markets de energia, ERY perde fortemente. Decay inverso. Apenas hedges táticos.',
    },
    'TMV': {
        'resumo': 'Direxion Daily 20+ Year Treasury Bear 3x — Treasuries longos 3x inverso. Aposta em alta de juros.',
        'estrategia': '-3x retorno diário do ICE US Treasury 20+ Year Index (TLT). Em 2022 (quando juros subiram fortemente), TMV foi um dos ETFs com melhor retorno. Aposta direta em continuação de alta de juros.',
        'composicao': 'Swaps inversos -3x sobre TLT/Treasuries 20+ + T-Bills.',
        'riscos': 'EXTREMO RISCO. Se Fed cortar juros agressivamente, TLT sobe e TMV cai 3x. Duração efetiva de -51 anos. Decay severo em mercados de juros laterais. Apenas para convicção muito forte em alta de juros.',
    },
    'TBT': {
        'resumo': 'ProShares UltraShort 20+ Year Treasury 2x — Treasuries longos 2x inverso. Similar ao TMV mas com menor alavancagem.',
        'estrategia': '-2x retorno diário do ICE US Treasury 20+ Year Index. Em 2022 foi um dos melhores ETFs disponíveis por apostar corretamente na alta de juros. Menos extremo que TMV (-3x).',
        'composicao': 'Swaps inversos -2x sobre TLT/Treasuries 20+ anos + T-Bills. Duração efetiva de ~-34 anos.',
        'riscos': 'ALTO RISCO. Em ciclos de queda de juros, TBT perde fortemente (não tão catastrófico quanto TMV). Decay presente. Apenas para apostas táticas em alta de juros.',
    },
    'UBT': {
        'resumo': 'ProShares Ultra 20+ Year Treasury 2x — Treasuries longos 2x alavancado. Aposta em queda de juros amplificada.',
        'estrategia': '2x retorno diário do TLT (Treasuries 20+). Quando Fed corta juros, TLT sobe — UBT sobe 2x. Em 2022 (juros subindo), caiu ~60%. Popular entre investidores apostando em pivot dovish do Fed.',
        'composicao': 'Swaps 2x sobre TLT/Treasuries 20+ + T-Bills.',
        'riscos': 'ALTO RISCO. Alta sensibilidade a política monetária. Em 2022 caiu ~60%. Decay de alavancagem. Apenas swing trade de dias em ciclos claros de queda de juros.',
    },
    'SH': {
        'resumo': 'ProShares Short S&P 500 — S&P 500 INVERSO simples (1x). Hedge básico contra quedas do mercado.',
        'estrategia': '-1x retorno diário do S&P 500. Sem alavancagem adicional além da inversão. Usado como hedge de portfólio ou para manter exposição neutra ao mercado. Em 2022 (S&P -18%), SH subiu ~+17% (líquido do decay).',
        'composicao': 'Swaps inversos -1x sobre S&P 500 + T-Bills. Mesmo sem alavancagem adicional, tem custo de rebalanceamento diário.',
        'riscos': 'Decay presente mesmo sem alavancagem adicional. Em mercados de alta, perde consistentemente. Custo de oportunidade vs estar em cash. Adequado para hedges de semanas a meses (não décadas).',
    },
    'PSQ': {
        'resumo': 'ProShares Short QQQ — Nasdaq 100 INVERSO simples (1x). Hedge básico contra quedas de tech.',
        'estrategia': '-1x retorno diário do Nasdaq-100. Sem alavancagem adicional. Alternativa menos extrema ao SQQQ para hedgear posições compradas em tech. Em 2022 (QQQ -33%), PSQ subiu ~+30%.',
        'composicao': 'Swaps inversos -1x sobre QQQ + T-Bills.',
        'riscos': 'Decay em bull markets. Em 2023 (QQQ +55%), PSQ teria caído ~40%+. Adequado para hedges de semanas, não de longo prazo.',
    },
    'DOG': {
        'resumo': 'ProShares Short Dow30 — Dow Jones INVERSO simples (1x). Hedge básico contra quedas do DJIA.',
        'estrategia': '-1x retorno diário do Dow Jones Industrial Average. Sem alavancagem adicional. Menos líquido que SH (S&P) ou PSQ (Nasdaq). Usado para hedges específicos contra quedas das 30 grandes empresas do DJIA.',
        'composicao': 'Swaps inversos -1x sobre DJIA + T-Bills.',
        'riscos': 'Decay em bull markets. Menor liquidez que SH/PSQ. Metodologia do DJIA (ponderação por preço) torna o hedge menos preciso. Adequado apenas para hedges de curto prazo.',
    },
    'RWM': {
        'resumo': 'ProShares Short Russell 2000 — small caps INVERSO simples (1x). Hedge contra recessão via small caps.',
        'estrategia': '-1x retorno diário do Russell 2000. Small caps caem mais em recessões — RWM é hedge eficiente de portfólios durante desacelerações econômicas. Em 2022 (IWM -21%), RWM subiu ~+19%.',
        'composicao': 'Swaps inversos -1x sobre Russell 2000 + T-Bills.',
        'riscos': 'Decay em mercados de alta de small caps. Em recuperações econômicas pós-recessão, small caps lideram — RWM perde. Adequado para hedges de meses de pico de recessão.',
    },
    'SVXY': {
        'resumo': 'ProShares Short VIX Short-Term ETF — inverso do VIX. Lucra em períodos de baixa volatilidade e mercado calmo.',
        'estrategia': 'Oferece -0.5x o retorno diário dos futuros de VIX de curto prazo. Quando VIX cai (mercado calmo), SVXY sobe. Ganha com o roll POSITIVO dos futuros de VIX em contango — o oposto do UVXY.',
        'composicao': 'Swaps inversos sobre futuros de VIX de curto prazo + T-Bills. -0.5x (não -1x) por razões de proteção após o "VIXplosion" de fevereiro 2018.',
        'riscos': 'Em eventos de mercado (COVID crash em 2020, VIX spike), SVXY pode perder 50%+ em horas. Evento "volmageddon" 2018 quase destruiu o produto original. Adequado para mercados calmos de tendência clara.',
    },
    'VXX': {
        'resumo': 'iPath S&P 500 VIX Short-Term Futures ETN — "índice do medo" sem alavancagem. Perde valor constantemente.',
        'estrategia': 'ETN (não ETF) que replica o S&P 500 VIX Short-Term Futures Index Total Return. Investe em futuros de VIX de 1 e 2 meses sem alavancagem. Historicamente, VXX perde valor quase constantemente pelo custo de roll — futuros de VIX sempre em contango.',
        'composicao': 'Futuros de VIX do CBOE (1º e 2º vencimentos) + pesos dinâmicos. Roll diário para manter a posição constante.',
        'riscos': 'PERDA ESTRUTURAL: pode perder 50-80% ao ano em mercados tranquilos pelo custo de roll. Requere reverse splits frequentes. ETN = risco de crédito da emissora (Barclays). Apenas hedge de horas/dias em eventos específicos.',
    },
    'BITI': {
        'resumo': 'ProShares Short Bitcoin ETF — Bitcoin INVERSO simples. Lucra quando BTC cai. Hedge de curto prazo.',
        'estrategia': '-1x retorno diário do Bitcoin (via futuros CME). Hedge para posições compradas em Bitcoin. Em bear markets de cripto, pode subir significativamente. O custo de roll de futuros inversos adiciona drag.',
        'composicao': 'Swaps inversos e futuros de Bitcoin na CME + T-Bills. -1x do preço do BTC.',
        'riscos': 'ALTO RISCO. Em bull markets de Bitcoin (podem ser explosivos), BITI perde muito rapidamente. Decay de futuros inversos. Bitcoin 24/7 pode mover após fechamento do ETF. Apenas hedge de 1-5 dias.',
    },
    'UGL': {
        'resumo': 'ProShares Ultra Gold 2x — ouro 2x alavancado. Para apostas alavancadas na subida do ouro.',
        'estrategia': '2x retorno diário do Bloomberg Gold Subindex (futuros de ouro). Quando ouro sobe 1%, UGL sobe ~2%. Usado para amplificar retornos em ambientes favoráveis ao ouro (juros reais negativos, dólar fraco, stress geopolítico).',
        'composicao': 'Swaps 2x sobre futuros de ouro + T-Bills. Rebalanceamento diário.',
        'riscos': 'ALTO RISCO. Ouro pode ser volátil — 2x amplifica. Decay presente. Em períodos de juros reais positivos (desfavoráveis ao ouro), UGL pode perder 30-40%. Apenas swing trade.',
    },
    'GLL': {
        'resumo': 'ProShares UltraShort Gold 2x — ouro 2x inverso. Aposta na queda do ouro ou hedge de posições long.',
        'estrategia': '-2x retorno diário do ouro. Usado quando se acredita que juros reais subirão ou dólar se fortalecerá — condições desfavoráveis ao ouro.',
        'composicao': 'Swaps inversos -2x sobre futuros de ouro + T-Bills.',
        'riscos': 'ALTO RISCO. Em bull markets de ouro (crise, inflação, guerra), GLL perde explosivamente. Decay inverso. Apenas hedges táticos de dias.',
    },
    'AGQ': {
        'resumo': 'ProShares Ultra Silver 2x — prata 2x alavancado. Alta volatilidade pelo uso industrial + aspecto monetário.',
        'estrategia': '2x retorno diário do Bloomberg Silver Subindex (futuros de prata). Prata é mais volátil que ouro (maior uso industrial). Em ciclos favoráveis (energia solar, EV, baixos juros reais), pode subir explosivamente.',
        'composicao': 'Swaps 2x sobre futuros de prata + T-Bills.',
        'riscos': 'EXTREMO RISCO. Prata 2x = altíssima volatilidade. Pode subir ou cair 20%+ em semanas. Decay em mercados laterais. Apenas swing trade em tendências fortes.',
    },
    'ZSL': {
        'resumo': 'ProShares UltraShort Silver 2x — prata 2x inverso. Aposta na queda da prata.',
        'estrategia': '-2x retorno diário da prata. Usado quando ciclo industrial enfraquece ou juros reais sobem (desfavoráveis a metais preciosos).',
        'composicao': 'Swaps inversos -2x sobre futuros de prata + T-Bills.',
        'riscos': 'EXTREMO RISCO. Em bull markets de prata (que podem ser explosivos), ZSL perde catastroficamente. Apenas hedges táticos.',
    },

    # ══ MULTI-ASSET — NOVOS ═══════════════════════════════════════════════════
    'AOM': {
        'resumo': 'iShares Core Moderate Allocation ETF — portfólio moderado 40% ações / 60% renda fixa em um único ETF.',
        'estrategia': 'ETF de ETFs da iShares. Investe em ~15 ETFs BlackRock para atingir alocação 40% ações globais + 60% renda fixa global. Perfil conservador — para investidores mais avessos a risco que o AOR (60/40).',
        'composicao': 'Renda variável (~40%): IVV, IEFA, IEMG. Renda fixa (~60%): AGG, IGOV, corporativos IG. Rebalanceamento periódico automático.',
        'riscos': 'Taxa dupla (AOM + ETFs subjacentes). Alocação fixa pode não ser ideal para todos os ciclos. Em crises onde bonds e ações caem juntos (2022), não protege totalmente.',
    },
    'AOA': {
        'resumo': 'iShares Core Aggressive Allocation ETF — portfólio agressivo 80% ações / 20% renda fixa em um único ETF.',
        'estrategia': 'ETF de ETFs da iShares com perfil agressivo: 80% ações globais + 20% renda fixa. Ideal para investidores de longo prazo com alta tolerância a volatilidade. Rebalanceamento automático periódico.',
        'composicao': 'Ações (~80%): IVV (S&P 500), IEFA (desenvolvidos), IEMG (emergentes). Renda fixa (~20%): AGG, IGOV. ~15 ETFs subjacentes.',
        'riscos': 'Taxas duplas. Alta exposição a ações (~80%) = queda significativa em bear markets. Em 2022, AOA teria caído ~18%+ pela combinação de ações e bonds em queda.',
    },
    'AOK': {
        'resumo': 'iShares Core Conservative Allocation ETF — portfólio conservador 30% ações / 70% renda fixa.',
        'estrategia': 'O mais conservador da série iShares Core Allocation. Apenas 30% ações + 70% renda fixa. Para investidores com horizonte curto ou muito avessos a risco. Volatilidade mínima entre os ETFs de alocação.',
        'composicao': 'Ações (~30%): IVV, IEFA, IEMG. Renda fixa (~70%): AGG, bonds internacionais, TIPS. ~15 ETFs subjacentes.',
        'riscos': 'Crescimento lento por dominância de bonds. Em ambiente de juros altos/inflação, bonds caem = portfólio sofre. Taxas duplas. Yield real pode ser negativo em inflação alta.',
    },
    'GAL': {
        'resumo': 'SPDR SSGA Global Allocation ETF — portfólio global balanceado 60/40 com visão estratégica da State Street.',
        'estrategia': 'ETF de ETFs gerido pela State Street Global Advisors. Alocação global estratégica: ~60% ações + ~40% renda fixa com ajustes táticos trimestrais baseados nas visões macro da SSGA. Gestão semi-ativa.',
        'composicao': 'ETFs SPDR de ações globais (~60%): SPY, SPDW (desenvolvidos), SPEM (emergentes). ETFs de bonds (~40%): SPSB, SPLB, SPIB. Ajustes táticos baseados no ciclo econômico.',
        'riscos': 'Custo de 0.25% + taxas dos ETFs subjacentes. Gestão semi-ativa pode underperformar alocação passiva. Exposição cambial global. Em 2022, ambas as classes caíram.',
    },
    'MDIV': {
        'resumo': 'First Trust Multi-Asset Diversified Income ETF — renda diversificada: ações + REITs + preferências + bonds + MLPs.',
        'estrategia': 'Gestão ativa focada em maximizar renda corrente via múltiplas classes: ações de dividendo americanas (~20%), REITs (~20%), ações preferenciais (~20%), bonds de alto yield (~20%), MLPs (infraestrutura energética, ~20%).',
        'composicao': 'Cinco segmentos de ~20% cada: dividendo (SCHD-like), REITs, preferred (PFF-like), high yield bonds, MLPs de energia (Magellan Midstream, Enterprise Products). Alta diversificação de fontes de renda.',
        'riscos': 'Alta exposição a energia (MLPs ~20%). Sensível a juros por todos os segmentos. Gestão ativa com custo de 0.68%. MLPs têm tributação especial (K-1). Distribuição mensal pode incluir retorno de capital.',
    },
    'RPAR': {
        'resumo': 'RPAR Risk Parity ETF — distribui risco igualmente: ações + bonds + ouro + commodities. Estratégia de Ray Dalio.',
        'estrategia': 'Implementa risk parity: ao invés de alocar capital igualmente, distribui o RISCO igualmente entre 4 classes. Como bonds têm menor risco, precisam de mais capital; como ações têm maior risco, recebem menos capital.',
        'composicao': 'TIPS (~35%), bonds nominais longo prazo (~10%), ações globais (~25%), ouro (~15%), commodities (~10%), outros (~5%). A alavancagem embutida nos bonds equilibra os riscos entre classes.',
        'riscos': 'Em 2022 (ações E bonds caíram juntos), risk parity performou muito mal. Custo de 0.23%. Alavancagem implícita nos bonds. Estratégia mais adequada para período 1970-2020 que para hoje.',
    },
    'GDE': {
        'resumo': 'WisdomTree Efficient Gold Plus Equity ETF — S&P 500 + exposição de 90% a ouro via futuros. Portfólio eficiente.',
        'estrategia': 'Detém ações do S&P 500 (100% do capital) e usa os 10% em futuros de ouro com alavancagem de 9x, obtendo exposição de ~90% a ouro. Resultado: portfólio com 100% ações + 90% ouro usando apenas 100% do capital.',
        'composicao': '100% S&P 500 (implícito via futures/swaps) + futuros de ouro com exposição de ~90% do valor do portfólio. Ouro como proteção contra inflação e crises enquanto ações fornecem crescimento.',
        'riscos': 'Alavancagem nos futuros de ouro. Custo de roll dos futuros de ouro. Se ouro E ações caírem juntos (pouco comum mas possível), portfólio sofre duplamente. Custo de 0.20%.',
    },

    # ══ ESG — NOVOS ════════════════════════════════════════════════════════════
    'ESGU': {
        'resumo': 'iShares ESG Aware MSCI USA ETF — S&P 500/MSCI EUA com filtros ESG. Exclui armas, tabaco e carvão.',
        'estrategia': 'Replica o MSCI USA Extended ESG Focus Index. Começa com o MSCI USA e aplica: (1) exclusões setoriais (armas, tabaco, carvão, entretenimento adulto), (2) scoring ESG empresarial, (3) overweight em empresas com alto score ESG.',
        'composicao': 'Muito similar ao VOO/IVV com exclusões. Apple, Microsoft, Nvidia, Amazon, Alphabet dominam (~30%). Sem Lockheed Martin, Philip Morris, algumas empresas de carvão.',
        'riscos': 'Underperforma ligeiramente vs VOO em alguns períodos por excluir empresas "sin stocks" rentáveis. Custo de 0.15% vs 0.03% do VOO. O que é "ESG" é subjetivo.',
    },
    'ESGE': {
        'resumo': 'iShares ESG Aware MSCI Emerging Markets ETF — emergentes com filtros ESG. Reduz exposição a governança ruim.',
        'estrategia': 'Replica o MSCI Emerging Markets Extended ESG Focus Index. Aplica filtros ESG ao universo de emergentes — particularmente relevante em emergentes onde governança corporativa é muitas vezes problemática.',
        'composicao': 'China (~25%), Taiwan (~15%), Índia (~20%), Coreia (~11%), Brasil (~5%). Exclui empresas de armas, carvão. Similarmente ao EEM/IEMG mas com scoring ESG.',
        'riscos': 'Mesmos riscos de emergentes. O filtro ESG em emergentes é mais subjetivo. Custo de 0.25% vs 0.09% do IEMG. Pode excluir oportunidades rentáveis por critérios discutíveis.',
    },
    'ESGD': {
        'resumo': 'iShares ESG Aware MSCI EAFE ETF — desenvolvidos ex-EUA com filtros ESG. Versão ESG do EFA.',
        'estrategia': 'Replica o MSCI EAFE Extended ESG Focus Index. Aplica filtros ESG ao universo de mercados desenvolvidos ex-EUA. Japão, Europa, Austrália com exclusões setoriais e scoring ESG.',
        'composicao': 'Japão (~24%), UK (~14%), França (~11%), Suíça (~10%), Alemanha (~9%). Excluí empresas de armas, tabaco, carvão. Similar ao EFA/IEFA em composição geral.',
        'riscos': 'Mesmos do EFA/IEFA. Custo de 0.20% vs 0.07% do IEFA. Subjetividade do scoring ESG. Pode underperformar em ciclos de energia ou defesa.',
    },
    'SNPE': {
        'resumo': 'Xtrackers S&P 500 ESG ETF — S&P 500 com filtros ESG da DWS/Xtrackers. Custo de 0.10%.',
        'estrategia': 'Replica o S&P 500 ESG Index. Começa com o S&P 500 e exclui empresas de armas, tabaco, petróleo areias betuminosas e com baixo score ESG do MSCI. Mantém a exposição setorial próxima ao S&P 500 original.',
        'composicao': 'Muito similar ao SPY/VOO. Apple, Microsoft, Nvidia dominam. Sem Exxon, sem empresas de defesa pura, sem tabaco. Diversificação sectorial próxima ao original.',
        'riscos': 'Underperforma quando energia/defesa/tabaco lideraram (2022). Custo de 0.10% vs 0.03% do VOO. Metodologia ESG da S&P pode mudar.',
    },
    'SUSL': {
        'resumo': 'iShares ESG MSCI USA Leaders ETF — top 50% das empresas americanas em score ESG. Seleção mais rigorosa que ESGU.',
        'estrategia': 'Replica o MSCI USA ESG Leaders Index. Seleciona apenas as empresas com score ESG ACIMA da mediana dentro de cada setor do MSCI USA. Mais rigoroso que ESGU — seleciona líderes ESG, não só exclui os piores.',
        'composicao': 'Apple, Microsoft, Visa, Mastercard, Alphabet dominam. Menos empresas (~375 vs ~700 do ESGU). Setores: TI (~28%), Saúde (~14%), Financeiro (~14%), Industrial (~11%).',
        'riscos': 'Menor diversificação por ser mais seletivo. Custo de 0.10%. Critérios ESG subjetivos. Pode excluir empresas rentáveis por scores questionáveis.',
    },

    # ══ NOVOS CRIPTO & FINTECH ════════════════════════════════════════════════
    'ETH': {
        'resumo': 'Grayscale Ethereum Mini Trust — Ethereum físico com estrutura de mini trust. Custo mais baixo que ETHA.',
        'estrategia': 'Detém Ethereum físico. Estrutura de "mini" trust com cota menor e expense ratio mais baixo que o ETHE original da Grayscale. Aprovado junto aos ETF spot de Ethereum em maio/2024.',
        'composicao': '100% Ethereum físico. Cada cota representa uma fração de ETH. Custódia pela Coinbase. Sem alavancagem ou derivativos.',
        'riscos': 'Volatilidade extrema do Ethereum. Risco regulatório. Risco de custódia. Smart contract bugs no protocolo Ethereum. Ethereum passou para Proof of Stake em 2022 — mudança de infraestrutura.',
    },
    'BTC': {
        'resumo': 'Grayscale Bitcoin Mini Trust — Bitcoin físico com estrutura mini. Alternativa mais barata ao GBTC histórico.',
        'estrategia': 'Detém Bitcoin físico. Lançado como spin-off do GBTC com expense ratio menor. Os holders do GBTC receberam BTC proporcionalmente. Custódia pela Coinbase.',
        'composicao': '100% Bitcoin físico custodiado pela Coinbase. Cota menor que GBTC. Expense ratio intermediário entre GBTC (1.50%) e IBIT (0.25%).',
        'riscos': 'Mesmos do Bitcoin: volatilidade extrema, regulação, custódia. Menor AUM que IBIT/FBTC. Emissora Grayscale tem histórico controverso (GBTC discount).',
    },
    'ETHE': {
        'resumo': 'Grayscale Ethereum Trust ETF — conversão do antigo trust de ETH da Grayscale. Expense ratio alto (2.50%).',
        'estrategia': 'Originalmente trust fechado como o GBTC para Bitcoin, convertido para ETF spot em maio/2024. Detém Ethereum físico. Custo muito alto (2.50%) vs concorrentes (ETHA: 0.25%). Investidores têm migrado para ETHA.',
        'composicao': '100% Ethereum físico. AUM bilionário mas em declínio por saída de capital para concorrentes mais baratos (ETHA, FETH).',
        'riscos': 'Custo 10x maior que ETHA (2.50% vs 0.25%) corrói retorno significativamente no longo prazo. Mesmos riscos de volatilidade do ETH. Erosão estrutural de AUM.',
    },
    'BSOL': {
        'resumo': 'Bitwise Solana Staking ETF — primeiro ETF de Solana nos EUA com staking. Exposição ao terceiro maior criptoativo.',
        'estrategia': 'Detém Solana (SOL) físico com possibilidade de staking para gerar renda adicional (~6-8% ao ano em SOL). Solana é blockchain de alta performance: 65.000 TPS vs 15 TPS do Ethereum. Competição direta com ETH no espaço DeFi/NFT.',
        'composicao': '100% Solana (SOL) físico + renda de staking. Aprovado pela SEC em 2024/2025. Staking gera SOL adicional que pode ser distribuído ou reinvestido.',
        'riscos': 'ALTO RISCO. Solana sofreu 3 interrupções graves da rede. Altcoin com maior volatilidade que BTC/ETH. Risco de concentração — FTX detinha grande parte do SOL (FTX colapsou em 2022). Regulação mais incerta que BTC/ETH.',
    },

    # ══ NOVOS GERAL ════════════════════════════════════════════════════════════
    'DYNF': {
        'resumo': 'iShares U.S. Equity Factor Rotation Active ETF — rotação dinâmica entre fatores conforme o ciclo econômico.',
        'estrategia': 'Gestão ativa pela BlackRock. Aloca entre os 5 fatores principais (value, quality, momentum, low volatility, size) conforme sinais quantitativos do ciclo econômico. Em expansão: momentum; em contração: quality/low vol.',
        'composicao': 'Portfólio dinâmico que rotaciona entre ETFs iShares de fator (QUAL, MTUM, VLUE, USMV, SIZE). Alocação muda mensalmente. Diversificado entre ~500-700 ações americanas em dado momento.',
        'riscos': 'Gestão ativa pode errar o timing dos ciclos. Custo de 0.30% + transações de rotação. Rotação de fator pode gerar ganhos de capital tributáveis. Backtests podem não refletir futuro.',
    },
    'EMLC': {
        'resumo': 'VanEck EM Local Currency Bond ETF — bonds soberanos de emergentes em moeda local. Yield alto + aposta cambial.',
        'estrategia': 'Replica o J.P. Morgan GBI-EMG Core Index. Bonds governamentais de emergentes em suas moedas locais (real, peso, rupia, lira, etc.). Exposição ao yield local + potencial de valorização cambial das moedas emergentes vs USD.',
        'composicao': 'Brasil (~10%), México (~9%), Indonésia (~9%), África do Sul (~8%), Tailândia (~7%), China, Polônia, Colômbia. ~20 países. Yield local ~5-10%.',
        'riscos': 'Risco cambial DUPLO para investidores em USD: moeda local vs USD + USD vs BRL. Risco político de cada país. Inflação local pode erodir yield real. Alta volatilidade.',
    },
    'CGDV': {
        'resumo': 'Capital Group Dividend Value ETF — gestão ativa da Capital Group (American Funds) em dividendos de valor.',
        'estrategia': 'Gestão ativa pela Capital Group, uma das maiores gestoras do mundo (~$2T em AUM). Seleciona ações americanas e globais com dividend yield acima da média e perspectivas de crescimento de dividendo. Filosofia de baixo turnover.',
        'composicao': 'Mix de ações americanas e internacionais de valor com dividendos. Financeiro, Saúde, Consumo Básico dominam. Gestão conservadora típica da Capital Group.',
        'riscos': 'Gestão ativa com custo de 0.33%. Exposição internacional adiciona risco cambial. Pode underperformar ETFs de dividendo passivos (SCHD, VYM). Capital Group menos transparente que gestoras passivas.',
    },
    'BLCR': {
        'resumo': 'iShares Large Cap Core Active ETF — S&P 500 com gestão ativa da BlackRock para pequeno alpha sobre o índice.',
        'estrategia': 'Gestão ativa quantitativa da BlackRock sobre o universo de large caps americanas. Usa modelos de machine learning para pequenos desvios do S&P 500 buscando alpha incremental. "Enhanced indexing" — custo maior que VOO mas menor que fundos ativos tradicionais.',
        'composicao': 'Similar ao S&P 500 (Apple, Microsoft, Nvidia dominam) com small tilts sobre/subpeso de acordo com modelos quantitativos da BlackRock.',
        'riscos': 'Custo maior que VOO por gestão ativa. Alpha prometido pode ser zero no longo prazo. Menor transparência de portfólio. A BlackRock tem track record misto em gestão ativa.',
    },
    'CGGR': {
        'resumo': 'Capital Group Growth ETF — gestão ativa da Capital Group focada em ações de crescimento globais.',
        'estrategia': 'Gestão ativa pela Capital Group. Investe em ações de crescimento americanas e internacionais com seleção fundamental rigorosa. Capital Group é conhecida pela gestão de longo prazo de baixo turnover.',
        'composicao': 'Concentrado em large cap growth: Microsoft, Nvidia, Apple, Amazon. Mix com exposição internacional a empresas de crescimento (ASML, Novo Nordisk). ~50-80 posições.',
        'riscos': 'Gestão ativa com custo de 0.39%. Concentração em growth tech. Exposição internacional adiciona câmbio. Capital Group menos transparente que gestoras passivas.',
    },
    'DFAI': {
        'resumo': 'Dimensional International Core Equity Market ETF — mercado desenvolvido ex-EUA com tilt de fatores da Dimensional.',
        'estrategia': 'Gestão ativa quantitativa da Dimensional. Cobre mercados desenvolvidos ex-EUA amplos com sobreposição em value e profitability. Alternativa ao EFA/IEFA com factor tilts incorporados.',
        'composicao': 'Japão (~23%), UK (~14%), Europa continental (~40%), Austrália (~7%), Outros (~16%). ~3.000 empresas. More value/profitable weighting vs IEFA.',
        'riscos': 'Gestão ativa com custo de 0.23% vs 0.07% do IEFA. Factor tilts podem underperformar em ciclos de growth internacional. Risco cambial múltiplo.',
    },
    'AVEM': {
        'resumo': 'Avantis Emerging Markets Equity ETF — emergentes com tilt de value + profitability da Avantis.',
        'estrategia': 'Gestão ativa quantitativa da Avantis em mercados emergentes. Sobrepesa ações de emergentes com baixo Price-to-Book e alta lucratividade. Alternativa com factor tilts ao IEMG/EEM.',
        'composicao': 'China (~25%), Taiwan (~15%), Índia (~18%), Coreia (~10%), Brasil (~6%). Similar ao IEMG/EEM mas com mais peso em value/profitable. ~800 ações.',
        'riscos': 'Gestão ativa com custo de 0.33% vs 0.09% do IEMG. Mesmos riscos de emergentes. Factor tilts podem underperformar growth de emergentes.',
    },
    'EMXC': {
        'resumo': 'iShares MSCI Emerging Markets ex China ETF — emergentes excluindo China. Diversificação sem risco político chinês.',
        'estrategia': 'Replica o MSCI Emerging Markets ex China Index. Com os riscos regulatórios e geopolíticos da China crescendo, muitos investidores buscam exposição a emergentes sem China. Índia, Taiwan, Coreia, Brasil ganham maior peso.',
        'composicao': 'Índia (~26%), Taiwan (~21%), Coreia do Sul (~16%), Brasil (~7%), Arábia Saudita (~6%), África do Sul (~5%). Samsung, TSMC, Reliance, Naspers. ~700 empresas sem nenhuma chinesa.',
        'riscos': 'Sem China = perde mercado de 1.4B de consumidores. Concentração em Taiwan/Coreia = risco geopolítico asiático persiste. Custo de 0.25%. Índia com valuation elevado.',
    },
    'EFG': {
        'resumo': 'iShares MSCI EAFE Growth ETF — metade de crescimento dos mercados desenvolvidos ex-EUA.',
        'estrategia': 'Replica o MSCI EAFE Growth Index. Seleciona ações de crescimento (alto P/B, alto crescimento de EPS) dos mercados desenvolvidos ex-EUA. Complemento ao EFV (value) no universo internacional.',
        'composicao': 'ASML (~6%), Novo Nordisk (~5%), Roche (~4%), SAP (~4%), L\'Oréal (~4%), LVMH, Hermès, AIA Group. Tech e saúde dominam. Países: Japão (~20%), UK (~11%), França (~12%), Suíça (~12%).',
        'riscos': 'Risco cambial múltiplo. Growth internacional mais sensível a juros americanos (taxas de desconto). Underperforma vs EFV em ciclos de value. Custo de 0.37%.',
    },
    'EFV': {
        'resumo': 'iShares MSCI EAFE Value ETF — metade de value dos mercados desenvolvidos ex-EUA.',
        'estrategia': 'Replica o MSCI EAFE Value Index. Seleciona ações baratas (baixo P/B, baixo P/E) dos mercados desenvolvidos ex-EUA. Bancos, energia e industriais europeus/japoneses dominam.',
        'composicao': 'Toyota (~4%), HSBC (~3%), Shell (~3%), TotalEnergies (~3%), Novartis (~3%), Samsung, Mitsubishi UFJ, ANZ. Financeiro (~25%), Energia (~13%), Industrial (~12%). Países: Japão (~25%), UK (~17%).',
        'riscos': 'Value internacional pode continuar underperformando growth por muito tempo. Alta exposição a financeiro e energia (setores tradicionais). Risco cambial múltiplo. Custo de 0.36%.',
    },
    'EUFN': {
        'resumo': 'iShares MSCI Europe Financials ETF — bancos e financeiro europeu. Alta sensibilidade à saúde bancária da Europa.',
        'estrategia': 'Replica o MSCI Europe Financials Index. Exposição concentrada em bancos, seguradoras e gestoras de ativos europeias. Europa tem grandes bancos universais: BNP Paribas, HSBC, UBS, Deutsche Bank, Santander.',
        'composicao': 'HSBC (~11%), UBS (~8%), BNP Paribas (~7%), Santander (~7%), ING (~6%), Intesa Sanpaolo (~5%), Deutsche Bank, UniCredit, Barclays. ~50 empresas. Bancos (~70%), Seguros (~20%).',
        'riscos': 'Risco de crédito bancário europeu. Regulação bancária europeia (Basileia III+). Risco euro/USD. Exposição a dívida soberana periférica (Itália, Espanha). Lucratividade bancária europeia historicamente baixa.',
    },
    'FEZ': {
        'resumo': 'SPDR EURO STOXX 50 ETF — as 50 maiores empresas da Zona do Euro. Exposição direta ao euro e economia europeia.',
        'estrategia': 'Replica o Euro Stoxx 50 Index — as 50 maiores empresas dos países membros da Zona do Euro (exclui UK, Suíça). Similar a um "S&P 500 europeu" mas muito mais concentrado.',
        'composicao': 'ASML (~8%), SAP (~6%), TotalEnergies (~5%), Sanofi (~5%), Schneider Electric (~5%), LVMH (~4%), Air Liquide, Airbus, BNP Paribas, Siemens. 50 empresas de 11 países.',
        'riscos': 'Exclusão do UK (pós-Brexit) e Suíça. Concentração em França (~36%) e Alemanha (~28%). Risco euro/USD. Crescimento econômico europeu estruturalmente menor que EUA. Risco político europeu.',
    },
    'EZU': {
        'resumo': 'iShares MSCI Eurozone ETF — mercado amplo da Zona do Euro (~240 empresas). Mais diversificado que FEZ.',
        'estrategia': 'Replica o MSCI EMU Index (~240 empresas vs 50 do FEZ). Cobre todos os países da Zona do Euro com large e mid caps. Mais diversificado mas menos conhecido que FEZ para traders ativos.',
        'composicao': 'França (~34%), Alemanha (~26%), Países Baixos (~12%), Espanha (~8%), Itália (~7%), Bélgica (~4%). ASML, SAP, TotalEnergies, LVMH, Sanofi no topo. ~240 empresas.',
        'riscos': 'Risco euro/USD. Crescimento europeu lento. Risco político de cada país membro. Concentração em França/Alemanha. Custo de 0.49%.',
    },
    'DBO': {
        'resumo': 'Invesco DB Oil Fund ETF — petróleo via futuros com estratégia de roll otimizada para reduzir custo de contango.',
        'estrategia': 'Investe em futuros de crude WTI com algoritmo de roll otimizado — seleciona o vencimento que maximiza roll yield (positivo em backwardation) ou minimiza custo de roll (negativo em contango). Superior ao USO que simplesmente rola o contrato mais próximo.',
        'composicao': 'Futuros de crude WTI em vencimentos otimizados pelo algoritmo DB. T-Bills como colateral. Performance tipicamente melhor que USO no longo prazo por roll otimizado.',
        'riscos': 'Mesmo com otimização, custo de roll presente. Petróleo muito volátil (OPEP, geopolítica). Adequado para swing trade de semanas (melhor que USO) mas ainda não para longo prazo.',
    },
    'BIZD': {
        'resumo': 'VanEck BDC Income ETF — Business Development Companies. Empréstimos privados a pequenas/médias empresas. Yield ~10%.',
        'estrategia': 'Replica o MVIS US Business Development Companies Index. BDCs são empresas que emprestam para small e mid caps americanas que não conseguem crédito bancário convencional. Obrigadas por lei a distribuir 90%+ do lucro tributável — dividend yield muito alto (~10%).',
        'composicao': 'Ares Capital (~20%), Prospect Capital (~9%), FS KKR (~8%), Blue Owl Capital (~8%), Golub Capital (~7%), New Mountain Finance. ~25 BDCs americanas.',
        'riscos': 'Alta alavancagem dos BDCs (empréstimos com dívida própria). Em recessão, defaults dos tomadores sobem. Risco de liquidez (portfólio de empréstimos privados não marcado a mercado diariamente). Complexidade tributária (K-1). Custo de 0.40%.',
    },
    'IUSG': {
        'resumo': 'iShares Core S&P US Growth ETF — ações de crescimento do S&P 900. Tecnologia + saúde em alta.',
        'estrategia': 'Replica o S&P 900 Growth Index — ações de crescimento de large, mid e small caps americanas. Mais amplo que QQQ por incluir todas as capitalizações com características de growth.',
        'composicao': 'Apple, Microsoft, Nvidia, Amazon, Meta, Alphabet (~35%). ~450 ações de crescimento. Tecnologia (~40%), Saúde (~14%), Consumo Discricionário (~12%).',
        'riscos': 'Concentração em tech. Sensível a juros. Alta volatilidade em risk-off. Custo de 0.04%.',
    },
    'IUSV': {
        'resumo': 'iShares Core S&P US Value ETF — ações de valor do S&P 900. Financeiro + energia + saúde.',
        'estrategia': 'Replica o S&P 900 Value Index — ações de valor de large, mid e small caps americanas. Mais amplo que VLUE por incluir todas as capitalizações com características de value.',
        'composicao': 'Berkshire, JPMorgan, Exxon Mobil, Johnson & Johnson, Chevron, Bank of America. ~450 ações de valor. Financeiro (~22%), Saúde (~16%), Energia (~10%).',
        'riscos': 'Historicamente underperformou growth. Concentração em setores tradicionais. Value traps possíveis. Custo de 0.04%.',
    },
}



def get_prospecto(ticker):
    """Retorna prospecto do ETF: hardcoded se disponível, senão busca do cache da sessão."""
    if ticker in ETF_PROSPECTO:
        return ETF_PROSPECTO[ticker]
    # Tenta retornar do cache de prospectos gerados por IA na sessão atual
    cache = st.session_state.get('prospecto_cache', {})
    return cache.get(ticker)   # None se ainda não gerado


def gerar_prospecto_ia(ticker, nome, categoria, er, info_etf):
    """Chama a API do Claude para gerar prospecto resumido e traduzido do ETF."""
    er_str  = f"{er:.3f}%/ano" if er else "não disponível"
    aum_str = ""
    if info_etf and info_etf.get('aum'):
        aum = info_etf['aum']
        aum_str = f"${aum/1e12:.2f}T" if aum >= 1e12 else f"${aum/1e9:.1f}B" if aum >= 1e9 else f"${aum/1e6:.0f}M"
    cat_str  = info_etf.get('category', '') if info_etf else ''
    gest_str = info_etf.get('fund_family', '') if info_etf else ''
    beta_str = f"{info_etf['beta']:.2f}" if info_etf and info_etf.get('beta') else ''

    prompt = f"""Você é um especialista em ETFs americanos. Gere um prospecto resumido e traduzido para português brasileiro do ETF abaixo.

ETF: {ticker}
Nome completo: {nome}
Categoria Nomad: {categoria}
Categoria yFinance: {cat_str}
Gestora: {gest_str}
Expense Ratio: {er_str}
AUM: {aum_str}
Beta (3 anos): {beta_str}

Responda APENAS com um objeto JSON válido (sem markdown, sem texto antes ou depois):
{{
  "resumo": "Uma frase direta explicando o que é o ETF e para quem serve (máx 120 chars)",
  "estrategia": "2-4 frases explicando: índice replicado (se passivo) ou metodologia (se ativo), critérios de seleção, rebalanceamento, gestora. Em português.",
  "composicao": "2-3 frases sobre: top holdings ou setores dominantes, número de ativos, concentração, países se internacional. Em português.",
  "riscos": "2-3 frases sobre riscos específicos deste ETF: concentração, sensibilidade a juros/câmbio, ciclicidade, alavancagem se aplicável. Em português."
}}"""

    try:
        import urllib.request, json as _json
        payload = _json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 600,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = _json.loads(resp.read())
        text = data['content'][0]['text'].strip()
        # Limpar possível markdown
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        result = _json.loads(text.strip())
        # Garantir que todas as chaves existem
        for key in ('resumo', 'estrategia', 'composicao', 'riscos'):
            if key not in result or not result[key]:
                raise ValueError(f"Chave ausente: {key}")
        return result
    except Exception:
        return None


def nome_curto(ticker, maxlen=30):
    n = NOME_MAP.get(ticker, ticker)
    return n[:maxlen] + "…" if len(n) > maxlen else n


# =============================================================================
# ANÁLISE TÉCNICA
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados(tickers_tuple):
    tickers = list(tickers_tuple)
    try:
        df = yf.download(tickers, period=PERIODO, auto_adjust=True,
                         progress=False, timeout=60, threads=True)
        if df.empty:
            return pd.DataFrame()
        if not isinstance(df.columns, pd.MultiIndex):
            df.columns = pd.MultiIndex.from_tuples([(c, tickers[0]) for c in df.columns])
        return df.dropna(axis=1, how='all')
    except Exception as e:
        st.error(f"Erro no download: {e}")
        return pd.DataFrame()


def calcular_indicadores(df):
    df_calc = df.copy()
    tickers = df_calc.columns.get_level_values(1).unique()
    pb = st.progress(0, text="Calculando indicadores…")
    for i, ticker in enumerate(tickers):
        try:
            close = df_calc[('Close', ticker)]
            high  = df_calc[('High',  ticker)]
            low   = df_calc[('Low',   ticker)]
            delta = close.diff()
            g = delta.clip(lower=0).rolling(14).mean()
            p = (-delta.clip(upper=0)).rolling(14).mean().replace(0, np.nan)
            df_calc[('RSI14',    ticker)] = 100 - (100 / (1 + g / p))
            ll = low.rolling(14).min(); hh = high.rolling(14).max()
            df_calc[('Stoch_K',  ticker)] = 100 * ((close - ll) / (hh - ll).replace(0, np.nan))
            df_calc[('EMA20',    ticker)] = close.ewm(span=20,  adjust=False).mean()
            df_calc[('EMA50',    ticker)] = close.ewm(span=50,  adjust=False).mean()
            df_calc[('EMA200',   ticker)] = close.ewm(span=200, adjust=False).mean()
            sma = close.rolling(20).mean(); std = close.rolling(20).std()
            df_calc[('BB_Lower', ticker)] = sma - 2 * std
            df_calc[('BB_Upper', ticker)] = sma + 2 * std
            e12 = close.ewm(span=12, adjust=False).mean()
            e26 = close.ewm(span=26, adjust=False).mean()
            macd = e12 - e26
            df_calc[('MACD_Hist', ticker)] = macd - macd.ewm(span=9, adjust=False).mean()
        except Exception:
            pass
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    return df_calc


def calcular_fibonacci(df_t):
    try:
        h = df_t['High'].max(); l = df_t['Low'].min()
        return {'61.8%': l + (h - l) * 0.618}
    except Exception:
        return None


def classificar(s):
    if s >= 4: return "Muito Alta"
    if s >= 2: return "Alta"
    if s >= 1: return "Média"
    return "Baixa"


def gerar_sinal(row, df_t):
    sinais, explicacoes, score = [], [], 0
    try:
        close  = row.get('Close');  rsi    = row.get('RSI14');   stoch  = row.get('Stoch_K')
        macd_h = row.get('MACD_Hist'); bb_low = row.get('BB_Lower'); ema200 = row.get('EMA200')
        if pd.notna(rsi):
            if rsi < 30:
                sinais.append("RSI Oversold"); score += 3
                explicacoes.append(f"📉 RSI {rsi:.1f} (<30): Forte sobrevenda")
            elif rsi < 40:
                sinais.append("RSI Baixo"); score += 1
                explicacoes.append(f"📊 RSI {rsi:.1f} (<40): Sobrevenda moderada")
        if pd.notna(stoch):
            if stoch < 20:
                sinais.append("Stoch. Fundo"); score += 2
                explicacoes.append(f"📉 Estoc. {stoch:.1f} (<20): Muito sobrevendido")
            elif stoch < 30:
                sinais.append("Stoch. Baixo"); score += 1
                explicacoes.append(f"📊 Estoc. {stoch:.1f} (<30): Sobrevendido")
        if pd.notna(close) and pd.notna(ema200) and close > ema200:
            sinais.append("Acima EMA200"); score += 2
            explicacoes.append("📈 ETF acima da EMA200: Tendência de alta")
        if pd.notna(macd_h) and macd_h > 0:
            sinais.append("MACD Virando"); score += 1
            explicacoes.append("🔄 MACD positivo: Momentum de alta começando")
        if pd.notna(close) and pd.notna(bb_low):
            if close < bb_low:
                sinais.append("Abaixo BB"); score += 2
                explicacoes.append("⚠️ Abaixo da Banda Inferior: Sobrevenda extrema")
            elif close < bb_low * 1.02:
                sinais.append("Suporte BB"); score += 1
                explicacoes.append("🎯 Próximo da Banda Inferior: Zona de suporte")
        fibo = calcular_fibonacci(df_t)
        if fibo and pd.notna(close):
            f618 = fibo['61.8%']
            if f618 * 0.99 <= close <= f618 * 1.01:
                sinais.append("Fibo 61.8%"); score += 2
                explicacoes.append("⭐ Zona de Ouro Fibonacci 61.8%: Reversão provável!")
    except Exception:
        pass
    return sinais, score, classificar(score), explicacoes


def calcular_liquidez(df_t, n=20):
    try:
        n = min(n, len(df_t))
        vol = df_t['Volume'].tail(n); vm = vol.mean()
        if pd.isna(vm): vm = 0
        n_gaps = sum(1 for i in range(1, min(n+1, len(df_t)))
                     if df_t['Close'].iloc[-i-1] > 0 and
                     abs((df_t['Open'].iloc[-i] - df_t['Close'].iloc[-i-1])
                         / df_t['Close'].iloc[-i-1]) * 100 > 1)
        consist = sum(1 for v in vol if pd.notna(v) and v >= vm * 0.8) / n if n > 0 else 0
        liq = (40 if vm > 50e6 else 35 if vm > 10e6 else 30 if vm > 5e6 else
               25 if vm > 1e6 else 20 if vm > 500e3 else 15 if vm > 100e3 else 5)
        for t, p in zip([0, 1, 3, 6, 9, 13, 99], [30, 25, 20, 15, 10, 5, 5]):
            if n_gaps <= t: liq += p; break
        liq += 30 if consist >= 0.75 else 20 if consist >= 0.50 else 10 if consist >= 0.25 else 5
        return max(0, min(10, round(liq / 10)))
    except Exception:
        return 1


def analisar_oportunidades(df_calc):
    resultados = []
    tickers = df_calc.columns.get_level_values(1).unique()
    pb = st.progress(0, text="Varrendo ETFs em queda…")
    for i, ticker in enumerate(tickers):
        try:
            df_t = df_calc.xs(ticker, axis=1, level=1).dropna()
            if len(df_t) < 50: continue
            last = df_t.iloc[-1]; ant = df_t.iloc[-2]
            preco = last.get('Close'); p_ant = ant.get('Close')
            if pd.isna(preco) or pd.isna(p_ant): continue
            queda = (preco - p_ant) / p_ant * 100
            if queda >= 0: continue
            p_open = last.get('Open')
            gap = (p_open - p_ant) / p_ant * 100 if pd.notna(p_open) else 0
            sinais, score_tec, potencial, explicacoes = gerar_sinal(last, df_t)
            rsi   = float(last.get('RSI14',   50) or 50)
            stoch = float(last.get('Stoch_K', 50) or 50)
            is_index = ((100 - rsi) + (100 - stoch)) / 2
            vol_yf = int(last.get('Volume', 0) or 0)
            liq = get_liquidez_score(ticker, vol_yf)
            resultados.append({
                'Ticker':      ticker,
                'ETF':         nome_curto(ticker),
                'Categoria':   CATEGORIA_MAP.get(ticker, 'Outro'),
                'Liquidez':    liq,
                'Preco':       round(preco, 2),
                'Queda_Dia':   round(queda, 2),
                'IS':          round(is_index, 1),
                'Volume':      int(last.get('Volume', 0) or 0),
                'Gap':         round(gap, 2),
                'Potencial':   potencial,
                'Score':       score_tec,
                'RSI14':       round(rsi, 1),
                'Stoch':       round(stoch, 1),
                'Sinais':      ", ".join(sinais) if sinais else "—",
                'Explicacoes': explicacoes,
            })
        except Exception:
            pass
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    resultados.sort(key=lambda x: x['Queda_Dia'])
    return resultados


# =============================================================================
# ANÁLISE INFORMATIVA DO ETF (adaptada — sem score de ação)
# =============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def buscar_info_etf(ticker):
    """Busca dados informativos do ETF via yfinance + dicionário hardcoded."""
    try:
        info = yf.Ticker(ticker).info or {}

        # ── Expense Ratio ─────────────────────────────────────────────────────
        # Fonte 1: dicionário hardcoded (sempre em %, ex: 0.09 = 0.09%/ano)
        er_pct = ETF_EXPENSE_RATIO.get(ticker)
        if er_pct is None:
            # Fonte 2: yfinance — pode vir como decimal (0.0009) ou % (0.09)
            raw = (info.get('annualReportExpenseRatio')
                   or info.get('expenseRatio')
                   or info.get('netExpenseRatio'))
            if raw and isinstance(raw, (int, float)) and raw > 0:
                er_pct = raw * 100 if raw < 0.01 else raw

        # ── AUM ───────────────────────────────────────────────────────────────
        aum = info.get('totalAssets')
        if aum and not isinstance(aum, (int, float)):
            aum = None

        # ── Retorno YTD ───────────────────────────────────────────────────────
        # yfinance pode retornar decimal (0.15=15%) ou % (15.0=15%)
        ytd_raw = info.get('ytdReturn')
        ytd_pct = None
        if ytd_raw is not None and isinstance(ytd_raw, (int, float)):
            if abs(ytd_raw) <= 5:
                ytd_pct = round(ytd_raw * 100, 2)   # decimal → %
            elif abs(ytd_raw) <= 500:
                ytd_pct = round(float(ytd_raw), 2)  # já em %
            # acima de 500% = dado inválido, ignora

        # ── Outros campos ─────────────────────────────────────────────────────
        category    = info.get('category') or ''
        fund_family = info.get('fundFamily') or ''
        nav         = info.get('navPrice') or info.get('regularMarketPrice')
        beta        = info.get('beta3Year') or info.get('beta')
        volume_avg  = info.get('averageVolume') or info.get('averageDailyVolume10Day')

        # ── Score 0-100 ───────────────────────────────────────────────────────
        score = 50
        detalhes = {}

        if er_pct is not None:
            detalhes['expense_ratio'] = round(er_pct, 3)
            if   er_pct <= 0.10: score += 20; detalhes['er_av'] = 'Excelente (≤0.10%/ano)'
            elif er_pct <= 0.20: score += 15; detalhes['er_av'] = 'Muito bom (≤0.20%/ano)'
            elif er_pct <= 0.50: score += 10; detalhes['er_av'] = 'Bom (≤0.50%/ano)'
            elif er_pct <= 1.00: score += 5;  detalhes['er_av'] = 'Razoável (≤1.0%/ano)'
            else:                score -= 5;  detalhes['er_av'] = 'Alto (>1.0%/ano)'

        if aum:
            detalhes['aum'] = aum
            if   aum >= 10e9:  score += 20; detalhes['aum_av'] = 'Mega (>$10B)'
            elif aum >= 1e9:   score += 15; detalhes['aum_av'] = 'Grande (>$1B)'
            elif aum >= 100e6: score += 10; detalhes['aum_av'] = 'Médio (>$100M)'
            elif aum >= 10e6:  score += 5;  detalhes['aum_av'] = 'Pequeno (>$10M)'
            else:              score -= 5;  detalhes['aum_av'] = 'Micro (<$10M) — risco de liquidez'

        if ytd_pct is not None:
            detalhes['ytd_return'] = ytd_pct
            if   ytd_pct > 20:  score += 10; detalhes['ytd_av'] = 'Excepcional (>20%)'
            elif ytd_pct > 10:  score += 7;  detalhes['ytd_av'] = 'Muito bom (>10%)'
            elif ytd_pct > 0:   score += 3;  detalhes['ytd_av'] = 'Positivo'
            elif ytd_pct > -10: score -= 3;  detalhes['ytd_av'] = 'Leve queda (>-10%)'
            else:               score -= 10; detalhes['ytd_av'] = 'Queda forte (<-10%)'

        score = max(0, min(100, score))

        if   score >= 80: label = 'EXCELENTE'; grad = 'linear-gradient(135deg,#d4fc79,#96e6a1)'; tc = '#166534'
        elif score >= 65: label = 'BOM';       grad = 'linear-gradient(135deg,#a7f3d0,#6ee7b7)'; tc = '#065f46'
        elif score >= 50: label = 'NEUTRO';    grad = 'linear-gradient(135deg,#fde047,#fbbf24)'; tc = '#92400e'
        elif score >= 35: label = 'ATENÇÃO';   grad = 'linear-gradient(135deg,#fdcb6e,#ff7043)'; tc = '#7c3626'
        else:             label = 'EVITAR';    grad = 'linear-gradient(135deg,#ef5350,#c62828)'; tc = 'white'

        return {
            'score': score, 'label': label, 'grad': grad, 'tc': tc,
            'er_pct': er_pct, 'aum': aum, 'ytd_pct': ytd_pct,
            'category': category, 'fund_family': fund_family,
            'nav': nav, 'beta': beta, 'volume_avg': volume_avg,
            'detalhes': detalhes,
        }
    except Exception:
        return None

# =============================================================================
# ESTILOS DA TABELA
# =============================================================================
COR_LIQ = {
    0: '#c62828', 1: '#e53935', 2: '#ef5350', 3: '#ff7043', 4: '#ffa726',
    5: '#fdd835', 6: '#d4e157', 7: '#9ccc65', 8: '#66bb6a', 9: '#2e7d32', 10: '#1b5e20'
}

def estilizar_is(val):
    try:
        v = float(val)
    except (ValueError, TypeError):
        return ''
    if v >= 75: return 'background-color:#d32f2f;color:white;font-weight:bold'
    if v >= 60: return 'background-color:#ffa726;color:black;font-weight:bold'
    return 'color:#888888'

def estilizar_potencial(val):
    if not isinstance(val, str): return ''
    if val == 'Muito Alta': return 'background-color:#2e7d32;color:white;font-weight:bold'
    if val == 'Alta':       return 'background-color:#66bb6a;color:black;font-weight:bold'
    if val == 'Média':      return 'background-color:#ffa726;color:black'
    return 'background-color:#e0e0e0;color:#555555'

def estilizar_liquidez(val):
    try:
        v = int(float(val))
    except (ValueError, TypeError):
        return 'background-color:#9e9e9e;color:white'
    bg = COR_LIQ.get(v, '#9e9e9e')
    fg = 'black' if v in [4, 5, 6, 7] else 'white'
    return f'background-color:{bg};color:{fg};font-weight:bold'

def estilizar_queda(val):
    return 'color:#c62828;font-weight:bold'


# =============================================================================
# GRÁFICO TÉCNICO
# =============================================================================
def plotar_grafico(df_t, ticker, etf_nome):
    close  = df_t['Close']
    ema20  = df_t.get('EMA20');  ema50  = df_t.get('EMA50'); ema200 = df_t.get('EMA200')
    bb_low = df_t.get('BB_Lower'); bb_up = df_t.get('BB_Upper')
    rsi_s  = df_t.get('RSI14');  st_s   = df_t.get('Stoch_K')
    h = df_t['High'].max(); l = df_t['Low'].min(); d = h - l
    fibs = {'0%':h, '23.6%':h-d*.236, '38.2%':h-d*.382, '50%':h-d*.5,
            '61.8%':h-d*.618, '78.6%':h-d*.786, '100%':l}
    fib_cores = {'0%':'#ef5350','23.6%':'#ff7043','38.2%':'#ffa726',
                 '50%':'#42a5f5','61.8%':'#2ecc71','78.6%':'#26a69a','100%':'#ab47bc'}

    fig = make_subplots(
        rows=3, cols=1, row_heights=[0.6, 0.2, 0.2], shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=[f"📈 {ticker} — {etf_nome}", "RSI 14", "Estocástico %K"],
    )
    if 'Open' in df_t.columns and 'High' in df_t.columns:
        fig.add_trace(go.Candlestick(
            x=df_t.index, open=df_t['Open'], high=df_t['High'],
            low=df_t['Low'], close=close, name='OHLC', showlegend=False,
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=close.index, y=close, name='Close',
                                 line=dict(color='#90caf9', width=2)), row=1, col=1)
    if bb_low is not None and bb_up is not None:
        fig.add_trace(go.Scatter(x=bb_up.index, y=bb_up,
                                 line=dict(color='rgba(120,144,156,0.5)', width=1, dash='dot'),
                                 showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb_low.index, y=bb_low,
                                 line=dict(color='rgba(120,144,156,0.5)', width=1, dash='dot'),
                                 fill='tonexty', fillcolor='rgba(120,144,156,0.06)',
                                 showlegend=False), row=1, col=1)
    if ema20  is not None: fig.add_trace(go.Scatter(x=ema20.index,  y=ema20,  name='EMA20',  line=dict(color='#2962FF', width=1.4)), row=1, col=1)
    if ema50  is not None: fig.add_trace(go.Scatter(x=ema50.index,  y=ema50,  name='EMA50',  line=dict(color='#FF6D00', width=1.4)), row=1, col=1)
    if ema200 is not None: fig.add_trace(go.Scatter(x=ema200.index, y=ema200, name='EMA200', line=dict(color='#00695C', width=2.0)), row=1, col=1)
    for nivel, pf in fibs.items():
        cor = fib_cores[nivel]
        fig.add_hline(y=pf, line_dash="dot", line_color=cor, line_width=0.9,
                      annotation_text=f" {nivel}", annotation_position="right",
                      annotation_font_color=cor, annotation_font_size=9, row=1, col=1)
    f382 = fibs['38.2%']; f618 = fibs['61.8%']
    fig.add_hrect(y0=min(f382, f618), y1=max(f382, f618),
                  fillcolor='rgba(46,204,113,0.07)', row=1, col=1)
    if rsi_s is not None:
        fig.add_trace(go.Scatter(x=rsi_s.index, y=rsi_s, name='RSI14',
                                 line=dict(color='#FF6F00', width=1.5)), row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#F44336", line_width=1, row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#4CAF50", line_width=1, row=2, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(244,67,54,0.10)",  row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(76,175,80,0.10)",  row=2, col=1)
    if st_s is not None:
        fig.add_trace(go.Scatter(x=st_s.index, y=st_s, name='Stoch %K',
                                 line=dict(color='#9C27B0', width=1.5)), row=3, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#F44336", line_width=1, row=3, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#4CAF50", line_width=1, row=3, col=1)
        fig.add_hrect(y0=0,  y1=20,  fillcolor="rgba(244,67,54,0.10)",  row=3, col=1)
        fig.add_hrect(y0=80, y1=100, fillcolor="rgba(76,175,80,0.10)",  row=3, col=1)
    fig.update_layout(
        height=620, template='plotly_dark', paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
        legend=dict(orientation='h', y=1.07, x=0, font=dict(size=11)),
        margin=dict(l=40, r=70, t=60, b=20), xaxis_rangeslider_visible=False,
    )
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Varredura")
    categorias_todas = sorted(set(CATEGORIA_MAP.values()))
    cats_sel = st.multiselect(
        "Categorias (vazio = todas)",
        options=categorias_todas, default=[],
        placeholder="Todas as categorias",
    )
    tickers_analise = (
        [tk for tk, (_, c) in NOMAD_ETFS.items() if c in cats_sel]
        if cats_sel else list(NOMAD_ETFS.keys())
    )
    st.info(f"🗂️ **{len(tickers_analise)} ETFs** selecionados")

    st.divider()
    if st.button("🔄 Atualizar Análise", type="primary"):
        st.session_state['run'] = True
        for k in ['oportunidades', 'df_calc', 'etf_cache', 'n_ok']:
            st.session_state.pop(k, None)

    if st.button("🗑️ Limpar Cache"):
        st.cache_data.clear()
        st.session_state.clear()
        st.success("Cache limpo!")

    st.divider()
    st.markdown("""
    <div style="text-align:center;font-size:0.72rem;color:#888;">
        ⚠️ Apenas fins educacionais.<br>Não é recomendação de investimento.
    </div>""", unsafe_allow_html=True)


# =============================================================================
# CABEÇALHO
# =============================================================================
fuso  = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso)
dias_pt = {'Monday':'Segunda-feira','Tuesday':'Terça-feira','Wednesday':'Quarta-feira',
           'Thursday':'Quinta-feira','Friday':'Sexta-feira','Saturday':'Sábado','Sunday':'Domingo'}
dia_pt = dias_pt.get(agora.strftime("%A"), agora.strftime("%A"))

st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">📊 Monitor de ETFs Nomad — Swing Trade Pro</h1>
    <p class="main-subtitle">Análise Técnica Avançada | Rastreamento de Oportunidades em Tempo Real</p>
    <p style="color:rgba(255,255,255,0.8);font-size:0.88rem;text-align:center;margin-top:0.4rem;">
        🕐 {dia_pt}, {agora.strftime('%d/%m/%Y às %H:%M')} (Horário de Brasília) &nbsp;|&nbsp;
        ~{len(tickers_analise)} ETFs · NYSE + Nasdaq · Ações · Bonds · Commodities · Cripto
    </p>
</div>
""", unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)
with col_i1: st.markdown("**📈 Estratégia:** Reversão em Sobrevenda")
with col_i2: st.markdown("**🎯 Foco:** ETFs em Queda com Potencial")
with col_i3: st.markdown("**⏱️ Timeframe:** 1 Ano | Diário")

st.markdown("---")

with st.expander("📚 Guia dos Indicadores — Entenda os Sinais", expanded=False):
    st.markdown("""
    ### 🎯 Índice de Sobrevenda (I.S.)
    Combina RSI e Estocástico para medir o nível de sobrevenda do ETF.
    - **75-100**: 🔴 Muito sobrevendido — alta probabilidade de reversão
    - **60-75**: 🟠 Sobrevendido moderado
    - **< 60**: ⚪ Neutro

    ### 📊 EMAs — Médias Móveis Exponenciais
    - **ETF acima da EMA200**: tendência de alta de longo prazo
    - **ETF em queda MAS acima das EMAs**: correção em tendência de alta = **oportunidade!**

    ### 🌟 Fibonacci 61.8% — Zona de Ouro
    Nível mais importante para reversão. ETF próximo a 61.8% = suporte forte.

    ### 💼 Análise Informativa do ETF
    Ao clicar em um ETF você verá:
    - **Expense Ratio**: taxa de administração anual (quanto menor melhor)
    - **AUM**: ativos sob gestão — mede tamanho e liquidez do fundo
    - **Retorno YTD**: performance acumulada no ano
    - **Categoria**: tipo do ETF (ex: Large Blend, Bond, Commodities...)

    ### 💡 Estratégia
    1. Filtre por **EMA200** para garantir tendência de alta
    2. Procure **I.S. > 75** (forte sobrevenda)
    3. Confirme com **RSI < 30** e **Stoch < 20**
    4. Verifique se está próximo de **Fibonacci 61.8%**
    5. Clique na linha para ver análise completa 📈
    """)

st.markdown("---")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if st.session_state.get('run') and 'oportunidades' not in st.session_state:

    with st.spinner("⬇️ Conectando à API e baixando dados…"):
        df = buscar_dados(tuple(tickers_analise))
        if df.empty:
            st.error("Erro ao carregar dados. Aguarde alguns minutos e tente novamente.")
            st.stop()
        n_ok = len(df.columns.get_level_values(1).unique())

    st.success(f"✅ {df.shape[0]} dias históricos | {n_ok} ETFs válidos")

    with st.spinner("🔢 Calculando indicadores técnicos…"):
        df_calc = calcular_indicadores(df)

    with st.spinner("🔍 Varrendo ETFs em queda…"):
        oportunidades = analisar_oportunidades(df_calc)

    st.success(f"✅ {len(oportunidades)} oportunidades detectadas!")

    st.session_state['oportunidades'] = oportunidades
    st.session_state['df_calc']       = df_calc
    st.session_state['etf_cache']     = {}
    st.session_state['n_ok']          = n_ok
    st.session_state['run']           = False


# =============================================================================
# EXIBIÇÃO
# =============================================================================
if 'oportunidades' not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#94a3b8;">
        <h3>🎯 Pronto para analisar</h3>
        <p>Clique em <b>🔄 Atualizar Análise</b> na barra lateral para começar</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

oportunidades = st.session_state['oportunidades']
df_calc       = st.session_state['df_calc']
etf_cache     = st.session_state['etf_cache']
n_ok          = st.session_state.get('n_ok', 0)
df_opp        = pd.DataFrame(oportunidades)

st.success(f"✅ {len(oportunidades)} oportunidades detectadas!")

# ── Filtros inline ────────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">🎯 Filtros de Tendência</h3>', unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
    <p>💡 <strong>Dica:</strong> Selecione as médias móveis para filtrar ETFs em correção dentro de tendências de alta</p>
</div>""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtrar_ema20  = st.checkbox("📈 Acima da EMA20",  value=False, help="Preço acima da EMA20 (curto prazo)")
with col_f2:
    filtrar_ema50  = st.checkbox("📊 Acima da EMA50",  value=False, help="Preço acima da EMA50 (médio prazo)")
with col_f3:
    filtrar_ema200 = st.checkbox("📉 Acima da EMA200", value=False, help="Preço acima da EMA200 (longo prazo)")

st.markdown("**💧 Liquidez mínima:**")
liq_min = st.slider("0 = sem filtro  |  10 = máxima exigência",
                    min_value=0, max_value=10, value=0, step=1)
pot_min = st.selectbox("🎯 Potencial mínimo", ['Todos', 'Média', 'Alta', 'Muito Alta'])

# ── Aplicar filtros ────────────────────────────────────────────────────────────
ordens = {'Baixa':0, 'Média':1, 'Alta':2, 'Muito Alta':3}
df_res = df_opp.copy()
if pot_min != 'Todos':
    df_res = df_res[df_res['Potencial'].map(lambda x: ordens.get(x, -1)) >= ordens[pot_min]]
if liq_min > 0:
    df_res = df_res[df_res['Liquidez'] >= liq_min]

if filtrar_ema20 or filtrar_ema50 or filtrar_ema200:
    contadores = {'ema20': 0, 'ema50': 0, 'ema200': 0, 'sem_dados': 0}
    df_filtrado = []
    for _, opp in df_res.iterrows():
        tk = opp['Ticker']
        try:
            df_t  = df_calc.xs(tk, axis=1, level=1).dropna()
            tam   = len(df_t); preco = df_t['Close'].iloc[-1]; ok = True
            if filtrar_ema20 and 'EMA20' in df_t.columns and tam >= 20:
                v = df_t['EMA20'].iloc[-1]
                if pd.notna(v) and preco > v: contadores['ema20'] += 1
                else: ok = False
            elif filtrar_ema20: ok = False
            if ok and filtrar_ema50 and 'EMA50' in df_t.columns and tam >= 50:
                v = df_t['EMA50'].iloc[-1]
                if pd.notna(v) and preco > v: contadores['ema50'] += 1
                else: ok = False
            elif ok and filtrar_ema50: ok = False
            if ok and filtrar_ema200 and 'EMA200' in df_t.columns and tam >= 50:
                v = df_t['EMA200'].iloc[-1]
                if pd.notna(v) and preco > v: contadores['ema200'] += 1
                else: ok = False
            elif ok and filtrar_ema200: ok = False
            if ok: df_filtrado.append(opp)
        except Exception:
            contadores['sem_dados'] += 1

    if df_filtrado:
        df_res = pd.DataFrame(df_filtrado).reset_index(drop=True)
        ativos = []
        if filtrar_ema20:  ativos.append(f"EMA20 ({contadores['ema20']} ✓)")
        if filtrar_ema50:  ativos.append(f"EMA50 ({contadores['ema50']} ✓)")
        if filtrar_ema200: ativos.append(f"EMA200 ({contadores['ema200']} ✓)")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#d4fc79,#96e6a1);padding:1rem;border-radius:8px;margin:1rem 0;'>
            <p style='margin:0;color:#166534;font-weight:600;font-size:1rem;'>
                ✅ {len(df_res)} ETFs encontrados &nbsp;|&nbsp; Filtros: {' + '.join(ativos)}
            </p>
        </div>""", unsafe_allow_html=True)
    else:
        ativos = []
        if filtrar_ema20:  ativos.append(f"EMA20 ({contadores['ema20']} acima)")
        if filtrar_ema50:  ativos.append(f"EMA50 ({contadores['ema50']} acima)")
        if filtrar_ema200: ativos.append(f"EMA200 ({contadores['ema200']} acima)")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#ffeaa7,#fdcb6e);padding:1rem;border-radius:8px;margin:1rem 0;'>
            <p style='margin:0;color:#7c3626;font-weight:600;'>⚠️ Nenhum ETF passou em todos os filtros combinados</p>
            <p style='margin:0.4rem 0 0;color:#7c3626;font-size:0.88rem;'>
                📊 {' | '.join(ativos)} | {contadores['sem_dados']} sem dados suficientes
            </p>
        </div>""", unsafe_allow_html=True)
        df_res = pd.DataFrame()

if df_res.empty:
    st.stop()

# ── Tabela principal ──────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">📊 ETFs em Queda com Potencial de Reversão</h3>',
            unsafe_allow_html=True)
st.markdown("""
<div class="tip-box">
    <p>💡 <strong>Dica:</strong> Clique em qualquer linha para ver o gráfico técnico e informações do ETF</p>
</div>""", unsafe_allow_html=True)

evento = st.dataframe(
    df_res.style
        .map(estilizar_potencial, subset=['Potencial'])
        .map(estilizar_is,        subset=['IS'])
        .map(estilizar_liquidez,  subset=['Liquidez'])
        .map(estilizar_queda,     subset=['Queda_Dia'])
        .format({
            'Preco':     '${:.2f}',
            'Queda_Dia': '{:.2f}%',
            'Gap':       '{:.2f}%',
            'IS':        '{:.0f}',
            'RSI14':     '{:.0f}',
            'Stoch':     '{:.0f}',
            'Liquidez':  '{:.0f}',
            'Volume':    '{:,.0f}',
        }),
    column_order=("Ticker", "ETF", "Queda_Dia", "IS", "Potencial", "Categoria",
                  "Liquidez", "Preco", "Volume", "Gap", "Score", "Sinais"),
    column_config={
        "ETF":       st.column_config.TextColumn("Nome ETF",    width="large"),
        "Categoria": st.column_config.TextColumn("Categoria",   width="medium"),
        "Liquidez":  st.column_config.NumberColumn("💧 Liq.",   width="small",
                         help="Ranking de liquidez 0-10 (🔴 baixa → 🟢 alta)"),
        "IS":        st.column_config.NumberColumn("I.S.",      help="Índice de Sobrevenda"),
        "Volume":    st.column_config.NumberColumn("Vol.",      help="Volume do dia"),
        "Score":     st.column_config.ProgressColumn("Força",  format="%d", min_value=0, max_value=10),
        "Potencial": st.column_config.Column("Sinal"),
        "Sinais":    st.column_config.TextColumn("Sinais Técnicos", width="large"),
    },
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    height=min(700, 38 + 35 * len(df_res)),
)

# CSV + buscar info de todos ETFs na tabela
csv = df_res.drop(columns=['Explicacoes'], errors='ignore').to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Exportar CSV", data=csv,
                   file_name=f"etf_nomad_{agora.strftime('%Y%m%d_%H%M')}.csv",
                   mime="text/csv")

tickers_tabela  = df_res['Ticker'].tolist()
tickers_faltando = [tk for tk in tickers_tabela if tk not in etf_cache]
if tickers_faltando:
    pb_f = st.progress(0, text=f"💼 Buscando dados dos ETFs ({len(tickers_faltando)} fundos)…")
    for i, tk in enumerate(tickers_faltando):
        etf_cache[tk] = buscar_info_etf(tk)
        pb_f.progress((i + 1) / len(tickers_faltando))
    pb_f.empty()
    st.session_state['etf_cache'] = etf_cache


# =============================================================================
# ANÁLISE DETALHADA ao clicar na linha
# =============================================================================
if evento.selection and evento.selection.rows:
    idx     = evento.selection.rows[0]
    row     = df_res.iloc[idx]
    ticker  = row['Ticker']
    etf_nome = row['ETF']

    st.markdown("---")
    st.markdown(f'<h3 class="section-header">📈 Análise Técnica: {ticker} — {etf_nome}</h3>',
                unsafe_allow_html=True)

    # ── Card de prospecto do ETF ───────────────────────────────────────────────
    er_hard   = ETF_EXPENSE_RATIO.get(ticker)
    er_badge  = f"&nbsp;|&nbsp; 💰 <b>{er_hard:.3f}%/ano</b>" if er_hard else ""
    cat_badge = row['Categoria']

    # Busca prospecto: hardcoded → cache IA → gerar agora
    prosp = get_prospecto(ticker)
    if prosp is None:
        with st.spinner(f"🤖 Gerando prospecto de {ticker} via IA…"):
            fd_local = etf_cache.get(ticker)
            prosp = gerar_prospecto_ia(
                ticker,
                NOME_MAP.get(ticker, ticker),
                row['Categoria'],
                er_hard,
                fd_local,
            )
        if prosp:
            cache = st.session_state.get('prospecto_cache', {})
            cache[ticker] = prosp
            st.session_state['prospecto_cache'] = cache
        else:
            # Fallback mínimo se a API falhar
            prosp = {
                'resumo':    f"{NOME_MAP.get(ticker, ticker)} — {row['Categoria']}",
                'estrategia': 'Não foi possível gerar a análise no momento. Consulte etf.com para detalhes.',
                'composicao': 'Consulte a gestora do fundo para composição atualizada.',
                'riscos':     'Consulte o prospecto oficial para lista completa de riscos.',
            }

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);
                padding:1rem 1.25rem;border-radius:10px;margin-bottom:1rem;
                border-left:4px solid #0288d1;">
        <p style="margin:0 0 0.3rem;font-size:0.73rem;font-weight:700;
                  color:#0277bd;text-transform:uppercase;letter-spacing:.06em;">
            🗂️ {cat_badge}{er_badge}
        </p>
        <p style="margin:0;color:#0d2f4f;font-size:0.93rem;line-height:1.55;font-weight:500;">
            {prosp['resumo']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Prospecto Resumido — Estratégia, Composição e Riscos", expanded=True):
        col_e, col_c, col_r = st.columns(3)

        with col_e:
            st.markdown("""
            <div style="background:#e8f5e9;border-left:4px solid #2e7d32;
                        padding:0.8rem;border-radius:6px;">
                <p style="margin:0;font-size:0.75rem;font-weight:700;
                           color:#1b5e20;text-transform:uppercase;letter-spacing:.05em;">
                    📐 Estratégia
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#1a3a1a;line-height:1.6;margin-top:0.5rem;'>{prosp['estrategia']}</p>",
                        unsafe_allow_html=True)

        with col_c:
            st.markdown("""
            <div style="background:#fff8e1;border-left:4px solid #f9a825;
                        padding:0.8rem;border-radius:6px;">
                <p style="margin:0;font-size:0.75rem;font-weight:700;
                           color:#e65100;text-transform:uppercase;letter-spacing:.05em;">
                    🧩 Composição
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#3a2a00;line-height:1.6;margin-top:0.5rem;'>{prosp['composicao']}</p>",
                        unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div style="background:#fce4ec;border-left:4px solid #c62828;
                        padding:0.8rem;border-radius:6px;">
                <p style="margin:0;font-size:0.75rem;font-weight:700;
                           color:#b71c1c;text-transform:uppercase;letter-spacing:.05em;">
                    ⚠️ Riscos
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#3a0000;line-height:1.6;margin-top:0.5rem;'>{prosp['riscos']}</p>",
                        unsafe_allow_html=True)

    col_graf, col_info = st.columns([3, 1])

    with col_graf:
        try:
            df_t = df_calc.xs(ticker, axis=1, level=1).dropna()
            fig  = plotar_grafico(df_t, ticker, etf_nome)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {e}")

    with col_info:
        pot = row['Potencial']
        if 'Alta' in pot:
            cor_bg = "linear-gradient(135deg,#d4fc79,#96e6a1)"; cor_tx = "#166534"; ico = "🟢"
        elif 'Média' in pot:
            cor_bg = "linear-gradient(135deg,#ffeaa7,#fdcb6e)"; cor_tx = "#7c3626"; ico = "🟡"
        else:
            cor_bg = "linear-gradient(135deg,#dfe6e9,#b2bec3)"; cor_tx = "#2d3436"; ico = "⚪"

        st.markdown(f"""
        <div style="background:{cor_bg};padding:0.8rem;border-radius:8px;
                    margin-bottom:0.75rem;text-align:center;">
            <h2 style="margin:0;color:{cor_tx};">{ico} {pot}</h2>
        </div>""", unsafe_allow_html=True)

        st.metric("💰 Preço",         f"${row['Preco']:.2f}")
        st.metric("📉 Queda Dia",     f"{row['Queda_Dia']:.2f}%", delta_color="inverse")
        st.metric("🎯 I.S.",          f"{row['IS']:.0f}/100")
        if row['Gap'] < -1:
            st.metric("⚡ Gap Abertura", f"{row['Gap']:.2f}%", delta_color="inverse")
        st.markdown(f"**⭐ Score:** {row['Score']}/10")
        st.markdown(f"**📊 Volume:** {row['Volume']:,.0f}")
        st.markdown(f"**🗂️ Categoria:** {row['Categoria']}")

        st.markdown("""
        <div style="background:#e0e7ff;padding:0.6rem;border-radius:6px;margin-top:0.75rem;">
            <p style="margin:0;font-weight:600;color:#3730a3;font-size:0.85rem;">📋 Sinais Detectados</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.82rem;color:#475569;'>{row['Sinais']}</p>",
                    unsafe_allow_html=True)

        if row.get('Explicacoes'):
            st.markdown("""
            <div style="background:#fef3c7;padding:0.6rem;border-radius:6px;margin-top:0.5rem;">
                <p style="margin:0;font-weight:600;color:#92400e;font-size:0.85rem;">💡 O que isso significa?</p>
            </div>""", unsafe_allow_html=True)
            for exp in row['Explicacoes']:
                st.markdown(f"<p style='font-size:0.8rem;color:#92400e;margin:0.2rem 0;'>• {exp}</p>",
                            unsafe_allow_html=True)

    # ── Painel informativo do ETF ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<h3 class="section-header">💼 Dados do Fundo</h3>', unsafe_allow_html=True)

    fd = etf_cache.get(ticker)
    if fd is None:
        with st.spinner(f"Buscando dados do ETF {ticker}…"):
            fd = buscar_info_etf(ticker)

    if fd:
        score = fd['score']
        st.markdown(f"""
        <div style="background:{fd['grad']};padding:1.25rem;border-radius:12px;
                    margin-bottom:1.5rem;text-align:center;">
            <h1 style="margin:0;color:{fd['tc']};font-size:3.5rem;font-weight:900;">{score}/100</h1>
            <p style="margin:0.3rem 0 0;color:{fd['tc']};font-size:1.3rem;font-weight:600;">{fd['label']}</p>
            <p style="margin:0.2rem 0 0;color:{fd['tc']};font-size:0.85rem;opacity:0.85;">
                Score baseado em Expense Ratio + AUM + Retorno YTD
            </p>
        </div>""", unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("### 💰 Custo & Tamanho")
            er = fd.get('er_pct') or ETF_EXPENSE_RATIO.get(ticker)
            st.metric("Expense Ratio",
                      f"{er:.3f}%/ano" if er is not None else "N/A",
                      help="Taxa de administração anual — quanto menor melhor")
            aum = fd.get('aum')
            if aum:
                aum_str = f"${aum/1e12:.2f}T" if aum >= 1e12 else f"${aum/1e9:.1f}B" if aum >= 1e9 else f"${aum/1e6:.0f}M"
                st.metric("AUM (Patrimônio)", aum_str, help="Ativos sob gestão do fundo")
            else:
                st.metric("AUM (Patrimônio)", "N/A")

        with col_b:
            st.markdown("### 📈 Performance")
            ytd = fd.get('ytd_pct')
            if ytd is not None:
                st.metric("Retorno YTD", f"{ytd:+.2f}%",
                          delta=f"{ytd:.2f}%" if ytd > 0 else None)
            else:
                st.metric("Retorno YTD", "N/A")
            beta = fd.get('beta')
            st.metric("Beta (3 anos)", f"{beta:.2f}" if beta else "N/A",
                      help="Volatilidade relativa ao S&P 500. >1 = mais volátil")

        with col_c:
            st.markdown("### 🏷️ Informações")
            category = fd.get('category', 'N/A')
            st.markdown(f"**Categoria:** {category if category else 'N/A'}")
            fund_family = fd.get('fund_family', '')
            st.markdown(f"**Gestora:** {fund_family if fund_family else 'N/A'}")
            nav = fd.get('nav')
            st.metric("NAV", f"${nav:.2f}" if nav else "N/A",
                      help="Net Asset Value — valor intrínseco da cota")
            vol_avg = fd.get('volume_avg')
            if vol_avg:
                vol_str = f"{vol_avg/1e6:.1f}M" if vol_avg >= 1e6 else f"{vol_avg/1e3:.0f}K"
                st.metric("Volume Médio", vol_str)

        # Tabela de detalhamento
        det = fd.get('detalhes', {})
        linhas = []
        if det.get('expense_ratio') is not None:
            linhas.append({
                'Critério': 'Expense Ratio',
                'Valor': f"{det['expense_ratio']:.3f}%/ano",
                'Avaliação': det.get('er_av', ''),
            })
        if det.get('aum') is not None:
            aum_v = det['aum']
            linhas.append({
                'Critério': 'AUM (Patrimônio)',
                'Valor': f"${aum_v/1e12:.2f}T" if aum_v >= 1e12 else f"${aum_v/1e9:.1f}B" if aum_v >= 1e9 else f"${aum_v/1e6:.0f}M",
                'Avaliação': det.get('aum_av', ''),
            })
        if det.get('ytd_return') is not None:
            linhas.append({
                'Critério': 'Retorno YTD',
                'Valor': f"{det['ytd_return']:+.2f}%",
                'Avaliação': det.get('ytd_av', ''),
            })
        if linhas:
            st.markdown("---")
            st.markdown("#### 📋 Detalhamento do Score")
            df_det = pd.DataFrame(linhas)
            st.dataframe(df_det, hide_index=True, use_container_width=True,
                         column_config={
                             'Critério':  st.column_config.TextColumn("Critério",  width="medium"),
                             'Valor':     st.column_config.TextColumn("Valor",     width="small"),
                             'Avaliação': st.column_config.TextColumn("Avaliação", width="medium"),
                         })
            st.caption(f"Score Total: {score}/100 (Base 50 + bônus por Expense Ratio, AUM e Retorno YTD)")
    else:
        st.info(f"""
        ℹ️ Dados do fundo não disponíveis para **{ticker}** via API pública.
        Isso é comum em ETFs alavancados, ETPs de cripto ou fundos muito novos.
        A análise técnica acima permanece válida.
        """)

else:
    st.markdown("""
    <div class="select-prompt">
        <p>👆 Selecione um ETF na tabela acima para visualizar o gráfico técnico e os dados do fundo</p>
    </div>""", unsafe_allow_html=True)


# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1.5rem 0;color:#64748b;">
    <p style="margin:0;font-size:0.9rem;">
        <strong>Monitor de ETFs Nomad — Swing Trade Pro</strong>
        &nbsp;|&nbsp; Powered by Python, yFinance &amp; Streamlit
    </p>
    <p style="margin:0.4rem 0 0;font-size:0.8rem;">
        ⚠️ Este sistema é apenas para fins educacionais. Não constitui recomendação de investimento.
    </p>
</div>""", unsafe_allow_html=True)
