#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終的なワークフローテストスクリプト
"""

import requests
import json

def test_final_workflow():
    """最終的なワークフローをテスト"""
    
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    
    print("=== 最終的なZohoCRM認証ワークフローテスト ===\n")
    
    try:
        # 認証テスト
        test_url = f"{N8N_BASE_URL}/webhook/zoho-auth"
        test_data = {
            "action": "test_auth",
            "timestamp": "2025-01-08T22:15:00.000Z"
        }
        
        print("🧪 認証テストを実行中...")
        response = requests.post(
            test_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"認証テストレスポンス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 認証テスト成功")
            print(f"レスポンス: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 認証テスト失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
            
            # リフレッシュトークンテスト
            print("\n🔄 リフレッシュトークンテストを実行中...")
            refresh_data = {
                "action": "refresh_token",
                "timestamp": "2025-01-08T22:15:00.000Z"
            }
            
            refresh_response = requests.post(
                test_url,
                json=refresh_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"リフレッシュテストレスポンス: {refresh_response.status_code}")
            
            if refresh_response.status_code == 200:
                refresh_result = refresh_response.json()
                print("✅ リフレッシュトークンテスト成功")
                print(f"レスポンス: {json.dumps(refresh_result, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ リフレッシュトークンテスト失敗: {refresh_response.status_code}")
                print(f"レスポンス: {refresh_response.text}")
    
    except Exception as e:
        print(f"❌ テストエラー: {e}")

def create_summary():
    """セットアップ完了サマリーを作成"""
    
    summary = """
# ZohoCRM認証ワークフローセットアップ完了

## 作成されたワークフロー
- **ワークフローID**: Rl7gREpA6d0QvyYA
- **ワークフロー名**: Zoho CRM - Final Auth System
- **Webhook URL**: https://cts-automation.onrender.com/webhook/zoho-auth
- **認証情報ID**: 1pqBixOsaWZ0tiLn (ZohoCTS)

## 機能
✅ ZohoCRM認証テスト
✅ リフレッシュトークン自動更新
✅ エラーハンドリング
✅ ルーティング機能

## 使用方法

### 認証テスト
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-auth \\
  -H "Content-Type: application/json" \\
  -d '{"action": "test_auth"}'
```

### リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-auth \\
  -H "Content-Type: application/json" \\
  -d '{"action": "refresh_token"}'
```

## 注意事項
- ワークフローは作成済みですが、手動でアクティブ化が必要です
- n8nダッシュボードでワークフローを有効化してください
- 認証情報は既存のものを使用しています

## 次のステップ
1. n8nダッシュボードにアクセス
2. ワークフロー「Zoho CRM - Final Auth System」を開く
3. ワークフローをアクティブ化
4. 上記のcurlコマンドでテスト実行
"""
    
    print(summary)

def main():
    """メイン実行関数"""
    test_final_workflow()
    create_summary()

if __name__ == "__main__":
    main() 