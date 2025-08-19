import toml

# 读取pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as f:
    config = toml.load(f)

# 获取当前版本号
current_version = config["project"]["version"]
major, minor, patch = map(int, current_version.split("."))

# 递增补丁号（小版本）
new_version = f"{major}.{minor}.{patch + 1}"
config["project"]["version"] = new_version

# 写回pyproject.toml
with open("pyproject.toml", "w", encoding="utf-8") as f:
    toml.dump(config, f)

# 仅输出新版本号（供批处理脚本捕获）
print(new_version)
