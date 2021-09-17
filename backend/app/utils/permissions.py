from app.core.config import settings

models = settings.MODELS
actions = ["add", "change", "view", "delete"]

permissions = [
    {"label": model_name.capitalize(), "options": [{"value": f"{action_name}_{model_name}", "label": f"{action_name.capitalize()} {model_name.capitalize()}"}
                                                   for action_name in actions]} for model_name in models
]
