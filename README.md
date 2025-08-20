# Fighting Game

シンプル人間格闘ゲーム。PvPおよびAI対戦モードに対応しており、PythonとPygameで作成されています。

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


## 実行方法
以下のコマンドを実行してアプリを起動します。  

```bash
streamlit run app.py
```

仮想環境が作成され，ライブラリがインストールされます。  
その後ブラウザが自動で開かれ，アプリを利用できます。  

## ファイル構成
stickman_fighting_game/  
│  
├─ main.py&emsp;&emsp;&emsp;&emsp;&emsp;# メインループ  
├─ fighter.py&emsp;&emsp;&emsp;&emsp;# キャラクタークラス  
├─ assets/  
│&emsp;&emsp;├─ bgm.mp3  
│&emsp;&emsp;├─ hit.mp3  
│&emsp;&emsp;└─ background.jpg  
├─ requirements.txt  
└─ run_app.bat  

