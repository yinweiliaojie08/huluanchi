import pandas as pd
from pathlib import Path

INPUT = "new_bill.xlsx"
OUTPUT = "new_bill_summary.xlsx"

# 读取 Excel 并保持所有列
def main():
    src = Path(INPUT)
    if not src.exists():
        raise FileNotFoundError(f"找不到输入文件: {INPUT}")

    df = pd.read_excel(src, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # 自动识别金额列（包含关键字）
    amount_keywords = ["价", "金额", "抵扣", "支付", "税"]
    AMOUNT_COLS = [c for c in df.columns if any(k in c for k in amount_keywords)]

    # 金额列转数值
    for col in AMOUNT_COLS:
        df[col] = df[col].fillna("0").astype(str).str.replace(r"[^\d\.\-]", "", regex=True)
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 分组：按产品整年汇总
    GROUP_COLS = ["产品"] if "产品" in df.columns else [df.columns[0]]

    # 聚合规则：金额列求和，其他列取第一个值
    agg_dict = {col: ("sum" if col in AMOUNT_COLS else "first") for col in df.columns}

    summary = df.groupby(GROUP_COLS, as_index=False).agg(agg_dict)

    # 添加总计行
    total_row = {col: summary[col].sum() if col in AMOUNT_COLS else "总计" for col in summary.columns}
    summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)

    # 导出 Excel
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="原始数据", index=False)
        summary.to_excel(writer, sheet_name="汇总结果", index=False)

    print(f"✅ 完成: {OUTPUT} (整年按产品汇总，列数与原始数据一致)")

if __name__ == "__main__":
    main()
