import pytest

from .classification_model import ClassificationModel
from .memoryset import LabeledMemoryLookup
from .telemetry import ClassificationPrediction, FeedbackCategory


def test_get_prediction(classification_model: ClassificationModel):
    predictions = classification_model.predict(["Do you love soup?", "Are cats cute?"])
    assert len(predictions) == 2
    assert predictions[0].prediction_id is not None
    assert predictions[1].prediction_id is not None
    prediction_with_telemetry = ClassificationPrediction.get(predictions[0].prediction_id)
    assert prediction_with_telemetry is not None
    assert prediction_with_telemetry.label == 0
    assert prediction_with_telemetry.input_value == "Do you love soup?"


def test_get_predictions(classification_model: ClassificationModel):
    predictions = classification_model.predict(["Do you love soup?", "Are cats cute?"])
    assert len(predictions) == 2
    assert predictions[0].prediction_id is not None
    assert predictions[1].prediction_id is not None
    prediction_with_telemetry = ClassificationPrediction.get(
        [predictions[0].prediction_id, predictions[1].prediction_id]
    )
    assert len(prediction_with_telemetry) == 2
    assert prediction_with_telemetry[0].label == 0
    assert prediction_with_telemetry[0].input_value == "Do you love soup?"
    assert prediction_with_telemetry[1].label == 1


def test_get_predictions_with_expected_label_match(classification_model: ClassificationModel):
    classification_model.predict(
        ["Do you love soup?", "Are cats cute?"], expected_labels=[0, 0], tags={"expected_label_match"}
    )
    classification_model.predict("no expectations", tags={"expected_label_match"})
    assert len(classification_model.predictions(tag="expected_label_match")) == 3
    assert len(classification_model.predictions(expected_label_match=True, tag="expected_label_match")) == 1
    assert len(classification_model.predictions(expected_label_match=False, tag="expected_label_match")) == 1


def test_get_prediction_memory_lookups(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    assert isinstance(prediction.memory_lookups, list)
    assert len(prediction.memory_lookups) > 0
    assert all(isinstance(lookup, LabeledMemoryLookup) for lookup in prediction.memory_lookups)


def test_record_feedback(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    assert "correct" not in prediction.feedback
    prediction.record_feedback(category="correct", value=prediction.label == 0)
    assert prediction.feedback["correct"] is True


def test_record_feedback_with_invalid_value(classification_model: ClassificationModel):
    with pytest.raises(ValueError, match=r"Invalid input.*"):
        classification_model.predict("Do you love soup?").record_feedback(category="correct", value="not a bool")  # type: ignore


def test_record_feedback_with_inconsistent_value_for_category(classification_model: ClassificationModel):
    classification_model.predict("Do you love soup?").record_feedback(category="correct", value=True)
    with pytest.raises(ValueError, match=r"Invalid input.*"):
        classification_model.predict("Do you love soup?").record_feedback(category="correct", value=-1.0)


def test_delete_feedback(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    prediction.record_feedback(category="test_delete", value=True)
    assert "test_delete" in prediction.feedback
    prediction.delete_feedback("test_delete")
    assert "test_delete" not in prediction.feedback


def test_list_feedback_categories(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    prediction.record_feedback(category="correct", value=True)
    prediction.record_feedback(category="confidence", value=0.8)
    categories = FeedbackCategory.all()
    assert len(categories) >= 2
    assert any(c.name == "correct" and c.value_type == bool for c in categories)
    assert any(c.name == "confidence" and c.value_type == float for c in categories)


def test_drop_feedback_category(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    prediction.record_feedback(category="test_category", value=True)
    assert any(c.name == "test_category" for c in FeedbackCategory.all())
    FeedbackCategory.drop("test_category")
    assert not any(c.name == "test_category" for c in FeedbackCategory.all())
    prediction.refresh()
    assert "test_category" not in prediction.feedback


def test_update_prediction(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    assert prediction.expected_label is None
    assert prediction.tags == set()
    # update expected label
    prediction.update(expected_label=1)
    assert prediction.expected_label == 1

    # update tags
    prediction.update(tags={"test_tag1", "test_tag2"})
    assert prediction.tags == {"test_tag1", "test_tag2"}

    # update both
    prediction.update(expected_label=0, tags={"new_tag"})
    assert prediction.expected_label == 0
    assert prediction.tags == {"new_tag"}

    # remove expected label
    prediction.update(expected_label=None)
    assert prediction.expected_label is None

    # remove tags
    prediction.update(tags=None)
    assert prediction.tags == set()
