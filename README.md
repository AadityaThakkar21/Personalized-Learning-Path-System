# 🎓 Personalized Learning Path System
### IE402 — Optimization Course Project  
**Academic Year 2024-2025**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 👥 Team Members

| Name | Student ID |
|------|-----------|
| Vraj Patel | 202301408 |
| Aaditya Thakkar | 202301417 |
| Yogesh Bagotia | 202301114 |
| Vansh Padaliya | 202301065 |
| Siva Suhas Thatavarthy | 202301050 |

**Course Instructor:** Prof. Nabin Kumar Sahu

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [System Architecture](#-system-architecture)
- [Core Features](#-core-features)
- [Optimization Techniques](#-optimization-techniques)
- [Technologies Used](#-technologies-used)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Mathematical Foundations](#-mathematical-foundations)
- [Future Enhancements](#-future-enhancements)

---

## 🧠 Overview

The **Personalized Learning Path System** is an intelligent, adaptive academic optimization platform that addresses the fundamental limitations of traditional "one-size-fits-all" education. By leveraging **advanced optimization techniques**, **machine learning models**, and **data-driven analytics**, our system creates a personalized, efficient, and engaging learning ecosystem tailored to each student's unique needs.

### Why This Matters
Traditional education forces students to guess what to study, wasting time, overlooking weaknesses, and hindering long-term retention. Our system provides:
- ✅ Continuous diagnostic assessment
- ✅ Adaptive learning path optimization
- ✅ Predictive performance analytics
- ✅ Evidence-based study scheduling
- ✅ Social motivation through gamification

---

## 🎯 Problem Statement

Students face three critical challenges in their academic journey:

1. **Lack of Continuous Diagnosis**: No real-time feedback on knowledge gaps and weaknesses
2. **Inefficient Time Management**: Manual scheduling leads to suboptimal resource allocation
3. **Poor Retention**: Traditional study methods ignore scientifically-proven spaced repetition principles

Our system transforms these pain points into optimization problems with mathematically rigorous, data-driven solutions.

---

## 🏗️ System Architecture

Our platform follows a **four-stage learner-centric flow**, creating a complete feedback loop for continuous improvement:

```
┌─────────────────┐
│  1. DIAGNOSIS   │──► Initial assessment & knowledge gap detection
│  "Where am I?"  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. PLANNING    │──► Personalized timetables & spaced repetition
│  "What's next?" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. EXECUTION   │──► Continuous tracking & adaptive re-optimization
│  "Am I better?" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. ENHANCEMENT  │──► Social learning & competitive motivation
│  "Learn together"│
└─────────────────┘
```

### Stage 1: Diagnosis — "Where am I now?"
- **Quiz Maker**: Initial diagnostic assessment with optimized question selection
- **Knowledge Gap Detector**: Identify weaknesses and predict performance

### Stage 2: Planning — "What's the path forward?"
- **Timetable Creator**: Multi-objective optimization for personalized study schedules
- **Spaced Repetition Engine**: Predictive modeling for optimal review intervals

### Stage 3: Execution & Feedback — "How am I progressing?"
- **GradeLink**: Continuous progress tracking with adaptive re-optimization
- **Dynamic Path Updates**: Real-time adjustments based on performance data

### Stage 4: Enhancement — "How can I improve with others?"
- **Study Group Optimizer**: Performance-based collaborative learning groups
- **Leaderboard**: Gamified motivation through competitive rankings

---

## 🚀 Core Features

### 1️⃣ Quiz Maker — Intelligent Assessment System
**Optimization Techniques**: Constraint Satisfaction, Game Theory, Sensitivity Analysis

- **Resource Allocation Model**: Ensures exactly 5 questions per quiz through constraint satisfaction
- **Game-Theoretic Randomization**: Nash Equilibrium-inspired random sampling prevents pattern exploitation
- **Multi-Level Difficulty**: Easy, Medium, Hard levels for comprehensive assessment
- **Performance Tracking**: Detailed score for each attempt

---

### 2️⃣ Knowledge Gap & Performance Predictor
**Optimization Techniques**: Time-Series Forecasting, Linear Regression, Decision Optimization

Transforms quiz data into actionable insights using three-layer optimization:

#### Layer 1: Time-Series Weighted Forecasting
- **Recency Weighting**: Recent attempts weighted higher (wₜ = 1 + (t-1)/(n-1))
- **Difficulty Adjustment**: Scores adjusted by difficulty (Easy: 0.8, Medium: 1.0, Hard: 1.2)
- **Weighted Average Prediction**: Ŝₐᵥ = Σ(wₜs'ₜ) / Σ(wₜ)

#### Layer 2: Linear Trend Analysis
- **Least-Squares Regression**: Identifies improvement/decline patterns
- **Slope-Based Classification**: β₁ > 0.1 (Improving), β₁ < -0.1 (Declining)
- **Combined Prediction**: P = round(Ŝₐᵥ + β̂₁)

#### Layer 3: Contextual Feedback Generation
- **Rule-Based Intelligence**: Translates numerical trends into actionable advice
- **Difficulty-Specific Insights**: Targeted recommendations based on quiz type
- **Progress Visualization**: Interactive charts showing performance trends

---

### 3️⃣ Personalized Timetable Generator
**Optimization Techniques**: Mixed-Integer Linear Programming (MILP), Maximum Entropy, Multi-Objective Optimization

Three complementary optimization modes for flexible scheduling:

#### Mode A: Smart Auto — Two-Stage MILP
**Stage 1**: Maximize subject coverage (0-1 Knapsack Problem)
```
max Σyᵢ
subject to: Σ(mᵢyᵢ) ≤ H
```

**Stage 2**: Maximize time utilization with proportional fairness
```
max Σxᵢ
subject to: xᵢ = pᵢt (proportional allocation)
            mᵢyᵢ ≤ xᵢ ≤ Hyᵢ (activation constraints)
```

#### Mode B: Entropy Mode — Maximum Entropy Heuristic
- **Softmax Transformation**: ŵᵢ = exp(pᵢ) / Σexp(pⱼ)
- **Priority-Weighted Allocation**: xᵢ = mᵢ + Hᵣₑₘ · ŵᵢ
- **Fast Computation**: O(n) complexity vs O(n²) for MILP

#### Mode C: Pareto Mode — Multi-Objective Balance
- **Combined Score**: sᵢ = λp̃ᵢ + (1-λ)d̃ᵢ (priority + difficulty)
- **Tunable Trade-offs**: λ = 0.6 (priority weight), β = 2 (sharpness)
- **Balanced Allocation**: Rewards high-priority, high-difficulty subjects

**Key Features**:
- Respects minimum time constraints per subject
- User-defined priorities (1-5 scale)
- Difficulty-aware scheduling (optional)
- Half-hour time blocks for practical implementation

---

### 4️⃣ Spaced Repetition Scheduler
**Optimization Techniques**: Ensemble Learning (Random Forest), Predictive Modeling, Adaptive Scheduling

An ML-powered system that predicts optimal review intervals based on performance data.

#### Ensemble Random Forest Model
```
Prediction = (1/N) Σ Treeᵢ(x)
```
- **100 estimators** for robust predictions
- **Bootstrap aggregation** reduces overfitting
- **4D feature vector**: [Score%, Attempts, Time, Difficulty]

#### Heuristic Target Definition
Based on spaced repetition cognitive science:
```
Days to Wait = {
  7 days  if score ≥ 90%
  5 days  if 75% ≤ score < 90%
  3 days  if 60% ≤ score < 75%
  2 days  if score < 60%
}
```

#### Adaptive Prediction Logic
- **Case 1**: Uses most recent attempt data for known difficulties
- **Case 2**: Generalizes from average performance for new difficulties
- **Dynamic Updates**: Model retrains as new data becomes available

**Benefits**:
- Personalized to individual learning patterns
- Prevents cramming and promotes long-term retention
- Adapts to performance improvements automatically

---

### 5️⃣ GradeLink Pro — AI-Powered Grade Tracker
Real-time academic progress monitoring with continuous feedback integration.

**Features**:
- Multi-course grade tracking
- Weighted GPA calculations
- Visual performance analytics (Plotly charts)
- Trend analysis and predictions
- Integration with timetable optimizer

---

### 6️⃣ Leaderboard — Gamified Motivation
Competitive rankings based on quiz performance and engagement.

**Metrics**:
- Total quiz attempts
- Average scores across difficulties
- Consistency ratings
- Subject-wise performance

---

## 🔬 Optimization Techniques

Our system implements state-of-the-art optimization methods from operations research and machine learning:

| Technique | Application | Complexity |
|-----------|-------------|------------|
| **0-1 Knapsack** | Quiz question selection | O(nk) |
| **Mixed-Integer LP** | Timetable optimization | O(n²) |
| **Maximum Entropy** | Priority-based allocation | O(n) |
| **Random Forest** | Interval prediction | O(n log n) |
| **Linear Regression** | Trend analysis | O(n) |
| **Game Theory** | Random sampling | O(1) |
| **Softmax** | Weight normalization | O(n) |

---

## 🛠️ Technologies Used

| Category | Tools & Libraries |
|----------|-------------------|
| **Language** | Python 3.8+ |
| **Frontend** | Streamlit |
| **Optimization** | PuLP, SciPy, NumPy |
| **Machine Learning** | scikit-learn (Random Forest, Linear Regression) |
| **Data Processing** | pandas, NumPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Storage** | CSV, Pandas DataFrames, Pickle |
| **Mathematical Modeling** | PuLP (LP/MILP solver) |

## Deployed Website 
https://personalized-learning-path-system.streamlit.app/
