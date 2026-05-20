from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    category: str


CATEGORIES = {
    "cognitive_load": "認知過負荷",
    "verification_fatigue": "確認疲れ",
    "decision_fatigue": "判断疲れ",
    "dependency_anxiety": "依存・自信低下",
    "info_overload": "情報過多",
    "physical_fatigue": "身体疲労",
}


QUESTIONS: List[Question] = [
    Question("q01", "AIの回答を読むだけで疲れることがある", "cognitive_load"),
    Question("q02", "AIに聞くほど、逆に考えることが増えていると感じる", "cognitive_load"),
    Question("q03", "AIの長い回答を整理するだけで時間を使ってしまう", "cognitive_load"),

    Question("q04", "AIの回答が正しいか確認するのに疲れる", "verification_fatigue"),
    Question("q05", "AIの出力をそのまま使うのが不安で、毎回かなり確認している", "verification_fatigue"),
    Question("q06", "AIの回答に誤りがないか気になって作業が止まることがある", "verification_fatigue"),

    Question("q07", "AIに複数案を出させた結果、選ぶのがしんどい", "decision_fatigue"),
    Question("q08", "AIに相談するほど選択肢が増えて、決めにくくなる", "decision_fatigue"),

    Question("q09", "AIを使わないと不安になることがある", "dependency_anxiety"),
    Question("q10", "自分で考える前に、まずAIに聞いてしまう", "dependency_anxiety"),
    Question("q11", "AIを使っているのに、自分の実力が落ちているように感じることがある", "dependency_anxiety"),

    Question("q12", "新しいAIツールや機能を追いかけるのが負担に感じる", "info_overload"),
    Question("q13", "AI活用の情報収集だけで疲れることがある", "info_overload"),
    Question("q14", "どのAIツールを使うべきか迷うことが多い", "info_overload"),

    Question("q15", "AI作業後に目・肩・頭が疲れていることが多い", "physical_fatigue"),
    Question("q16", "AIを使っていると作業の区切りがつきにくく、休憩が遅れる", "physical_fatigue"),
]


CHOICES = {
    "まったくない": 0,
    "あまりない": 1,
    "ときどきある": 2,
    "よくある": 3,
    "かなりある": 4,
}
