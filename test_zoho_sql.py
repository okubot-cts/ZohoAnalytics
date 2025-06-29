import requests
import json
import time

class ZohoAnalyticsQueryTester:
    def __init__(self, access_token, workspace_id, org_id):
        self.access_token = access_token
        self.workspace_id = workspace_id
        self.org_id = org_id
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        
    def get_headers(self):
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
            'ZANALYTICS-ORGID': str(self.org_id)
        }
    
    def execute_sql_query(self, sql_query, output_format='json'):
        """SQLクエリを実行"""
        url = f"{self.base_url}/workspaces/{self.workspace_id}/data"
        
        data = {
            'responseFormat': output_format,
            'sqlQuery': sql_query
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data, timeout=30)
            
            if response.status_code == 200:
                if output_format == 'json':
                    return {'success': True, 'data': response.json()}
                else:
                    return {'success': True, 'data': response.text}
            else:
                return {
                    'success': False, 
                    'error': f"HTTP {response.status_code}: {response.text[:500]}"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_basic_queries(self):
        """基本クエリをテスト"""
        test_queries = [
            {
                'name': '商談基本クエリ',
                'sql': 'SELECT "Deal_Name", "Amount", "Stage" FROM "Deals" LIMIT 5;'
            },
            {
                'name': '連絡先基本クエリ', 
                'sql': 'SELECT "First_Name", "Last_Name", "Email" FROM "Contacts" LIMIT 5;'
            },
            {
                'name': '取引先基本クエリ',
                'sql': 'SELECT "Account_Name", "Phone" FROM "Accounts" LIMIT 5;'
            },
            {
                'name': '商談件数確認',
                'sql': 'SELECT COUNT(*) as total_deals FROM "Deals";'
            }
        ]
        
        results = []
        print("=== Zoho Analytics SQLテスト ===\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. {query['name']}")
            print(f"   SQL: {query['sql']}")
            
            result = self.execute_sql_query(query['sql'])
            
            if result['success']:
                print("   ✓ 成功")
                if 'data' in result and isinstance(result['data'], dict):
                    # データの簡単な表示
                    data = result['data']
                    if 'data' in data and 'rows' in data['data']:
                        row_count = len(data['data']['rows'])
                        print(f"   📊 取得行数: {row_count}")
                        if row_count > 0:
                            print(f"   📝 サンプル: {data['data']['rows'][0]}")
                    elif 'rows' in data:
                        row_count = len(data['rows'])
                        print(f"   📊 取得行数: {row_count}")
                else:
                    print(f"   📊 レスポンス: {str(result['data'])[:100]}...")
            else:
                print(f"   ✗ 失敗: {result['error']}")
            
            results.append({
                'query': query['name'],
                'sql': query['sql'],
                'success': result['success'],
                'error': result.get('error') if not result['success'] else None
            })
            
            print()
            time.sleep(1)  # レート制限対策
        
        return results
    
    def test_analytics_queries(self):
        """分析クエリをテスト"""
        analytics_queries = [
            {
                'name': '商談ステージ別集計',
                'sql': '''SELECT 
    "Stage",
    COUNT(*) as deal_count,
    SUM(CAST("Amount" as DECIMAL)) as total_amount
FROM "Deals"
WHERE "Amount" IS NOT NULL
GROUP BY "Stage"
ORDER BY total_amount DESC;'''
            },
            {
                'name': '月次商談作成数',
                'sql': '''SELECT 
    DATE_FORMAT("Created_Time", '%Y-%m') as month,
    COUNT(*) as new_deals
FROM "Deals"
GROUP BY DATE_FORMAT("Created_Time", '%Y-%m')
ORDER BY month DESC
LIMIT 6;'''
            }
        ]
        
        print("=== 分析クエリテスト ===\n")
        results = []
        
        for i, query in enumerate(analytics_queries, 1):
            print(f"{i}. {query['name']}")
            print("   SQL:")
            for line in query['sql'].split('\n'):
                print(f"     {line}")
            
            result = self.execute_sql_query(query['sql'])
            
            if result['success']:
                print("   ✓ 実行成功")
                # 結果の詳細表示
                self.display_query_result(result['data'])
            else:
                print(f"   ✗ 実行失敗: {result['error']}")
            
            results.append({
                'query': query['name'],
                'success': result['success'],
                'error': result.get('error') if not result['success'] else None
            })
            
            print()
            time.sleep(1)
        
        return results
    
    def display_query_result(self, data):
        """クエリ結果を表示"""
        try:
            if isinstance(data, dict):
                if 'data' in data and 'rows' in data['data']:
                    rows = data['data']['rows']
                    columns = data['data'].get('columns', [])
                elif 'rows' in data:
                    rows = data['rows']
                    columns = data.get('columns', [])
                else:
                    print(f"   📊 データ: {data}")
                    return
                
                print(f"   📊 取得行数: {len(rows)}")
                
                if columns and len(rows) > 0:
                    # 列名表示
                    col_names = [col.get('columnName', col.get('name', f'col_{i}')) 
                               for i, col in enumerate(columns)]
                    print(f"   📋 列: {', '.join(col_names)}")
                    
                    # 最初の数行を表示
                    for i, row in enumerate(rows[:3]):
                        if isinstance(row, dict):
                            print(f"   📝 行{i+1}: {row}")
                        elif isinstance(row, list):
                            row_dict = dict(zip(col_names, row))
                            print(f"   📝 行{i+1}: {row_dict}")
                        
        except Exception as e:
            print(f"   ⚠️ 結果表示エラー: {e}")
    
    def generate_sql_validation_report(self, results):
        """SQLバリデーションレポートを生成"""
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        report = f"""=== Zoho Analytics SQL実行レポート ===

実行日時: {time.strftime('%Y-%m-%d %H:%M:%S')}
ワークスペースID: {self.workspace_id}
組織ID: {self.org_id}

成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)

詳細結果:
"""
        
        for result in results:
            status = "✓ 成功" if result['success'] else "✗ 失敗"
            report += f"- {result['query']}: {status}\n"
            if not result['success']:
                report += f"  エラー: {result['error']}\n"
        
        if success_count < total_count:
            report += f"""
=== 修正が必要な可能性 ===
- テーブル名の確認 (CRM APIとAnalyticsで異なる場合)
- フィールド名の確認 (大文字小文字、アンダースコア等)
- データ型キャストの調整
- Analytics固有の関数使用
"""
        
        with open('zoho_sql_validation_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print("✓ レポートを zoho_sql_validation_report.txt に保存")

def main():
    # Analytics用トークンと設定
    try:
        with open('zoho_tokens.json', 'r') as f:
            tokens = json.load(f)
        access_token = tokens['access_token']
    except:
        print("エラー: zoho_tokens.jsonが見つかりません")
        return
    
    # ワークスペース設定（実際の値を使用）
    workspace_id = "2527115000001040002"  # Zoho CRMの分析ワークスペース
    org_id = "772044231"
    
    tester = ZohoAnalyticsQueryTester(access_token, workspace_id, org_id)
    
    print("Zoho Analytics SQLクエリテストを開始します...\n")
    
    try:
        # 基本クエリテスト
        basic_results = tester.test_basic_queries()
        
        # 分析クエリテスト
        analytics_results = tester.test_analytics_queries()
        
        # 全結果をまとめてレポート生成
        all_results = basic_results + analytics_results
        tester.generate_sql_validation_report(all_results)
        
    except Exception as e:
        print(f"テスト実行エラー: {e}")

if __name__ == "__main__":
    main()