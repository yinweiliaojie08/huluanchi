import pandas as pd
from pathlib import Path

INPUT = "w.xlsx"
OUTPUT = "w_summary.xlsx"

# 金额列
AMOUNT_COLS = [
    "目录总价", "优惠金额", "优惠券抵扣金额", "抹零金额",
    "应付金额", "已还款金额", "待还款金额"
]

# 分组列
GROUP_COLS = [
    "产品code", "产品名称", "商品code", "商品名称",
    "资源购买账号ID", "资源购买账号", "资源归属账号ID", "资源归属账号","账单状态", "币种"
]

# 想要固定在最前的四个
ACCOUNT_FIRST = [
    "资源购买账号ID", "资源购买账号", "资源归属账号ID", "资源归属账号"
]

def main():
    src = Path(INPUT)
    if not src.exists():
        raise FileNotFoundError(f"找不到输入文件: {INPUT}")

    # 读入所有列为字符串（避免账号ID科学计数法）
    df = pd.read_excel(src, dtype=str)

    orig_cols_raw = df.columns.tolist()
    orig_cols = [c.strip() for c in orig_cols_raw]
    df.columns = orig_cols

    # 金额列转数值
    for col in AMOUNT_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.replace(r"[^\d\.\-]", "", regex=True)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 按分组聚合
    present_amounts = [c for c in AMOUNT_COLS if c in df.columns]
    summary = df.groupby(GROUP_COLS, as_index=False)[present_amounts].sum()

    # 构造导出列顺序
    ordered = []
    for c in ACCOUNT_FIRST:
        if c in summary.columns:
            ordered.append(c)
    for c in GROUP_COLS:
        if c in summary.columns and c not in ordered:
            ordered.append(c)
    for c in orig_cols:
        if c in summary.columns and c not in ordered:
            ordered.append(c)
    for c in summary.columns:
        if c not in ordered:
            ordered.append(c)

    summary = summary[ordered]

    # ✅ 导出两个 sheet：原始数据 + 汇总结果
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="原始数据", index=False)
        summary.to_excel(writer, sheet_name="汇总结果", index=False)

    print(f"✅ 完成: {OUTPUT} (包含原始数据 + 汇总结果)")

if __name__ == "__main__":
    main()
