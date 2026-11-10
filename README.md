---
emoji: 🚚
title: QuickBite Late Order Check
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.31.0
python_version: "3.12"
app_file: app.py
pinned: false
short_description: Will this order arrive late?
---

# QuickBite Late Order Check

## What it does

QuickBite Late Order Check is a Gradio application that helps dispatchers estimate whether an order will arrive more than 10 minutes late. Dispatchers enter the order details to receive a late-delivery probability and a recommendation on whether to offer the customer a $4 voucher.

Hugging Face Space: **TODO .**

## How to run it locally

Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate lab06-ship-it
```

Start the application:

```bash
python app.py
```

Open the local Gradio URL displayed in the terminal.

## Decisions

The application validates order information before sending it to the prediction model. Values outside the supported ranges and unknown categories are rejected.

| Field | Allowed values | Why |
|---|---|---|
| distance_km | 0.1–30 | Keeps predictions within the supported training-data range. |
| items | 1–20 (whole numbers) | Represents a realistic order size within the supported range. |
| hour | 10–22 (whole numbers) | Limits predictions to the operating hours represented by the model. |
| prep_minutes | 1–60 or empty | Preparation time may not be available when an order is placed. |
| courier_months | 0–120 | Keeps courier experience within the supported range. |
| weather | clear, rain, snow | Only categories supported by the training data are accepted. |
| day_type | weekday, weekend | Uses the two day categories represented in the data. |
| vehicle | bike, scooter, car | Uses the supported delivery vehicle categories. |

**Category validation:** The model's one-hot encoder uses `handle_unknown="ignore"`, which can silently ignore an unseen category. The application therefore validates categories before prediction instead of allowing unsupported values through.

**Snow vs. Snow experiment:** The model was tested directly using `weather="snow"` and then `weather="Snow"`, bypassing the application's input validation. The probability for `"snow"` was **TODO**, while the probability for `"Snow"` was **TODO**. This demonstrates that category spelling and capitalization matter: `"snow"` is a known category, while `"Snow"` is unseen and is ignored by the one-hot encoder. This is why the application rejects unknown categories before prediction.

## Result

The model was evaluated on a held-out test set of 750 orders using a classification threshold of 0.30.

| Metric | Result |
|---|---:|
| Accuracy | 84.13% |
| Precision | 49.07% |
| Recall | 45.30% |
| F1-score | 47.11% |
| ROC-AUC | 0.7962 |

The business cost comparison was:

| Decision policy | Total cost |
|---|---:|
| Flag nobody | $1,755 |
| Flag everybody | $3,000 |
| Model | $1,392 |

Using the model saves **$363 (approximately 21%)** compared with flagging nobody.

## Tests

The automated tests cover prediction validation, probability ranges, voucher decisions, supported categories, model loading, and deployment configuration.

Run the project checks from the repository root:

```bash
python -m ruff format .
python -m ruff check .
python -m pytest
```

## Limitations

The model was trained on 3,000 synthetic QuickBite orders rather than real historical delivery records. Its predictions reflect patterns in that generated dataset and may not represent actual delivery operations.

The model cannot account for unexpected events such as road closures, traffic accidents, sudden weather changes, courier cancellations, or unusually busy restaurant conditions unless those patterns are represented in its input data.

Dispatchers should use the prediction as a decision-support tool, not as a guarantee that an order will be late. It should not replace operational judgment or be used as the sole basis for customer compensation decisions.