import sys
import subprocess

def main():
    print("Starting Lin-Paper System...")
    
    # ✨ [调整点] 根据启动参数决定运行模式
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # 启动纯命令行模式
        from interface.cli import run_cli
        run_cli()
    else:
        # 默认启动 Streamlit Web 界面
        print("启动 Web 界面模式，如果需要命令行模式，请使用: python main.py --cli")
        subprocess.run(["streamlit", "run", "interface/web_app.py"])

if __name__ == "__main__":
    main()