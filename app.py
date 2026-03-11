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
    """Busca dados informativos do ETF via yfinance: AUM, Expense Ratio, Retorno YTD, Categoria."""
    try:
        info = yf.Ticker(ticker).info
        if not info or len(info) < 3:
            return None

        # Campos específicos de ETF
        aum           = info.get('totalAssets')
        expense_ratio = info.get('annualReportExpenseRatio') or info.get('expenseRatio')
        ytd_return    = info.get('ytdReturn')
        one_yr_return = info.get('threeYearAverageReturn') # fallback útil
        category      = info.get('category') or info.get('fundFamily') or ''
        fund_family   = info.get('fundFamily') or ''
        nav           = info.get('navPrice') or info.get('regularMarketPrice')
        beta          = info.get('beta3Year') or info.get('beta')
        holdings_n    = info.get('totalHoldings') or info.get('holdings')
        volume_avg    = info.get('averageVolume') or info.get('averageDailyVolume10Day')

        # Score informativo 0-100 baseado em critérios de ETF
        score = 50
        detalhes = {}

        # Expense Ratio — quanto menor melhor
        if expense_ratio and isinstance(expense_ratio, (int, float)):
            detalhes['expense_ratio'] = round(expense_ratio * 100, 3)
            if expense_ratio <= 0.0010:   score += 20; detalhes['er_av'] = 'Excelente (≤0.10%)'
            elif expense_ratio <= 0.0020: score += 15; detalhes['er_av'] = 'Muito bom (≤0.20%)'
            elif expense_ratio <= 0.0050: score += 10; detalhes['er_av'] = 'Bom (≤0.50%)'
            elif expense_ratio <= 0.0100: score += 5;  detalhes['er_av'] = 'Razoável (≤1.0%)'
            else:                         score -= 5;  detalhes['er_av'] = 'Alto (>1.0%)'

        # AUM — quanto maior, mais líquido e confiável
        if aum and isinstance(aum, (int, float)):
            detalhes['aum'] = aum
            if aum >= 10e9:   score += 20; detalhes['aum_av'] = 'Mega (>$10B)'
            elif aum >= 1e9:  score += 15; detalhes['aum_av'] = 'Grande (>$1B)'
            elif aum >= 100e6:score += 10; detalhes['aum_av'] = 'Médio (>$100M)'
            elif aum >= 10e6: score += 5;  detalhes['aum_av'] = 'Pequeno (>$10M)'
            else:             score -= 5;  detalhes['aum_av'] = 'Micro (<$10M) — risco de liquidez'

        # Retorno YTD
        if ytd_return and isinstance(ytd_return, (int, float)):
            detalhes['ytd_return'] = round(ytd_return * 100, 2)
            if ytd_return > 0.20:    score += 10; detalhes['ytd_av'] = 'Excepcional (>20%)'
            elif ytd_return > 0.10:  score += 7;  detalhes['ytd_av'] = 'Muito bom (>10%)'
            elif ytd_return > 0.00:  score += 3;  detalhes['ytd_av'] = 'Positivo'
            elif ytd_return > -0.10: score -= 3;  detalhes['ytd_av'] = 'Leve queda (>-10%)'
            else:                    score -= 10; detalhes['ytd_av'] = 'Queda forte (<-10%)'

        score = max(0, min(100, score))

        if   score >= 80: label = 'EXCELENTE'; grad = 'linear-gradient(135deg,#d4fc79,#96e6a1)'; tc = '#166534'
        elif score >= 65: label = 'BOM';       grad = 'linear-gradient(135deg,#a7f3d0,#6ee7b7)'; tc = '#065f46'
        elif score >= 50: label = 'NEUTRO';    grad = 'linear-gradient(135deg,#fde047,#fbbf24)'; tc = '#92400e'
        elif score >= 35: label = 'ATENÇÃO';   grad = 'linear-gradient(135deg,#fdcb6e,#ff7043)'; tc = '#7c3626'
        else:             label = 'EVITAR';    grad = 'linear-gradient(135deg,#ef5350,#c62828)'; tc = 'white'

        return {
            'score': score, 'label': label, 'grad': grad, 'tc': tc,
            'aum': aum, 'expense_ratio': expense_ratio, 'ytd_return': ytd_return,
            'category': category, 'fund_family': fund_family,
            'nav': nav, 'beta': beta, 'volume_avg': volume_avg,
            'detalhes': detalhes,
        }
    except Exception:
        return None


# =============================================================================
# ESTILOS DA TABELA
# =============================================================================
COR_LIQ = {0:'#c62828', 1:'#e53935', 2:'#ef5350', 3:'#ff7043', 4:'#ffa726',
           5:'#fdd835', 6:'#d4e157', 7:'#9ccc65', 8:'#66bb6a', 9:'#2e7d32', 10:'#1b5e20'}

def estilizar_is(val):
    if val >= 75: return 'background-color:#d32f2f;color:white;font-weight:bold'
    if val >= 60: return 'background-color:#ffa726;color:black;font-weight:bold'
    return 'color:#888888'

def estilizar_potencial(val):
    if val == 'Muito Alta': return 'background-color:#2e7d32;color:white;font-weight:bold'
    if val == 'Alta':       return 'background-color:#66bb6a;color:black;font-weight:bold'
    if val == 'Média':      return 'background-color:#ffa726;color:black'
    return 'background-color:#e0e0e0;color:#555555'

def estilizar_liquidez(val):
    bg = COR_LIQ.get(int(val), '#9e9e9e')
    fg = 'black' if int(val) in [4, 5, 6, 7] else 'white'
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
    column_order=("Ticker", "ETF", "Categoria", "Liquidez", "Preco",
                  "Queda_Dia", "IS", "Volume", "Gap", "Potencial", "Score", "Sinais"),
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
            er = fd.get('expense_ratio')
            st.metric("Expense Ratio",
                      f"{er*100:.3f}%/ano" if er else "N/A",
                      help="Taxa de administração anual — quanto menor melhor")
            aum = fd.get('aum')
            if aum:
                aum_str = f"${aum/1e12:.2f}T" if aum >= 1e12 else f"${aum/1e9:.1f}B" if aum >= 1e9 else f"${aum/1e6:.0f}M"
                st.metric("AUM (Patrimônio)", aum_str, help="Ativos sob gestão do fundo")
            else:
                st.metric("AUM (Patrimônio)", "N/A")

        with col_b:
            st.markdown("### 📈 Performance")
            ytd = fd.get('ytd_return')
            if ytd is not None:
                st.metric("Retorno YTD", f"{ytd*100:+.2f}%",
                          delta=f"{ytd*100:.2f}%" if ytd > 0 else None)
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
