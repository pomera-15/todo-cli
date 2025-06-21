# Todo CLI 仕様書

## 概要
コマンドラインで動作するシンプルで使いやすいTodo管理ツール

## 主要機能

### 1. Todo項目の管理
- **追加**: `todo add "タスク内容"`
- **一覧表示**: `todo list`
- **完了**: `todo done <ID>`
- **削除**: `todo delete <ID>`
- **編集**: `todo edit <ID> "新しい内容"`

### 2. 優先度管理
- 3段階の優先度: high, medium, low
- 追加時に指定: `todo add "タスク" -p high`
- デフォルトは medium

### 3. カテゴリ/タグ
- タグ付け: `todo add "タスク" -t work,urgent`
- タグでフィルタ: `todo list -t work`
- 複数タグのサポート

### 4. 期限管理
- 期限設定: `todo add "タスク" -d 2024-12-31`
- 期限切れの表示
- 期限が近いタスクの警告表示

### 5. データ保存
- **形式**: JSON形式で保存
- **保存場所**: ホームディレクトリの`.todo/todos.json`
- **信頼性**: データの整合性を保証、パースエラーを防止

## 技術仕様

### 実装言語
- Python 3.8以上

### データ形式
JSONファイルに以下の形式で保存:

```json
[
  {
    "id": 1,
    "task": "タスク名",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2024-12-31",
    "created_at": "2024-12-20T10:30:00.000000",
    "completed_at": null
  },
  {
    "id": 2,
    "task": "完了したタスク",
    "priority": "medium", 
    "tags": ["personal"],
    "due_date": null,
    "created_at": "2024-12-20T09:00:00.000000",
    "completed_at": "2024-12-20T15:00:00.000000"
  }
]
```

### コマンドライン仕様

#### 基本コマンド
- `todo add <task>` - 新しいタスクを追加
- `todo list` - すべてのタスクを表示
- `todo done <id>` - タスクを完了
- `todo delete <id>` - タスクを削除
- `todo edit <id> <new_task>` - タスクを編集

#### オプション
- `-p, --priority <level>` - 優先度を設定 (high/medium/low)
- `-t, --tags <tags>` - カンマ区切りでタグを設定
- `-d, --due <date>` - 期限を設定 (YYYY-MM-DD形式)
- `--show-completed` - 完了したタスクも表示
- `--filter-tag <tag>` - 特定のタグでフィルタ

### ディレクトリ構造
```
todo-cli/
├── todo.py          # メインスクリプト
├── requirements.txt # 依存関係
├── README.md        # 使用方法
├── specification.md # この仕様書
└── tests/           # テストコード
    └── test_todo.py
```

## 拡張機能（将来的な実装）
- サブタスクのサポート
- 繰り返しタスク
- タスクのアーカイブ
- 統計情報の表示
- エクスポート機能（CSV, JSON）