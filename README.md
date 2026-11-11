---
title: QuickBite Late Order Check
emoji: 🚚
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

Hugging Face Space: https://huggingface.co/spaces/Oleg04/quickbite-late-delivery

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

**Snow vs. Snow experiment:** The model was tested directly using `weather="snow"` and then `weather="Snow"`, bypassing the application's input validation. We used the example order from the team sheet (3.5 km, 3 items, 13:00, 14 min prep, 12-month courier, weekday, scooter). The probability for `"snow"` was **0.194**, while the probability for `"Snow"` was **0.156**. The model gave no error and no warning for the misspelled value. Because `"Snow"` is an unseen category, the one-hot encoder sets every weather column to zero. The order is then scored as if it had no weather, and the snow penalty is silently lost. The result also does not match any real category (`"clear"` gives 0.069 and `"rain"` gives 0.141). One wrong capital letter changes the prediction without anyone noticing, so the application rejects unknown categories before prediction.

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

The automated tests (31 in total) are in `tests/`:

- **`tests/test_predict.py`** checks `predict.py`:
  - The probability is between 0 and 1.
  - A heavy order (far, large, snow, rush hour, new courier) scores higher than a light one.
  - The voucher boundary works: offered at exactly the threshold and just above it, but not just below it.
  - The threshold is read from `models/model_info.json`.
  - An empty `prep_minutes` is accepted.
  - Out-of-range numbers, unknown categories (such as `"Snow"`) and missing fields are rejected with an error that names the field.
  - The model is loaded only once.
- **`tests/test_deployment.py`** checks the deployment setup:
  - The installed scikit-learn version matches `model_info.json` and the pin in `requirements.txt`.
  - `gradio` is not listed in `requirements.txt`, because Hugging Face installs it.
  - The `sdk_version` in this README matches the installed Gradio version.
  - The `app_file` named in this README exists.
- **`tests/conftest.py`** provides shared fixtures (a valid order, light and heavy orders, and the model info).

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