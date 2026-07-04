---
tags:
  - Machine Learning
  - Remote Sensing
  - Classification Metrics
  - Accuracy Assessment
---

# Precision, Recall, and Classification Intuition

## Why These Terms Feel Confusing

Different communities often use different vocabulary for the same underlying ideas.

- Machine learning talks about:
  - false positives
  - false negatives
  - precision
  - recall

- Remote sensing often talks about:
  - omission error
  - commission error
  - producer's accuracy
  - user's accuracy

The goal of this note is to build a simple conceptual understanding that remains intuitive even months later.

---

## Start with the Main Idea

Suppose we are interested in detecting something:

- water
- cancer
- flood extent
- glacier pixels
- spam email
- defects in manufacturing

The thing we are interested in detecting is called the **positive class**.

Everything else is the **negative class**.

For example:

```text
Positive  = water
Negative  = non-water
```

or

```text
Positive  = cancer
Negative  = healthy
```

This simple framing makes the rest of the terminology much easier.

---

## Core Classification Outcomes

### Mental Model

A classifier compares:

```text
REALITY  --->  MODEL PREDICTION
```

The prediction can either agree or disagree with reality.

---

## The Four Possible Outcomes

| Reality | Prediction | ML Term | Remote Sensing Term | Intuition |
|---|---|---|---|---|
| Positive | Positive | True Positive (TP) | Correct detection | Correctly found the phenomenon |
| Positive | Negative | False Negative (FN) | Omission error | Missed phenomenon / falsely predicted as negative |
| Negative | Positive | False Positive (FP) | Commission error | False alarm / false inclusion |
| Negative | Negative | True Negative (TN) | Correct rejection | Correctly ignored non-target |

---

## False Negative (FN): The Most Important Intuition

A false negative occurs when:

```text
Something truly positive
is falsely predicted as negative.
```

Example:

```text
Reality:     Water
Prediction:  Non-water
```

The water existed.
The classifier missed it.

This is:

- a False Negative (FN)
- an omission error
- a missed detection

### Cancer Example

```text
Reality:     Cancer exists
Prediction:  Healthy
```

The disease existed, but the detector failed to identify it.

---

## False Positive (FP)

A false positive occurs when:

```text
Something truly negative
is falsely predicted as positive.
```

Example:

```text
Reality:     Road or shadow
Prediction:  Water
```

This is:

- a False Positive (FP)
- a commission error
- a false alarm

---

## Recall and Precision

| Concept | Question | Equation | Core Intuition |
|---|---|---|---|
| Recall | Out of all real positive cases, how many did we recover? | Recall = TP / (TP + FN) | Completeness / sensitivity |
| Precision | Out of everything predicted as positive, how many were actually positive? | Precision = TP / (TP + FP) | Purity / trustworthiness |

Notice that both metrics share the same numerator:

```text
TP = correctly detected positive cases
```

The denominator changes:

- Recall is anchored to reality.
- Precision is anchored to model predictions.

---

## Why Not Just Use Accuracy?

Accuracy is the most familiar metric:

```text
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

It answers a simple question: out of everything, how much did the classifier get right?

That question becomes misleading the moment the positive class is rare, which is the normal case in remote sensing and many real-world detection problems.

Suppose flood pixels make up 1% of an image. A classifier that predicts:

```text
Everything is non-flood.
```

gets every non-flood pixel right and every flood pixel wrong. Yet:

```text
Accuracy = 99%
```

The classifier never once detected the actual phenomenon of interest, and the headline number still looks excellent.

This is the same failure mode as the earlier "everything is water" example, just measured with the wrong metric:

- Recall = 0% (no flood pixels recovered) — correctly exposes the failure
- Accuracy = 99% — hides the failure entirely

The rarer the positive class, the more accuracy rewards a model for ignoring it. This is exactly why:

- cancer screening,
- flood mapping,
- glacier/ice detection,
- fraud and defect detection,

are never evaluated with plain accuracy. In each of these, the positive class is rare relative to the negative class, so accuracy stays high even when the model is essentially non-functional. Precision and recall are anchored to the positive class specifically (TP, FN, FP), which is what makes them resistant to this failure mode.

**Rule of thumb**: whenever the phenomenon of interest is rare compared to everything else in the dataset, accuracy alone is not a trustworthy metric. Reach for recall, precision, and F1 instead.

---

## Flood Mapping Example

Suppose we are mapping flood extent after a hurricane.

Missing flooded areas can be dangerous:

- rescue teams may miss affected regions
- risk estimates become too low
- emergency response becomes incomplete

In this situation, high recall is often preferred.

---

## Extreme Recall Example

Suppose a classifier predicts:

```text
Everything is water.
```

Then:

- no water pixels are missed
- recall becomes very high (possibly 100%)

But many non-water pixels are also incorrectly classified as water.

So:

- high recall alone is not enough

---

## Medical Screening Intuition

In medicine, missing a dangerous disease is often considered worse than temporarily flagging healthy individuals for additional testing.

During the early stages of the COVID-19 pandemic, many public-health strategies emphasized avoiding missed cases, illustrating a high-recall mindset.

---

## Spam Email Example

Suppose a spam filter incorrectly sends important emails into the spam folder.

Users quickly lose trust in the system.

In this case:

- high precision matters strongly
- emails classified as spam should truly be spam

---

## Extreme Precision Example

Suppose a model predicts only one water pixel in an entire image.

If that single pixel is truly water:

```text
Precision = 100%
```

But almost all real water pixels were missed.

So:

```text
Recall ≈ 0
```

This shows:

- precision alone is also not enough

---

## Why We Need Both Precision and Recall

| Goal | Metric |
|---|---|
| Capture as much real phenomenon as possible | Recall |
| Ensure detections are trustworthy | Precision |

A good classifier usually needs balance between both.

---

## F1 Score

The F1 score combines precision and recall into a single metric.

```math
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

The F1 score becomes low when either:

- precision is poor
- recall is poor

This prevents "cheating" by:

- predicting everything positive
- or predicting almost nothing positive

Conceptually:

```text
F1 rewards models that are both:
- complete
- trustworthy
```

---

## Vocabulary Bridge

| Scientific / Remote Sensing Language | ML / Statistics Language | Core Meaning |
|---|---|---|
| Omission error | False Negative (FN) | Missed positive phenomenon |
| Commission error | False Positive (FP) | False inclusion / false alarm |
| Producer's accuracy | Recall | How much real phenomenon was captured |
| User's accuracy | Precision | How trustworthy detections are |
| Completeness | Recall | Detection coverage |
| Purity | Precision | Detection quality |

---

## Mental Model Summary

### Recall

```text
Did we capture the real phenomenon?
```

Recall penalizes:

- missed detections
- omission errors
- false negatives

---

### Precision

```text
Can we trust our predictions?
```

Precision penalizes:

- false alarms
- commission errors
- false positives

---

## Final Conceptual Takeaway

A classifier is fundamentally making decisions about:

```text
what belongs to the phenomenon of interest
and what does not.
```

Once the positive class is clearly defined:

- false negatives become missed positives
- false positives become false alarms
- recall measures completeness
- precision measures trustworthiness

Understanding these concepts intuitively is far more valuable than memorizing formulas.
