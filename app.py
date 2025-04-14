import streamlit as st
import subprocess
import os
import tempfile
import base64
import re

# 🔧 リソースのパス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(SCRIPT_DIR, "ffmpeg")
DVDAUTHOR_PATH = os.path.join(SCRIPT_DIR, "dvdauthor")
MKISOFS_PATH = os.path.join(SCRIPT_DIR, "mkisofs")

# ✅ ロゴ画像Base64埋め込み
def load_logo_base64():
    with open(os.path.join(SCRIPT_DIR, "ISOMANIA.png"), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# ✅ 安全なテキスト生成（未使用だが残しておく）
def sanitize_text(text):
    return re.sub(r"[^\w\u3000-\u30FF\u4E00-\u9FFF\-\u30fb()（）]+", " ", text)

# ✅ MP4 → MPEG2変換
def convert_mp4s_to_mpeg2(mp4_files, work_dir, log_area):
    mpeg2_files = []
    for i, uploaded_file in enumerate(mp4_files):
        input_path = os.path.join(work_dir, f"input_{i}.mp4")
        output_path = os.path.join(work_dir, f"output_{i}.mpg")
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())
        result = subprocess.run([
            FFMPEG_PATH, '-i', input_path,
            '-target', 'ntsc-dvd', '-aspect', '16:9',
            output_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        log_area.write(f"📼 ffmpeg 出力（input_{i}.mp4）:")
        log_area.code(result.stderr)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)
        mpeg2_files.append(output_path)
    return mpeg2_files

# ✅ ISO作成（メニューなし）
def create_dvd_iso(mpeg2_files, output_iso, work_dir, log_area):
    dvd_dir = os.path.join(work_dir, "dvd")
    os.makedirs(os.path.join(dvd_dir, "VIDEO_TS"), exist_ok=True)
    env = os.environ.copy()
    env["VIDEO_FORMAT"] = "NTSC"

    for mpg in mpeg2_files:
        result = subprocess.run(
            [DVDAUTHOR_PATH, '-o', dvd_dir, '-t', mpg],
            cwd=work_dir, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        log_area.write("📤 dvdauthor -t 出力:")
        log_area.code(result.stdout + result.stderr)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)

    result = subprocess.run(
        [DVDAUTHOR_PATH, '-o', dvd_dir, '-T'],
        cwd=work_dir, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    log_area.write("📤 dvdauthor -T 出力:")
    log_area.code(result.stdout + result.stderr)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, result.args)

    # ✅ mkisofs で ISO 作成
    result = subprocess.run([
        MKISOFS_PATH, '-dvd-video', '-udf',
        '-o', output_iso, dvd_dir
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    log_area.write("💿 mkisofs 出力:")
    log_area.code(result.stdout + result.stderr)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, result.args)

# ✅ ロゴ付きタイトル
logo_base64 = load_logo_base64()
st.markdown(
    f"""
    <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 30px;'>
        <img src="data:image/png;base64,{logo_base64}" width="80">
        <h1 style='margin: 0;'>MP4 → DVD ISO 変換ツール</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ✅ UI
uploaded_files = st.file_uploader("MP4ファイルを選択（複数可）", type=["mp4"], accept_multiple_files=True)

if uploaded_files and st.button("変換する！"):
    # ステータスメッセージやログの出力領域を予約
    status_area = st.empty()
    result_area = st.empty()
    log_area = st.container()

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            status_area.info("🔄 変換中...少々お待ちください ⏳")
            mpeg2_files = convert_mp4s_to_mpeg2(uploaded_files, tmpdir, log_area)
            iso_path = os.path.join(tmpdir, "output.iso")
            create_dvd_iso(mpeg2_files, iso_path, tmpdir, log_area)

            # ✅ 成功メッセージとダウンロードボタンを最上部に表示
            status_area.success("✅ ISOファイルの作成が完了しました！")
            with open(iso_path, "rb") as iso_file:
                result_area.download_button("📥 ISOをダウンロード", iso_file, file_name="dvd_output.iso", mime="application/octet-stream")

        except Exception as e:
            status_area.error(f"❌ エラーが発生しました：\n{e}")
