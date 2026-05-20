from typing import Dict, List
from questions import CATEGORIES


TYPE_DETAILS: Dict[str, Dict[str, object]] = {
    "cognitive_load": {
        "name": "認知過負荷タイプ",
        "summary": "AIの回答量や情報整理に脳の処理容量を使いすぎている状態です。",
        "actions": [
            "AIには『短く、箇条書きで、次の行動まで』と指定する",
            "1回の質問で広げすぎず、1テーマずつ聞く",
            "長文回答を受け取ったら、すぐに要約させてから読む",
        ],
    },
    "verification_fatigue": {
        "name": "確認疲れタイプ",
        "summary": "AIの回答が正しいかを確認し続けることで疲れている状態です。",
        "actions": [
            "重要度で確認レベルを分ける",
            "低リスク作業ではAIを下書き用途に限定する",
            "AIに『不確かな点』『確認が必要な点』を明示させる",
        ],
    },
    "decision_fatigue": {
        "name": "判断疲れタイプ",
        "summary": "AIに案を出させることで、かえって選択肢が増えすぎている状態です。",
        "actions": [
            "AIに出させる案は最大3つまでにする",
            "比較軸を先に決めてからAIに相談する",
            "最後の意思決定は1分以内に仮決めする",
        ],
    },
    "dependency_anxiety": {
        "name": "依存・自信低下タイプ",
        "summary": "AIなしで考えることへの不安や、自分の判断力への不信感が出ている状態です。",
        "actions": [
            "AIに聞く前に自分の仮説を1行書く",
            "AIは答えではなく壁打ち相手として使う",
            "週1回はAIなしで初稿を作る時間を持つ",
        ],
    },
    "info_overload": {
        "name": "情報過多タイプ",
        "summary": "AIツール、ニュース、ノウハウを追いかけすぎて疲れている状態です。",
        "actions": [
            "常用AIツールを3つまでに絞る",
            "AI情報収集の時間を週2回に制限する",
            "『今すぐ使う情報』と『いつか試す情報』を分ける",
        ],
    },
    "physical_fatigue": {
        "name": "身体疲労タイプ",
        "summary": "AI作業が目・肩・頭・睡眠など身体面に影響している状態です。",
        "actions": [
            "AI作業は30分ごとに区切る",
            "長文生成・調査作業は夜遅くにやらない",
            "目や頭痛、不眠が続く場合は専門家に相談する",
        ],
    },
}


GENERAL_RECOMMENDATIONS = [
    "AIに聞く前に、目的を1行で書く",
    "AIには『3案まで』『500字以内』など制約を入れる",
    "重要資料では、AI回答と一次情報を分けて扱う",
    "AI作業は30分単位で区切る",
    "夜遅い時間のAI調査・長文生成を減らす",
]


def get_type_detail(category_key: str) -> Dict[str, object]:
    return TYPE_DETAILS.get(
        category_key,
        {
            "name": CATEGORIES.get(category_key, category_key),
            "summary": "この項目の負荷が高めです。",
            "actions": GENERAL_RECOMMENDATIONS,
        },
    )
