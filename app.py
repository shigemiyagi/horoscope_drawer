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

# 日本語フォントファイル名 (適宜変更してください)
JP_FONT_FILE = "ipaexg.ttf"

# Matplotlibの日本語フォント設定
try:
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
        # フォントが見つからない場合は、システムデフォルトのゴシック体を使用
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'TakaoPGothic', 'sans-serif']
        st.warning("IPAexゴシックフォントが見つかりませんでした。システムのデフォルトフォントで描画します。文字化けする場合は、`JP_FONT_FILE`に有効なフォントパスを指定してください。")

except Exception as e:
    st.error(f"フォント設定中にエラーが発生しました: {e}")


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
    "ドラゴンヘッド": "gray", "ドラゴンテイル": "gray",
    "ASC": "black", "MC": "black"
}
LUMINARIES = [swe.SUN, swe.MOON]
SENSITIVE_POINTS = ["ASC", "MC"]

# アスペクト
ASPECTS = {
    "コンジャンクション (0°)": {"angle": 0, "orb": 8, "symbol": "☌", "color": "blue"},
    "オポジション (180°)": {"angle": 180, "orb": 8, "symbol": "☍", "color": "red"},
    "トライン (120°)": {"angle": 120, "orb": 8, "symbol": "△", "color": "green"},
    "スクエア (90°)": {"angle": 90, "orb": 7, "symbol": "□", "color": "red"},
    "セクスタイル (60°)": {"angle": 60, "orb": 4, "symbol": "✶", "color": "green"},
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
    """度数を星座と度数表記に変換する"""
    d %= 360
    sign_index = int(d / DEGREES_PER_SIGN)
    pos_in_sign = d % DEGREES_PER_SIGN
    return SIGN_NAMES[sign_index], f"{int(pos_in_sign):02d}°{int((pos_in_sign - int(pos_in_sign)) * 60):02d}'"

def get_house_number(degree, cusps):
    """天体の度数からハウス番号を特定する"""
    cusps_with_13th = list(cusps) + [(cusps[0] + 360) % 360]
    for i in range(12):
        start, end = cusps[i], cusps_with_13th[i+1]
        if start > end: # 0度をまたぐハウス
            if degree >= start or degree < end: return i + 1
        else:
            if start <= degree < end: return i + 1
    return 12

# --- 計算関数 ---
def _calculate_celestial_bodies(jd_ut, lat, lon, calc_houses=False):
    """指定されたユリウス日の天体情報を計算する内部関数"""
    celestial_bodies = {}
    iflag = swe.FLG_SWIEPH | swe.FLG_SPEED
    for name, p_id in PLANET_NAMES.items():
        res = swe.calc_ut(jd_ut, p_id, iflag)
        celestial_bodies[name] = {'id': p_id, 'pos': res[0][0], 'is_retro': res[0][3] < 0}
    
    head_pos = celestial_bodies["ドラゴンヘッド"]['pos']
    celestial_bodies["ドラゴンテイル"] = {'id': -1, 'pos': (head_pos + 180) % 360, 'is_retro': False}

    if calc_houses:
        try:
            cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P')
            celestial_bodies["ASC"] = {'id': 'ASC', 'pos': ascmc[0], 'is_retro': False}
            celestial_bodies["MC"] = {'id': 'MC', 'pos': ascmc[1], 'is_retro': False}
            return celestial_bodies, cusps, ascmc
        except swe.Error as e:
            st.warning(f"ハウスが計算できませんでした: {e}")
            return celestial_bodies, None, None
    return celestial_bodies, None, None


def calculate_all_data(dt_utc, lat, lon):
    """ネイタル、プログレス、トランジットの全データを計算する"""
    ephe_path = 'ephe'
    if not os.path.exists(ephe_path):
        st.error(f"天体暦ファイルが見つかりません。'{ephe_path}' フォルダをアプリのルートに配置してください。")
        return None, None, None, None, None
    swe.set_ephe_path(ephe_path)

    # 1. ネイタル計算
    jd_ut_natal, _ = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second, 1)
    natal_bodies, cusps, ascmc = _calculate_celestial_bodies(jd_ut_natal, lat, lon, calc_houses=True)
    if not cusps: # ハウス計算失敗時は中止
        return None, None, None, None, None

    # 2. プログレス計算 (一日一年法) - 修正箇所
    # 満年齢を日数で計算
    age_in_days = (datetime.now(timezone.utc) - dt_utc).days
    # 経過年数を計算 (正確性のため)
    age_in_years = age_in_days / 365.2425
    # プログレスの日付を計算 (出生日 + 経過年数に相当する日数)
    prog_dt_utc = dt_utc + timedelta(days=age_in_years)
    jd_ut_prog, _ = swe.utc_to_jd(prog_dt_utc.year, prog_dt_utc.month, prog_dt_utc.day, prog_dt_utc.hour, prog_dt_utc.minute, prog_dt_utc.second, 1)
    progressed_bodies, _, _ = _calculate_celestial_bodies(jd_ut_prog, lat, lon)

    # 3. トランジット計算
    transit_dt_utc = datetime.now(timezone.utc)
    jd_ut_transit, _ = swe.utc_to_jd(transit_dt_utc.year, transit_dt_utc.month, transit_dt_utc.day, transit_dt_utc.hour, transit_dt_utc.minute, transit_dt_utc.second, 1)
    transit_bodies, _, _ = _calculate_celestial_bodies(jd_ut_transit, lat, lon)

    return natal_bodies, progressed_bodies, transit_bodies, cusps, ascmc

def calculate_natal_aspects(celestial_bodies):
    """ネイタルチャート内のアスペクトを計算する"""
    aspect_list = []
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
                    aspect_list.append({
                        "p1_name": p1_name, "p2_name": p2_name,
                        "p1_pos": p1['pos'], "p2_pos": p2['pos'],
                        "aspect_name": aspect_name, "orb": current_orb,
                        "params": params
                    })
    return aspect_list

# --- 描画関数 ---
def _plot_planets_on_circle(ax, bodies, radius, rotation_offset, label, label_color='black'):
    """指定された半径の円周上に天体をプロットする内部関数"""
    # 円を描画
    circle = plt.Circle((0, 0), radius, transform=ax.transData._b, color='lightgray', fill=False, linestyle='--', linewidth=0.5)
    ax.add_artist(circle)

    # ラベルをプロット
    ax.text(np.deg2rad(rotation_offset + 90), radius, label,
            ha='center', va='center', fontsize=10, color=label_color,
            bbox=dict(boxstyle="round,pad=0.3", fc='white', ec="none", alpha=0.8))

    # 天体をプロット
    plot_info = {}
    # SENSITIVE_POINTSを除外してソート
    planets_to_plot = {name: data for name, data in bodies.items() if name not in SENSITIVE_POINTS}
    sorted_planets = sorted(planets_to_plot.items(), key=lambda item: item[1]['pos'])
    
    # 衝突回避のための簡易的なロジック
    last_angle_deg = -999
    last_radius_offset = 0
    radius_step = 0.6 # 天体が近い場合にずらす半径

    for name, data in sorted_planets:
        angle_deg = (data['pos'] + rotation_offset) % 360
        angle_rad = np.deg2rad(angle_deg)
        
        # 角度が近い場合に半径をずらす
        angle_diff = (angle_deg - last_angle_deg + 360) % 360
        current_radius_offset = 0
        if angle_diff < 15:
            current_radius_offset = last_radius_offset - radius_step if last_radius_offset >= 0 else last_radius_offset + radius_step
            if abs(current_radius_offset) > radius_step * 2 : current_radius_offset = 0 # 3つ以上重なったらリセット
        
        plot_info[name] = {'angle': angle_rad, 'radius': radius + current_radius_offset}
        last_angle_deg = angle_deg
        last_radius_offset = current_radius_offset

    for name, data in bodies.items():
        if name in plot_info:
            info = plot_info[name]
            ax.text(info['angle'], info['radius'], PLANET_SYMBOLS[name], ha='center', va='center', fontsize=14,
                    color=PLANET_COLORS.get(name, 'black'), weight='bold', zorder=15)
            pos_in_sign = data['pos'] % 30
            retro_str = ' R' if data.get('is_retro') else ''
            ax.text(info['angle'], info['radius'] - 0.5, f"{int(pos_in_sign):02d}{retro_str}",
                    ha='center', va='top', fontsize=7, zorder=14)


def create_tri_chart(natal, prog, trans, cusps, ascmc, aspects):
    """三重円ホロスコープチャートを作成する"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(1)
    ax.set_rlim(0, 10)
    ax.spines['polar'].set_visible(False)
    ax.set_thetagrids([], [])
    ax.set_rgrids([], [])

    # ASCが左側(180度)に来るようにチャート全体を回転
    rotation_offset = 180 - ascmc[0]
    def apply_rotation(pos): return (pos + rotation_offset) % 360

    # 1. サインの円 (一番外側)
    radius_sign = 9.5
    for i in range(12):
        start_deg, end_deg = apply_rotation(i * 30), apply_rotation((i + 1) * 30)
        mid_deg = apply_rotation(i * 30 + 15)
        start_angle, end_angle, mid_angle = np.deg2rad(start_deg), np.deg2rad(end_deg), np.deg2rad(mid_deg)
        color = "aliceblue" if i % 2 == 0 else "white"
        
        # 0度をまたぐ描画の補正
        if start_deg > end_deg:
            ax.fill_between(np.linspace(start_angle, 2 * np.pi, 50), radius_sign - 1, radius_sign, color=color, zorder=0)
            ax.fill_between(np.linspace(0, end_angle, 50), radius_sign - 1, radius_sign, color=color, zorder=0)
        else:
            ax.fill_between(np.linspace(start_angle, end_angle, 100), radius_sign - 1, radius_sign, color=color, zorder=0)
        
        ax.plot([start_angle, start_angle], [radius_sign - 1, radius_sign], color='lightgray', linewidth=1)
        ax.text(mid_angle, radius_sign - 0.5, SIGN_SYMBOLS[i], ha='center', va='center', fontsize=20, zorder=2)

    # 2. ハウスのカスプとASC/MC
    radius_house_num = 3.5
    for i, cusp_deg in enumerate(cusps):
        angle = np.deg2rad(apply_rotation(cusp_deg))
        is_ascmc_line = (i == 0 or i == 9) # ASC(1室) or MC(10室)
        ax.plot([angle, angle], [0, radius_sign - 1],
                color='black' if is_ascmc_line else 'gray',
                linestyle='-' if is_ascmc_line else '--',
                linewidth=1.5 if is_ascmc_line else 1, zorder=5)
        
        next_cusp_deg = cusps[(i + 1) % 12]
        mid_angle_deg = cusp_deg + (((next_cusp_deg - cusp_deg) + 360) % 360) / 2
        mid_angle_rad = np.deg2rad(apply_rotation(mid_angle_deg))
        ax.text(mid_angle_rad, radius_house_num, str(i + 1), ha='center', va='center', fontsize=12, color='gray', zorder=6)
    
    # ASC/MCラベル
    ax.text(np.deg2rad(apply_rotation(ascmc[0])), radius_sign-1.2, "ASC", ha='right', va='center', fontsize=12, weight='bold', color='black')
    ax.text(np.deg2rad(apply_rotation(ascmc[1])), radius_sign-1.2, "MC", ha='center', va='bottom', fontsize=12, weight='bold', color='black')

    # 3. アスペクトライン (ネイタル)
    for aspect in aspects:
        p1_angle = np.deg2rad(apply_rotation(aspect['p1_pos']))
        p2_angle = np.deg2rad(apply_rotation(aspect['p2_pos']))
        ax.plot([p1_angle, p2_angle], [4.2, 4.2], color=aspect['params']['color'],
                linestyle='-', linewidth=1, zorder=3)

    # 4. 天体を三重円でプロット
    _plot_planets_on_circle(ax, trans, 8.0, rotation_offset, "Transit", "blue")
    _plot_planets_on_circle(ax, prog, 6.2, rotation_offset, "Progressed", "green")
    _plot_planets_on_circle(ax, natal, 4.4, rotation_offset, "Natal", "red")
    
    return fig

# --- Streamlit UI ---
st.set_page_config(page_title="三重円ホロスコープ作成", page_icon="🪐", layout="wide")
st.title("🪐 三重円ホロスコープ作成アプリ")
st.write("ネイタル（内円）、プログレス（中円）、トランジット（外円）の三重円ホロスコープを作成します。")

with st.sidebar:
    st.header("出生情報を入力")
    birth_date = st.date_input("📅 生年月日", datetime(1990, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime.now())
    birth_time_str = st.text_input("⏰ 出生時刻 (HH:MM)", "12:00")
    prefecture = st.selectbox("📍 出生地（都道府県）", PREFECTURE_DATA.keys(), index=12)
    is_ready = st.button("ホロスコープを作成する", type="primary")

if is_ready:
    try:
        birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
        # 入力はJST(UTC+9)と仮定
        dt_local = datetime.combine(birth_date, birth_time)
        dt_utc = dt_local.replace(tzinfo=timezone(timedelta(hours=9))).astimezone(timezone.utc)
        
        lat, lon = PREFECTURE_DATA[prefecture]["lat"], PREFECTURE_DATA[prefecture]["lon"]
        
        st.header(f"{dt_local.strftime('%Y年%m月%d日 %H:%M')} 生まれ ({prefecture})")
        st.caption(f"現在時刻 (トランジット): {datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S JST')}")
        
        with st.spinner("ホロスコープを計算中..."):
            natal_bodies, prog_bodies, trans_bodies, cusps, ascmc = calculate_all_data(dt_utc, lat, lon)
            natal_aspects = calculate_natal_aspects(natal_bodies) if natal_bodies else []

        if natal_bodies and cusps:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader("ホロスコープチャート")
                with st.spinner("チャートを描画中..."):
                    fig = create_tri_chart(natal_bodies, prog_bodies, trans_bodies, cusps, ascmc, natal_aspects)
                    st.pyplot(fig)
            with col2:
                st.subheader("天体位置データ")

                tab_natal, tab_prog, tab_trans, tab_aspect = st.tabs(["ネイタル", "プログレス", "トランジット", "アスペクト"])

                with tab_natal:
                    planet_data = []
                    for name, data in natal_bodies.items():
                        sign, deg_str = get_degree_parts(data['pos'])
                        retro = "R" if data.get('is_retro') else ""
                        house = get_house_number(data['pos'], cusps) if cusps else "-"
                        name_str = f"{PLANET_SYMBOLS.get(name, '')} {name}"
                        planet_data.append([name_str, sign, deg_str, retro, house])
                    df = pd.DataFrame(planet_data, columns=["天体/感受点", "サイン", "度数", "逆行", "ハウス"])
                    st.dataframe(df, use_container_width=True)

                with tab_prog:
                    planet_data = []
                    for name, data in prog_bodies.items():
                        sign, deg_str = get_degree_parts(data['pos'])
                        retro = "R" if data.get('is_retro') else ""
                        house = get_house_number(data['pos'], cusps) if cusps else "-"
                        name_str = f"{PLANET_SYMBOLS.get(name, '')} {name}"
                        planet_data.append([name_str, sign, deg_str, retro, house])
                    df = pd.DataFrame(planet_data, columns=["天体", "サイン", "度数", "逆行", "ハウス"])
                    st.dataframe(df, use_container_width=True)

                with tab_trans:
                    planet_data = []
                    for name, data in trans_bodies.items():
                        sign, deg_str = get_degree_parts(data['pos'])
                        retro = "R" if data.get('is_retro') else ""
                        house = get_house_number(data['pos'], cusps) if cusps else "-"
                        name_str = f"{PLANET_SYMBOLS.get(name, '')} {name}"
                        planet_data.append([name_str, sign, deg_str, retro, house])
                    df = pd.DataFrame(planet_data, columns=["天体", "サイン", "度数", "逆行", "ハウス"])
                    st.dataframe(df, use_container_width=True)

                with tab_aspect:
                    st.write("ネイタル天体間のアスペクト")
                    if natal_aspects:
                        aspect_data = []
                        for aspect in sorted(natal_aspects, key=lambda x: x['orb']):
                            p1_sym = PLANET_SYMBOLS.get(aspect['p1_name'], aspect['p1_name'])
                            p2_sym = PLANET_SYMBOLS.get(aspect['p2_name'], aspect['p2_name'])
                            aspect_sym = aspect['params']['symbol']
                            aspect_data.append([
                                f"{p1_sym} - {p2_sym}",
                                aspect['aspect_name'].split(" ")[0],
                                f"{aspect['orb']:.2f}°"
                            ])
                        df_aspect = pd.DataFrame(aspect_data, columns=["天体ペア", "アスペクト", "オーブ"])
                        st.dataframe(df_aspect, use_container_width=True)
                    else:
                        st.info("設定されたオーブ内に主要なアスペクトは見つかりませんでした。")

        else:
            st.error("データの計算に失敗しました。入力時刻が高緯度などの理由でハウス分割できない可能性があります。")
    except ValueError:
        st.error("時刻の形式が正しくありません。「HH:MM」（例: 16:29）の形式で入力してください。")
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
        st.exception(e) # デバッグ用に例外の詳細を出力
