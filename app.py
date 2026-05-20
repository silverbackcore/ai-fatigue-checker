from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

from questions import QUESTIONS, CHOICES, CATEGORIES
from recommendations import get_type_detail, GENERAL_RECOMMENDATIONS
from scoring import calculate_scores, make_ai_usage_rules


APP_TITLE = "AI疲れセルフチェック"
HISTORY_FILE = Path("data/history.csv")


def init_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 1.2rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.13), rgba(14, 165, 233, 0.10));
            border: 1px solid rgba(99, 102, 241, 0.20);
            margin-bottom: 1rem;
        }
        .notice {
            padding: 0.9rem 1rem;
            border-radius: 0.8rem;
            border-left: 5px solid #f59e0b;
            background: rgba(245, 158, 11, 0.10);
            margin: 0.8rem 0 1.2rem 0;
        }
        .result-card {
            padding: 1.2rem;
            border-radius: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.35);
            background: rgba(248, 250, 252, 0.60);
            margin-bottom: 1rem;
        }
        .small-muted {
            color: #64748b;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_history_file() -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        with HISTORY_FILE.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "user_name",
                    "score_100",
                    "risk_level",
                    *[f"category_{key}" for key in CATEGORIES.keys()],
                ]
            )


def save_history(user_name: str, result: Dict) -> None:
    ensure_history_file()
    row = [
        datetime.now().isoformat(timespec="seconds"),
        user_name,
        result["score_100"],
        result["risk"]["level"],
        *[result["category_scores"][key] for key in CATEGORIES.keys()],
    ]
    with HISTORY_FILE.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def load_history() -> pd.DataFrame:
    ensure_history_file()
    try:
        return pd.read_csv(HISTORY_FILE)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def render_sidebar() -> str:
    st.sidebar.title("🧠 AI疲れチェック")
    st.sidebar.caption("AI利用による負荷傾向をセルフチェックします。")

    user_name = st.sidebar.text_input("名前またはニックネーム", value="ゲスト")
    st.sidebar.divider()

    st.sidebar.markdown("### 判定項目")
    for label in CATEGORIES.values():
        st.sidebar.write(f"- {label}")

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **注意**  
        このアプリは医療診断ではありません。  
        強い不眠、不安、抑うつ、頭痛などが続く場合は、医療・心理の専門家に相談してください。
        """
    )
    return user_name.strip() or "ゲスト"


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🧠 AI疲れセルフチェック</h1>
            <p>
            ChatGPT、Claude、Gemini、Copilotなどの生成AI利用による
            <b>確認疲れ・判断疲れ・情報過多・依存不安・身体疲労</b>を可視化します。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notice">
        この結果は、現在のAI利用による負荷傾向を示すセルフチェックです。
        医療上の診断ではありません。
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_questionnaire() -> Dict[str, int]:
    st.subheader("1. 質問に回答してください")
    st.caption("直近1〜2週間の状態に近いものを選んでください。")

    answers: Dict[str, int] = {}

    category_to_questions: Dict[str, List] = {}
    for q in QUESTIONS:
        category_to_questions.setdefault(q.category, []).append(q)

    with st.form("diagnosis_form"):
        for category_key, qs in category_to_questions.items():
            st.markdown(f"#### {CATEGORIES[category_key]}")
            for q in qs:
                selected = st.radio(
                    q.text,
                    options=list(CHOICES.keys()),
                    index=2,
                    horizontal=True,
                    key=q.id,
                )
                answers[q.id] = CHOICES[selected]
            st.divider()

        submitted = st.form_submit_button("診断する", use_container_width=True)

    if submitted:
        st.session_state["answers"] = answers
        st.session_state["submitted"] = True

    return answers


def score_color_label(score: int) -> str:
    if score <= 25:
        return "🟢"
    if score <= 50:
        return "🟡"
    if score <= 75:
        return "🟠"
    return "🔴"


def render_result(user_name: str, result: Dict) -> None:
    st.subheader("2. 診断結果")

    risk = result["risk"]
    score = result["score_100"]
    icon = score_color_label(score)

    col1, col2, col3 = st.columns([1.1, 1.3, 1.6])
    with col1:
        st.metric("AI疲れ度", f"{score} / 100")
    with col2:
        st.metric("判定", f"{icon} {risk['level']}")
    with col3:
        st.metric("状態", risk["label"])

    st.markdown(
        f"""
        <div class="result-card">
            <h3>{icon} {risk["level"]}：{risk["label"]}</h3>
            <p>{risk["message"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    category_df = pd.DataFrame(
        {
            "カテゴリ": [CATEGORIES[key] for key in result["category_scores"].keys()],
            "スコア": list(result["category_scores"].values()),
            "key": list(result["category_scores"].keys()),
        }
    )

    chart_col1, chart_col2 = st.columns([1.2, 1])
    with chart_col1:
        fig = px.bar(
            category_df,
            x="カテゴリ",
            y="スコア",
            text="スコア",
            range_y=[0, 100],
            title="カテゴリ別スコア",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=None, yaxis_title="スコア / 100")
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        radar_df = category_df.copy()
        radar_df = pd.concat([radar_df, radar_df.iloc[[0]]], ignore_index=True)
        fig = px.line_polar(
            radar_df,
            r="スコア",
            theta="カテゴリ",
            line_close=True,
            range_r=[0, 100],
            title="AI疲れ傾向レーダー",
        )
        fig.update_traces(fill="toself")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 主なタイプ")
    for category_key, category_score in result["top_types"]:
        detail = get_type_detail(category_key)
        st.markdown(f"#### {detail['name']}：{category_score}点")
        st.write(detail["summary"])
        for action in detail["actions"]:
            st.write(f"- {action}")

    st.markdown("### あなた向けAI利用ルール")
    rules = make_ai_usage_rules(result["category_scores"])
    for i, rule in enumerate(rules, start=1):
        st.write(f"{i}. {rule}")

    st.markdown("### まず試す改善アクション")
    for action in GENERAL_RECOMMENDATIONS:
        st.write(f"- {action}")

    save_col1, save_col2 = st.columns([1, 1])
    with save_col1:
        if st.button("この結果を履歴に保存する", use_container_width=True):
            save_history(user_name, result)
            st.success("履歴に保存しました。")
    with save_col2:
        result_text = build_result_text(user_name, result, rules)
        st.download_button(
            "結果をテキストで保存",
            data=result_text,
            file_name=f"ai_fatigue_result_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


def build_result_text(user_name: str, result: Dict, rules: List[str]) -> str:
    lines = [
        "AI疲れセルフチェック結果",
        "=" * 30,
        f"日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"名前: {user_name}",
        f"AI疲れ度: {result['score_100']} / 100",
        f"判定: {result['risk']['level']} - {result['risk']['label']}",
        "",
        "カテゴリ別スコア",
    ]

    for key, value in result["category_scores"].items():
        lines.append(f"- {CATEGORIES[key]}: {value} / 100")

    lines.extend(["", "主なタイプ"])
    for category_key, category_score in result["top_types"]:
        detail = get_type_detail(category_key)
        lines.append(f"- {detail['name']}: {category_score} / 100")
        lines.append(f"  {detail['summary']}")

    lines.extend(["", "あなた向けAI利用ルール"])
    for i, rule in enumerate(rules, start=1):
        lines.append(f"{i}. {rule}")

    lines.extend(
        [
            "",
            "注意",
            "この結果はAI利用による負荷傾向を示すセルフチェックであり、医療診断ではありません。",
            "強い不眠、不安、抑うつ、頭痛などが続く場合は、専門家に相談してください。",
        ]
    )

    return "\n".join(lines)


def render_history() -> None:
    st.subheader("3. 履歴")

    df = load_history()
    if df.empty or len(df) == 0:
        st.info("まだ履歴はありません。診断結果を保存すると、ここに表示されます。")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp")

    st.dataframe(df.tail(20), use_container_width=True, hide_index=True)

    if "score_100" in df.columns:
        fig = px.line(
            df,
            x="timestamp",
            y="score_100",
            markers=True,
            title="AI疲れ度の推移",
        )
        fig.update_layout(xaxis_title="日時", yaxis_title="AI疲れ度 / 100", yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "履歴CSVをダウンロード",
        data=csv_bytes,
        file_name="ai_fatigue_history.csv",
        mime="text/csv",
    )


def render_about() -> None:
    st.subheader("このアプリについて")
    st.markdown(
        """
        このアプリは、生成AIを日常的に使う人が、自分の疲れ方を把握するためのセルフチェックツールです。

        **測定している観点**

        - 認知過負荷
        - 確認疲れ
        - 判断疲れ
        - 依存・自信低下
        - 情報過多
        - 身体疲労

        **想定用途**

        - 個人のAI利用セルフケア
        - 生成AI研修の事前・事後チェック
        - チームのAI導入後の負荷把握
        - 生成AIコンサルのデモアプリ

        **注意**

        このアプリは医療機器ではありません。
        診断、治療、予防を目的とするものではなく、セルフケアの参考情報を提供するものです。
        """
    )


def main() -> None:
    init_page()
    user_name = render_sidebar()
    render_header()

    tab1, tab2, tab3 = st.tabs(["診断", "履歴", "概要"])

    with tab1:
        answers = render_questionnaire()

        if st.session_state.get("submitted"):
            result = calculate_scores(st.session_state.get("answers", answers))
            render_result(user_name, result)
        else:
            st.info("質問に回答して、下部の「診断する」を押してください。")

    with tab2:
        render_history()

    with tab3:
        render_about()


if __name__ == "__main__":
    main()
