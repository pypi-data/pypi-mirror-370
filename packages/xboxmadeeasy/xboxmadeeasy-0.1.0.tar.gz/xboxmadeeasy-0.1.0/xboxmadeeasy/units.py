def format_axis(value):
    return round(value, 3)

def debug_state(state):
    print("🎮 Buttons:")
    for k, v in state.buttons.items():
        print(f"  {k}: {'Pressed' if v else 'Released'}")
    print("🕹️ Axes:")
    for k, v in state.axes.items():
        print(f"  {k}: {v}")