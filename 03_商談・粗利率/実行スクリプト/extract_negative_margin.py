import pandas as pd
import numpy as np
import re

def clean_currency(value):
    """通貨文字列（¥ 123,456）を数値に変換"""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    
    # 文字列の場合、通貨記号とカンマを除去
    cleaned = re.sub(r'[¥\s,，]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return np.nan

# Excelファイルを読み込み（正しいパスに修正）
df = pd.read_excel('../データ/2025年1月以降_商談_商品内訳_レポート_計算式付き.xlsx')

print('数値列の値を確認:')
print(f'小計の例: {df["小計"].dropna().head(3).tolist()}')
print(f'原価の例: {df["原価（税別）"].dropna().head(3).tolist()}')

# 通貨データを数値に変換
df['小計_数値'] = df['小計'].apply(clean_currency)
df['原価_数値'] = df['原価（税別）'].apply(clean_currency)

# 有効なデータを抽出
valid_data = df[(df['小計_数値'].notna()) & (df['原価_数値'].notna()) & (df['小計_数値'] != 0)].copy()
print(f'\n計算可能なデータ: {len(valid_data)}件')

if len(valid_data) > 0:
    # 粗利と粗利率を計算
    valid_data['粗利_計算'] = valid_data['小計_数値'] - valid_data['原価_数値']
    valid_data['粗利率_計算'] = (valid_data['粗利_計算'] / valid_data['小計_数値']) * 100
    
    print('\n粗利率の統計:')
    print(valid_data['粗利率_計算'].describe())
    
    # マイナス粗利率を抽出
    negative_margin = valid_data[valid_data['粗利率_計算'] < 0]
    print(f'\n粗利率がマイナスの件数: {len(negative_margin)}件')
    
    if len(negative_margin) > 0:
        print('\n粗利率がマイナスのデータ:')
        display_cols = ['商談名', '商品名', '小計', '原価（税別）', '粗利_計算', '粗利率_計算']
        result = negative_margin[display_cols].copy()
        result['粗利_計算'] = result['粗利_計算'].round(0)
        result['粗利率_計算'] = result['粗利率_計算'].round(2)
        print(result.to_string(index=False))
        
        # CSVファイルとして保存
        negative_margin.to_csv('../データ/粗利率マイナス_抽出結果.csv', index=False, encoding='utf-8-sig')
        print('\n結果を「粗利率マイナス_抽出結果.csv」に保存しました')
    else:
        print('\n粗利率がマイナスのデータはありませんでした')
        
    # 参考：粗利率の分布
    print(f'\n全体の粗利率分布:')
    print(f'  最小値: {valid_data["粗利率_計算"].min():.2f}%')
    print(f'  最大値: {valid_data["粗利率_計算"].max():.2f}%')
    print(f'  平均値: {valid_data["粗利率_計算"].mean():.2f}%')
    print(f'  中央値: {valid_data["粗利率_計算"].median():.2f}%')
else:
    print('\n計算に必要なデータがありません')