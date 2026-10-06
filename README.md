# Obstacle-Avoiding-Robot

# Autonomous Obstacle Avoidance Robot with Neural-Network Action Selection

A final-year Artificial Intelligence module project combining a **LEGO SPIKE Prime physical prototype** with a **PyTorch neural-network classifier** trained to imitate a rule-based obstacle-avoidance policy. The project explores reactive robotic control, supervised learning, and the gap between simulation-trained models and real-world deployment.

---

## Overview

Mobile robots must convert noisy sensor readings into safe movement decisions without human intervention. This project investigates that problem in two parts:

1. **Physical reactive controller** - a LEGO SPIKE Prime robot that uses two distance sensors, a colour sensor, and separate drive/steering motors to avoid obstacles, detect a red floor marker, and stop when required.
2. **Machine-learning experiment** - a small multilayer perceptron (MLP) trained in PyTorch to predict one of four navigation actions ('FORWARD', 'LEFT', 'RIGHT', 'STOP') from three synthetic distance readings.

The two components are deliberately separated: the LEGO program uses explicit priority rules, while the neural network explores whether those rules can be approximated from data. This distinction — between a hand-coded controller, a trained classifier, and a verified deployment — is the core AI lesson of the project.

---

## Key Results

Metric -- Value 

Dataset -- 20,000 synthetic samples, 3 features (front/left/right distance)
Classes -- 4 — 'FORWARD', 'LEFT', 'RIGHT', 'STOP'
Model -- MLP: 3 → 64 → 64 → 4
Trainable parameters -- 4,676
Training -- 100 epochs, Adam (lr = 0.001), batch size 256
Validation accuracy -- **98.25%**
Macro F1-score -- **0.98**
STOP precision / recall -- **1.00 / 1.00**
Sample errors -- 89 of 5,080 (all between FORWARD and turning actions)

The 33 unique STOP samples in the raw dataset were oversampled to 3,000 rows before the train/validation split. This is a known limitation of the reported results - see **Limitations** below.


## The Machine-Learning Pipeline

### 1. Synthetic data generation

Since no real robot datasets were available for this scope, the training data was generated from an explicit expert policy:

if front > 40 cm: label = FORWARD
elif left > right and left > 20: label = LEFT
elif right > left and right > 20: label = RIGHT
elif left > 20: label = LEFT
elif right > 20: label = RIGHT
else: label = STOP


Gaussian noise (σ = 3 cm) was added to inputs *after* labelling to simulate sensor error, and distances were clipped to a minimum of 2 cm.

**Class distribution (raw):**

Class -- Raw count

FORWARD -- 16,396
LEFT -- 1,779
RIGHT -- 1,792
STOP -- 33

Rare classes were oversampled to 3,000 each before the 80/20 stratified split, giving 20,316 training and 5,080 validation samples.

### 2. Model architecture

Input (3) → Linear(64) → ReLU
→ Linear(64) → ReLU
→ Linear(4) → logits

Cross-entropy loss applied directly to logits. Softmax computed at inference for confidence reporting.

### 3. Training

- Optimiser: Adam (Kingma & Ba, 2015), learning rate 1e-3
- Batch size: 256
- Epochs: 100 (no early stopping)
- Input standardisation: 'StandardScaler' fit on training data only

Training and validation loss converged to ~0.041 and ~0.043 respectively, with no sign of overfitting within the synthetic distribution.


## Physical Prototype

**Hardware** (LEGO SPIKE Prime):

Component -- Port

Steering motor -- A
Drive motor -- E
Left distance sensor -- D
Right distance sensor -- C
Colour sensor (floor-facing) -- F

**Controller logic** ('robotics_program.py'):

1. If red detected ('r > 50 and r > 1.5g and r > 1.5b') → stop drive, centre steering.
2. If either distance sensor reads below 180 mm → reverse briefly, steer away from the blocked side.
3. Otherwise, wander with fixed probabilities: straight (50%), gentle left (20%), gentle right (20%), reverse (10%).

**Observed behaviour on test runs:**

- Red-floor stopping: **reliable every trial**
- Obstacle avoidance: **no collisions recorded**
- Main weakness: long pauses when a large obstacle sat directly ahead, likely because the reverse step re-presented the same obstacle to the sensors.


## Limitations

These are stated explicitly because the report flags them and they matter for honest evaluation:

1. **Duplicate leakage in validation.** Oversampling was performed *before* the train/validation split, so identical rows appear in both subsets. With only 33 unique STOP samples expanded to 3,000 rows, the perfect STOP score reflects memorisation rather than generalisation.
2. **Synthetic inputs.** The classifier was trained on uniformly-distributed distances with Gaussian noise, not real ultrasonic readings. Real sensors produce missed echoes, out-of-range values, and correlated noise that the model has never seen.
3. **Model not deployed on the robot.** The LEGO controller runs an independent rule-based program. No end-to-end integration between the trained network and the physical prototype was completed.
4. **No closed-loop evaluation.** The GPIO runtime that loads 'avoider_model.pt' was written but not benchmarked on hardware.



## Getting Started

### Run the training notebook

1. pip install torch numpy pandas scikit-learn matplotlib (installing the required libraries)
2. jupyter notebook robotics_model.ipynb
OR
upload robotics_model.ipynb to Google Colab and run all cells. Total runtime is under one minute on CPU.
