import pandas as pd

def filter_target_tables():
    # テーブル一覧を読み込み
    df = pd.read_excel('zoho_table_list.xlsx', sheet_name='Main_Tables')
    
    print(f"元の主要テーブル数: {len(df)} 個")
    
    # 除外条件を設定
    exclude_keywords = [
        'zoho books', 'zoho survey', 'books', 'survey',
        'analytics', 'audit', 'api', 'activity', 'access'
    ]
    
    # Notes関連で対象とするキーワード
    target_notes_keywords = ['商談', 'クラス', '詳細', '手配', '受講生']
    
    filtered_tables = []
    
    for _, row in df.iterrows():
        table_name = row['view_name'].lower()
        
        # ZohoBooks、ZohoSurvey関連を除外
        if any(keyword in table_name for keyword in exclude_keywords):
            continue
        
        # Notesテーブルの場合、特定のキーワードのみ対象
        if 'notes' in table_name:
            if any(keyword in row['view_name'] for keyword in target_notes_keywords):
                filtered_tables.append(row)
        else:
            # Notes以外のテーブルは基本的に対象
            filtered_tables.append(row)
    
    # 結果をデータフレームに変換
    filtered_df = pd.DataFrame(filtered_tables)
    
    print(f"\nフィルタ後のテーブル数: {len(filtered_df)} 個")
    print(f"削減数: {len(df) - len(filtered_df)} 個")
    
    # ワークスペース別の内訳
    if not filtered_df.empty:
        workspace_counts = filtered_df['workspace_name'].value_counts()
        print(f"\nワークスペース別テーブル数:")
        for workspace, count in workspace_counts.items():
            print(f"  {workspace}: {count} 個")
    
    # Notesテーブルの詳細確認
    notes_tables = filtered_df[filtered_df['view_name'].str.contains('Notes', case=False, na=False)]
    if not notes_tables.empty:
        print(f"\n対象Notesテーブル ({len(notes_tables)} 個):")
        for _, row in notes_tables.iterrows():
            print(f"  - {row['view_name']}")
    
    # 結果を保存
    filtered_df.to_excel('filtered_target_tables.xlsx', index=False)
    print(f"\n✓ フィルタ結果を filtered_target_tables.xlsx に保存")
    
    # テーブル名一覧をテキストでも出力
    with open('target_table_list.txt', 'w', encoding='utf-8') as f:
        f.write("=== 対象テーブル一覧 ===\n\n")
        for i, (_, row) in enumerate(filtered_df.iterrows(), 1):
            f.write(f"{i:3d}. {row['view_name']} (ID: {row['view_id']})\n")
    
    print(f"✓ テーブル名一覧を target_table_list.txt に保存")
    
    return len(filtered_df)

if __name__ == "__main__":
    target_count = filter_target_tables()