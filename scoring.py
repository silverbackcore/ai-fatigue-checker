from typing import Dict, List, Tuple
from questions import QUESTIONS, CATEGORIES


def calculate_scores(answers: Dict[str, int]) -> Dict:
    """回答値から合計点、100点換算、カテゴリ別スコア、判定を返す。"""
    max_total = len(QUESTIONS) * 4
    total = sum(int(answers.get(q.id, 0)) for q in QUESTIONS)
    score_100 = round((total / max_total) * 100)

    category_raw = {key: 0 for key in CATEGORIES}
    category_max = {key: 0 for key in CATEGORIES}

    for q in QUESTIONS:
        category_raw[q.category] += int(answers.get(q.id, 0))
        category_max[q.category] += 4

    category_scores = {
        key: round((category_raw[key] / category_max[key]) * 100) if category_max[key] else 0
        for key in CATEGORIES
    }

    risk = judge_risk(score_100)
    top_types = determine_top_types(category_scores)

    return {
        "total": total,
        "max_total": max_total,
        "score_100": score_100,
        "category_scores": category_scores,
        "risk": risk,
        "top_types": top_types,
    }


def judge_risk(score_100: int) -> Dict[str, str]:
    """100点換算スコアからリスク帯を判定する。"""
    if score_100 <= 25:
        return {
            "level": "低リスク",
            "label": "健全に使えている傾向",
            "message": "現時点ではAI利用による負荷は比較的低めです。今の使い方を保ちながら、休憩と確認ルールを整えるとさらに安定します。",
        }
    if score_100 <= 50:
        return {
            "level": "注意",
            "label": "軽度のAI疲れ傾向",
            "message": "AI利用による疲労が少し出始めている可能性があります。使う場面、時間、確認範囲を決めると改善しやすい状態です。",
        }
    if score_100 <= 75:
        return {
            "level": "高負荷",
            "label": "中度のAI疲れ傾向",
            "message": "AI利用が便利な一方で、確認・判断・情報処理の負荷が高くなっている可能性があります。AI利用ルールの見直しをおすすめします。",
        }
    return {
        "level": "要リセット",
        "label": "強いAI疲れ傾向",
        "message": "AI利用による負荷がかなり高い状態かもしれません。短期的にAI利用量を減らし、休憩・睡眠・作業設計を優先してください。",
    }


def determine_top_types(category_scores: Dict[str, int], limit: int = 2) -> List[Tuple[str, int]]:
    """カテゴリ別スコアの上位を返す。"""
    sorted_items = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_items[:limit]


def make_ai_usage_rules(category_scores: Dict[str, int]) -> List[str]:
    """カテゴリスコアに応じた個人向けAI利用ルールを生成する。"""
    rules = []

    if category_scores.get("cognitive_load", 0) >= 50:
        rules.append("AIには『結論→理由→次の一手』の順で短く回答させる。")
        rules.append("長文回答を避けるため、最初から『500字以内』などの制限を入れる。")

    if category_scores.get("verification_fatigue", 0) >= 50:
        rules.append("重要度の高い作業だけ一次情報を確認し、低リスク作業は下書き用途に限定する。")
        rules.append("AIの回答には『根拠・前提・不確かな点』を必ず分けて出させる。")

    if category_scores.get("decision_fatigue", 0) >= 50:
        rules.append("AIに出させる選択肢は最大3案までにする。")
        rules.append("AIに聞く前に、判断基準を3つだけ先に書く。")

    if category_scores.get("dependency_anxiety", 0) >= 50:
        rules.append("AIに聞く前に、自分の仮説を1行だけ書く。")
        rules.append("週1回はAIなしで文章・設計・企画の初稿を作る。")

    if category_scores.get("info_overload", 0) >= 50:
        rules.append("常用するAIツールを3つまでに絞る。")
        rules.append("AIニュースや新ツール調査は週2回までにする。")

    if category_scores.get("physical_fatigue", 0) >= 50:
        rules.append("AI作業は30分単位で区切り、目・肩・首を休ませる。")
        rules.append("夜遅い時間のAI調査・長文生成を減らす。")

    if not rules:
        rules.append("AIに聞く前に目的を1行で書き、回答後は次の行動を1つだけ決める。")
        rules.append("AI作業は時間を区切り、画面から目を離す休憩を入れる。")

    # 重複除去しつつ最大6件に制限
    unique_rules = []
    for rule in rules:
        if rule not in unique_rules:
            unique_rules.append(rule)

    return unique_rules[:6]
