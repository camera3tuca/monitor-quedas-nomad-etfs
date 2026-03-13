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
}

CATEGORIA_MAP = {tk: v[1] for tk, v in NOMAD_ETFS.items()}
NOME_MAP      = {tk: v[0] for tk, v in NOMAD_ETFS.items()}
PERIODO       = "1y"

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

def get_prospecto(ticker):
    """Retorna prospecto estruturado do ETF ou gera um genérico baseado no nome e categoria."""
    if ticker in ETF_PROSPECTO:
        return ETF_PROSPECTO[ticker]
    nome = NOME_MAP.get(ticker, ticker)
    cat  = CATEGORIA_MAP.get(ticker, 'ETF')
    er   = ETF_EXPENSE_RATIO.get(ticker)
    er_str = f" Expense ratio: {er:.3f}%/ano." if er else ""

    # Prospectos genéricos por categoria
    riscos_cat = {
        'Alavancado / Inverso': 'ETF alavancado ou inverso — sujeito a volatility decay. NÃO adequado para buy & hold. Use apenas para operações táticas de curtíssimo prazo.',
        'Renda Fixa': 'Risco de duração (sensível a variações de juros). Risco de crédito (dependendo do tipo). Câmbio USD/BRL para investidores brasileiros.',
        'Commodities': 'Risco de preço da commodity. Possível custo de roll em futuros. Sem geração de renda. Alta volatilidade em crises.',
        'Cripto & Fintech': 'Volatilidade extrema. Risco regulatório. Mercado 24/7 sem circuit breakers. Risco de custódia.',
        'Mercados Emergentes': 'Risco cambial elevado. Risco político e regulatório. Menor liquidez e governança corporativa vs mercados desenvolvidos.',
    }
    riscos_genericos = riscos_cat.get(cat, 'Risco de mercado do setor/categoria. Câmbio USD/BRL. Consulte o prospecto oficial para detalhes completos.')

    return {
        'resumo': f'{nome} — ETF da categoria {cat}.{er_str}',
        'estrategia': f'ETF passivo ou ativo da categoria {cat}. Consulte o prospecto oficial em etf.com ou o site da gestora para detalhes sobre metodologia de seleção, índice replicado e rebalanceamento.',
        'composicao': 'Consulte os maiores componentes no site da gestora (iShares, Vanguard, SPDR, Invesco etc.) ou em etf.com para a lista atualizada de holdings.',
        'riscos': riscos_genericos,
    }


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
            liq = calcular_liquidez(df_t)
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
    prosp    = get_prospecto(ticker)
    er_hard  = ETF_EXPENSE_RATIO.get(ticker)
    er_badge = f"&nbsp;|&nbsp; 💰 <b>{er_hard:.3f}%/ano</b>" if er_hard else ""
    cat_badge = row['Categoria']

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
                        padding:0.8rem;border-radius:6px;height:100%;">
                <p style="margin:0 0 0.4rem;font-size:0.75rem;font-weight:700;
                           color:#1b5e20;text-transform:uppercase;letter-spacing:.05em;">
                    📐 Estratégia
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#1a3a1a;line-height:1.55;margin-top:0.5rem;'>{prosp['estrategia']}</p>",
                        unsafe_allow_html=True)

        with col_c:
            st.markdown("""
            <div style="background:#fff8e1;border-left:4px solid #f9a825;
                        padding:0.8rem;border-radius:6px;height:100%;">
                <p style="margin:0 0 0.4rem;font-size:0.75rem;font-weight:700;
                           color:#e65100;text-transform:uppercase;letter-spacing:.05em;">
                    🧩 Composição
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#3a2a00;line-height:1.55;margin-top:0.5rem;'>{prosp['composicao']}</p>",
                        unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div style="background:#fce4ec;border-left:4px solid #c62828;
                        padding:0.8rem;border-radius:6px;height:100%;">
                <p style="margin:0 0 0.4rem;font-size:0.75rem;font-weight:700;
                           color:#b71c1c;text-transform:uppercase;letter-spacing:.05em;">
                    ⚠️ Riscos
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#3a0000;line-height:1.55;margin-top:0.5rem;'>{prosp['riscos']}</p>",
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
