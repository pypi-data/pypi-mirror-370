# 貢献ガイド

rfbプロジェクトへの貢献に興味をお持ちいただき、ありがとうございます！このガイドでは、プロジェクトへの貢献方法について説明します。

## 開発環境の準備

### 1. リポジトリのクローン

```bash
git clone https://github.com/shotakaha/rfb.git
cd rfb
```

### 2. 開発環境のセットアップ

```bash
# uv を使用して仮想環境をセットアップ
uv venv
# 開発モードでインストール
uv pip install -e ".[dev]"
```

## コーディング規約

- Python 3.12以上の機能を活用
- [PEP 8](https://peps.python.org/pep-0008/)に従うコードスタイル
- 型ヒントを使用したタイプセーフなコード
- 適切なドキュメンテーション（docstring）
- 十分なテストカバレッジ

## コミットメッセージ

コミットメッセージは[Conventional Commits](https://www.conventionalcommits.org/)の形式に従ってください：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

例：

```
feat(backup): add snapshot functionality
fix(fetcher): resolve SSH connection issue
docs(readme): update installation instructions
test(config): add tests for environment variable expansion
```

## プルリクエストプロセス

1. 新しいブランチを作成（`feature/your-feature`または`fix/your-fix`）
2. 変更を実装
3. テストを追加・実行
4. ドキュメントを更新
5. プルリクエストを作成
6. レビューとフィードバック
7. マージ

## テスト

テストの実行：

```bash
pytest
```

カバレッジレポートの生成：

```bash
pytest --cov=rfb --cov-report=html
```

## ドキュメントの構築

ドキュメントの構築と表示：

```bash
# ドキュメントをローカルで表示
mkdocs serve

# ドキュメントをビルド
mkdocs build
```

## 新機能の提案

新機能やエンハンスメントのアイデアがある場合：

1. Githubの[Issues](https://github.com/shotakaha/rfb/issues)で新しいissueを作成
2. 「enhancement」ラベルを追加
3. 機能の説明と使用例を記載

## バグ報告

バグを報告する場合：

1. Githubの[Issues](https://github.com/shotakaha/rfb/issues)で新しいissueを作成
2. 「bug」ラベルを追加
3. 再現手順を詳細に記載
4. 可能であれば、修正案や回避策を提案

## リリースプロセス

リリースは以下の手順で行われます：

1. バージョン番号の更新（`pyproject.toml`）
2. CHANGELOGの更新
3. タグ付け（`git tag v0.x.x`）
4. PyPIへの公開

## コードレビュー

プルリクエストのレビュー基準：

- 適切なテストカバレッジ
- コード品質と読みやすさ
- エラー処理の適切さ
- ドキュメントの完全性
- パフォーマンスの考慮

## ライセンス

このプロジェクトはMITライセンスの下で公開
