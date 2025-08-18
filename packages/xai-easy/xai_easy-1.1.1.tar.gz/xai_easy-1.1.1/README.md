**XAI Easy** is a powerful Python package designed to make machine learning models interpretable and explainable. Whether you're working with classification, regression, or clustering models, XAI Easy provides comprehensive tools to understand what your models are doing and why they make specific predictions.

### Key Features
- 🎯 **Global Model Explanations** - Understand feature importance across your entire dataset
- 🔍 **Local Instance Explanations** - Explain individual predictions with precision
- 📊 **Professional Visualizations** - Generate publication-ready charts and interactive reports
- 🎨 **Modern HTML Reports** - Create stunning, responsive reports with professional branding
- ⚡ **Model Agnostic** - Works with any scikit-learn compatible model
- 🔧 **SHAP Integration** - Automatic integration with SHAP when available

---

## 🚀 Applications

### Real-World Use Cases
- 🏥 **Healthcare**: Explain medical diagnosis predictions and treatment recommendations
- 🏦 **Finance**: Interpret credit scoring and risk assessment models
- 🛒 **E-commerce**: Understand customer behavior and recommendation systems  
- 🏭 **Manufacturing**: Analyze quality control and predictive maintenance models
- 📊 **Research**: Generate publication-ready model interpretability reports

---

## ⚡ Quick Installation

```bash
pip install xai-easy
```

---

## � Simple Example Usage

Here's a complete example showing how to use XAI Easy to explain a machine learning model:

![Code Example - Professional XAI Easy implementation showing model training and explanation generation](./code.png)
*Professional implementation example demonstrating XAI Easy's simple yet powerful API for model explainability*

### Console Output
![Console Output - Clean, professional terminal output with structured explanations and success confirmation](./output.png)  
*Clean console output showing feature importance rankings and successful HTML report generation with professional branding*

---

## 🎨 Professional Report Visualizations

XAI Easy generates comprehensive HTML reports with modern, responsive design:

### 1. Report Header & Summary Dashboard
![Report Header - Professional gradient header with model analysis summary and key statistics dashboard](./opui1.png)
*Modern report header featuring gradient styling, model analysis title, and key performance metrics in an intuitive dashboard layout*

### 2. Global Feature Importance Analysis  
![Global Feature Importance - Interactive horizontal bar chart showing model-wide feature contributions with gradient colors](./opui2.png)
*Interactive feature importance visualization with gradient color coding and precise value labels, showing which features matter most globally*

### 3. Detailed Feature Importance Table
![Feature Importance Table - Professional data table with rankings, importance scores, and detailed explanations](./opui3.png) 
*Comprehensive feature importance table with professional styling, clear rankings, and detailed explanations for stakeholder communication*

### 4. Local Instance Explanation Dashboard
![Local Explanation Dashboard - Instance-specific analysis showing positive/negative feature contributions with summary statistics](./opui4.png)
*Local explanation dashboard displaying positive and negative feature contributions with summary statistics for specific prediction analysis*

### 5. Local Feature Contributions Chart
![Local Feature Contributions - Diverging bar chart showing positive and negative feature impacts on individual predictions](./opui5.png)
*Professional diverging bar chart visualizing how individual features positively or negatively influence specific model predictions*

---

## � Advanced Usage

### Complete Workflow Example

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from xai_easy import explain_model, explain_instance, save_html_report

# 1. Prepare your data
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
feature_names = [f"feature_{i+1}" for i in range(X.shape[1])]
X_df = pd.DataFrame(X, columns=feature_names)

# 2. Train your model  
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_df, y)

# 3. Generate global explanations
global_explanations = explain_model(
    model, X_df, y, 
    task="classification", 
    top_n=10
)

# 4. Generate local explanations
local_explanations = explain_instance(
    model, X_df, 
    X_df.iloc[0],  # Explain first instance
    feature_names=feature_names
)

# 5. Create professional HTML report
save_html_report(
    global_explanations, 
    local_explanations,
    title="Professional ML Model Analysis Report",
    filename="model_analysis.html"
)
```

### Key Functions

#### `explain_model(model, X, y=None, **kwargs)`
- **Purpose**: Generate global model explanations
- **Returns**: DataFrame with feature importance rankings and explanations
- **Parameters**: 
  - `model`: Trained scikit-learn compatible model
  - `X`: Feature data (DataFrame or array)
  - `y`: Target labels (optional)
  - `top_n`: Number of top features (default: 20)

#### `explain_instance(model, X, instance, **kwargs)`
- **Purpose**: Generate local explanations for specific predictions
- **Returns**: DataFrame with feature contributions and explanations  
- **Parameters**:
  - `model`: Trained model
  - `X`: Training data
  - `instance`: Single instance to explain
  - `feature_names`: Feature names (optional)

#### `save_html_report(global_df, local_df=None, **kwargs)`
- **Purpose**: Create professional HTML reports
- **Features**: Modern design, responsive layout, interactive elements
- **Parameters**:
  - `global_df`: Global explanations DataFrame
  - `local_df`: Local explanations DataFrame (optional)
  - `title`: Report title
  - `filename`: Output filename

---

## � Report Features

Every generated report includes:

### Professional Design Elements
- ✅ **Gradient Headers** with model analysis branding
- ✅ **Summary Statistics** dashboard with key metrics
- ✅ **Interactive Charts** with gradient colors and value labels
- ✅ **Responsive Tables** with hover effects and clean typography
- ✅ **Professional Footer** with package attribution and creator recognition

### Technical Capabilities  
- ✅ **Mobile Responsive** design for all devices
- ✅ **High-Resolution Charts** suitable for presentations
- ✅ **Structured Data** tables for easy interpretation
- ✅ **Professional Branding** with creator attribution
- ✅ **Export Ready** HTML format for sharing

---

## 📊 Supported Models

XAI Easy works with any scikit-learn compatible model:

- **Tree-based Models**: RandomForest, XGBoost, LightGBM, CatBoost
- **Linear Models**: LogisticRegression, LinearRegression, Ridge, Lasso
- **Ensemble Models**: GradientBoosting, AdaBoost, Voting classifiers
- **SVM Models**: SVC, SVR with probability estimates
- **Neural Networks**: MLPClassifier, MLPRegressor

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Pull Requests or open issues for feature requests and bug reports.

### Development Setup
```bash
git clone https://github.com/PrajwalChopade/xai_easy.git
cd xai_easy
pip install -e .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 About the Creator

**XAI Easy** was created by **Prajwal** with the vision of making machine learning more transparent and accessible. The package combines cutting-edge explainability techniques with professional-grade visualizations to bridge the gap between complex AI models and human understanding.

### Philosophy
*"Making artificial intelligence transparent, one explanation at a time."*

### Connect
- 🐙 **GitHub**: [@PrajwalChopade](https://github.com/PrajwalChopade)
- 📦 **Package**: Making ML interpretable for everyone
- 🎯 **Mission**: Responsible and explainable AI for all

---

## 🌟 Support XAI Easy

If you find XAI Easy useful, please consider:

- ⭐ **Star** this repository on GitHub
- 🐛 **Report** bugs and issues
- 💡 **Suggest** new features and improvements  
- 📢 **Share** with your colleagues and community

---

**Built with ❤️ for the AI/ML community by Prajwal**

*Professional explainable AI made simple and accessible*