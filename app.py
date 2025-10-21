import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io

# Streamlit app title
st.title("Excel Data Processing App")

# File upload
uploaded_file = st.file_uploader("Upload your Excel file (data.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Read the Excel file, skipping the first row
    df = pd.read_excel(uploaded_file, skiprows=1)

    # Data processing (same as your original code)
    df1 = df.iloc[:, 6:]
    df2 = df1.iloc[:, [0, 1, 4, 6, 17]]
    df2 = df2[df2.위탁량 > 0]
    df2['배출차량'] = df2.iloc[:, 3].str.replace(r'^.*(.{4})$', r'\1', regex=True)
    df2['배출차량'] = pd.to_numeric(df2['배출차량'], errors='coerce')
    df2['인계일자'] = df2['인계일자'].apply(lambda x: x.replace(year=1900, month=1))

    # Mapping dictionary for company names
    replace_map = {
        '수도권매립지관리공사(반입팀)': '매립지',
        '농업회사법인 석계 (주)': '석계',
        '서울물재생시설공단-서남센터': '서남',
        '서울특별시 난지 물재생센터': '난지',
        '정애영농조합법인': '정애영농',
        '인천환경공단 가좌사업소': '가좌사업소',
        '전주리싸이클링에너지(주)-완산': '전주',
        '서울시중랑물재생센터-처리자': '중랑',
        '칠성에너지 영농조합법인': '칠성에너지'
    }
    df2['업체명.2'] = df2['업체명.2'].replace(replace_map)
    df2['업체명.2'] = df2['업체명.2'].str.replace(r'\(주\)', '', regex=True)

    # Adjust 위탁량 values
    df2.loc[df2['위탁량'] < 100, '위탁량'] *= 1000

    # Final data transformations
    df2['인계일자'] = pd.to_datetime(df2['인계일자']).dt.date
    df2['업체명'] = df2.iloc[:, 0].str.replace(r'\s+', '', regex=True)
    df2 = df2[['배출차량', '인계일자', '업체명', '업체명.2', '위탁량']]

    # Display processed data
    st.subheader("Processed Data Preview")
    st.dataframe(df2)

    # Optional filtering by 업체명.2
    st.subheader("Filter by Company Name")
    company_options = df2['업체명'].unique().tolist()
    selected_company = st.multiselect("Select company names", company_options, default=company_options)
    filtered_df = df2[df2['업체명'].isin(selected_company)]

    # Display filtered data
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    # Generate Excel file for download
    current_date = date.today()
    yesterday = current_date - timedelta(days=1)
    file_name = f'new_data_{yesterday}.xlsx'

    # Create a buffer to store the Excel file
    buffer = io.BytesIO()
    filtered_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Download button
    st.download_button(
        label="Download Processed Excel File",
        data=buffer,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Optional: Display basic statistics
    st.subheader("Data Summary")
    st.write(f"Total Records: {len(filtered_df)}")
    st.write(f"Total 위탁량: {filtered_df['위탁량'].sum():,.2f}")
else:
    st.info("Please upload an Excel file to start processing.")
