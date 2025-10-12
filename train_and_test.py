import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, precision_recall_fscore_support
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow as tf

# ==========================
# GPU check
# ==========================
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    print(f"[INFO] GPU detected: {physical_devices}")
    for gpu in physical_devices:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("[WARNING] No GPU detected. Training will use CPU.")

# ==========================
# Paths
# ==========================
DATASET_PATH = "dataset_fixed"
GRAPH_DIR = "training_outputs/graphs"
MODEL_PATH = "training_outputs/heart_mri_model.keras"

os.makedirs(GRAPH_DIR, exist_ok=True)
os.makedirs("training_outputs", exist_ok=True)

# ==========================
# Data generators
# ==========================
datagen = ImageDataGenerator(rescale=1.0/255)

train_gen = datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224,224),
    batch_size=32,
    class_mode="binary"
)

val_gen = datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224,224),
    batch_size=32,
    class_mode="binary"
)

test_gen = datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "test"),
    target_size=(224,224),
    batch_size=32,
    class_mode="binary",
    shuffle=False
)

# ==========================
# Model
# ==========================
model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(1, activation="sigmoid")
])

model.compile(optimizer=Adam(0.001),
              loss="binary_crossentropy",
              metrics=["accuracy"])

# ==========================
# Callbacks
# ==========================
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
checkpoint = ModelCheckpoint(MODEL_PATH, monitor='val_loss', save_best_only=True)

# ==========================
# Train
# ==========================
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=50,
    callbacks=[early_stop, checkpoint]
)

# ==========================
# Save training graphs
# ==========================
plt.figure(figsize=(10,5))
# Accuracy
plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label="Train Acc")
plt.plot(history.history['val_accuracy'], label="Val Acc")
plt.title("Accuracy")
plt.legend()
# Loss
plt.subplot(1,2,2)
plt.plot(history.history['loss'], label="Train Loss")
plt.plot(history.history['val_loss'], label="Val Loss")
plt.title("Loss")
plt.legend()
acc_loss_path = os.path.join(GRAPH_DIR, "loss_accuracy.png")
plt.savefig(acc_loss_path)
plt.close()
print(f"[INFO] Saved training graph at {acc_loss_path}")

# ==========================
# Confusion matrix
# ==========================
y_pred = model.predict(test_gen)
y_pred_classes = (y_pred > 0.5).astype("int32")
y_true = test_gen.classes

cm = confusion_matrix(y_true, y_pred_classes)
disp = ConfusionMatrixDisplay(cm, display_labels=list(test_gen.class_indices.keys()))
disp.plot(cmap="Blues", values_format="d")
cm_path = os.path.join(GRAPH_DIR, "confusion_matrix.png")
plt.savefig(cm_path)
plt.close()
print(f"[INFO] Saved confusion matrix at {cm_path}")

# ==========================
# Precision, Recall, F1
# ==========================
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred_classes, average='binary')
plt.figure(figsize=(6,6))
plt.bar(['Precision','Recall','F1'], [precision, recall, f1], color=['#3498db','#2ecc71','#e74c3c'])
plt.title("Precision / Recall / F1 Score")
for i, v in enumerate([precision, recall, f1]):
    plt.text(i, v+0.01, f"{v:.2f}", ha='center')
prf_path = os.path.join(GRAPH_DIR, "precision_recall_f1.png")
plt.savefig(prf_path)
plt.close()
print(f"[INFO] Saved Precision/Recall/F1 graph at {prf_path}")
