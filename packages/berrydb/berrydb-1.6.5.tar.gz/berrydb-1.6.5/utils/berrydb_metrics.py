from enum import Enum

class Metrics(Enum):
  answer_relevancy = ["AnswerRelevancyMetric"]
  faithfulness = ["FaithfulnessMetric"]
  contextual_precision = ["ContextualPrecisionMetric"]
  contextual_recall = ["ContextualRecallMetric"]
  contextual_relevancy = ["ContextualRelevancyMetric"]
  hallucination_metric = ["HallucinationMetric"]
  retrieval = ["ContextualPrecisionMetric", "ContextualRecallMetric", "ContextualRelevancyMetric"]
  generation = ["AnswerRelevancyMetric", "FaithfulnessMetric"]