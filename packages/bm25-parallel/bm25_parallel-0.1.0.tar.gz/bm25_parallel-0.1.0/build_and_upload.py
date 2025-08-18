import subprocess, sys, os, shutil

ROOT = os.path.dirname(__file__)
os.chdir(ROOT)

# 1. 清理旧包
shutil.rmtree("dist", ignore_errors=True)

# 2. 构建 wheel & sdist
subprocess.check_call([sys.executable, "-m", "build"])

# 3. 本地检查
subprocess.check_call([sys.executable, "-m", "twine", "check", "dist/*"])

# 4. 上传到 PyPI（首次用 --repository testpypi 测试）
repo = "pypi"  # 或 "testpypi"
token = input(f"输入 {repo} API token：").strip()
subprocess.check_call([
    sys.executable, "-m", "twine", "upload",
    "--repository", repo,
    "--username", "__token__",
    "--password", token,
    "dist/*"
])
print("✅ 发布完成！")