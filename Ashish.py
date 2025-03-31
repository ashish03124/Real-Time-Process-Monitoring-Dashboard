import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import plotly.express as px

# Set Streamlit Page Config
st.set_page_config(page_title="Human Action Recognition", page_icon="🏡", layout="wide")

# Custom CSS for Grey, Black, and White Theme
st.markdown("""
    <style>
    /* General Background and Text Styling */
    body {
        background-color: #2e2b29; /* Dark Brown-Grey */
        color: #ffffff; /* White Text */
        font-family: 'Arial', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        text-align: center;
        color: #d2b48c; /* Tan/Brown */
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #5c4033; /* Brown Shade */
        color: #ffffff;
        border-radius: 12px;
        padding: 12px;
        width: 100%;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #a67b5b; /* Lighter Brown */
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #3b3735; /* Deep Grey */
        padding: 15px;
    }
    
    /* Metrics Cards */
    .metric-card {
        background-color: #524e4c; /* Darker Grey */
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 12px 0;
        transition: 0.3s;
    }
    .metric-card:hover {
        background-color: #766b63; /* Warm Grey */
    }
    
    /* Dataset Table */
    .dataframe tbody tr:nth-child(odd) {
        background-color: #4a4341;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #625a57;
    }
    
    /* Key Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Title Animation */
    .title {
        animation: fadeIn 2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Generate Synthetic Dataset with More Features
def generate_synthetic_data():
    actions = ['Walking', 'Sitting', 'Standing', 'Lying', 'Running']
    num_samples = 1000
    data = {
        'Accel_X': np.random.normal(0, 10, num_samples),
        'Accel_Y': np.random.normal(0, 10, num_samples),
        'Gyro_X': np.random.normal(0, 5, num_samples),
        'Gyro_Y': np.random.normal(0, 5, num_samples),
        'Temp': np.random.uniform(20, 40, num_samples),
        'Action': np.random.choice(actions, num_samples)
    }
    return pd.DataFrame(data)

# Load or Generate Data
if 'df' not in st.session_state:
    st.session_state.df = generate_synthetic_data()

df = st.session_state.df

# Data Preprocessing
label_encoder = LabelEncoder()
df['Action'] = label_encoder.fit_transform(df['Action'])
X = df.drop('Action', axis=1)
y = df['Action']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# Celebration for High Accuracy
if accuracy > 0.85:
    st.balloons()
elif accuracy > 0.75:
    st.snow()

# UI Title with Animation
st.markdown("""
    <h1 style='color: #b0b0b0; animation: fadeIn 2s;'>🏡 Human Action Recognition in Smart Homes</h1>
    <style> @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } </style>
""", unsafe_allow_html=True)
st.markdown("---")

# Layout: Tabs for Data, Visualization, and Performance
tab1, tab2, tab3 = st.tabs(["📊 Data", "📈 Visualizations", "🚀 Performance"])

with tab1:
    st.markdown("### Sample Dataset")
    st.dataframe(df.head(10).style.set_properties(**{'background-color': '#333333', 'color': '#ffffff'}), 
                 use_container_width=True)
    
    # Download Button
    csv = df.to_csv(index=False)
    st.download_button(label="📥 Download Dataset", data=csv, file_name="smart_home_data.csv", mime="text/csv")

with tab2:
    st.markdown("### 🔥 Interactive Visualizations")
    
    # Correlation Heatmap with Plotly (Grey Scale)
    fig_heatmap = px.imshow(df.drop(columns=["Action"]).corr(), text_auto=True, color_continuous_scale="gray")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 3D Scatter Plot (Grey Scale)
    fig_3d = px.scatter_3d(df, x='Accel_X', y='Accel_Y', z='Gyro_X', color=df['Action'].astype(str), 
                           title="3D Sensor Data Distribution", opacity=0.7, 
                           color_discrete_sequence=['#cccccc', '#999999', '#666666', '#333333', '#ffffff'])
    st.plotly_chart(fig_3d, use_container_width=True)

with tab3:
    st.markdown("### 🚀 Model Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="🔥 Model Accuracy", value=f"{accuracy * 100:.2f}%")
    
    with col2:
        st.text("📊 Classification Report:")
        st.text(classification_report(y_test, y_pred))

# Sidebar: Real-time Prediction UI
st.sidebar.markdown("<h2 style='text-align: center;'>🔮 Predict Action</h2>", unsafe_allow_html=True)

accel_x = st.sidebar.slider("📡 Accel_X", -20, 20, 0)
accel_y = st.sidebar.slider("📡 Accel_Y", -20, 20, 0)
gyro_x = st.sidebar.slider("📡 Gyro_X", -10, 10, 0)
gyro_y = st.sidebar.slider("📡 Gyro_Y", -10, 10, 0)
temp = st.sidebar.slider("🌡 Temperature", 20, 40, 30)

if st.sidebar.button("🔍 Predict", use_container_width=True):
    input_data = np.array([[accel_x, accel_y, gyro_x, gyro_y, temp]])
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)
    predicted_action = label_encoder.inverse_transform(prediction)[0]

    st.sidebar.markdown(
        f"<h3 style='text-align: center; color: #cccccc;'>🎯 Predicted Action: {predicted_action}</h3>",
        unsafe_allow_html=True
    )
