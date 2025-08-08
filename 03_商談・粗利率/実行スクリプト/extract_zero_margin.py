#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
粗利率が0のデータを抽出するスクリプト
"""

import pandas as pd
import numpy as np
import re

def clean_currency_string(value):
    """
    通貨文字列を数値に変換
    例: '¥ 75，000' -> 75000
    """
    if pd.isna(value) or value == '' or value == 0:
        return 0
    
    # 文字列の場合のみ処理
    if isinstance(value, str):
        # ¥記号、スペース、全角・半角カンマを除去
        cleaned = re.sub(r'[¥,，\s]', '', value)
        try:
            return float(cleaned)
        except ValueError:
            print(f"変換エラー: '{value}' -> '{cleaned}'")
            return 0
    
    # 既に数値の場合はそのまま返す
    return float(value) if not pd.isna(value) else 0

def main():
    # Excelファイルを読み込み
    file_path = '2025年1月以降_商談_商品内訳_レポート_計算式付き.xlsx'
    df = pd.read_excel(file_path)
    
    print(f"総データ数: {len(df)}")
    print(f"小計データがある行数: {df['小計'].notna().sum()}")
    print(f"原価データがある行数: {df['原価（税別）'].notna().sum()}")
    
    # 小計と原価が両方とも存在する行のみを抽出
    valid_data = df[(df['小計'].notna()) & (df['原価（税別）'].notna())].copy()
    print(f"小計と原価の両方がある行数: {len(valid_data)}")
    
    if len(valid_data) == 0:
        print("計算可能なデータが見つかりませんでした。")
        return
    
    # 通貨文字列を数値に変換
    valid_data['小計_数値'] = valid_data['小計'].apply(clean_currency_string)
    valid_data['原価_数値'] = valid_data['原価（税別）'].apply(clean_currency_string)
    
    # 粗利と粗利率を計算
    valid_data['計算済み粗利'] = valid_data['小計_数値'] - valid_data['原価_数値']
    
    # 小計が0でない行のみで粗利率を計算（ゼロ除算を避ける）
    valid_data['計算済み粗利率'] = np.where(
        valid_data['小計_数値'] != 0,
        (valid_data['計算済み粗利'] / valid_data['小計_数値']) * 100,
        np.nan
    )
    
    # 粗利率が0またはマイナスの行を抽出
    zero_or_negative_margin = valid_data[
        (valid_data['計算済み粗利率'] <= 0) & 
        (valid_data['計算済み粗利率'].notna())
    ]
    
    print(f"\n粗利率が0以下の行数: {len(zero_or_negative_margin)}")
    
    if len(zero_or_negative_margin) > 0:
        # 結果を表示
        result_columns = [
            'データID', '商談名', '商品名', '小計', '原価（税別）', 
            '小計_数値', '原価_数値', '計算済み粗利', '計算済み粗利率'
        ]
        
        print("\n粗利率が0以下のデータ:")
        print("=" * 100)
        for idx, row in zero_or_negative_margin.iterrows():
            print(f"行番号: {idx + 1}")
            print(f"商談名: {row['商談名']}")
            print(f"商品名: {row['商品名']}")
            print(f"小計: {row['小計']} ({row['小計_数値']:,.0f}円)")
            print(f"原価: {row['原価（税別）']} ({row['原価_数値']:,.0f}円)")
            print(f"粗利: {row['計算済み粗利']:,.0f}円")
            print(f"粗利率: {row['計算済み粗利率']:.2f}%")
            print("-" * 80)
        
        # CSVファイルとして出力
        output_filename = '粗利率0以下のデータ.csv'
        zero_or_negative_margin[result_columns].to_csv(
            output_filename, 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"\n結果を '{output_filename}' に保存しました。")
        
        # Excelファイルとしても出力
        excel_filename = '粗利率0以下のデータ.xlsx'
        zero_or_negative_margin[result_columns].to_excel(
            excel_filename, 
            index=False, 
            engine='openpyxl'
        )
        print(f"結果を '{excel_filename}' にも保存しました。")
        
    else:
        print("粗利率が0以下のデータは見つかりませんでした。")
    
    # 統計情報を表示
    print(f"\n統計情報:")
    print(f"平均粗利率: {valid_data['計算済み粗利率'].mean():.2f}%")
    print(f"最小粗利率: {valid_data['計算済み粗利率'].min():.2f}%")
    print(f"最大粗利率: {valid_data['計算済み粗利率'].max():.2f}%")

if __name__ == "__main__":
    main()