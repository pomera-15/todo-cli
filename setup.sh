#!/bin/bash

# Todo CLI セットアップスクリプト

echo "Todo CLI をセットアップしています..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# シンボリックリンクを作成する方法
setup_symlink() {
    echo "シンボリックリンクを作成しています..."
    # /usr/local/bin が存在しない場合は作成
    sudo mkdir -p /usr/local/bin
    
    # シンボリックリンクを作成
    sudo ln -sf "$SCRIPT_DIR/todo.py" /usr/local/bin/todo
    sudo ln -sf "$SCRIPT_DIR/todo.py" /usr/local/bin/td
    
    echo "✓ シンボリックリンクを /usr/local/bin/todo と /usr/local/bin/td に作成しました"
}

# エイリアスを設定する方法
setup_alias() {
    echo "シェルエイリアスを設定しています..."
    
    # 使用しているシェルを検出
    SHELL_NAME=$(basename "$SHELL")
    
    case $SHELL_NAME in
        bash)
            RC_FILE="$HOME/.bashrc"
            ;;
        zsh)
            RC_FILE="$HOME/.zshrc"
            ;;
        *)
            echo "警告: 不明なシェル $SHELL_NAME です。.bashrc を使用します。"
            RC_FILE="$HOME/.bashrc"
            ;;
    esac
    
    # エイリアスを追加
    TODO_ALIAS="alias todo='python3 $SCRIPT_DIR/todo.py'"
    TD_ALIAS="alias td='python3 $SCRIPT_DIR/todo.py'"
    
    # すでにエイリアスが存在するかチェック
    if ! grep -q "alias todo=" "$RC_FILE" 2>/dev/null; then
        echo "" >> "$RC_FILE"
        echo "# Todo CLI aliases" >> "$RC_FILE"
        echo "$TODO_ALIAS" >> "$RC_FILE"
        echo "$TD_ALIAS" >> "$RC_FILE"
        echo "✓ エイリアス (todo, td) を $RC_FILE に追加しました"
        echo "→ 新しいターミナルを開くか、'source $RC_FILE' を実行してください"
    else
        echo "! エイリアスはすでに設定されています"
    fi
}

# ラッパースクリプトを作成する方法
setup_wrapper() {
    echo "ラッパースクリプトを作成しています..."
    
    # todoラッパースクリプトを作成
    cat > "$SCRIPT_DIR/todo" << EOF
#!/bin/bash
exec python3 "$SCRIPT_DIR/todo.py" "\$@"
EOF
    
    # tdラッパースクリプトを作成
    cat > "$SCRIPT_DIR/td" << EOF
#!/bin/bash
exec python3 "$SCRIPT_DIR/todo.py" "\$@"
EOF
    
    # 実行権限を付与
    chmod +x "$SCRIPT_DIR/todo"
    chmod +x "$SCRIPT_DIR/td"
    
    # PATHに追加するための指示を表示
    echo "✓ ラッパースクリプト (todo, td) を作成しました"
    echo "→ 以下のコマンドを実行してPATHに追加してください:"
    echo "  export PATH=\"$SCRIPT_DIR:\$PATH\""
    echo "→ 永続化するには、上記を ~/.bashrc または ~/.zshrc に追加してください"
}

# メニューを表示
echo ""
echo "セットアップ方法を選択してください:"
echo "1) シンボリックリンク (/usr/local/bin/todo) - 管理者権限が必要"
echo "2) シェルエイリアス (alias todo='...') - 現在のユーザーのみ"
echo "3) ラッパースクリプト + PATH追加 - 管理者権限不要"
echo ""
read -p "選択してください (1-3): " choice

case $choice in
    1)
        setup_symlink
        ;;
    2)
        setup_alias
        ;;
    3)
        setup_wrapper
        ;;
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "セットアップが完了しました！"
echo "使い方:"
echo "  todo add \"タスク名\"  または  td a \"タスク名\""
echo "  todo list          または  td l"