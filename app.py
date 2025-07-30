import streamlit as st
import swisseph as swe
from datetime import datetime, timezone, timedelta
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

# --- 定数定義 ---

# 日本語フォントファイル名
JP_FONT_FILE = "ipaexg.ttf"

# Matplotlibの日本語フォント設定
jp_font_path = None
if os.path.exists(JP_FONT_FILE):
    jp_font_path = JP_FONT_FILE
else:
    font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font_path in font_paths:
        if 'ipaexg' in font_path or 'IPAexGothic' in font_path:
            jp_font_path = font_path
            break

if jp_font_path:
    font_prop = fm.FontProperties(fname=jp_font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    plt.rcParams['font.family'] = 'sans-serif'


# サイン (星座)
SIGN_NAMES = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
DEGREES_PER_SIGN = 30
ZODIAC_DEGREES = 360

# 天体
PLANET_NAMES = {
    "太陽": swe.SUN, "月": swe.MOON, "水星": swe.MERCURY, "金星": swe.VENUS, "火星": swe.MARS,
    "木星": swe.JUPITER, "土星": swe.SATURN, "天王星": swe.URANUS, "海王星": swe.NEPTUNE,
    "冥王星": swe.PLUTO, "キロン": swe.CHIRON, "リリス": swe.MEAN_APOG,
    "ドラゴンヘッド": swe.MEAN_NODE
}
PLANET_SYMBOLS = {
    "太陽": "☉", "月": "☽", "水星": "☿", "金星": "♀", "火星": "♂", "木星": "♃", "土星": "♄",
    "天王星": "♅", "海王星": "♆", "冥王星": "♇", "キロン": "⚷", "リリス": "⚸",
    "ドラゴンヘッド": "☊", "ドラゴンテイル": "☋", "ASC": "ASC", "MC": "MC"
}
PLANET_COLORS = {
    "太陽": "gold", "月": "silver", "水星": "lightgrey", "金星": "hotpink", "火星": "red",
    "木星": "orange", "土星": "saddlebrown", "天王星": "cyan", "海王星": "blue",
    "冥王星": "darkviolet", "キロン": "green", "リリス": "black",
    "ドラゴンヘッド": "gray", "ドラゴンテイル": "gray"
}
LUMINARIES = [swe.SUN, swe.MOON]
SENSITIVE_POINTS = ["ASC", "MC"]

# アスペクト
ASPECTS = {
    "コンジャンクション (0°)": {"angle": 0, "orb": 8},
    "オポジション (180°)": {"angle": 180, "orb": 8},
    "トライン (120°)": {"angle": 120, "orb": 8},
    "スクエア (90°)": {"angle": 90, "orb": 7},
    "セクスタイル (60°)": {"angle": 60, "orb": 4},
}

# 都道府県データ
PREFECTURE_DATA = {
    "北海道": {"lat": 43.064, "lon": 141.348}, "青森県": {"lat": 40.825, "lon": 140.741},
    "岩手県": {"lat": 39.704, "lon": 141.153}, "宮城県": {"lat": 38.269, "lon": 140.872},
    "秋田県": {"lat": 39.719, "lon": 140.102}, "山形県": {"lat": 38.240, "lon": 140.364},
    "福島県": {"lat": 37.750, "lon": 140.468}, "茨城県": {"lat": 36.342, "lon": 140.447},
    "栃木県": {"lat": 36.566, "lon": 139.884}, "群馬県": {"lat": 36.391, "lon": 139.060},
    "埼玉県": {"lat": 35.857, "lon": 139.649}, "千葉県": {"lat": 35.605, "lon": 140.123},
    "東京都": {"lat": 35.690, "lon": 139.692}, "神奈川県": {"lat": 35.448, "lon": 139.643},
    "新潟県": {"lat": 37.902, "lon": 139.023}, "富山県": {"lat": 36.695, "lon": 137.211},
    "石川県": {"lat": 36.594, "lon": 136.626}, "福井県": {"lat": 36.065, "lon": 136.222},
    "山梨県": {"lat": 35.664, "lon": 138.568}, "長野県": {"lat": 36.651, "lon": 138.181},
    "岐阜県": {"lat": 35.391, "lon": 136.722}, "静岡県": {"lat": 34.977, "lon": 138.383},
    "愛知県": {"lat": 35.180, "lon": 136.907}, "三重県": {"lat": 34.730, "lon": 136.509},
    "滋賀県": {"lat": 35.005, "lon": 135.869}, "京都府": {"lat": 35.021, "lon": 135.756},
    "大阪府": {"lat": 34.686, "lon": 135.520}, "兵庫県": {"lat": 34.691, "lon": 135.183},
    "奈良県": {"lat": 34.685, "lon": 135.833}, "和歌山県": {"lat": 34.226, "lon": 135.168},
    "鳥取県": {"lat": 35.504, "lon": 134.238}, "島根県": {"lat": 35.472, "lon": 133.051},
    "岡山県": {"lat": 34.662, "lon": 133.934}, "広島県": {"lat": 34.396, "lon": 132.459},
    "山口県": {"lat": 34.186, "lon": 131.471}, "徳島県": {"lat": 34.066, "lon": 134.559},
    "香川県": {"lat": 34.340, "lon": 134.043}, "愛媛県": {"lat": 33.842, "lon": 132.765},
    "高知県": {"lat": 33.560, "lon": 133.531}, "福岡県": {"lat": 33.607, "lon": 130.418},
    "佐賀県": {"lat": 33.249, "lon": 130.299}, "長崎県": {"lat": 32.745, "lon": 129.874},
    "熊本県": {"lat": 32.790, "lon": 130.742}, "大分県": {"lat": 33.238, "lon": 131.613},
    "宮崎県": {"lat": 31.911, "lon": 131.424}, "鹿児島県": {"lat": 31.560, "lon": 130.558},
    "沖縄県": {"lat": 26.212, "lon": 127.681}
}

# --- ヘルパー関数 ---
def get_degree_parts(d):
    d %= 360
    sign_index = int(d / DEGREES_PER_SIGN)
    pos_in_sign = d % DEGREES_PER_SIGN
    return SIGN_NAMES[sign_index], f"{int(pos_in_sign):02d}°{int((pos_in_sign - int(pos_in_sign)) * 60):02d}'"

def get_house_number(degree, cusps):
    cusps_with_13th = list(cusps) + [(cusps[0] + 360) % 360]
    for i in range(12):
        start, end = cusps[i], cusps_with_13th[i+1]
        if start > end:
            if degree >= start or degree < end: return i + 1
        else:
            if start <= degree < end: return i + 1
    return 12

# --- 計算関数 ---
def calculate_celestial_data(dt_utc, lat, lon):
    ephe_path = 'ephe'
    if not os.path.exists(ephe_path):
        st.error(f"天体暦ファイルが見つかりません。'{ephe_path}' フォルダをアプリのルートに配置してください。")
        return None, None, None
    swe.set_ephe_path(ephe_path)
    jd_ut, _ = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second, 1)
    celestial_bodies = {}
    iflag = swe.FLG_SWIEPH | swe.FLG_SPEED
    for name, p_id in PLANET_NAMES.items():
        res = swe.calc_ut(jd_ut, p_id, iflag)
        celestial_bodies[name] = {'id': p_id, 'pos': res[0][0], 'is_retro': res[0][3] < 0}
    head_pos = celestial_bodies["ドラゴンヘッド"]['pos']
    celestial_bodies["ドラゴンテイル"] = {'id': -1, 'pos': (head_pos + 180) % 360, 'is_retro': False}
    try:
        cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P')
        celestial_bodies["ASC"] = {'id': 'ASC', 'pos': ascmc[0], 'is_retro': False}
        celestial_bodies["MC"] = {'id': 'MC', 'pos': ascmc[1], 'is_retro': False}
        return celestial_bodies, cusps, ascmc
    except swe.Error as e:
        st.warning(f"ハウスが計算できませんでした: {e}")
        return celestial_bodies, None, None

def calculate_aspects_dict(celestial_bodies):
    aspect_dict = {name: [] for name in ASPECTS.keys()}
    all_points = list(celestial_bodies.keys())
    for i in range(len(all_points)):
        for j in range(i + 1, len(all_points)):
            p1_name, p2_name = all_points[i], all_points[j]
            p1, p2 = celestial_bodies[p1_name], celestial_bodies[p2_name]
            angle_diff = abs(p1['pos'] - p2['pos'])
            if angle_diff > 180: angle_diff = 360 - angle_diff
            for aspect_name, params in ASPECTS.items():
                orb = params['orb']
                if p1.get('id') in LUMINARIES or p2.get('id') in LUMINARIES: orb += 2
                current_orb = abs(angle_diff - params['angle'])
                if current_orb < orb:
                    name1 = p1_name if p1_name in ["ASC", "MC"] else f"{PLANET_SYMBOLS.get(p1_name, '')} {p1_name}"
                    name2 = p2_name if p2_name in ["ASC", "MC"] else f"{PLANET_SYMBOLS.get(p2_name, '')} {p2_name}"
                    aspect_string = f"{name1} - {name2} (オーブ {current_orb:.2f}°)"
                    aspect_dict[aspect_name].append(aspect_string)
    return aspect_dict

# --- 描画関数 ---
def create_horoscope_chart(celestial_bodies, cusps, ascmc):
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(1)
    ax.set_rlim(0, 10)
    ax.spines['polar'].set_visible(False)
    ax.set_thetagrids([], [])
    ax.set_rgrids([], [])

    rotation_offset = 180 - ascmc[0]
    def apply_rotation(pos): return (pos + rotation_offset) % 360

    # 1. サインの円
    radius_sign = 9.5
    for i in range(12):
        start_deg, end_deg = apply_rotation(i * 30), apply_rotation((i + 1) * 30)
        mid_deg = apply_rotation(i * 30 + 15)
        start_angle, end_angle, mid_angle = np.deg2rad(start_deg), np.deg2rad(end_deg), np.deg2rad(mid_deg)
        color = "aliceblue" if i % 2 == 0 else "white"
        if start_deg > end_deg:
            ax.fill_between(np.linspace(start_angle, 2 * np.pi, 50), radius_sign - 1.5, radius_sign, color=color, zorder=0)
            ax.fill_between(np.linspace(0, end_angle, 50), radius_sign - 1.5, radius_sign, color=color, zorder=0)
        else:
            ax.fill_between(np.linspace(start_angle, end_angle, 100), radius_sign - 1.5, radius_sign, color=color, zorder=0)
        ax.plot([start_angle, start_angle], [radius_sign - 1.5, radius_sign], color='lightgray', linewidth=1)
        ax.text(mid_angle, radius_sign - 0.7, SIGN_SYMBOLS[i], ha='center', va='center', fontsize=20, zorder=2)

    # 2. ハウスのカスプ
    radius_house_num = 6.5
    for i, cusp_deg in enumerate(cusps):
        angle = np.deg2rad(apply_rotation(cusp_deg))
        ax.plot([angle, angle], [0, radius_sign - 1.5],
                color='gray', linestyle='--', linewidth=1, zorder=1)
        next_cusp_deg = cusps[(i + 1) % 12]
        mid_angle_deg = cusp_deg + (((next_cusp_deg - cusp_deg) + 360) % 360) / 2
        mid_angle_rad = np.deg2rad(apply_rotation(mid_angle_deg))
        ax.text(mid_angle_rad, radius_house_num, str(i + 1), ha='center', va='center', fontsize=12, color='gray', zorder=2)

    # 3. 天体
    radius_planet_base, radius_step = 7.8, 0.9
    planets_to_plot = {name: data for name, data in celestial_bodies.items() if name not in SENSITIVE_POINTS}
    sorted_planets = sorted(planets_to_plot.items(), key=lambda item: apply_rotation(item[1]['pos']))
    plot_info = {}
    last_angle_deg = -999
    last_radius = radius_planet_base
    for name, data in sorted_planets:
        angle_deg = apply_rotation(data['pos'])
        angle_diff = (angle_deg - last_angle_deg + 360) % 360
        current_radius = radius_planet_base
        if angle_diff < 15: # 重なり判定の角度を広げる
            if last_radius == radius_planet_base:
                current_radius = radius_planet_base - radius_step
            else:
                current_radius = radius_planet_base
        plot_info[name] = {'angle': np.deg2rad(angle_deg), 'radius': current_radius}
        last_angle_deg = angle_deg
        last_radius = current_radius
        
    for name, data in celestial_bodies.items():
        if name in plot_info:
            info = plot_info[name]
            ax.text(info['angle'], info['radius'], PLANET_SYMBOLS[name], ha='center', va='center', fontsize=16, color=PLANET_COLORS[name], weight='bold', zorder=5)
            pos_in_sign = data['pos'] % 30
            ax.text(info['angle'], info['radius'] - 0.8, f"{int(pos_in_sign)}°{int((pos_in_sign - int(pos_in_sign)) * 60):02d}'{' R' if data.get('is_retro') else ''}", ha='center', va='top', fontsize=8, zorder=4)

    return fig

# --- Streamlit UI ---
st.set_page_config(page_title="ホロスコープ作成アプリ", page_icon="🪐", layout="wide")
st.title("🪐 ホロスコープ作成アプリ")
st.write("生年月日、出生時刻、出生地（都道府県）を入力して、あなたのホロスコープを作成します。")

with st.sidebar:
    st.header("出生情報を入力")
    birth_date = st.date_input("📅 生年月日", datetime(1990, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime(2099, 12, 31))
    birth_time_str = st.text_input("⏰ 出生時刻 (HH:MM)", "12:00")
    prefecture = st.selectbox("📍 出生地（都道府県）", PREFECTURE_DATA.keys(), index=12)
    is_ready = st.button("ホロスコープを作成する", type="primary")

if is_ready:
    try:
        birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
        dt_local = datetime.combine(birth_date, birth_time)
        dt_utc = dt_local.replace(tzinfo=timezone(timedelta(hours=9))).astimezone(timezone.utc)
        lat, lon = PREFECTURE_DATA[prefecture]["lat"], PREFECTURE_DATA[prefecture]["lon"]
        st.header(f"{dt_local.strftime('%Y年%m月%d日 %H:%M')} 生まれ ({prefecture})")
        with st.spinner("ホロスコープを計算中..."):
            celestial_bodies, cusps, ascmc = calculate_celestial_data(dt_utc, lat, lon)
        if celestial_bodies and cusps:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("ホロスコープチャート")
                with st.spinner("チャートを描画中..."):
                    fig = create_horoscope_chart(celestial_bodies, cusps, ascmc)
                    st.pyplot(fig)
            with col2:
                st.subheader("天体位置リスト")
                planet_data = []
                for name, data in celestial_bodies.items():
                    sign, deg_str = get_degree_parts(data['pos'])
                    retro = "R" if data.get('is_retro') else ""
                    house = get_house_number(data['pos'], cusps) if cusps else "-"
                    
                    # ASC/MCの重複表記を修正
                    name_str = name if name in ["ASC", "MC"] else f"{PLANET_SYMBOLS.get(name, '')} {name}"
                    
                    planet_data.append([
                        name_str,
                        sign,
                        deg_str,
                        retro,
                        house
                    ])
                
                df = pd.DataFrame(
                    planet_data,
                    columns=["天体/感受点", "サイン", "度数", "逆行", "ハウス"]
                )
                
                # DataFrameを中央揃えで表示
                st.dataframe(
                    df.style.set_properties(**{'text-align': 'center'}),
                    hide_index=True,
                    use_container_width=True
                )

                st.subheader("アスペクトリスト")
                with st.spinner("アスペクトを計算中..."):
                    aspects_by_type = calculate_aspects_dict(celestial_bodies)
                
                has_any_aspect = any(aspects_by_type.values())
                if has_any_aspect:
                    for aspect_name, aspect_list in aspects_by_type.items():
                        if aspect_list:
                            short_name = aspect_name.split(" ")[0]
                            with st.expander(f"{short_name} ({len(aspect_list)})"):
                                for aspect_string in aspect_list:
                                    st.text(f"・{aspect_string}")
                else:
                    st.info("設定されたオーブ内に主要なアスペクトは見つかりませんでした。")

        else:
            st.error("データの計算に失敗しました。入力時刻が高緯度などの理由でハウス分割できない可能性があります。")
    except ValueError:
        st.error("時刻の形式が正しくありません。「HH:MM」（例: 16:29）の形式で入力してください。")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
