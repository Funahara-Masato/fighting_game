@echo off
REM --- ゲーム起動用バッチファイル ---

REM 1. 仮想環境を作成（venvフォルダがなければ作る）
if not exist venv (
    py -m venv venv
)

REM 2. 仮想環境を有効化
call venv\Scripts\activate

REM 3. 必要なライブラリをインストール
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    pip install pygame
)

REM 4. ゲームを起動
py main.py

pause
