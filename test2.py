import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib.ticker as mticker
from datetime import timedelta
from tqdm import tqdm

# --- 1. SIMULATION PARAMETERS ---
TICKER = "^GSPC"
Name = "sp500"

# Simulation Period
START_DATE = "2000-01-01" 
END_DATE = pd.to_datetime('today').strftime('%Y-%m-%d')

# Monthly Investment Amount (in Dollars)
INVESTISSEMENT_MENSUEL = 100 

# Video Parameters
FPS = 10  # Smoother framerate (needs more data points)
DPI = 120 # High quality

# --- END OF PARAMETERS ---

# --- 2. DATA DOWNLOAD AND PREPARATION ---
print(f"Downloading data for {TICKER} from {START_DATE} to {END_DATE}...")
try:
    # Get ticker info for the long name
    ticker_obj = yf.Ticker(TICKER)
    try:
        ASSET_NAME = ticker_obj.info.get('longName', TICKER)
    except:
        ASSET_NAME = Name
    
    # Download history with dividends
    # actions=True ensures we get Dividends and Stock Splits
    data = ticker_obj.history(start=START_DATE, end=END_DATE, auto_adjust=False)
    
    if data.empty:
        raise ValueError("No price data found for the specified period.")
    
    # Ensure we have Close and Dividends
    if 'Dividends' not in data.columns:
        data['Dividends'] = 0.0
        
except Exception as e:
    print(f"Error: Unable to download data. Check the Ticker, period, or internet connection. Detail: {e}")
    exit()

# Output filename
NOM_FICHIER_VIDEO = f"evolution_capital_{ASSET_NAME}.mp4"

# Resampling to WEEKLY ('W') for smoother/longer animation (approx 4x more frames than Monthly)
# We take the last price of the week and the SUM of dividends during that week
logic = {'Close': 'last', 'Dividends': 'sum'}
data_weekly = data.resample('ME').apply(logic)
data_weekly = data_weekly.dropna(subset=['Close']) # Drop weeks with no price

# Create a DataFrame to store simulation results
simulation_df = pd.DataFrame(index=data_weekly.index)
simulation_df['Prix_Unitaire'] = data_weekly['Close']
simulation_df['Dividends'] = data_weekly['Dividends']

# --- 3. WEEKLY SIMULATION EXECUTION (DCA + DIVIDENDS) ---
capital_total_investi = 0.0
nombre_unites = 0.0
liste_valeur_portefeuille = []
liste_capital_investi = []
liste_plus_value = []
liste_dividendes_cumules = []

total_dividendes_recus = 0.0

# We need to track when to invest the monthly amount.
# We'll invest in the first week of each month.
last_month_invested = -1

print("Executing weekly investment simulation (with dividends)...")
for date, row in tqdm(simulation_df.iterrows(), total=len(simulation_df), desc="Calculating evolution"):
    prix = row['Prix_Unitaire']
    div_unit = row['Dividends']
    
    # 1. Reinvest Dividends (if any)
    # Dividend is per share, so total dividend received = units * dividend_per_share
    if div_unit > 0 and nombre_unites > 0:
        montant_dividende = nombre_unites * div_unit
        nouvelles_unites_div = montant_dividende / prix
        nombre_unites += nouvelles_unites_div
        total_dividendes_recus += montant_dividende
    
    # 2. Monthly Investment (DCA)
    # Check if we are in a new month compared to last iteration
    current_month = date.month
    if current_month != last_month_invested:
        montant_investi_ce_mois = INVESTISSEMENT_MENSUEL
        
        # Buy new units
        nouvelles_unites = montant_investi_ce_mois / prix
        nombre_unites += nouvelles_unites
        
        # Update total invested capital (cash from pocket)
        capital_total_investi += montant_investi_ce_mois
        
        last_month_invested = current_month
    
    # 3. Calculate Portfolio Value
    valeur_portefeuille = nombre_unites * prix
    
    # 4. Store Results
    liste_valeur_portefeuille.append(valeur_portefeuille)
    liste_capital_investi.append(capital_total_investi)
    liste_plus_value.append(valeur_portefeuille - capital_total_investi)
    liste_dividendes_cumules.append(total_dividendes_recus)


# Add results to simulation DataFrame
simulation_df['Valeur_Portefeuille'] = liste_valeur_portefeuille
simulation_df['Capital_Investi'] = liste_capital_investi
simulation_df['Plus_Value'] = liste_plus_value
simulation_df['Dividendes_Cumules'] = liste_dividendes_cumules

# Check if there are any dividends
if liste_dividendes_cumules:
    has_dividends = liste_dividendes_cumules[-1] > 0
else:
    has_dividends = False

# --- 4. ANIMATION PREPARATION (MODERN DARK THEME) ---

# Colors
COLOR_BG = '#0A0A0A'       # Very Dark Gray
COLOR_GRID = '#2E2E2E'     # Dark Gray
COLOR_TEXT = '#F0F0F0'     # Near White
COLOR_PORTFOLIO = '#00FFC0' # Neon Green
COLOR_INVESTED = '#00CFFF'  # Neon Blue
COLOR_DIVIDENDS = '#FF00FF' # Neon Magenta (New curve for Dividends)

# Setup Style
plt.rcParams.update({
    'figure.facecolor': COLOR_BG,
    'axes.facecolor': COLOR_BG,
    'axes.edgecolor': COLOR_GRID,
    'axes.labelcolor': COLOR_TEXT,
    'xtick.color': COLOR_TEXT,
    'ytick.color': COLOR_TEXT,
    'grid.color': COLOR_GRID,
    'text.color': COLOR_TEXT,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
})

# Create Figure (9:16 Aspect Ratio for Mobile/Shorts)
fig, ax = plt.subplots(figsize=(9, 16))
fig.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.10)

# Initializing plot lines
# Adding a glow effect by plotting the same line with higher linewidth and lower alpha behind
line_portefeuille_glow, = ax.plot([], [], color=COLOR_PORTFOLIO, linewidth=8, alpha=0.15)
line_portefeuille, = ax.plot([], [], label='Portfolio Value', color=COLOR_PORTFOLIO, linewidth=2.5)

line_investi, = ax.plot([], [], label='Invested Capital', color=COLOR_INVESTED, linestyle='--', linewidth=2)

# New Line for Dividends
line_dividendes, = ax.plot([], [], label='Accumulated Dividends', color=COLOR_DIVIDENDS, linestyle=':', linewidth=2)

# Fill under the curve for a modern look
fill_poly = ax.fill_between([], [], color=COLOR_PORTFOLIO, alpha=0.05)

# Points at the end of curves
point_portefeuille, = ax.plot([], [], 'o', color=COLOR_PORTFOLIO, markersize=12, markeredgecolor='white', markeredgewidth=2)
point_investi, = ax.plot([], [], 'o', color=COLOR_INVESTED, markersize=8, markeredgecolor='white', markeredgewidth=1)
point_dividendes, = ax.plot([], [], 'o', color=COLOR_DIVIDENDS, markersize=8, markeredgecolor='white', markeredgewidth=1)

# Texts following the curves
text_portefeuille = ax.text(0, 0, '', color=COLOR_PORTFOLIO, fontweight='bold', fontsize=20)
text_investi = ax.text(0, 0, '', color=COLOR_INVESTED, fontweight='bold', fontsize=18)
text_dividendes = ax.text(0, 0, '', color=COLOR_DIVIDENDS, fontweight='bold', fontsize=18)

# Info Box (Top Left)
text_info = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=16, verticalalignment='top', color='white',
                    bbox=dict(boxstyle="round,pad=0.5", fc="#1A1A1A", ec="#333333", lw=1, alpha=0.9))

# Title
ax.set_title(f"{ASSET_NAME}\nDCA Strategy", fontsize=24, pad=30, color='white', fontweight='bold')
ax.set_xlabel("Year", fontsize=14, labelpad=15)
ax.set_ylabel("Value ($)", fontsize=14, labelpad=15)

# Grid
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

# Legend
#legend = ax.legend(loc='upper left', bbox_to_anchor=(0, 0.88), frameon=True, facecolor='#1A1A1A', edgecolor='#333333')
#for text in legend.get_texts():
    #text.set_color(COLOR_TEXT)

# Formatter for Y axis (Currency)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f} $'))

# --- ANIMATION LOGIC ---

def init():
    line_portefeuille.set_data([], [])
    line_portefeuille_glow.set_data([], [])
    line_investi.set_data([], [])
    line_dividendes.set_data([], [])
    point_portefeuille.set_data([], [])
    point_investi.set_data([], [])
    point_dividendes.set_data([], [])
    text_portefeuille.set_text('')
    text_investi.set_text('')
    text_dividendes.set_text('')
    text_info.set_text('')
    return line_portefeuille, line_portefeuille_glow, line_investi, line_dividendes, point_portefeuille, point_investi, point_dividendes, text_portefeuille, text_investi, text_dividendes, text_info

def update(frame):
    current_df = simulation_df.iloc[:frame+1]
    
    if current_df.empty:
        return line_portefeuille, line_portefeuille_glow, line_investi, line_dividendes, point_portefeuille, point_investi, point_dividendes, text_portefeuille, text_investi, text_dividendes, text_info

    # Update Data
    x_data = current_df.index
    y_port = current_df['Valeur_Portefeuille']
    y_inv = current_df['Capital_Investi']
    y_div = current_df['Dividendes_Cumules']
    
    line_portefeuille.set_data(x_data, y_port)
    line_portefeuille_glow.set_data(x_data, y_port)
    line_investi.set_data(x_data, y_inv)
    if has_dividends:
        line_dividendes.set_data(x_data, y_div)
    
    # Update Points
    last_date = current_df.index[-1]
    last_val_port = y_port.iloc[-1]
    last_val_inv = y_inv.iloc[-1]
    last_val_div = y_div.iloc[-1]
    
    point_portefeuille.set_data([last_date], [last_val_port])
    point_investi.set_data([last_date], [last_val_inv])
    if has_dividends:
        point_dividendes.set_data([last_date], [last_val_div])
    
    # Dynamic Axis Limits
    max_val_current = max(last_val_port, last_val_inv)
    ax.set_ylim(0, max_val_current * 1.25) # More headroom
    
    duree_ecoulee = last_date - simulation_df.index[0]
    marge = max(timedelta(days=60), duree_ecoulee * 0.1)
    ax.set_xlim(simulation_df.index[0], last_date + marge)
    
    # Text Positioning
    text_portefeuille.set_position((last_date, last_val_port))
    text_portefeuille.set_text(f" {last_val_port:,.0f} $")
    
    text_investi.set_position((last_date, last_val_inv))
    text_investi.set_text(f" {last_val_inv:,.0f} $")
    
    if has_dividends:
        text_dividendes.set_position((last_date, last_val_div))
        text_dividendes.set_text(f" {last_val_div:,.0f} $")
    
    # Info Text
    current_plus_value = current_df['Plus_Value'].iloc[-1]
    roi = (current_plus_value / last_val_inv) * 100 if last_val_inv > 0 else 0
    
    info_lines = [
        f"Date: {last_date.strftime('%Y-%m-%d')}",
        f"Gain: {current_plus_value:+,.0f} $"
    ]
    if has_dividends:
        info_lines.append(f"Dividends: {last_val_div:,.0f} $")
    info_lines.append(f"ROI: {roi:+.1f}%")
    
    info_text = "\n".join(info_lines)
    text_info.set_text(info_text)
    
    return line_portefeuille, line_portefeuille_glow, line_investi, line_dividendes, point_portefeuille, point_investi, point_dividendes, text_portefeuille, text_investi, text_dividendes, text_info

# Create Animation
print(f"Creating animation ({len(simulation_df)} frames)...")
ani = FuncAnimation(
    fig, 
    update, 
    frames=len(simulation_df), 
    init_func=init, 
    blit=False, 
    interval=1000/FPS 
)

# --- 5. VIDEO RECORDING ---
print(f"Saving video to '{NOM_FICHIER_VIDEO}'...")

writer = FFMpegWriter(fps=FPS, metadata=dict(artist='Me'), bitrate=2500)

with tqdm(total=len(simulation_df), desc="Recording") as pbar:
    ani.save(NOM_FICHIER_VIDEO, writer=writer, dpi=DPI, progress_callback=lambda i, n: pbar.update(1))

print(f"\n✅ Video '{NOM_FICHIER_VIDEO}' generated successfully!")

# Final Stats
resultat_final = simulation_df.iloc[-1]
print("\n--- Final Result ---")
print(f"Final Date : {resultat_final.name.strftime('%Y-%m-%d')}")
print(f"Total Invested : {resultat_final['Capital_Investi']:,.2f} $")
print(f"Portfolio Value : {resultat_final['Valeur_Portefeuille']:,.2f} $")
print(f"Total Dividends : {resultat_final['Dividendes_Cumules']:,.2f} $")
print(f"Total Gain : {resultat_final['Plus_Value']:,.2f} $")
