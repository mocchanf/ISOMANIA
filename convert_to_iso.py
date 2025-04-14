import subprocess
import os

def mp4_to_dvd_iso(input_mp4, output_iso, work_dir):
    temp_mpg = os.path.join(work_dir, "temp_dvd_video.mpg")
    dvddir = os.path.join(work_dir, "dvd")

    # 🔧 スクリプトのある場所を基準にコマンドパスを指定
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FFMPEG_PATH = os.path.join(SCRIPT_DIR, "ffmpeg")
    DVDAUTHOR_PATH = os.path.join(SCRIPT_DIR, "dvdauthor")
    MKISOFS_PATH = os.path.join(SCRIPT_DIR, "mkisofs")

    try:
        print("🎬 MP4 → MPEG2 に変換中...")
        subprocess.run([
            FFMPEG_PATH, '-i', input_mp4,
            '-target', 'ntsc-dvd',
            '-aspect', '16:9',
            temp_mpg
        ], check=True)

        print("📁 DVDフォルダ作成中...")
        os.makedirs(os.path.join(dvddir, "VIDEO_TS"), exist_ok=True)

        print("📀 dvdauthor (1回目) 実行中...")
        subprocess.run([DVDAUTHOR_PATH, '-o', dvddir, '-t', temp_mpg], check=True)

        print("📀 dvdauthor (2回目) 実行中（NTSC指定）...")
        env_vars = os.environ.copy()
        env_vars["VIDEO_FORMAT"] = "NTSC"
        subprocess.run(
            [DVDAUTHOR_PATH, '-o', dvddir, '-T'],
            check=True,
            cwd=work_dir,
            env=env_vars
        )

        print("💿 ISOファイル作成中...")
        subprocess.run([MKISOFS_PATH, '-dvd-video', '-udf', '-o', output_iso, dvddir], check=True)

        print(f"✅ 完了！ISOファイル: {output_iso}")

    except subprocess.CalledProcessError as e:
        print(f"❌ コマンドエラー：\n{e}")
        raise
    except Exception as e:
        print(f"⚠️ その他のエラー：\n{e}")
        raise
