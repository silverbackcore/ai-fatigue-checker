from questions import CATEGORIES, QUESTIONS
from scoring import calculate_scores, determine_top_types, judge_risk, make_ai_usage_rules


def answers_with_value(value: int) -> dict[str, int]:
    return {question.id: value for question in QUESTIONS}


def test_judge_risk_boundaries() -> None:
    expected_levels = {
        0: "低リスク",
        25: "低リスク",
        26: "注意",
        50: "注意",
        51: "高負荷",
        75: "高負荷",
        76: "要リセット",
        100: "要リセット",
    }

    for score, expected_level in expected_levels.items():
        assert judge_risk(score)["level"] == expected_level


def test_calculate_scores_all_zero_answers() -> None:
    result = calculate_scores(answers_with_value(0))

    assert result["total"] == 0
    assert result["max_total"] == len(QUESTIONS) * 4
    assert result["score_100"] == 0
    assert result["risk"]["level"] == "低リスク"
    assert result["category_scores"] == {key: 0 for key in CATEGORIES}


def test_calculate_scores_all_max_answers() -> None:
    result = calculate_scores(answers_with_value(4))

    assert result["total"] == len(QUESTIONS) * 4
    assert result["score_100"] == 100
    assert result["risk"]["level"] == "要リセット"
    assert result["category_scores"] == {key: 100 for key in CATEGORIES}


def test_calculate_scores_category_scores_are_independent() -> None:
    answers = answers_with_value(0)
    for question in QUESTIONS:
        if question.category == "decision_fatigue":
            answers[question.id] = 4

    result = calculate_scores(answers)

    assert result["category_scores"]["decision_fatigue"] == 100
    for category in CATEGORIES:
        if category != "decision_fatigue":
            assert result["category_scores"][category] == 0


def test_determine_top_types_respects_limit_and_score_order() -> None:
    category_scores = {
        "cognitive_load": 25,
        "verification_fatigue": 80,
        "decision_fatigue": 60,
    }

    assert determine_top_types(category_scores, limit=2) == [
        ("verification_fatigue", 80),
        ("decision_fatigue", 60),
    ]


def test_make_ai_usage_rules_has_default_rules_for_low_scores() -> None:
    rules = make_ai_usage_rules({key: 0 for key in CATEGORIES})

    assert len(rules) == 2
    assert all(isinstance(rule, str) and rule for rule in rules)
