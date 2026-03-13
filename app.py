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
ETF_DESCRICAO = {
    # ── Amplos EUA ────────────────────────────────────────────────────────────
    'SPY': "O ETF mais negociado do mundo, lançado em 1993. Replica o S&P 500 com ~$550B em ativos. Referência global de mercado, composto pelas 500 maiores empresas americanas. Amplamente usado para especulação, hedge e alocação de longo prazo.",
    'VOO': "Versão Vanguard do S&P 500, com expense ratio de 0.03% — um dos mais baratos do mundo. Ideal para buy & hold de longo prazo. Mesma carteira do SPY a uma fração do custo.",
    'IVV': "Versão iShares do S&P 500. Concorre diretamente com VOO e SPY. Expense ratio de 0.03% e grande liquidez. Diferencial: permite empréstimo de ações na carteira.",
    'QQQ': "Replica o Nasdaq 100 — as 100 maiores não-financeiras da Nasdaq. Alta concentração em Big Tech (Apple, Microsoft, Nvidia, Amazon, Google). Mais volátil e de maior beta que SPY.",
    'QQQM': "Versão 'Mini' do QQQ da Invesco, com custo menor (0.15% vs 0.20%). Criado para investidores de longo prazo que não precisam da liquidez intradiária extrema do QQQ.",
    'VTI': "Cobre o mercado americano inteiro — mais de 3.600 ações (large, mid e small caps). Diversificação máxima com custo mínimo. Principal ETF de mercado total da Vanguard.",
    'SCHB': "Versão Schwab do mercado total americano. Cobre ~2.500 ações. Expense ratio de 0.03%. Ideal para investidores que preferem a plataforma Schwab.",
    'IWM': "Principal ETF de small caps americanas (Russell 2000). Mais cíclico e volátil que o S&P 500. Tende a superar em recuperações econômicas e subperformar em crises.",
    'DIA': "Replica o Dow Jones Industrial Average — as 30 maiores empresas dos EUA ponderadas por preço (não por valor de mercado). Dominado por UnitedHealth, Goldman Sachs e Microsoft.",
    'RSP': "S&P 500 com ponderação igual — cada ação representa ~0.2%. Evita a superponderação em mega-caps. Historicamente supera o S&P 500 ponderado por valor no longo prazo.",
    'MDY': "Mid caps americanas via S&P 400 (empresas de $2B a $10B). Historicamente o 'ponto doce' entre crescimento e estabilidade, com retornos que superam large e small caps no longo prazo.",

    # ── Setoriais ─────────────────────────────────────────────────────────────
    'XLK': "Maior ETF de tecnologia dos EUA. Concentrado em Apple, Microsoft e Nvidia (~50% do fundo). Alto beta, lidera em bull markets e cai mais em correções.",
    'XLF': "Exposure ao setor financeiro americano: bancos, seguros, gestoras de investimento. Beneficia de juros altos e curva de juros positiva. Altamente cíclico.",
    'XLE': "Petróleo, gás e energia. Correlacionado ao preço do crude. Inclui Exxon, Chevron, ConocoPhillips. Hedge natural contra inflação de energia.",
    'XLV': "Saúde americana: farmacêuticas, planos de saúde, devices médicos. Setor defensivo com crescimento secular pela demografia (envelhecimento populacional).",
    'XLI': "Setor industrial: aeroespacial, defesa, transporte, maquinário. Sensível ao ciclo econômico e gastos em infraestrutura.",
    'XLY': "Consumo discricionário: varejo, automóveis, restaurantes, hotéis. Muito sensível ao ciclo econômico e confiança do consumidor. Amazon é o maior componente.",
    'XLP': "Consumo básico: alimentos, bebidas, higiene. Setor defensivo que resiste bem em recessões. Inclui P&G, Costco, Coca-Cola, PepsiCo.",
    'XLRE': "REITs americanos: escritórios, shopping centers, galpões logísticos, data centers, torres de celular. Sensível a juros — sobe quando os juros caem.",
    'XLU': "Utilities: energia elétrica, gás, água. O setor mais defensivo do mercado. Paga dividendos altos e estáveis. Inversamente correlacionado às taxas de juros.",
    'XLC': "Comunicações e mídia: Alphabet, Meta, Netflix, Disney, T-Mobile. Criado em 2018 para incluir 'tech de plataforma' que migrou do setor de tecnologia.",
    'XLB': "Materiais básicos: mineração, químicas, papel. Cíclico e correlacionado ao crescimento global, especialmente China.",
    'VNQ': "REITs via Vanguard. Mais diversificado que XLRE, incluindo REITs menores. Custo de 0.12% vs 0.09% do XLRE, mas maior diversificação.",
    'SOXX': "Semicondutores via iShares. Inclui fabricantes (Intel, Qualcomm), designers (Nvidia, AMD) e equipamentos (ASML, Applied Materials). Altíssima volatilidade e retorno.",
    'SMH': "Semicondutores via VanEck. Similar ao SOXX mas mais concentrado nas top 25. TSMC é o maior componente. Ligeiramente diferente na composição.",
    'XBI': "Biotecnologia equal-weight: cada empresa pesa ~0.7%. Mais exposição a small e mid caps do que IBB. Altíssimo risco, altíssimo potencial. Muito sensível a dados clínicos.",
    'IBB': "Biotecnologia ponderada por cap: Amgen, Gilead, Regeneron dominam. Menos volátil que XBI. Inclui grandes farmacêuticas de biotech.",
    'KRE': "Bancos regionais americanos. Muito sensível à curva de juros e saúde do crédito regional. Alta volatilidade em crises bancárias.",
    'XOP': "Empresas de exploração e produção de petróleo e gás. Mais volátil que XLE, pois exclui as integradas (Exxon, Chevron) e foca nas E&P puras.",
    'OIH': "Serviços e equipamentos de petróleo: Schlumberger, Halliburton, Baker Hughes. Leva mais 3-6 meses para reagir vs preço do petróleo.",
    'JETS': "Companhias aéreas e aeroportos globais. Setor destruído no COVID e que luta para se recuperar. Alta volatilidade, custo de 0.60%.",
    'ITA': "Aeroespacial e defesa americana: Lockheed, RTX, Boeing, Northrop. Beneficia de tensões geopolíticas e aumento de orçamentos militares.",
    'ITB': "Construtoras residenciais americanas: D.R. Horton, Lennar, PulteGroup. Muito sensível às taxas hipotecárias e demanda por moradia.",

    # ── Tech & IA ──────────────────────────────────────────────────────────────
    'CIBR': "Cibersegurança via First Trust. Inclui Palo Alto, CrowdStrike, Fortinet, Zscaler. Setor de crescimento secular com gastos que só aumentam.",
    'BUG': "Cibersegurança via Global X. Portfolio de 27 empresas puras de cybersecurity. Mais concentrado que CIBR.",
    'CLOU': "Cloud computing: empresas de SaaS, PaaS e IaaS. Inclui Salesforce, Snowflake, Datadog, ServiceNow. Correlacionado às taxas de juros por ser growth.",
    'BOTZ': "Robótica e IA via Global X. Empresas de automação industrial, carros autônomos e manufatura inteligente. Mix de EUA e Japão.",
    'ARKK': "ETF flagship da Cathie Wood. Aposta em tecnologias disruptivas: IA, biotech, fintech, cripto, veículos elétricos. Altíssima volatilidade e convicção.",
    'ARKW': "ARK focado em Internet de nova geração: streaming, cloud, IA, cripto. Inclui Tesla, Coinbase, Block.",
    'ARKG': "ARK Genomic: edição genética, CRISPR, terapias genéticas. Altíssimo risco-retorno. Nicho de biotecnologia de vanguarda.",
    'AIQ': "IA e Big Data via Global X. Exposição a empresas que desenvolvem ou utilizam IA: chips, cloud, software.",
    'CHAT': "ETF focado exclusivamente em IA Generativa: Nvidia, Microsoft, Alphabet, Meta. Tema de investimento dominante dos últimos anos.",
    'IGPT': "IA e software de próxima geração via Invesco. Exposição a desenvolvedores de modelos de IA e infraestrutura.",

    # ── Cripto & Fintech ───────────────────────────────────────────────────────
    'IBIT': "Bitcoin spot ETF da BlackRock, o maior gestor do mundo. Aprovado em jan/2024, rapidamente tornou-se o maior Bitcoin ETF com >$50B em AUM. Expense ratio de 0.25%.",
    'FBTC': "Bitcoin spot ETF da Fidelity. Segunda maior gestora americana. Custody próprio — a Fidelity guarda o BTC diretamente, diferente de outros que usam Coinbase.",
    'BITB': "Bitcoin spot ETF da Bitwise, gestora especializada em cripto. Expense ratio mais baixo entre os aprovados em 2024 (0.20%).",
    'ARKB': "Bitcoin spot ETF da ARK Invest + 21Shares. A ARK já tinha exposição indireta via GBTC e estratégias da Coinbase.",
    'GBTC': "O mais antigo veículo de Bitcoin listado (2015). Era um trust fechado que negociava com desconto/prêmio ao NAV. Convertido para ETF em 2024. Custo alto (1.50%).",
    'BITO': "Primeiro ETF de Bitcoin nos EUA (2021), mas baseado em futuros — não no Bitcoin spot. Tem custo de roll dos futuros que corrói retorno vs BTC real.",
    'ETHA': "Ethereum spot ETF da BlackRock. Aprovado em maio/2024. Exposição direta ao segundo maior criptoativo por capitalização.",
    'FINX': "Fintech global: PayPal, Square, Adyen, StoneCo. Empresas de pagamentos digitais, empréstimos peer-to-peer e serviços bancários digitais.",
    'BLOK': "Blockchain e cripto indiretamente: mineradoras, exchanges, empresas que detêm Bitcoin no balanço (MicroStrategy). Gestão ativa.",

    # ── Energia Limpa ──────────────────────────────────────────────────────────
    'ICLN': "Energia limpa global: solar, eólica, hidráulica, geotérmica. Bastante afetado por juros altos (projetos intensivos em capital). Global, com exposição à Europa e Ásia.",
    'TAN': "Energia solar pura: fabricantes de painéis (First Solar), inversores (Enphase), instaladores (SunPower). Alta volatilidade com políticas de subsídio.",
    'FAN': "Energia eólica global: Vestas, Siemens Gamesa, Orsted. Exposição europeia significativa. Beneficia da transição energética.",
    'LIT': "Lítio e baterias: mineradoras (Albemarle, SQM), fabricantes (BYD, Samsung SDI). Correlacionado à adoção de veículos elétricos.",
    'URA': "Urânio e energia nuclear: Cameco (mineradora), NexGen Energy, utilities nucleares. Renascimento da energia nuclear como energia limpa.",

    # ── Internacional Desenvolvidos ────────────────────────────────────────────
    'EFA': "Mercados desenvolvidos ex-EUA: Europa, Japão, Austrália, Canadá. ~750 empresas. Versão 'barata' da diversificação internacional. O mais antigo dos iShares internacionais.",
    'VEA': "Desenvolvidos ex-EUA da Vanguard. Similar ao EFA mas com custo de 0.06% vs 0.32%. Excelente opção para alocação internacional de longo prazo.",
    'EWJ': "Japão via iShares. Exposição ao Nikkei 225 e economia japonesa. Afetado pelo iene — queda do iene reduz retorno em USD.",
    'EWZ': "Brasil via iShares. Concentrado em Petrobras, Vale, bancos (Itaú, Bradesco) e commodities. Alto dividend yield mas grande risco político-cambial.",
    'ACWI': "Mercado global completo: EUA (~60%) + desenvolvidos ex-EUA (~30%) + emergentes (~10%). Uma única posição para diversificação mundial máxima.",

    # ── Mercados Emergentes ────────────────────────────────────────────────────
    'EEM': "Emergentes via iShares — o mais antigo e líder histórico. Expense ratio de 0.70% é alto; VWO ou IEMG são alternativas mais baratas com portfólio similar.",
    'VWO': "Emergentes da Vanguard. 0.08% de custo — muito mais barato que EEM. Inclui China, Taiwan, Índia, Brasil, África do Sul. Difere do EEM por incluir países fronteiriços.",
    'KWEB': "Internet chinesa: Alibaba, Tencent, Meituan, JD.com, Baidu. Alta volatilidade regulatória. Potencial enorme, risco elevado pelas intervenções do governo chinês.",
    'FXI': "Ações chinesas large cap: H-shares de Hong Kong. Concentrado nos setores dominados pelo governo (bancos, energy, telecom). Mais 'China tradicional' que KWEB.",
    'INDA': "Índia via iShares. Exposição às maiores empresas indianas: Reliance Industries, Infosys, HDFC Bank. Crescimento demográfico e econômico secular.",
    'ARGT': "Argentina via Global X. Altíssimo risco político e cambial. Exposição a MercadoLibre (maior peso), bancos e energia argentina.",

    # ── Dividendos ────────────────────────────────────────────────────────────
    'SCHD': "O ETF de dividendos favorito do longo prazo americano. Seleciona 100 ações com histórico de dividendos consistente, baixo payout ratio e crescimento de lucros. 0.06% de custo.",
    'VIG': "Dividend Appreciation: empresas que aumentam dividendo há pelo menos 10 anos consecutivos. Mais focado em crescimento do dividendo do que em yield atual.",
    'VYM': "High Dividend Yield da Vanguard. ~400 empresas com dividendo acima da média do mercado. Mais renda imediata que VIG, com menor crescimento.",
    'JEPI': "Income ETF da JPMorgan. Combina ações defensivas com venda coberta de opções (covered calls) para gerar renda mensal alta (~7-9% ao ano). Menor upside em bull markets.",
    'JEPQ': "Versão Nasdaq do JEPI. Faz covered calls no QQQ para gerar renda. Maior exposição a tech com renda mensal. Upside limitado em fortes rallies de tecnologia.",
    'QYLD': "Covered calls no QQQ: vende calls ATM todo mês, capturando o prêmio como dividendo (~11-12% ao ano). Mas paga com a própria valorização — NAV erosion é o risco.",
    'NOBL': "S&P 500 Dividend Aristocrats: empresas que aumentaram dividendo por 25+ anos consecutivos. Qualidade máxima, baixa volatilidade, crescimento constante do dividendo.",
    'HDV': "High Dividend iShares. Seleciona empresas com alto yield E saúde financeira (tela de qualidade). Setor de saúde, energy e staples dominam.",

    # ── Renda Fixa ────────────────────────────────────────────────────────────
    'TLT': "Treasuries de 20+ anos. O ETF mais usado para apostar em queda de juros. Duração de ~17 anos — grande volatilidade de preço para variações de taxa.",
    'IEF': "Treasuries de 7-10 anos. Duração intermediária (~7.5 anos). Equilíbrio entre yield e sensibilidade a juros. Muito usado em portfolios balanceados.",
    'SHY': "Treasuries de 1-3 anos. Mínima sensibilidade a juros, máxima segurança. Quase equivalente a um money market em ETF.",
    'SGOV': "T-Bills de 0-3 meses. Pratica a taxa do Fed Funds. O ETF mais próximo de 'dinheiro em caixa' com yield de mercado monetário.",
    'AGG': "O 'S&P 500 dos bonds': replica o Bloomberg US Aggregate — toda a renda fixa investment grade americana. Governos, corporativos e MBS em uma única posição.",
    'BND': "Versão Vanguard do AGG. 0.03% de custo vs 0.03% do AGG. Composição levemente diferente. Excelente âncora de renda fixa.",
    'HYG': "High Yield americano: bonds corporativos com rating abaixo de BBB. Maior risco de crédito em troca de yield mais alto. Muito correlacionado à bolsa em crises.",
    'JNK': "High Yield via SPDR. Similar ao HYG mas com portfólio ligeiramente diferente. Maior liquidez intradiária por ser SPDR.",
    'LQD': "Investment Grade corporativo: bonds de empresas de alta qualidade (Apple, Microsoft, J&J emitem bonds aqui). Equilíbrio entre yield e segurança.",
    'TIP': "Títulos do Tesouro indexados à inflação (TIPS). Proteção direta contra CPI americano. Essencial em portfólios que precisam preservar poder de compra real.",
    'EMB': "Bonds soberanos de mercados emergentes em USD. Alta diversificação geográfica. Risco maior que Treasuries mas yield significativamente superior.",
    'TMF': "Treasuries 20+ anos 3x alavancado. Extremamente volátil — usado para especulação em queda de juros. Não adequado para buy & hold (decay diário).",

    # ── Commodities ────────────────────────────────────────────────────────────
    'GLD': "O ETF de ouro mais popular e líquido do mundo. Cada cota representa ~1/10 de onça troy de ouro físico armazenado no cofre do HSBC em Londres.",
    'IAU': "Ouro físico via iShares. Cota menor que GLD (~1/100 oz) e expense ratio mais baixo (0.25% vs 0.40%). Preferido por investidores de longo prazo.",
    'GLDM': "Ouro físico 'mini' da SPDR. 0.10% de custo — o mais barato entre os grandes ETFs de ouro. Lançado em 2018 para competir com IAU.",
    'SLV': "Prata física via iShares. Mais volátil que ouro — tem uso industrial relevante (eletrônicos, painéis solares) além do aspecto monetário.",
    'GDX': "Mineradoras de ouro: Newmont, Barrick, Agnico Eagle. Alavancagem ao preço do ouro (~2-3x). Quando o ouro sobe 10%, GDX tende a subir 20-30%.",
    'GDXJ': "Mineradoras de ouro e prata junior (menores). Maior risco que GDX mas maior potencial. Empresas em fase de exploração e desenvolvimento.",
    'USO': "Petróleo via futuros de crude WTI. Sofre 'roll cost' ao rolar contratos mensalmente. Bom para trades de curto prazo, problemático no longo prazo.",
    'PDBC': "Commodities diversificadas via Invesco: energia, metais, agricultura. Gestão ativa para minimizar o custo de roll dos futuros.",
    'LIT': "Lítio e baterias: mineradoras de lítio (Albemarle, SQM) e fabricantes de baterias (BYD, Samsung SDI). Ligado à cadeia de veículos elétricos.",
    'COPX': "Mineradoras de cobre global. O cobre é indicador da saúde econômica mundial. Beneficia da eletrificação e expansão de infraestrutura de IA (data centers precisam de cobre).",
    'URA': "Urânio: Cameco, NexGen Energy, Yellow Cake. Renascimento do interesse em energia nuclear como alternativa limpa à base de geração de energia.",
    'CORN': "Futuros de milho via Teucrium. Exposição direta ao preço spot do milho sem conta de futuros. Afetado por clima, etanol e exportações.",
    'WEAT': "Futuros de trigo via Teucrium. Muito volátil durante crises geopolíticas (Ucrânia/Rússia). Hedge contra inflação alimentar.",

    # ── Fator / Smart Beta ─────────────────────────────────────────────────────
    'QUAL': "Quality factor: empresas com alto ROE, balanço sólido e crescimento estável de lucros. Historicamente supera o mercado com menor volatilidade.",
    'MTUM': "Momentum: as ações que mais subiram nos últimos 12 meses (excluindo o último mês). Rebalanceamento semestral. Funciona bem em tendências fortes.",
    'VLUE': "Value: ações baratas por múltiplos (P/B, P/E, EV/FCF). Alternativa ao growth em ambientes de juros altos.",
    'USMV': "Minimum Volatility EUA: ações com menor volatilidade histórica. Cai menos em bear markets. Ideal para investidores avessos a risco.",
    'COWZ': "Cash Cows: 100 empresas do Russell 1000 com maior Free Cash Flow Yield. Seleção por FCF real, não por lucros contábeis. Grande sucesso nos últimos anos.",
    'AVUV': "Small Cap Value americano da Avantis (filha da Dimensional). Implementação de fatores de Fama-French: small + value + profitability. Preferido por adeptos de factor investing.",
    'SCHD': "O ETF de dividendos favorito do longo prazo americano. Seleciona 100 ações com histórico de dividendos consistente, baixo payout ratio e crescimento de lucros.",

    # ── Alavancados ───────────────────────────────────────────────────────────
    'TQQQ': "Nasdaq 100 3x alavancado diário. Para cada 1% de alta do QQQ, TQQQ sobe ~3%. Também cai ~3x. O decaimento por volatilidade (volatility decay) corrói o valor no longo prazo. Apenas para operações intradiárias ou de poucos dias.",
    'SQQQ': "Nasdaq 100 inverso 3x. Ganha quando a Nasdaq cai. Extremamente difícil de usar no longo prazo — perde em mercados laterais e sobe com qualidade a decay. Hedge de curto prazo.",
    'UPRO': "S&P 500 3x alavancado diário. Similar ao TQQQ mas sobre o S&P 500. Em 2022, caiu ~75% junto com a queda do mercado. Ferramenta de alta convicção de curto prazo.",
    'SPXL': "S&P 500 3x Bull da Direxion. Equivalente ao UPRO com leve diferença no swaps e custo. Mesmos riscos de decay.",
    'SOXL': "Semicondutores 3x Bull. Extremamente volátil — pode subir ou cair 20%+ em um único dia. Usado em especulações de curto prazo em semicondutores.",
    'TMF': "Treasuries 20+ anos 3x Bull. Apostas alavancadas em queda de juros. Em 2022 perdeu ~90% com alta dos juros. Um dos ETFs mais destrutivos se usado incorretamente.",
    'UVXY': "VIX de curto prazo 1.5x. O 'índice do medo'. Sobe explosivamente quando o mercado cai abruptamente. Perde valor constantemente quando mercado está calmo (custo enorme de roll).",
    'VXX': "VIX de curto prazo sem alavancagem. Histórico de queda constante por custo de roll dos futuros de VIX. Usado para hedge de cauda de curtíssimo prazo.",

    # ── Multi-Asset ────────────────────────────────────────────────────────────
    'AOR': "Portfólio crescimento 60/40 da iShares: 60% ações globais + 40% renda fixa. Uma posição única que mantém diversificação automática.",
    'AOM': "Portfólio moderado 40/60 da iShares. Mais conservador que AOR. Ideal para quem quer uma carteira balanceada sem gestão ativa.",
    'AOA': "Portfólio agressivo 80/20 da iShares. Maior exposição a ações para investidores com horizonte longo e tolerância a volatilidade.",
    'NTSX': "90% S&P 500 + 10% em futuros de bonds 6x alavancados = exposição equivalente a 90% ações + 60% bonds com apenas 100% de capital. Portfólio eficiente.",
    'SWAN': "BlackSwan Growth ETF: 90% em LEAPS do S&P 500 (protetores) + 10% em bonds. Protege contra quedas extremas enquanto participa de altas.",
    'RPAR': "Risk Parity: distribui risco igualmente entre ações, bonds, ouro e commodities. Estratégia de Ray Dalio adaptada para ETF.",
}

def get_descricao(ticker):
    """Retorna descrição do ETF ou gera uma baseada no nome e categoria."""
    if ticker in ETF_DESCRICAO:
        return ETF_DESCRICAO[ticker]
    nome = NOME_MAP.get(ticker, ticker)
    cat  = CATEGORIA_MAP.get(ticker, 'ETF')
    er   = ETF_EXPENSE_RATIO.get(ticker)
    er_str = f" Expense ratio: {er*100:.2f}%/ano." if er else ""
    return f"{nome} — ETF da categoria {cat}.{er_str} Consulte o prospecto do fundo para detalhes completos sobre estratégia, composição e riscos."


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

    # ── Card de descrição do ETF ───────────────────────────────────────────────
    descricao = get_descricao(ticker)
    er_hard = ETF_EXPENSE_RATIO.get(ticker)
    er_badge = f"&nbsp;|&nbsp; 💰 <b>{er_hard:.2f}%/ano</b>" if er_hard else ""
    cat_badge = row['Categoria']
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);
                padding:1rem 1.25rem;border-radius:10px;margin-bottom:1.25rem;
                border-left:4px solid #0288d1;">
        <p style="margin:0 0 0.4rem;font-size:0.75rem;font-weight:600;
                  color:#0277bd;text-transform:uppercase;letter-spacing:.05em;">
            🗂️ {cat_badge}{er_badge}
        </p>
        <p style="margin:0;color:#0d2f4f;font-size:0.92rem;line-height:1.55;">{descricao}</p>
    </div>
    """, unsafe_allow_html=True)

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
