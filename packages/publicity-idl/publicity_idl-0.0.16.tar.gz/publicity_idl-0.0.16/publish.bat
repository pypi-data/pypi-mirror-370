@echo off

:: 1. 清理旧构建产物
echo 清理旧构建产物...
if exist dist (
    rmdir /s /q dist
)
mkdir dist 2>nul

:: 2. 自动递增版本并获取新版本号
echo 自动递增版本号...
for /f "delims=" %%v in ('python bump_version.py') do set "NEW_VERSION=%%v"
echo 版本已更新为: %NEW_VERSION%

:: 3. 构建包
echo 构建新版本...
hatch build

:: 4. 处理Git提交信息（支持可选参数）
echo 准备提交代码...
:: 默认提交信息
set "COMMIT_MSG=idl更新- %NEW_VERSION%"

:: 关键修复：用"%~1"保留带空格的完整参数，再拼接版本号
if not "%~1"=="" (
    set "COMMIT_MSG=%NEW_VERSION% - %~1"
)

git add .
git commit -m "%COMMIT_MSG%"
git push

:: 5. 上传到PyPI
echo 上传到PyPI...
twine upload dist/*

echo 发布完成！
echo 提交信息: %COMMIT_MSG%
