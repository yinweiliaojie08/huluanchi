import pandas as pd
from pathlib import Path

INPUT = "bill.xlsx"
OUTPUT = "billby_product.xlsx"

# 需要输出的列（固定顺序）
OUTPUT_COLS = [
    "支付者UIN", "地域", "产品名称", "项目名称", "计费模式", "国内国际",
    "原价(元)", "优惠后总价(元)", "优惠券支付(元)", "赠送金支付(元)", "分成金支付(元)", "现金支付(元)"
]

# 金额列
AMOUNT_COLS = [
    "原价(元)", "优惠后总价(元)", "优惠券支付(元)",
    "赠送金支付(元)", "分成金支付(元)", "现金支付(元)"
]

GROUP_COLS = ["产品名称"]  # 按产品名称汇总整年

def main():
    src = Path(INPUT)
    if not src.exists():
        raise FileNotFoundError(f"找不到输入文件: {INPUT}")

    # 读入所有列为字符串
    df = pd.read_excel(src, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # 金额列转数值
    for col in AMOUNT_COLS:
        if col in df.columns:
            df[col] = (
                df[col].fillna("0").astype(str)
                .str.replace(r"[^\d\.\-]", "", regex=True)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 按产品名称聚合金额，其他非金额列取第一个值
    agg_dict = {col: "first" for col in OUTPUT_COLS if col not in AMOUNT_COLS}
    for col in AMOUNT_COLS:
        agg_dict[col] = "sum"

    summary = df.groupby(GROUP_COLS, as_index=False).agg(agg_dict)

    # 保证输出列顺序
    summary = summary[[c for c in OUTPUT_COLS if c in summary.columns]]

    # 计算总计行
    total_row = {col: summary[col].sum() if col in AMOUNT_COLS else "总计" for col in summary.columns}
    summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)

    # 导出 Excel
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="原始数据", index=False)
        summary.to_excel(writer, sheet_name="汇总结果", index=False)

    print(f"✅ 完成: {OUTPUT} (整年按产品名称汇总，保留指定列)")

if __name__ == "__main__":
    main()
