# fnb - Development TODO List

プロジェクト全体を分析した結果に基づく、GitLab issue提案です。優先度と工数を考慮して分類しました。

## 🔴 優先度: 高 (High Priority)

### 1. テストカバレッジの改善 (Improve Test Coverage) ✅ **IMPLEMENTED**
**現状**: 全体カバレッジ61%、多くのモジュールで50-60%台
**課題**:
- エラーハンドリング部分の未テスト
- CLI実行時の例外処理テスト不足
- `pexpect`を使うSSH認証部分のテスト不足

**工数**: 中（2-3日）

**GitLab実装状況**:
- **Milestone**: [Test Coverage Improvement to 80%+](https://gitlab.com/qumasan/fnb/-/milestones/1)
- **Issues Created**:
  - [#6: test: setup enhanced testing infrastructure and fixtures](https://gitlab.com/qumasan/fnb/-/issues/6) (0.5日・基盤) ✅ **COMPLETED**
  - [#1: test(gear): add SSH authentication and pexpect testing](https://gitlab.com/qumasan/fnb/-/issues/1) (1.5日・高優先) ✅ **COMPLETED**
  - [#2: test(reader): improve configuration reading error handling tests](https://gitlab.com/qumasan/fnb/-/issues/2) (1日・高優先) ✅ **COMPLETED**
  - [#3: test(cli): add CLI command error scenario testing](https://gitlab.com/qumasan/fnb/-/issues/3) (0.5日・中優先) ✅ **COMPLETED**
  - [#4: test(env): enhance environment handling test coverage](https://gitlab.com/qumasan/fnb/-/issues/4) (0.5日・中優先) ✅ **COMPLETED**
  - [#5: test(backuper,fetcher): add operation failure scenario testing](https://gitlab.com/qumasan/fnb/-/issues/5) (0.5日・中優先) ✅ **COMPLETED**
  - [#7: test: add integration tests for complete workflows](https://gitlab.com/qumasan/fnb/-/issues/7) (0.5日・統合) ✅ **COMPLETED**

**推奨実装順序**: #6 ✅ → #1 ✅,#2 ✅ → #3 ✅,#4 ✅,#5 ✅ → #7 ✅
**総工数**: 4.5日 (完了済み)

### 2. 設定検証の強化 (Enhanced Configuration Validation)
**現状**: 基本的なPydantic検証のみ
**課題**:
- パス存在確認が実行時のみ
- ホスト接続確認なし
- rsyncオプションの妥当性検証なし

**工数**: 中（2-3日）

### 3. ログ機能の実装 (Implement Logging System)
**現状**: print文ベースの出力のみ
**課題**:
- 構造化ログなし
- ログレベル制御なし
- 実行履歴の保存なし

**工数**: 中（2-3日）

## 🟡 優先度: 中 (Medium Priority)

### 4. プログレス表示機能 (Progress Display for Large Transfers)
**現状**: rsync実行中の進捗が見えない
**課題**:
- 大容量ファイル転送時の状況不明
- 推定完了時間なし

**工数**: 中（2-3日）

### 5. 設定ファイル管理機能の拡張 (Configuration Management Enhancement)
**現状**: 基本的な設定読み込みのみ
**課題**:
- 設定ファイルの分割・統合機能なし
- プロファイル（環境別設定）機能なし
- 設定テンプレート管理なし

**工数**: 大（4-5日）

### 6. バックアップ履歴・統計機能 (Backup History and Statistics)
**現状**: 実行結果の記録なし
**課題**:
- 実行履歴の保存なし
- 転送統計情報なし
- 失敗率などの分析機能なし

**工数**: 大（4-5日）

## 🟢 優先度: 低 (Low Priority / Enhancement)

### 7. 並列実行機能 (Parallel Execution Support)
**現状**: タスクの逐次実行のみ
**課題**:
- 複数タスクの同時実行不可
- CPU/ネットワーク効率化の余地

**工数**: 大（5-6日）

### 8. Web UI / Dashboard (Optional Web Interface)
**現状**: CLIのみ
**課題**:
- 視覚的なステータス確認機能なし
- ログ閲覧の利便性低い

**工数**: 特大（1-2週間）

### 9. 高度な同期戦略 (Advanced Synchronization Strategies)
**現状**: rsyncベースの基本同期のみ
**課題**:
- 増分バックアップ機能なし
- 重複排除機能なし
- バージョニング機能なし

**工数**: 特大（1-2週間）

---

## 📊 推奨開発順序

**Phase 1 (即効性重視)**:
1. テストカバレッジ改善
2. ログ機能実装
3. 設定検証強化

**Phase 2 (ユーザビリティ向上)**:
4. プログレス表示
5. 設定管理機能拡張

**Phase 3 (機能拡張)**:
6. バックアップ履歴・統計
7. 並列実行機能

**Phase 4 (長期的改善)**:
8. Web UI
9. 高度同期戦略

**総課題数**: 9個
**推定総工数**: 25-35日

---

## 🎯 実装状況サマリー

### ✅ 実装済み
1. **テストカバレッジの改善** - Milestone + 7個のIssues作成済み
   - **Issue #6: テストインフラ強化** ✅ **COMPLETED** (2025-08-16)
     - Enhanced conftest.py with comprehensive fixtures
     - Mock utilities for external dependencies
     - Temporary file management and environment cleanup
     - CLI testing framework and utility functions

   - **Issue #1: SSH認証・pexpectテスト** ✅ **COMPLETED** (2025-08-16)
     - gear.py カバレッジ: 57% → 87% (+30%向上)
     - SSH認証の包括的テスト11ケース追加
     - pexpectベースの異常系処理テスト完備

   - **Issue #2: 設定読み込みエラーハンドリングテスト** ✅ **COMPLETED** (2025-08-18)
     - reader.py カバレッジ: 50% → 89% (+39%向上)
     - 設定ファイル検索・TOML解析・環境変数展開の包括的テスト16ケース追加
     - UnboundLocalErrorバグ修正

   - **Issue #3: CLIコマンドエラーシナリオテスト** ✅ **COMPLETED** (2025-08-18)
     - cli.py カバレッジ: 76% → 99% (+23%向上)
     - CLIコマンドエラーハンドリングの包括的テスト16ケース追加
     - version・init・fetch・backup・syncコマンドの全エラーパス検証

   - **Issue #4: 環境変数ハンドリングテスト** ✅ **COMPLETED** (2025-08-18)
     - env.py カバレッジ: 57% → 68% (+11%向上)
     - 環境変数処理の包括的テスト14ケース追加
     - SSH パスワード取得・ホスト名正規化・プラットフォーム統合・セルフテスト機能検証
     - RFB_ → FNB_ 環境変数プレフィックス修正・テスト分離問題解決

### ✅ 全て完了 (All Issues Completed)
1. **テストカバレッジの改善** - 全7個のIssuesが完了済み
   - **Issue #7: 統合テスト** ✅ **COMPLETED** (2025-08-19)
     - 統合テスト新規作成: test_integration.py (540行、23テスト)
     - CLI ワークフロー統合テスト: 7テスト
     - マルチモジュール統合テスト: 6テスト
     - Syncワークフロー統合テスト: 6テスト
     - エンドツーエンド統合テスト: 2テスト
     - **テスト成功率: 100% (23/23)** - 全テストパス
     - 外部依存性を排除した信頼性の高いテスト設計

### 🔄 実装待ち (GitLab Issues未作成)
2. 設定検証の強化
3. ログ機能の実装
4. プログレス表示機能
5. 設定ファイル管理機能の拡張
6. バックアップ履歴・統計機能
7. 並列実行機能
8. Web UI / Dashboard
9. 高度な同期戦略

### 📈 次のアクション

1. **テストカバレッジ完了**: Issue #7 統合テストを完成し、全7個Issues完了 ✅
2. **80%+目標達成**: 全体カバレッジ83%で目標を上回って達成済み ✅
3. **新機能開始**: 設定検証の強化・ログ機能実装の準備
4. **フェーズ2**: 優先度に応じて残りの課題もGitLab Issueとして作成することを推奨

---

## 分析結果サマリー

### テストカバレッジ分析 (2025-08-19 更新)
```
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
src/fnb/__init__.py        1      0   100%
src/fnb/backuper.py       42      7    83%  ⬆️ +31% (Issue #5 完了)
src/fnb/cli.py            87      1    99%  ⬆️ +23% (Issue #3 完了)
src/fnb/config.py         56     12    79%
src/fnb/env.py            37     12    68%  ⬆️ +11% (Issue #4 完了)
src/fnb/fetcher.py        46      7    85%  ⬆️ +31% (Issue #5 完了)
src/fnb/gear.py           76     10    87%  ⬆️ +30% (Issue #1 完了)
src/fnb/generator.py      71     27    62%
src/fnb/reader.py         94     10    89%  ⬆️ +39% (Issue #2 完了)
----------------------------------------------------
TOTAL                    510     86    83%  ⬆️ +22%
```

### 🎯 Issue完了実績

#### Issue #1: SSH認証・pexpectテスト
- **gear.py カバレッジ**: 57% → **87%** (+30%向上)
- **SSH認証テスト**: 11個の新テストケース追加
- **実装範囲**: SSH成功・タイムアウト・EOF・シグナル・例外処理を網羅
- **実行時間**: < 2秒 (外部依存なしの高速テスト)

#### Issue #2: 設定読み込みエラーハンドリングテスト
- **reader.py カバレッジ**: 50% → **89%** (+39%向上)
- **新規テストケース**: 16個の包括的テスト追加
- **実装範囲**: 設定ファイル検索・TOML解析・環境変数展開・ステータス表示
- **バグ修正**: UnboundLocalError (\_check_directory メソッド)
- **全体カバレッジ**: 66% → **73%** (+7%向上)

#### Issue #3: CLIコマンドエラーシナリオテスト
- **cli.py カバレッジ**: 76% → **99%** (+23%向上)
- **新規テストケース**: 16個の包括的テスト追加
- **実装範囲**: version・init・fetch・backup・syncコマンドの全エラーパス検証
- **テスト種類**: 引数検証・例外処理・終了コード・エラーメッセージ・フラグ動作
- **全体カバレッジ**: 73% → **77%** (+4%向上)

#### Issue #4: 環境変数ハンドリングテスト
- **env.py カバレッジ**: 57% → **68%** (+11%向上)
- **新規テストケース**: 14個の包括的テスト追加（1スキップ）
- **実装範囲**: .env ファイル読み込み・SSH パスワード取得・ホスト名正規化・プラットフォーム統合・セルフテスト実行
- **修正内容**: RFB_ → FNB_ 環境変数プレフィックス修正・テスト分離問題解決
- **全体カバレッジ**: 77% → **78%** (+1%向上)

#### Issue #5: バックアップ・フェッチ運用失敗シナリオテスト
- **backuper.py カバレッジ**: 52% → **83%** (+31%向上)
- **fetcher.py カバレッジ**: 54% → **85%** (+31%向上)
- **新規テストケース**: 14個の包括的テスト追加
- **実装範囲**: SSH認証フロー・パスワード優先度・ディレクトリ検証・rsync実行失敗・例外伝播
- **全体カバレッジ**: 78% → **83%** (+5%向上)

#### Issue #7: 統合テスト - 完全ワークフロー
- **統合テストファイル**: test_integration.py 新規作成 (540行)
- **統合テスト総数**: 23テスト（100%成功率）
- **テストカテゴリ**:
  - CLI ワークフロー統合: 7テスト
  - マルチモジュール統合: 6テスト
  - Syncワークフロー統合: 6テスト
  - エンドツーエンド統合: 2テスト
  - 基盤フィクスチャ: 2テスト
- **テスト技術**: 外部依存性排除・戦略的モッキング・ドライラン統合・完全分離環境
- **最終成果**: 全モジュール統合フローの信頼性確保・ユーザーワークフロー検証

### 主な改善ポイント
- ~~SSH認証部分の複雑な処理テストが困難~~ ✅ **解決済み** (Issue #1)
- ~~設定読み込みエラーハンドリングのテスト不足~~ ✅ **解決済み** (Issue #2)
- ~~CLIコマンドエラーハンドリングのテスト不足~~ ✅ **解決済み** (Issue #3)
- ~~環境変数ハンドリングのテスト不足~~ ✅ **解決済み** (Issue #4)
- ~~実行時例外の網羅的テストが必要（backuper.py, fetcher.py等）~~ ✅ **解決済み** (Issue #5)
- ~~統合テストによる完全ワークフロー検証が必要~~ ✅ **解決済み** (Issue #7)
- 設定検証の事前チェック機能が不足
- ログ・監査機能の不在
