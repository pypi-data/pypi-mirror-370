from enum import Enum

class EvalMetrics(str, Enum):
    ANSWER_RELEVANCY = "answer_relevancy"
    FAITHFULNESS = "faithfulness"
    CONTEXTUAL_PRECISION = "contextual_precision"
    CONTEXTUAL_RECALL = "contextual_recall"
    CONTEXTUAL_RELEVANCY = "contextual_relevancy"
    HALLUCINATION_METRIC = "hallucination_metric"
    RETRIEVAL = "retrieval"
    GENERATION = "generation"