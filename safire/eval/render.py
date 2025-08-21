# =============================================================================
#  Safire Project - Library for testing of language models for jailbreaking
#
#  Description:
#      This module containsfunction to output Summary to a cell
#      The module is completely vibe-coding (!!!)
#
#  License:
#      This code is licensed under the MIT License.
#      See the LICENSE file in the project root for full license text.
#
#  Author:
#      ChatGPT-5
# =============================================================================

from IPython.display import HTML
import pandas as pd
from datetime import datetime

def render_eval_summary(df: pd.DataFrame) -> HTML:
    """
    Render a short HTML summary of run_eval results.
    Expects DataFrame with columns:
      - attack_name (str)
      - model_response (str)
      - result (optional: bool/int/str/dict)
    """

    # ---------- Colors ----------
    C_LIGHT = "#02A0FF"  # light blue
    C_BLUE  = "#130AFF"  # blue
    C_VIO   = "#9934FF"  # violet
    GRAD_BG = f"linear-gradient(135deg, {C_LIGHT} 0%, {C_BLUE} 50%, {C_VIO} 100%)"

    # ---------- Helper ----------
    def infer_pass(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            s = value.strip().lower()
            truthy = {"pass", "passed", "success", "successful", "true", "unsafe", "jailbroken"}
            falsy  = {"fail", "failed", "safe", "blocked", "false"}
            if s in truthy: return True
            if s in falsy:  return False
            return None
        if isinstance(value, dict):
            for k in ["passed", "success", "is_jailbroken", "jailbroken", "is_attack_successful", "unsafe"]:
                if k in value:
                    return infer_pass(value[k])
        return None

    # ---------- Stats ----------
    total = len(df)
    if "result" in df.columns:
        judged_mask = df["result"].notna()
    else:
        judged_mask = pd.Series([False] * total, index=df.index)

    judged = int(judged_mask.sum())

    passes, fails = 0, 0
    pass_flags = []

    if "result" in df.columns:
        for v in df["result"].tolist():
            flag = infer_pass(v)
            pass_flags.append(flag)
            if flag is True:
                passes += 1
            elif flag is False:
                fails += 1
    else:
        pass_flags = [None] * total

    pass_rate = (passes / judged * 100.0) if judged else 0.0
    unique_attacks = df["attack_name"].nunique() if "attack_name" in df.columns else 0

    # Per attack stats
    per_attack_top = []
    if "attack_name" in df.columns:
        tmp = df.copy()
        tmp["_flag"] = pass_flags
        grp = tmp.groupby("attack_name")["_flag"].apply(list).reset_index()
        per_attack = []
        for _, row in grp.iterrows():
            flags = row["_flag"]
            succ = sum(1 for f in flags if f is True)
            eva  = sum(1 for f in flags if f is not None)
            rate = (succ / eva * 100.0) if eva else 0.0
            per_attack.append({"name": row["attack_name"], "succ": succ, "eval": eva, "total": len(flags), "rate": rate})
        per_attack.sort(key=lambda x: (x["succ"], x["rate"], x["total"]), reverse=True)
        per_attack_top = per_attack[:5]

    # Examples
    examples_html = ""
    if passes and "attack_name" in df.columns:
        tmp = df.copy()
        tmp["_flag"] = pass_flags
        ex_rows = tmp[tmp["_flag"] == True].head(3)
        items = []
        for _, r in ex_rows.iterrows():
            aname = str(r.get("attack_name", "—"))
            uprompt = str(r.get("user_prompt", ""))
            items.append(f"""
                <div class="ex-item">
                    <div class="ex-title">{aname}</div>
                    <div class="ex-sub">{(uprompt[:180] + '…') if len(uprompt) > 180 else uprompt}</div>
                </div>
            """)
        examples_html = "".join(items)

    prog_width = f"{min(100, max(0, pass_rate)):.2f}%"

    # Top attacks table
    if per_attack_top:
        rows_html = []
        for i, a in enumerate(per_attack_top, start=1):
            rows_html.append(f"""
            <tr>
                <td class="rank">#{i}</td>
                <td class="attack-name">{a['name']}</td>
                <td class="num">{a['succ']}</td>
                <td class="num">{a['eval']}</td>
                <td class="num">{a['total']}</td>
                <td class="rate">{a['rate']:.1f}%</td>
            </tr>
            """)
        top_table_html = f"""
        <table class="top-table">
            <thead>
                <tr>
                    <th class="rank">Rank</th>
                    <th>Attack</th>
                    <th class="num">Success</th>
                    <th class="num">Judged</th>
                    <th class="num">Total</th>
                    <th class="rate">Success %</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
        """
    else:
        top_table_html = '<div class="muted">Not enough data for top list.</div>'

    # ---------- HTML ----------
    html = f"""
    <style>
        .jv-wrap {{
            font-family: ui-sans-serif, Segoe UI, Roboto, Ubuntu, Arial;
            color: #e2e8f0;
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            margin: 8px 0 18px 0;
        }}
        .jv-header {{
            background: {GRAD_BG};
            color: white;
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .jv-badge {{
            background: rgba(255,255,255,0.2);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
        }}
        .jv-title {{
            font-weight: 700;
            font-size: 18px;
        }}
        .jv-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            padding: 16px;
        }}
        .jv-card {{
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 14px;
            background: #1e293b;
        }}
        .jv-card .label {{
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 6px;
        }}
        .jv-card .value {{
            font-size: 24px;
            font-weight: 800;
            line-height: 1.1;
        }}
        .jv-card .sub {{
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }}
        .pill {{
            display: inline-block;
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 999px;
            color: white;
        }}
        .pill-pass {{ background: {C_VIO}; }}
        .pill-fail {{ background: {C_BLUE}; opacity: .9; }}
        .pill-unk  {{ background: {C_LIGHT}; color: #07364d; }}
        .progress {{
            height: 12px;
            border-radius: 999px;
            background: #334155;
            overflow: hidden;
        }}
        .progress > div {{
            height: 100%;
            width: {prog_width};
            background: {GRAD_BG};
        }}
        .section-title {{
            padding: 4px 16px 0 16px;
            font-weight: 700;
            font-size: 14px;
            color: #e2e8f0;
        }}
        .top-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}
        .top-table th, .top-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #334155;
            text-align: left;
            font-size: 13px;
        }}
        .top-table th.rank, .top-table td.rank, .top-table th.num, .top-table td.num {{
            width: 1%;
            text-align: right;
        }}
        .top-table th.rate, .top-table td.rate {{
            text-align: right;
        }}
        .attack-name {{
            max-width: 440px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .muted {{ color: #64748b; padding: 12px 16px; }}
        .examples {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            padding: 8px 16px 16px;
        }}
        .ex-item {{
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            background: #1e293b;
        }}
        .ex-title {{
            font-weight: 700;
            font-size: 13px;
            margin-bottom: 6px;
            color: #f1f5f9;
        }}
        .ex-sub {{
            font-size: 12px;
            color: #94a3b8;
        }}
        @media (max-width: 960px) {{
            .jv-grid {{ grid-template-columns: 1fr; }}
            .examples {{ grid-template-columns: 1fr; }}
        }}
    </style>

    <div class="jv-wrap">
        <div class="jv-header">
            <div class="jv-title">🔐 Jailbreak Evaluation — Summary</div>
            <div class="jv-badge">updated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>

        <div class="jv-grid">
            <div class="jv-card">
                <div class="label">Total attempts</div>
                <div class="value">{total}</div>
                <div class="sub">Unique attacks: {unique_attacks}</div>
            </div>
            <div class="jv-card">
                <div class="label">Judged</div>
                <div class="value">{judged}</div>
                <div class="sub">
                    <span class="pill pill-pass">passed: {passes}</span>
                    &nbsp; <span class="pill pill-fail">failed: {fails}</span>
                </div>
            </div>
            <div class="jv-card">
                <div class="label">Success rate</div>
                <div class="value">{pass_rate:.1f}%</div>
                <div class="sub">
                    <div class="progress"><div></div></div>
                </div>
            </div>
        </div>

        <div class="section-title">🏆 Top attacks by success</div>
        <div style="padding: 0 16px 16px;">
            {top_table_html}
        </div>

        <div class="section-title">🧾 Example successful attacks (up to 3)</div>
        <div class="examples">
            {examples_html if examples_html else '<div class="muted">No successful examples yet.</div>'}
        </div>
    </div>
    """

    return HTML(html)
