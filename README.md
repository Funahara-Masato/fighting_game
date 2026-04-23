# Fighting Game

Pygame で実装した 2D スティックマン格闘ゲーム。PvP と AI 対戦の 2 モード搭載。

## 特徴

- 膝・肘関節による 2 セグメント四肢アニメーション
- ジャンプ中の専用ポーズ・着地スクワッシュエフェクト
- 歩行サイクルのなめらかな加減速
- のけぞり・スタン・ヒットフラッシュ
- HP バー・BGM・効果音

## 操作方法

### プレイヤー 1（赤）
| アクション | キー |
|-----------|------|
| 移動 | `A` / `D` |
| ジャンプ | `W` |
| 攻撃 | `S` |

### プレイヤー 2（青）— PvP のみ
| アクション | キー |
|-----------|------|
| 移動 | `←` / `→` |
| ジャンプ | `↑` |
| 攻撃 | `↓` |

## 実行方法

```bash
pip install pygame
python main.py
```

Windows の場合は `run_app.bat` をダブルクリックでも起動できます。

## ファイル構成

```
fighting_game/
├── main.py          # メインループ・勝敗判定
├── fighter.py       # キャラクタークラス（描画・物理）
├── config.py        # 定数・Pygame 初期化
├── select_mode.py   # モード選択画面
├── assets/
│   ├── bgm.mp3
│   ├── hit.mp3
│   └── background.jpg
└── requirements.txt
```

## 作者

Masato Funahara — funaharamasato@gmail.com
