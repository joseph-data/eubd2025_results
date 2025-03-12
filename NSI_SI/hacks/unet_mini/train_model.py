import os
from tensorflow.keras.callbacks import ModelCheckpoint
from unet_mini import UNet

def train_model(model_name, patches, num_classes, output_dir, batch_size, epochs, callbacks=None, verbose=1):
    # Validate data
    if "train" not in patches or "valid" not in patches:
        raise ValueError("Patches dictionary must contain 'train' and 'valid' keys.")

    # Extract train and validation data
    X_train, y_train = patches["train"]
    X_valid, y_valid = patches["valid"]

    # Get input shape based on feature layers
    input_shape = X_train.shape[1:]  # Automatically determine input shape

    # Initialize UNet model
    model = UNet(input_shape, num_classes)

    # Compile the model
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy" if num_classes > 1 else "binary_crossentropy",
        metrics=["accuracy"],
    )

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define checkpoints
    checkpoint_path = os.path.join(output_dir, f"{model_name}_best.h5")
    checkpoint = ModelCheckpoint(checkpoint_path, save_best_only=True, monitor="val_loss", mode="min", verbose=1)

    # Add additional callbacks if provided
    if callbacks is None:
        callbacks = []
    callbacks.append(checkpoint)

    # Train the model
    model.fit(
        X_train,
        y_train,
        validation_data=(X_valid, y_valid),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=verbose,
    )

    # Save the final trained model
    final_model_path = os.path.join(output_dir, f"{model_name}_final.h5")
    model.save(final_model_path)
    print(f"Model {model_name} saved at {final_model_path}")

    return final_model_path
