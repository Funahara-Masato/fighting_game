# Stickman Fighting Game

2D棒人間格闘ゲーム。PvPおよびAI対戦モードに対応しており、PythonとPygameで作成されています。

## ゲーム内容
- プレイヤー1（赤）とプレイヤー2（青）による格闘
- PvPモードとAI対戦モードを選択可能
- ジャンプ・移動・攻撃の操作に対応
- HPバー、攻撃アニメーション、のけぞり効果あり
- BGMと効果音搭載

## 操作方法

### PvPモード
- プレイヤー1（赤）
  - 移動: `A / D`
  - ジャンプ: `W`
  - 攻撃: `S`
- プレイヤー2（青）
  - 移動: `← / →`
  - ジャンプ: `↑`
  - 攻撃: `↓`

### AIモード
- プレイヤー1が操作可能
- プレイヤー2はAIが自動で操作

## インストール方法

1. 仮想環境の作成
```bash
python -m venv venv

### macOS / Linuxでの仮想環境有効化
```bash
source venv/bin/activate

## 必要ライブラリのインストール

仮想環境を有効化した後、必要なPythonライブラリをインストールします。

```bash
# 仮想環境を有効化
source venv/bin/activate  # macOS / Linux

# requirements.txtに記載されたライブラリをインストール
pip install -r requirements.txt

これにより、pygame などゲーム実行に必要なライブラリがインストールされます。

実行方法
.\run_app.bat

ファイル構成
stickman_fighting_game/
│
├─ main.py          # メインループ
├─ fighter.py       # キャラクタークラス
├─ assets/
│   ├─ bgm.mp3
│   ├─ hit.mp3
│   └─ background.jpg
├─ requirements.txt
└─ run_app.bat

ライセンス

MIT License
