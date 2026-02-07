import yfinance as yf
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation 
from matplotlib.animation import FFMpegWriter
import seaborn as sns
from datetime import timedelta

from tqdm import tqdm

# --- 1. SIMULATION PARAMETERS ---
TICKER = "^FCHI"

# Simulation Period
START_DATE = "2000-01-01" 
END_DATE = pd.to_datetime('today').strftime('%Y-%m-%d')

# Monthly Investment Amount (in Euros)
INVESTISSEMENT_MENSUEL = 100 


FPS = 10
DPI = 100

# --- END OF PARAMETERS ---

# --- 2. DATA DOWNLOAD AND PREPARATION ---
print(f"Downloading data for {TICKER} from {START_DATE} to {END_DATE}...")
try:
    # Get ticker info for the long name
    ticker_obj = yf.Ticker(TICKER)
    try:
        ASSET_NAME = ticker_obj.info.get('longName', TICKER)
    except:
        ASSET_NAME = TICKER
        
    data = yf.download(TICKER, start=START_DATE, end=END_DATE, auto_adjust=True)
    prix_cloture = data['Close'].dropna()
    
    if prix_cloture.empty:
        raise ValueError("No price data found for the specified period.")
        
except Exception as e:
    print(f"Error: Unable to download data. Check the Ticker, period, or internet connection. Detail: {e}")
    exit()

# Video Parameters
NOM_FICHIER_VIDEO = f"evolution_capital_{ASSET_NAME}.mp4"

# Resampling: take the closing price of the last day of each month
prix_mensuel = prix_cloture.resample('ME').last()

# Create a DataFrame to store simulation results
simulation_df = pd.DataFrame(index=prix_mensuel.index)
simulation_df['Prix_Unitaire'] = prix_mensuel

# --- 3. MONTHLY SIMULATION EXECUTION (DCA) ---
capital_total_investi = 0.0
nombre_unites = 0.0
liste_valeur_portefeuille = []
liste_capital_investi = []
liste_plus_value = []

print("Executing monthly investment simulation...")
for date, prix in tqdm(simulation_df['Prix_Unitaire'].items(), desc="Calculating evolution"):
    # Monthly investment
    montant_investi_ce_mois = INVESTISSEMENT_MENSUEL
    
    # Calculating new units purchased
    nouvelles_unites = montant_investi_ce_mois / prix
    nombre_unites += nouvelles_unites
    
    # Updating total invested capital
    capital_total_investi += montant_investi_ce_mois
    
    # Calculating portfolio market value
    valeur_portefeuille = nombre_unites * prix
    
    # Storing results
    liste_valeur_portefeuille.append(valeur_portefeuille)
    liste_capital_investi.append(capital_total_investi)
    liste_plus_value.append(valeur_portefeuille - capital_total_investi)

# Add results to simulation DataFrame
simulation_df['Valeur_Portefeuille'] = liste_valeur_portefeuille
simulation_df['Capital_Investi'] = liste_capital_investi
simulation_df['Plus_Value'] = liste_plus_value

# --- 4. ANIMATION PREPARATION ---

# Seaborn style configuration
sns.set_theme(style="darkgrid", context="talk")

fig, ax = plt.subplots(figsize=(9, 16))

# Initializing plot lines
line_portefeuille, = ax.plot([], [], label='Portfolio Value', color='#2ecc71', linewidth=3)
line_investi, = ax.plot([], [], label='Invested Capital', color='#3498db', linestyle='--', linewidth=2)

# Points at the end of curves
point_portefeuille, = ax.plot([], [], 'o', color='#2ecc71', markersize=8)
point_investi, = ax.plot([], [], 'o', color='#3498db', markersize=8)

# Texts following the curves
text_portefeuille = ax.text(0, 0, '', color='#2ecc71', fontweight='bold', fontsize=12)
text_investi = ax.text(0, 0, '', color='#3498db', fontweight='bold', fontsize=12)

# Text for Capital Gain (fixed top left)
text_info = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=14, verticalalignment='top', 
                    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#7f8c8d", lw=1, alpha=0.9))

# Defining initial axis limits
ax.set_ylim(0, 1000)  # Initial value, will be updated dynamically
ax.set_xlim(simulation_df.index[0], simulation_df.index[0] + timedelta(days=60))

ax.set_title(f"Capital Evolution: {ASSET_NAME}", fontsize=20, pad=20)
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Value (€)", fontsize=14)
ax.legend(loc='upper left', bbox_to_anchor=(0, 0.90))

plt.tight_layout()

# Initialization function
def init():
    line_portefeuille.set_data([], [])
    line_investi.set_data([], [])
    point_portefeuille.set_data([], [])
    point_investi.set_data([], [])
    text_portefeuille.set_text('')
    text_investi.set_text('')
    text_info.set_text('')
    return line_portefeuille, line_investi, point_portefeuille, point_investi, text_portefeuille, text_investi, text_info

# Update function
def update(frame):
    # Data up to current frame
    current_df = simulation_df.iloc[:frame+1]
    
    if current_df.empty:
        return line_portefeuille, line_investi, point_portefeuille, point_investi, text_portefeuille, text_investi, text_info

    # Updating lines
    line_portefeuille.set_data(current_df.index, current_df['Valeur_Portefeuille'])
    line_investi.set_data(current_df.index, current_df['Capital_Investi'])
    
    # Updating points (last point)
    last_date = current_df.index[-1]
    last_val_port = current_df['Valeur_Portefeuille'].iloc[-1]
    last_val_inv = current_df['Capital_Investi'].iloc[-1]
    
    point_portefeuille.set_data([last_date], [last_val_port])
    point_investi.set_data([last_date], [last_val_inv])
    
    # Dynamic update of Y axis (Value in €)
    max_val_current = max(last_val_port, last_val_inv)
    ax.set_ylim(0, max_val_current * 1.15)
    
    # Smart text positioning to avoid overlaps
    diff_valeurs = abs(last_val_port - last_val_inv)
    seuil_chevauchement = max_val_current * 0.05  # 5% of max value
    
    if diff_valeurs < seuil_chevauchement:
        # Values are close, shift labels
        offset_port = max_val_current * 0.03
        offset_inv = -max_val_current * 0.03
    else:
        offset_port = 0
        offset_inv = 0
    
    text_portefeuille.set_position((last_date, last_val_port + offset_port))
    text_portefeuille.set_text(f" {last_val_port:,.0f} €")
    text_portefeuille.set_verticalalignment('center')
    
    text_investi.set_position((last_date, last_val_inv + offset_inv))
    text_investi.set_text(f" {last_val_inv:,.0f} €")
    text_investi.set_verticalalignment('center')
    
    # Updating global info text
    current_plus_value = current_df['Plus_Value'].iloc[-1]
    roi = (current_plus_value / last_val_inv) * 100 if last_val_inv > 0 else 0
    
    info_text = (
        f"Date: {last_date.strftime('%Y-%m-%d')}\n"
        f"Capital Gain: {current_plus_value:+,.2f} €\n"
        f"ROI: {roi:+.2f}%"
    )
    text_info.set_text(info_text)
    
    # Dynamic update of X axis (Date)
    duree_ecoulee = last_date - simulation_df.index[0]
    marge = max(timedelta(days=30), duree_ecoulee * 0.1)
    
    ax.set_xlim(simulation_df.index[0], last_date + marge)
    
    return line_portefeuille, line_investi, point_portefeuille, point_investi, text_portefeuille, text_investi, text_info

# Creating animation
print(f"Creating animation ({len(simulation_df)} frames)...")
ani = FuncAnimation(
    fig, 
    update, 
    frames=len(simulation_df), 
    init_func=init, 
    blit=False,  # Necessary because we modify axes dynamically
    interval=1000/FPS 
)

# --- 5. VIDEO RECORDING ---
print(f"Saving video to '{NOM_FICHIER_VIDEO}'...")

writer = FFMpegWriter(fps=FPS, metadata=dict(artist='Me'), bitrate=1800)

with tqdm(total=len(simulation_df), desc="Recording") as pbar:
    ani.save(NOM_FICHIER_VIDEO, writer=writer, dpi=DPI, progress_callback=lambda i, n: pbar.update(1))

print(f"\n✅ Video '{NOM_FICHIER_VIDEO}' generated successfully!")

# Displaying final data
print("\n--- Final Result ---")
resultat_final = simulation_df.iloc[-1]
print(f"Final Date : {resultat_final.name.strftime('%Y-%m-%d')}")
print(f"Total Invested Capital : {resultat_final['Capital_Investi']:,.2f} €")
print(f"Total Market Value : {resultat_final['Valeur_Portefeuille']:,.2f} €")
print(f"Realized Capital Gain : {resultat_final['Plus_Value']:,.2f} €")