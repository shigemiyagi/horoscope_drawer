import streamlit as st
import swisseph as swe
from datetime import datetime, timezone, timedelta
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --- 定数定義 ---

# Matplotlibの日本語フォント設定
# Streamlit Cloudで利用可能な日本語フォントを指定します。
# 利用可能なフォントがない場合は、フォントファイルをリポジトリに含める必要があります。
# ここでは一般的なフォント名を試みます。
font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
# IPAフォントなど、利用可能な日本語フォントを探す
jp_font_path = None
for font_path in font_paths:
    if 'ipaexg' in font_path or 'IPAexGothic' in font_path:
        jp_font_path = font_path
        break

if jp_font_path:
    font_prop = fm.FontProperties(fname=jp_font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    # フォントが見つからない場合は警告を出す
    st.warning("日本語フォントが見つかりませんでした。チャートの文字が正しく表示されない可能性があります。")
    # 代替としてデフォルトフォントを使用
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
    "ドラゴンヘッド": "☊", "ドラゴンテイル": "☋"
}
PLANET_COLORS = {
    "太陽": "gold", "月": "silver", "水星": "lightgrey", "金星": "hotpink", "火星": "red",
    "木星": "orange", "土星": "saddlebrown", "天王星": "cyan", "海王星": "blue",
    "冥王星": "darkviolet", "キロン": "green", "リリス": "black",
    "ドラゴンヘッド": "gray", "ドラゴンテイル": "gray"
}
# 光度 (アスペクトのオーブ計算で使用)
LUMINARIES = [swe.SUN, swe.MOON]

# 感受点
SENSITIVE_POINTS = ["ASC", "MC"]

# アスペクト
ASPECTS = {
    "コンジャンクション (0°)": {"angle": 0, "orb": 8, "symbol": "☌"},
    "セクスタイル (60°)": {"angle": 60, "orb": 4, "symbol": " sextile "},
    "スクエア (90°)": {"angle": 90, "orb": 7, "symbol": "□"},
    "トライン (120°)": {"angle": 120, "orb": 8, "symbol": "△"},
    "オポジション (180°)": {"angle": 180, "orb": 8, "symbol": "☍"},
}

# 都道府県の緯度経度データ
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

def format_degree(d):
    """度数を「サイン 度数'分"」の形式に変換"""
    d = d % ZODIAC_DEGREES
    sign_index = int(d / DEGREES_PER_SIGN)
    sign_name = SIGN_NAMES[sign_index]
    pos_in_sign = d % DEGREES_PER_SIGN
    deg = int(pos_in_sign)
    minute = int((pos_in_sign - deg) * 60)
    return f"{sign_name} {deg:02d}°{minute:02d}'"

def get_house_number(degree, cusps):
    """天体の度数からハウス番号を特定する"""
    cusps_with_13th = list(cusps) + [cusps[0]]
    for i in range(12):
        start_cusp = cusps_with_13th[i]
        end_cusp = cusps_with_13th[i+1]
        if start_cusp > end_cusp: # 0度をまたぐハウス
            if degree >= start_cusp or degree < end_cusp:
                return i + 1
        else:
            if start_cusp <= degree < end_cusp:
                return i + 1
    return -1 # エラー

# --- 計算関数 ---

def calculate_celestial_data(dt_utc, lat, lon):
    """指定された日時と場所の天体・ハウス情報を計算する"""
    # swissephのパス設定
    ephe_path = 'ephe'
    if not os.path.exists(ephe_path):
        st.error(f"天体暦ファイルが見つかりません。'{ephe_path}' フォルダをアプリのルートに配置してください。")
        return None, None, None
    swe.set_ephe_path(ephe_path)

    # ユリウス日(UT)に変換
    jd_ut, _ = swe.utc_to_jd(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second,
        1 # グレゴリオ暦
    )

    celestial_bodies = {}
    iflag = swe.FLG_SWIEPH | swe.FLG_SPEED

    # 天体の位置計算
    for name, p_id in PLANET_NAMES.items():
        res = swe.calc_ut(jd_ut, p_id, iflag)
        pos = res[0][0]
        speed = res[0][3]
        celestial_bodies[name] = {'id': p_id, 'pos': pos, 'is_retro': speed < 0}

    # ドラゴンテイルの位置計算 (ヘッドの180度反対)
    head_pos = celestial_bodies["ドラゴンヘッド"]['pos']
    tail_pos = (head_pos + 180) % ZODIAC_DEGREES
    celestial_bodies["ドラゴンテイル"] = {'id': -1, 'pos': tail_pos, 'is_retro': False}

    # ハウスと感受点の計算
    try:
        cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P') # プラシーダス法
        celestial_bodies["ASC"] = {'id': 'ASC', 'pos': ascmc[0], 'is_retro': False}
        celestial_bodies["MC"] = {'id': 'MC', 'pos': ascmc[1], 'is_retro': False}
        return celestial_bodies, cusps, ascmc
    except swe.Error as e:
        st.warning(f"ハウスが計算できませんでした（高緯度など）。ASC, MC, ハウスは表示されません。詳細: {e}")
        return celestial_bodies, None, None

def calculate_aspects_list(celestial_bodies):
    """天体間のアスペクトを計算してリストで返す"""
    aspect_list = []
    # 感受点も含めたリストを作成
    all_points = list(celestial_bodies.keys())
    
    # PoFやキロン、リリス、ノード軸とのアスペクトは除外することが多いが、ここでは全て計算
    # all_points = [p for p in all_points if p not in ["キロン", "リリス", "ドラゴンヘッド", "ドラゴンテイル"]]


    for i in range(len(all_points)):
        for j in range(i + 1, len(all_points)):
            p1_name = all_points[i]
            p2_name = all_points[j]

            p1 = celestial_bodies[p1_name]
            p2 = celestial_bodies[p2_name]

            # 角度差を計算
            angle_diff = abs(p1['pos'] - p2['pos'])
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # 各アスペクトをチェック
            for aspect_name, params in ASPECTS.items():
                orb = params['orb']
                # 光度（太陽・月）が絡む場合はオーブを広く取る
                if p1.get('id') in LUMINARIES or p2.get('id') in LUMINARIES:
                    orb += 2 # 例として2度加算

                current_orb = abs(angle_diff - params['angle'])
                if current_orb < orb:
                    aspect_list.append(
                        f"{PLANET_SYMBOLS[p1_name]} {p1_name} - "
                        f"{PLANET_SYMBOLS[p2_name]} {p2_name} : "
                        f"{aspect_name} (オーブ {current_orb:.2f}°)"
                    )
    return aspect_list


# --- 描画関数 ---

def create_horoscope_chart(celestial_bodies, cusps, ascmc):
    """Matplotlibでホロスコープチャートを描画する"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('W') # 0度を西(左)に設定 (牡羊座0度が左端)
    ax.set_theta_direction(-1) # 時計回り
    ax.set_rlim(0, 10)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)
    ax.spines['polar'].set_visible(False)

    # --- 1. サインの円を描画 ---
    radius_sign = 9.5
    for i in range(12):
        start_angle = np.deg2rad(i * DEGREES_PER_SIGN)
        end_angle = np.deg2rad((i + 1) * DEGREES_PER_SIGN)
        mid_angle = np.deg2rad((i + 0.5) * DEGREES_PER_SIGN)

        # サインの背景色
        color = "aliceblue" if i % 2 == 0 else "white"
        ax.fill_between(np.linspace(start_angle, end_angle, 100), radius_sign - 1.5, radius_sign, color=color, zorder=0)

        # サインの境界線
        ax.plot([start_angle, start_angle], [radius_sign - 1.5, radius_sign], color='lightgray', linewidth=1)

        # サインのシンボルと名前
        ax.text(mid_angle, radius_sign - 0.7, SIGN_SYMBOLS[i], ha='center', va='center', fontsize=20, zorder=2)
        if jp_font_path: # 日本語フォントがある場合のみ名前を表示
             ax.text(mid_angle, radius_sign - 2.2, SIGN_NAMES[i], ha='center', va='center', fontsize=9, rotation=np.rad2deg(mid_angle)+90, zorder=2)

    # 外側の円
    ax.plot(np.linspace(0, 2 * np.pi, 100), [radius_sign] * 100, color='gray', linewidth=1)

    # --- 2. ハウスのカスプを描画 ---
    radius_house_num = 6.5
    if cusps is not None and ascmc is not None:
        # ASC-DSCライン (地平線)
        asc_angle = np.deg2rad(ascmc[0])
        ax.plot([asc_angle, asc_angle + np.pi], [0, radius_sign-1.5], color='black', linewidth=2, zorder=3)
        ax.text(asc_angle, radius_house_num + 0.5, "ASC", ha='right', va='center', fontsize=12, weight='bold')

        # MC-ICライン
        mc_angle = np.deg2rad(ascmc[1])
        ax.plot([mc_angle, mc_angle + np.pi], [0, radius_sign-1.5], color='black', linewidth=2, zorder=3)
        ax.text(mc_angle, radius_house_num + 0.5, "MC", ha='center', va='bottom', fontsize=12, weight='bold')

        # ハウスカスプ線と番号
        for i, cusp_deg in enumerate(cusps):
            angle = np.deg2rad(cusp_deg)
            # ASC, MC以外のカスプ線
            if i + 1 not in [1, 4, 7, 10]:
                 ax.plot([angle, angle], [0, radius_sign-1.5], color='gray', linestyle='--', linewidth=1, zorder=1)

            # ハウス番号
            next_cusp_deg = cusps[(i + 1) % 12]
            # 0度をまたぐ場合の角度差を正しく計算
            if next_cusp_deg < cusp_deg:
                angle_diff = (next_cusp_deg + 360) - cusp_deg
            else:
                angle_diff = next_cusp_deg - cusp_deg
            mid_angle = np.deg2rad(cusp_deg + angle_diff / 2)
            ax.text(mid_angle, radius_house_num, str(i + 1), ha='center', va='center', fontsize=12, color='gray', zorder=2)

    # --- 3. 天体をプロット ---
    radius_planet = 7.5
    planet_positions_rad = {name: np.deg2rad(data['pos']) for name, data in celestial_bodies.items() if name not in SENSITIVE_POINTS}
    
    # 天体の位置を調整して重なりを避ける
    angles = list(planet_positions_rad.values())
    adjusted_radii = [radius_planet] * len(angles)
    for i in range(len(angles)):
        for j in range(i + 1, len(angles)):
            angle_diff = abs(angles[i] - angles[j])
            angle_diff = min(angle_diff, 2 * np.pi - angle_diff)
            if angle_diff < np.deg2rad(8): # 8度以内にあれば半径をずらす
                adjusted_radii[j] = radius_planet - 0.8
                if adjusted_radii[j] < 1: adjusted_radii[j] = radius_planet + 0.8

    i = 0
    for name, data in celestial_bodies.items():
        if name in SENSITIVE_POINTS: continue
        
        angle_rad = np.deg2rad(data['pos'])
        radius = adjusted_radii[i]
        
        # 天体シンボル
        ax.text(angle_rad, radius, PLANET_SYMBOLS[name], ha='center', va='center',
                fontsize=16, color=PLANET_COLORS[name], weight='bold', zorder=4)

        # 天体の度数情報
        pos_in_sign = data['pos'] % DEGREES_PER_SIGN
        deg = int(pos_in_sign)
        minute = int((pos_in_sign - deg) * 60)
        retro_str = " R" if data.get('is_retro', False) else ""
        
        ax.text(angle_rad, radius - 0.7, f"{deg}°{minute:02d}'{retro_str}",
                ha='center', va='center', fontsize=8, zorder=4)
        i += 1

    # 内側の円
    ax.add_artist(plt.Circle((0, 0), 3, color='white', zorder=0))
    ax.add_artist(plt.Circle((0, 0), 3, color='lightgray', fill=False, zorder=1))

    return fig

# --- Streamlit UI ---

st.set_page_config(page_title="ホロスコープ作成アプリ", page_icon="🪐", layout="wide")
st.title("🪐 ホロスコープ作成アプリ")
st.write("生年月日、出生時刻、出生地（都道府県）を入力して、あなたのホロスコープを作成します。")

# --- 入力フォーム ---
with st.sidebar:
    st.header("出生情報を入力")
    birth_date = st.date_input("📅 生年月日", value=datetime(1990, 1, 1))
    birth_time = st.time_input("⏰ 出生時刻 (24時間表記)", value=datetime(1990, 1, 1, 12, 0).time())
    prefecture = st.selectbox("📍 出生地（都道府県）", options=list(PREFECTURE_DATA.keys()), index=12) # デフォルトは東京

    if st.button("ホロスコープを作成する", type="primary"):
        is_ready = True
    else:
        is_ready = False
        st.info("情報を入力してボタンを押してください。")

# --- 計算と表示 ---
if is_ready:
    try:
        # 入力値をdatetimeオブジェクトに結合
        dt_local = datetime.combine(birth_date, birth_time)
        
        # JSTタイムゾーンを設定
        jst = timezone(timedelta(hours=9))
        dt_local_aware = dt_local.replace(tzinfo=jst)
        
        # UTCに変換
        dt_utc = dt_local_aware.astimezone(timezone.utc)

        # 緯度経度を取得
        lat = PREFECTURE_DATA[prefecture]["lat"]
        lon = PREFECTURE_DATA[prefecture]["lon"]

        st.header(f"{dt_local.strftime('%Y年%m月%d日 %H:%M')} 生まれ ({prefecture})")

        with st.spinner("ホロスコープを計算中..."):
            # 天体データとハウスを計算
            celestial_bodies, cusps, ascmc = calculate_celestial_data(dt_utc, lat, lon)

        if celestial_bodies:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("ホロスコープチャート")
                with st.spinner("チャートを描画中..."):
                    fig = create_horoscope_chart(celestial_bodies, cusps, ascmc)
                    st.pyplot(fig)

            with col2:
                # 天体リストの表示
                st.subheader("天体位置リスト")
                planet_data = []
                for name, data in celestial_bodies.items():
                    retro = "R" if data.get('is_retro', False) else ""
                    house_num = get_house_number(data['pos'], cusps) if cusps else "-"
                    planet_data.append([
                        f"{PLANET_SYMBOLS.get(name, '')} {name}",
                        format_degree(data['pos']),
                        retro,
                        house_num
                    ])
                st.dataframe(
                    planet_data,
                    column_config={
                        0: "天体/感受点",
                        1: "サインと度数",
                        2: "逆行",
                        3: "ハウス"
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # アスペクトリストの表示
                st.subheader("アスペクトリスト")
                with st.spinner("アスペクトを計算中..."):
                    aspects = calculate_aspects_list(celestial_bodies)
                if aspects:
                    st.text("\n".join(aspects))
                else:
                    st.info("設定されたオーブ内に主要なアスペクトは見つかりませんでした。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.error("入力内容を確認するか、管理者にお問い合わせください。")

