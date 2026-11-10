import gradio as gr

from predict import CHOICES, predict_order

try:  # present only on Hugging Face ZeroGPU hardware
    import spaces
except ImportError:
    spaces = None

if spaces is not None:

    @spaces.GPU
    def keep_zerogpu_happy() -> None:
        """ZeroGPU will not start without one GPU function. This one does nothing."""


def score(
    distance_km, items, hour, prep_minutes, courier_months, weather, day_type, vehicle
):
    order = {
        "distance_km": distance_km,
        "items": items,
        "hour": hour,
        "prep_minutes": prep_minutes,
        "courier_months": courier_months,
        "weather": weather,
        "day_type": day_type,
        "vehicle": vehicle,
    }
    if prep_minutes is None:
        gr.Warning("No preparation time given, a typical value was used.")
    try:
        result = predict_order(order)
    except ValueError as error:
        raise gr.Error(str(error)) from error
    chance = result["probability"]
    if result["voucher"]:
        action = "Offer the customer a $4 voucher now."
    else:
        action = "No voucher needed."
    return {"Late": chance, "On time": 1 - chance}, action


with gr.Blocks(title="QuickBite Late Order Check") as demo:
    gr.Markdown(
        "# QuickBite Late Order Check\n"
        "Will this order arrive late? Fill in what you know when the order is placed."
    )
    with gr.Row():
        with gr.Column():
            distance_in = gr.Number(label="Distance (km, 0.1 to 30)", value=3.5)
            items_in = gr.Number(label="Items (1 to 20)", value=3, precision=0)
            hour_in = gr.Number(label="Hour of day (10 to 22)", value=13, precision=0)
            prep_in = gr.Number(label="Preparation time (min, 1 to 60, optional)")
            courier_in = gr.Number(
                label="Courier experience (months, 0 to 120)", value=12
            )
            weather_in = gr.Dropdown(CHOICES["weather"], value="clear", label="Weather")
            day_in = gr.Dropdown(CHOICES["day_type"], value="weekday", label="Day type")
            vehicle_in = gr.Dropdown(
                CHOICES["vehicle"], value="scooter", label="Vehicle"
            )
            button = gr.Button("Check order", variant="primary")
        with gr.Column():
            chances_out = gr.Label(label="Chance of each outcome")
            action_out = gr.Textbox(label="What to do")
    inputs = [
        distance_in,
        items_in,
        hour_in,
        prep_in,
        courier_in,
        weather_in,
        day_in,
        vehicle_in,
    ]
    button.click(score, inputs=inputs, outputs=[chances_out, action_out])

if __name__ == "__main__":
    demo.launch()
