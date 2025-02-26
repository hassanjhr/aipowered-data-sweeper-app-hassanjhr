import streamlit as st
import pandas as pd
import os
from io import BytesIO
import google.generativeai as genai
import matplotlib.pyplot as plt

# Set up App
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #f0f4f8;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stButton>button, .stDownloadButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 12px 28px;
            border: none;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #45a049;
        }
        .stTextInput>div>input, .stSelectbox>div>div>div>div {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 10px;
            width: 100%;
            box-sizing: border-box;
            height: 50px;
            font-size: 16px;
        }
        .stSelectbox>div>div>div>div {
            overflow: hidden;
            width: 100% !important;
            max-width: 600px !important;
            margin: 0 auto;
        }
        .stSelectbox label {
            display: block;
            width: 100%;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .stDataFrame {
            border-radius: 10px;
            border: 1px solid #ddd;
            overflow: hidden;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #023047;
        }
        .stAlert, .stInfo {
            background-color: #e1f5fe;
            border-left: 5px solid #0288d1;
        }
        .stSidebar .sidebar-content {
            background-color: #e3f2fd;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            margin-bottom: 0.5rem;
        }
        .selectbox-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: space-between;
        }
        .selectbox-container > div {
            flex: 1;
            min-width: 45%;
        }
    </style>
""", unsafe_allow_html=True)

st.title("AI-Powered Data Sweeper ✨")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning, visualization, and AI insights!")

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAXp7h_MacJFtNCuxu-9mTHjuqrJPHD8fQ"
genai.configure(api_key=GEMINI_API_KEY)

# Upload files
uploaded_files = st.file_uploader("📂 **Upload your files (CSV or Excel):**", type=["csv", "xlsx"], accept_multiple_files=True)

# Dictionary to store DataFrames for chatbot use
dataframes = {}

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            file_bytes = BytesIO(file.getvalue())
            df = pd.read_excel(file_bytes, engine='openpyxl')
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue

        # Store DataFrame for chatbot
        dataframes[file.name] = df

        # Display information about the file
        st.markdown(f"**📑 File Name:** `{file.name}`")
        st.markdown(f"**📏 File Size:** `{file.size / 1024:.2f} KB`")

        # Show 5 rows of the file
        st.write("🔎 **Preview of the Uploaded Dataframe:**")
        st.dataframe(df.head(), use_container_width=True)

        # Options for data cleaning
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"🧽 **Clean Data for {file.name}**", key=f"clean_data_{file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑️ Remove Duplicates from {file.name}", key=f"remove_duplicates_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"🩹 Fill Missing Values for {file.name}", key=f"fill_missing_{file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

        # Choose specific columns to convert or keep
        st.subheader("🎯 Select Columns to Convert")
        columns = st.multiselect(f"📊 **Choose Columns for {file.name}:**", df.columns, default=df.columns, key=f"select_columns_{file.name}")
        df = df[columns]

        # Create visualizations
        st.subheader("📈 Data Visualization")
        if st.checkbox(f"📊 **Show Visualization for {file.name}**", key=f"show_viz_{file.name}"):
            # ✅ Added unique key for chart_type selectbox
            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot"], key=f"chart_type_{file.name}")

            # Better selectbox alignment with unique keys
            st.markdown('<div class="selectbox-container">', unsafe_allow_html=True)

            # ✅ Unique keys for X and Y axis selectboxes
            x_axis = st.selectbox("Select X-axis", df.columns.tolist(), key=f"x_axis_{file.name}")
            y_axis = st.selectbox("Select Y-axis", df.columns.tolist(), key=f"y_axis_{file.name}")
            st.markdown('</div>', unsafe_allow_html=True)

            try:
                if chart_type == "Bar Chart":
                    df_temp = df[[x_axis, y_axis]].dropna()
                    df_temp.set_index(x_axis, inplace=True)
                    st.bar_chart(df_temp[y_axis])
                elif chart_type == "Line Chart":
                    df_temp = df[[x_axis, y_axis]].dropna()
                    df_temp.set_index(x_axis, inplace=True)
                    st.line_chart(df_temp[y_axis])
                elif chart_type == "Histogram":
                    fig, ax = plt.subplots()
                    ax.hist(df[y_axis].dropna(), bins=20, color='skyblue')
                    ax.set_xlabel(y_axis)
                    ax.set_ylabel("Frequency")
                    st.pyplot(fig)
                elif chart_type == "Scatter Plot":
                    fig, ax = plt.subplots()
                    ax.scatter(df[x_axis], df[y_axis], alpha=0.6, c='purple')
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating the chart: {e}")

        # Convert the file
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"📤 **Convert {file.name} to:**", ["CSV", "Excel"], key=f"convert_{file.name}")
        if st.button(f"💾 Convert {file.name}", key=f"convert_btn_{file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Download button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

    st.success("🎉 All files processed successfully!")

# Gemini-powered Chatbot for file-related questions
st.subheader("🤖 Ask About Your Data with AI-Bot")
selected_file = st.selectbox("📁 **Select a file to ask questions about:**", list(dataframes.keys()), key="chatbot_select_file")

if selected_file:
    user_query = st.text_input("💬 **Ask a question about your data (e.g., 'What is the average of column X?'):**", key="chatbot_query")
    df = dataframes[selected_file]

    if user_query:
        df_sample = df.head(5).to_csv(index=False)
        prompt = f"Here is a sample of the dataset:\n{df_sample}\n\nUser's Question: {user_query}\nPlease provide a detailed and accurate answer based on the dataset."

        try:
            best_model = "models/gemini-1.5-pro-002"
            gemini_response = genai.GenerativeModel(best_model).generate_content(prompt)
            response_text = gemini_response.text
            st.info(f"🧠 **Response:**\n{response_text}")

        except Exception as e:
            st.error(f"❌ Error with Gemini API: {e}")
