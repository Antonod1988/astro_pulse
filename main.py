import streamlit as st
import swisseph as swe
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import os
import requests

# Import separate interpretations module
from interpretations import get_interpretation, KEYWORDS, ASPECT_KEYWORDS, INTERPRETATIONS_DB, get_planet_rarity
from i18n import TRANSLATIONS

# -------------------------------------
# 1. Page Configuration & Custom CSS
# -------------------------------------
# Initialize language early
if 'lang' not in st.session_state:
    st.session_state.lang = "ru"

L = TRANSLATIONS[st.session_state.lang]

st.set_page_config(page_title=L["page_title"], layout="wide", page_icon="✨")

st.markdown("""
    <style>
    /* Фон - Глубокий космос */
    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #e0e0e0;
    }
    /* Скрытие лишнего */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Заголовки */
    h1, h2, h3 { color: #FFD700 !important; font-weight: 200; }
    
    /* Карточки интерпретаций */
    .interpretation-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #FFD700;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 0 10px 10px 0;
    }
    .bad-aspect { border-left-color: #FF4500; } /* Красный для напряженных */
    .good-aspect { border-left-color: #00FF7F; } /* Зеленый для гармоничных */
    </style>
""", unsafe_allow_html=True)

# -------------------------------------
# 3. Calculation Core
# -------------------------------------
# Ensure ephemeris path is absolute or correct relative to execution
EPHEMERIS_PATH = os.path.join(os.path.dirname(__file__), 'ephemeris')
try:
    swe.set_ephe_path(EPHEMERIS_PATH)
except:
    st.error(f"Путь к эфемеридам не найден или некорректен: {EPHEMERIS_PATH}")

ALL_PLANETS = [
    (swe.SUN, "Sun"), (swe.MOON, "Moon"), (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"), (swe.MARS, "Mars"), (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"), (swe.URANUS, "Uranus"), (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto")
]

ASPECT_ANGLES = {"Conjunction": 0, "Sextile": 60, "Square": 90, "Trine": 120, "Opposition": 180}

# Цвета для графиков
ASPECT_COLORS_MAP = {
    "Conjunction": "#FFD700", # Gold
    "Sextile": "#00FF7F",     # Green
    "Square": "#FF4500",      # Red
    "Trine": "#1E90FF",       # Blue
    "Opposition": "#DC143C"   # Crimson
}

# Rarity Weights (Duration of influence)
PLANET_RARITY = {
    "Moon": 1.0, "Mercury": 1.2, "Venus": 1.4, "Sun": 1.5,
    "Mars": 2.0, "Jupiter": 5.0, "Saturn": 10.0, "Uranus": 20.0,
    "Neptune": 30.0, "Pluto": 50.0
}

# Base weights (Nature of influence)
PLANET_WEIGHTS = {
    "Moon": 10, "Mercury": 10, "Venus": 15, "Sun": 20,
    "Mars": 25, "Jupiter": 30, "Saturn": 35, "Uranus": 40,
    "Neptune": 40, "Pluto": 50
}

CONJUNCTION_SCORES = {
    "Sun": 1.0, "Moon": 0.5, "Mercury": 0.0, "Venus": 1.5, "Mars": -1.0,
    "Jupiter": 2.0, "Saturn": -2.0, "Uranus": 0.5, "Neptune": 0.0, "Pluto": -1.0
}
ASPECT_NATURE = {"Sextile": 0.5, "Square": -2.0, "Trine": 1.5, "Opposition": -2.0}

def get_coordinates_osm(city_name):
    """
    Fetches coordinates for a city using OpenStreetMap Nominatim API.
    Returns (lat, lon) or None if not found.
    User-Agent is required by OSM policy.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "AstroPulseDesktop/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

def datetime_to_jd(dt):
    if dt.tzinfo is not None: dt = dt.astimezone(pytz.UTC)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0, swe.GREG_CAL)

def get_planet_position(jd, planet):
    pos, _ = swe.calc_ut(jd, planet, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return pos[0]

def angle_diff(a, b):
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d

def is_aspect(diff, selected_aspects, orb):
    for aspect_name in selected_aspects:
        if abs(diff - ASPECT_ANGLES[aspect_name]) <= orb: return aspect_name
    return None

def calculate_peak_score(transiting_name, aspect_name):
    """Calculates the maximum potential score of an aspect (at exactness)."""
    # Base score from nature of aspect (+/-)
    if aspect_name == "Conjunction":
        base = CONJUNCTION_SCORES.get(transiting_name, 0)
    else:
        base = ASPECT_NATURE.get(aspect_name, 0)
    
    # Weight by planet importance
    p_weight = PLANET_WEIGHTS.get(transiting_name, 10)
    
    # Weight by Rarity
    r_weight = PLANET_RARITY.get(transiting_name, 1.0)
    
    return base * p_weight * r_weight

def get_dynamic_score(t, transiting_name, natal_name, aspect_name, natal_pos, orb_max):
    """Calculates score at specific time t based on orb precision."""
    jd = datetime_to_jd(t)
    t_pos_val = get_planet_position(jd, next(p[0] for p in ALL_PLANETS if p[1] == transiting_name))
    n_pos_val = natal_pos[next(p[0] for p in ALL_PLANETS if p[1] == natal_name)]
    
    diff = angle_diff(t_pos_val, n_pos_val)
    target_angle = ASPECT_ANGLES[aspect_name]
    current_orb = abs(diff - target_angle)
    
    if current_orb > orb_max:
        return 0
    
    # Precision factor (1.0 at exact, 0.0 at max orb)
    precision = 1.0 - (current_orb / orb_max)
    
    # Applying vs Separating
    # Check position 1 hour later
    jd_next = jd + (1/24.0)
    t_pos_next, _ = swe.calc_ut(jd_next, next(p[0] for p in ALL_PLANETS if p[1] == transiting_name), swe.FLG_SWIEPH)
    diff_next = angle_diff(t_pos_next[0], n_pos_val)
    orb_next = abs(diff_next - target_angle)
    
    is_applying = orb_next < current_orb
    trend_factor = 1.2 if is_applying else 0.8
    
    base_peak = calculate_peak_score(transiting_name, aspect_name)
    
    # Final Formula: Peak * Precision^2 (sharper curves) * Trend
    return base_peak * (precision ** 2) * trend_factor

def get_house_for_pos(pos, cusps):
    """
    Determines which house (1-12) a planet is in based on its longitude and house cusps.
    Args:
        pos (float): Planet longitude (0-360).
        cusps (list): List of 13 cusps (index 0 is usually ignored or dupe, swisseph returns 13 floats).
                      cusps[1] = House 1 cusp, etc.
    Returns:
        int: House number (1-12).
    """
    # Normalize positions
    pos = pos % 360
    
    # Determine offset based on swisseph returns (13 floats vs 12 floats)
    is_1based = len(cusps) > 12
    offset = 1 if is_1based else 0
    
    # Iterate houses 1 to 12
    for i in range(1, 13):
        # Index logic:
        # If 1-based: House 1 is at index 1.
        # If 0-based: House 1 is at index 0.
        idx_curr = i if is_1based else i-1
        idx_next = (i + 1) if is_1based else i
        
        # Handle wrap around index for House 12 -> 1
        if i == 12:
            idx_next = 1 if is_1based else 0

        h_start = cusps[idx_curr]
        h_end = cusps[idx_next]
        
        # Handle wraparound (e.g. Pisces -> Aries)
        if h_start < h_end:
            if h_start <= pos < h_end:
                return i
        else: # Wraps through 360/0
            if pos >= h_start or pos < h_end:
                return i
    return 1 # Fallback

@st.cache_data
def calculate_transits(start_date, end_date, hour_increment, natal_positions, chosen_planets, chosen_aspect_names, orb, natal_cusps):
    """
    Updated to include House calculation.
    natal_cusps: list of floats from swe.houses
    """
    start_dt = datetime.datetime.combine(start_date, datetime.time(0,0), tzinfo=pytz.UTC)
    end_dt = datetime.datetime.combine(end_date, datetime.time(23,59), tzinfo=pytz.UTC)
    delta = datetime.timedelta(hours=hour_increment)
    intervals = []
    active_aspects = {}
    
    # Calculate Natal Houses for all natal planets once (static)
    natal_houses_map = {}
    if natal_cusps:
         for pid, pname in chosen_planets:
             if pid in natal_positions:
                 natal_houses_map[pid] = get_house_for_pos(natal_positions[pid], natal_cusps)

    # Init dict
    for t_id, t_name in chosen_planets:
        for n_id, n_name in chosen_planets:
            if t_id != n_id:
                for aname in chosen_aspect_names:
                    active_aspects[(t_id, n_id, aname)] = {"active": False, "start": None}

    current = start_dt
    while current <= end_dt:
        jd = datetime_to_jd(current)
        t_pos = {pid: get_planet_position(jd, pid) for pid, _ in chosen_planets}

        for t_id, t_name in chosen_planets:
            # Transit House: Which house of the Natal Chart is the Transiting Planet in?
            t_house = 0
            if natal_cusps:
                t_house = get_house_for_pos(t_pos[t_id], natal_cusps)
                
            for n_id, n_name in chosen_planets:
                if t_id == n_id: continue
                
                n_house = natal_houses_map.get(n_id, 0)
                
                diff = angle_diff(t_pos[t_id], natal_positions[n_id])
                current_aspect = is_aspect(diff, chosen_aspect_names, orb)

                for aname in chosen_aspect_names:
                    key = (t_id, n_id, aname)
                    is_active = (current_aspect == aname)
                    if is_active and not active_aspects[key]["active"]:
                        active_aspects[key]["active"] = True
                        active_aspects[key]["start"] = current
                        # Capture House info at start of aspect
                        active_aspects[key]["t_house"] = t_house
                        active_aspects[key]["n_house"] = n_house
                        
                    elif not is_active and active_aspects[key]["active"]:
                        intervals.append({
                            "aspect": aname, "transiting": t_name, "natal": n_name,
                            "start": active_aspects[key]["start"], "end": current,
                            "t_house": active_aspects[key].get("t_house", 0),
                            "n_house": active_aspects[key].get("n_house", 0)
                        })
                        active_aspects[key]["active"] = False
        current += delta # Increment step
    
    # Close remaining
    for (t_id, n_id, aname), data in active_aspects.items():
        if data["active"]:
            t_name = next(p[1] for p in chosen_planets if p[0] == t_id)
            n_name = next(p[1] for p in chosen_planets if p[0] == n_id)
            intervals.append({
                "aspect": aname, "transiting": t_name, "natal": n_name,
                "start": data["start"], "end": end_dt,
                "t_house": data.get("t_house", 0),
                "n_house": data.get("n_house", 0)
            })
    return pd.DataFrame(intervals)

# -------------------------------------
# 4. UI Layout
# -------------------------------------
with st.sidebar:
    st.header(L["sidebar_header"])
    
    # Language Selection
    new_lang = st.selectbox(L["lang_selection"], ["ru", "en"], index=0 if st.session_state.lang == "ru" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    b_date = st.date_input(L["birth_date"], datetime.date(1988, 10, 18))
    b_time = st.text_input(L["birth_time"], "10:25")
    tz_list = pytz.common_timezones
    sel_tz = st.selectbox(L["timezone"], tz_list, index=tz_list.index("Europe/Moscow") if "Europe/Moscow" in tz_list else 0)
    
    st.markdown(f"### {L['location']}")
    city_str = st.text_input(L["city"], "Moscow" if st.session_state.lang == "en" else "Москва")
    
    # Initialize state if needed
    if 'lat_input' not in st.session_state: st.session_state.lat_input = 55.75
    if 'lon_input' not in st.session_state: st.session_state.lon_input = 37.61

    if st.button(L["find_coords"]):
        coords = get_coordinates_osm(city_str)
        if coords:
            st.session_state.lat_input = coords[0]
            st.session_state.lon_input = coords[1]
            st.success(L["coords_updated"])
            st.rerun() # Force rerun to update widgets immediately
        else:
            st.error(L["city_not_found"])

    c1, c2 = st.columns(2)
    with c1:
        lat = st.number_input(L["lat"], format="%.4f", key="lat_input")
    with c2:
        lon = st.number_input(L["lon"], format="%.4f", key="lon_input")

    st.markdown("---")
    s_date = st.date_input(L["forecast_start"], datetime.date.today())
    e_date = st.date_input(L["forecast_end"], datetime.date.today() + datetime.timedelta(days=30))
    
    with st.expander(L["detailed_settings"]):
        orb_val = st.slider(L["orbis"], 1.0, 5.0, 3.0)
        min_duration = st.slider(L["min_duration"], 0, 72, 0, step=1)
        sel_planets = st.multiselect(L["planets"], [p[1] for p in ALL_PLANETS], default=["Sun", "Mars", "Jupiter", "Saturn", "Pluto"])
        sel_aspects = st.multiselect(L["aspects"], list(ASPECT_ANGLES.keys()), default=["Conjunction", "Square", "Trine", "Opposition"])

    if st.button(L["calculate"], type="primary"):
        # Calc logic
        try:
            bt_h, bt_m = map(int, b_time.split(':'))
            local_birth = pytz.timezone(sel_tz).localize(datetime.datetime(b_date.year, b_date.month, b_date.day, bt_h, bt_m))
            birth_utc = local_birth.astimezone(pytz.UTC)
            birth_jd = datetime_to_jd(birth_utc)
            chosen_ids = [p for p in ALL_PLANETS if p[1] in sel_planets]
            natal_pos = {pid: get_planet_position(birth_jd, pid) for pid, _ in chosen_ids}
            
            # Calculate Natal Houses (Placidus)
            # swe.houses returns (cusps, ascmc)
            # cusps is a tuple of 13 floats (0..12), where 1-12 are the houses.
            # lat/lon must be floats.
            
            # Get coords from... wait, the UI code for location is minimal here.
            # In original code, there were no lat/lon inputs visible in sidebar!
            # Let's check sidebar again or add default/placeholder if missing.
            # Ah, the original code had:
            # b_date = st.date_input...
            # b_time = st.text_input...
            # tz_list...
            # No lat/lon inputs in the original file view!
            # We need to ADD lat/lon inputs or use a default since houses require location.
            # Let's add them to sidebar inside the 'try' block for now or assume Moscow default if not present?
            # Better to add inputs. But for this specific replacement chunk, let's assume we add them or default variables.
            # Let's add hardcoded default for now if variables aren't there, OR properly add inputs in a separate chunk.
            # Looking at lines 211-216, only date/time/tz.
            # I should probably add lat/lon inputs in a separate chunk. 
            # For now, I will use a default (Moscow) to make it work without breaking, 
            # OR better, I will assume variables `lat`, `lon` are available or just use 55.75, 37.61 (Moscow) for prototype
            # as the user didn't ask for full location picker yet.
            # Actually, let's use the TZ to key off a city? No, that's imprecise.
            # Attempt to calc houses (using lat/lon from sidebar)
            natal_cusps, ascmc = swe.houses(birth_jd, lat, lon, b'P')
            
            st.session_state['natal_pos'] = natal_pos # Store for dynamic chart
            st.session_state['orb_val'] = orb_val
            
            with st.spinner("Анализ звездного неба..."):
                # Use 1 hour step for better precision (especially for Moon)
                # UPDATED CALL: passing natal_cusps
                df = calculate_transits(s_date, e_date, 1, natal_pos, chosen_ids, sel_aspects, orb_val, natal_cusps)
                
            if not df.empty:
                # Convert active times to User's selected timezone
                user_tz = pytz.timezone(sel_tz)
                df["start"] = df["start"].dt.tz_convert(user_tz)
                df["end"] = df["end"].dt.tz_convert(user_tz)

                df["duration"] = (df["end"] - df["start"]).dt.total_seconds() / 3600
                
                # Filter by minimum duration
                if min_duration > 0:
                    df = df[df["duration"] >= min_duration]
                
                if not df.empty:
                    df["score"] = df.apply(lambda row: calculate_peak_score(row["transiting"], row["aspect"]), axis=1)
                    df["label"] = df["transiting"] + " " + df["aspect"] + " " + df["natal"]
                    st.session_state['data'] = df
                else:
                     st.session_state['data'] = pd.DataFrame()
            else:
                st.session_state['data'] = pd.DataFrame() # Empty but defined
        except ValueError as e:
            st.error(f"{L.get('time_error', 'Time error')}: {e}")

# Main Screen
st.title("AstroPulse")

# Donation Button (Prominent at the top)
st.link_button(L["donate"], "https://boosty.to/aodelski/donate", type="primary", use_container_width=True)

if 'data' in st.session_state and st.session_state['data'] is not None and not st.session_state['data'].empty:
    df = st.session_state['data']
    natal_pos = st.session_state.get('natal_pos', {})
    orb_val = st.session_state.get('orb_val', 3.0)

    # 1. GOLD PULSE CHART (Снизу, пульсирующая)
    st.subheader(L["energy_pulse_chart"])
    
    pulse_idx = pd.date_range(start=pd.Timestamp(s_date).tz_localize("UTC"), end=pd.Timestamp(e_date).tz_localize("UTC"), freq="4H")
    
    # NEW: Dynamic calculation per point
    pulse_values = []
    
    for i, t in enumerate(pulse_idx):
        # Find active aspects at this time
        active = df[(df["start"] <= t) & (df["end"] > t)]
        score_sum = 0
        if not active.empty:
            for _, row in active.iterrows():
                score_sum += get_dynamic_score(
                    t, row["transiting"], row["natal"], row["aspect"], 
                    natal_pos, orb_val
                )
        pulse_values.append(score_sum)
    
    # Smooth data for "organic" feel
    smooth_y = pd.Series(pulse_values).rolling(window=3, center=True, min_periods=1).mean().fillna(0)

    fig_pulse = go.Figure()

    # -- 1. Outer Glow --
    fig_pulse.add_trace(go.Scatter(
        x=pulse_idx, y=smooth_y, mode='lines',
        line=dict(color='rgba(255, 215, 0, 0.1)', width=20, shape='spline'),
        hoverinfo='skip', showlegend=False
    ))
    
    # -- 2. Inner Glow --
    fig_pulse.add_trace(go.Scatter(
        x=pulse_idx, y=smooth_y, mode='lines',
        line=dict(color='rgba(255, 215, 0, 0.4)', width=8, shape='spline'),
        hoverinfo='skip', showlegend=False
    ))

    # -- 3. Core Line --
    fig_pulse.add_trace(go.Scatter(
        x=pulse_idx, y=smooth_y, mode='lines',
        line=dict(color='#FFD700', width=2, shape='spline'),
        fill='tozeroy', fillcolor='rgba(255, 215, 0, 0.05)',
        name=L.get("energy", "Energy")
    ))

    # -- 4. "Pulsating" Markers on Peaks --
    threshold = smooth_y.max() * 0.7 if len(smooth_y) > 0 else 0
    high_energy_x = []
    high_energy_y = []
    if threshold > 0:
        for i, val in enumerate(smooth_y):
            if abs(val) > abs(threshold):
                high_energy_x.append(pulse_idx[i])
                high_energy_y.append(val)
    
    if high_energy_x:
        fig_pulse.add_trace(go.Scatter(
            x=high_energy_x, y=high_energy_y, mode='markers',
            marker=dict(size=12, color='#FFFFFF', line=dict(color='#FFD700', width=2), symbol='diamond-open'),
            hoverinfo='skip', showlegend=False
        ))

    fig_pulse.add_hline(y=0, line_color="#444", line_dash="dash")
    
    fig_pulse.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=350, margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor='#333', zeroline=False),
        hovermode="x unified"
    )
    st.plotly_chart(fig_pulse, use_container_width=True)

    # 2. TIMELINE (GANTT) - График событий
    st.subheader(L["aspect_timeline"])
    
    # Create simplified label for Y-axis (Planet Pair only) to group rows
    df["pair_label"] = df["transiting"] + " -> " + df["natal"]
    
    fig_gantt = px.timeline(
        df, x_start="start", x_end="end", y="pair_label", color="aspect",
        color_discrete_map=ASPECT_COLORS_MAP,
        hover_data=["label", "score"],
        opacity=0.9, # Solid lines
        title=L["aspect_timeline"]
    )
    
    # Calculate dynamic height based on unique pairs (not aspects!)
    n_rows = len(df["pair_label"].unique())
    
    fig_gantt.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=max(300, n_rows * 40), margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='top'),
        yaxis=dict(title="", autorange="reversed", showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

    # 3. INTERPRETATIONS (Интеллектуальная часть)
    st.markdown("---")
    st.subheader(f"🔮 {L['planet_influences']}")
    
    # Фильтруем и сортируем аспекты по силе влияния (модуль score)
    df['abs_score'] = df['score'].abs()
    top_aspects = df.sort_values('abs_score', ascending=False) # Показываем все аспекты

    for idx, row in top_aspects.iterrows():
        t_planet = row['transiting']
        n_planet = row['natal']
        aspect = row['aspect']
        score = row['score']
        
        # Получаем дома (если есть)
        t_house = int(row.get('t_house', 0))
        n_house = int(row.get('n_house', 0))
        
        # Получаем текст (теперь передаем дома + язык)
        text = get_interpretation(t_planet, aspect, n_planet, t_house, n_house, lang=st.session_state.lang)
        rarity_label = get_planet_rarity(t_planet, lang=st.session_state.lang)
        
        t_house_str = f" ({L['transit_house']}: {t_house} {L['house']})" if t_house else ""
        n_house_str = f" ({L['natal_house']}: {n_house} {L['house']})" if n_house else ""
        
        # Определяем стиль CSS и иконки
        css_class = "bad-aspect" if score < -0.5 else "good-aspect" if score > 0.5 else "interpretation-card"
        icon = "⚡" if score < -0.5 else "✨" if score > 0.5 else "⚪"
        
        # Формируем HTML для бейджа редкости
        rarity_html = ""
        if rarity_label:
            rarity_html = f'<span style="background-color:rgba(255, 215, 0, 0.2); color:#FFD700; padding:2px 8px; border-radius:10px; font-size:0.8em; margin-left:10px;">{rarity_label}</span>'

        st.markdown(f"""
        <div class="interpretation-card {css_class}">
            <h4 style="margin:0; color:white;">{t_planet}{t_house_str} {aspect} {n_planet}{n_house_str} {icon} {rarity_html}</h4>
            <p style="color:#aaa; font-size:0.9em; margin-bottom:5px;">
                {row['start'].strftime('%d.%m')} — {row['end'].strftime('%d.%m')}
            </p>
            <p style="font-size:1.05em;">{text}</p>
        </div>
        """, unsafe_allow_html=True)

elif 'data' in st.session_state and (st.session_state['data'] is None or st.session_state['data'].empty):
     if st.session_state.get('data') is not None and st.session_state['data'].empty:
         st.warning(L["no_aspects_found"])
     else:
         st.info(L["calculate_to_see"])
else:
    st.info(L["calculate_to_see"])
