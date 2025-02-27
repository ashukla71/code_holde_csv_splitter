import streamlit as st
import pandas as pd
import os
import shutil
import time

st.title("📂 Code Holder - CSV Data Splitter")
user_name = st.text_input("Enter your name:", "")
if user_name:
    st.write(f"👋 Welcome, {user_name}!")

# File uploader
uploaded_file = st.file_uploader("📤 Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.error("🚨 Uploaded CSV file is empty.")
    else:
        st.write("📋 **Preview of the uploaded file:**")
        st.dataframe(df.head())

        if not df.columns[0].isalpha(): # Check if headers look invalid
            st.warning("⚠ Column headers seem incorrect. Please rename them:")
            new_headers = [st.text_input(f"Rename column {i+1}:", col) for i, col in enumerate(df.columns)]
            df.columns = new_headers

        st.write("🔽 **Select the column to split:**")
        column_name = st.selectbox("", df.columns)

        unique_values = df[column_name].dropna().unique().tolist()
        st.write("📊 **Unique values count in selected column:**")
        st.dataframe(df[column_name].value_counts().reset_index().rename(columns={"index": "Value", column_name: "Count"}))

        selected_values = st.multiselect("🎯 Select specific values to process (leave empty for all):", unique_values)

        output_format = st.radio("📝 **Select output file format:**", ["CSV", "JSON", "TXT"])

        folder_name = st.text_input("📁 Enter folder name for output files:", "output_folder")

        if st.button("🚀 Process File"):
            if not os.path.exists(folder_name):
                os.makedirs(folder_name) # Create folder

            word_groups = {}
            total_rows = len(df)
            progress_bar = st.progress(0) # Progress bar

            for idx, (index, row) in enumerate(df.iterrows()):
                progress_bar.progress((idx + 1) / total_rows) # Update progress

                value = str(row[column_name]).strip()
                if value and (not selected_values or value in selected_values): # Process only selected values
                    if value not in word_groups:
                        word_groups[value] = []
                    word_groups[value].append(",".join(map(str, row.values)))

            for word, rows in word_groups.items():
                filename = os.path.join(folder_name, f"{word}.{output_format.lower()}")
                with open(filename, "w") as f:
                    if output_format == "CSV":
                        f.write("\n".join(rows))
                    elif output_format == "JSON":
                        import json
                        f.write(json.dumps(rows, indent=4))
                    else: # TXT
                        f.write("\n".join(rows))

            zip_filename = f"{folder_name}.zip"
            shutil.make_archive(folder_name, 'zip', folder_name)

            st.success(f"✅ Files have been created in '{folder_name}' folder.")
            with open(zip_filename, "rb") as f:
                st.download_button("📥 Download ZIP", f, file_name=f"{folder_name}.zip")

            st.write("🎉 **Processing Complete!**")