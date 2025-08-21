# インストール

rfbはシンプルなPythonパッケージであり、複数の方法でインストールできます。

## 必要条件

- Python 3.12以上
- rsync（システムにインストール済みであること）

## インストール方法

### pipを使用する場合

```bash
pip install rfb
```

### uv を使用する場合 (推奨)

[uv](https://github.com/astral-sh/uv) はモダンなPythonパッケージマネージャーです。

```bash
uv pip install rfb
```

### Homebrewを使用（macOS・準備中）

```bash
brew install rfb
```

!!! note
    Homebrewパッケージは検討中です。

### 開発用インストール（準備中）

開発目的の場合は、リポジトリをクローンして開発モードでインストールします：

```bash
git clone https://github.com/shotakaha/rfb.git
cd rfb
uv venv
uv pip install -e .

# 開発用依存関係もインストールする場合
uv pip install -e ".[dev]"
```

## 動作確認

インストールが成功したことを確認するにはバージョン情報を表示してください。

```bash
rfb --version
```

バージョン情報が表示されれば、インストールは成功しています。

## 次のステップ

- [基本的な使い方](usage/commands.md)を確認する
- [設定ファイル](usage/configuration.md)を作成する
