#!/usr/bin/env python3
"""
商談階層構造分析結果のサマリ表示
エラーが発生したため、結果のみ表示
"""

def display_hierarchy_findings():
    """階層分析の重要な発見を表示"""
    
    print("="*70)
    print("📊 ZohoCRM 商談階層構造分析 - 重要な発見")
    print("="*70)
    
    print("\n🔍 【重要な発見】")
    
    print("\n1. ✅ 明確な親子構造パターンが存在")
    print("   - 商談名によるグループ化：13グループ、43件の商談")
    print("   - 命名規則：「会社名_担当者名_期間」のパターン")
    
    print("\n2. ✅ 「Group」フィールドが存在")
    print("   - API名：Group")
    print("   - ラベル：グループ")  
    print("   - タイプ：picklist（選択リスト）")
    print("   - 現在のサンプルでは値が設定されていない")
    
    print("\n3. 📋 主要な親子構造パターン:")
    
    hierarchy_examples = [
        {
            "pattern": "村田製作所",
            "deals": 9,
            "total": 36400,
            "parent": "村田製作所_武市 真輝_2025上期（他社経由）",
            "parent_amount": 36400,
            "children": ["倉田 洋行", "竹内 裕太", "竹内 陸（他8件）"]
        },
        {
            "pattern": "中央精機株式会社", 
            "deals": 2,
            "total": 716000,
            "parent": "中央精機株式会社_赴任前_吉野 和晃(英語)",
            "parent_amount": 358000,
            "children": ["吉野 和音(英語)"]
        },
        {
            "pattern": "ANAAS",
            "deals": 4, 
            "total": 63745,
            "parent": "ANAAS_後藤 里奈_202509",
            "parent_amount": 26250,
            "children": ["北川 由梨", "石川 瑞紀", "中村 謙斗"]
        }
    ]
    
    for i, example in enumerate(hierarchy_examples, 1):
        print(f"\n   {i}. {example['pattern']}グループ")
        print(f"      商談数: {example['deals']}件")
        print(f"      合計金額: ¥{example['total']:,.0f}")
        print(f"      親商談: {example['parent']} (¥{example['parent_amount']:,.0f})")
        print(f"      子商談: {', '.join(example['children'])}")
    
    print("\n4. 🔍 階層構造の特徴:")
    print("   ✅ 同一企業内での複数担当者案件")
    print("   ✅ 研修・教育サービスの個人別契約")
    print("   ✅ 期間・プロジェクト単位でのグループ化")
    print("   ✅ 親商談が最大金額を持つ傾向")
    
    print("\n5. ⚠️  課題と限界:")
    print("   - 現在のデータで請求書との直接関連は確認できず")
    print("   - Groupフィールドが活用されていない")
    print("   - 商談名による暗黙的なグループ化に依存")
    
    print("\n6. 💡 請求書への影響（推測）:")
    print("   【パターンA: 親商談一括請求】")
    print("   - 親商談のreference_numberで一括請求")
    print("   - 子商談は請求書作成対象外")
    
    print("\n   【パターンB: 個別請求後の統合】")
    print("   - 各子商談で個別に請求書作成")
    print("   - 経理処理で親商談単位に統合")
    
    print("\n   【パターンC: 混在パターン】")
    print("   - 企業・案件により使い分け")
    print("   - 契約形態に応じて柔軟に対応")
    
    print("\n7. 🎯 推奨改善策:")
    print("   ✅ Groupフィールドの積極活用")
    print("   ✅ 親商談IDを子商談に明示的に記録")
    print("   ✅ 請求書作成時の親子関係考慮")
    print("   ✅ レポート機能での階層表示対応")
    
    print("\n" + "="*70)
    print("📝 結論:")
    print("ZohoCRMでは商談名による暗黙的な親子構造が存在し、")
    print("請求処理においても親商談を中心とした処理が行われている可能性が高い。")
    print("Groupフィールドの活用により、より明示的な階層管理が可能。")
    print("="*70)

if __name__ == "__main__":
    display_hierarchy_findings()