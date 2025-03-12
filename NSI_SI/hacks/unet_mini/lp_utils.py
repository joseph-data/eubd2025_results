from models import unet_mini

# Dynamic Model Selector
def select_model(model_name, input_shape, num_classes, weights_path=None):
    if model_name == "unet_mini":
        model = unet_mini.UNet(input_shape, num_classes)
        if weights_path:
            model.load_weights(weights_path)
        return model
    else:
        raise ValueError(f"Unsupported model: {model_name}. Only 'unet_mini' is available.")
