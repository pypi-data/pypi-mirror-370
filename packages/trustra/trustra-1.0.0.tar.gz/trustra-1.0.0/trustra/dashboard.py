# trustra/dashboard.py
import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="TrustRA Dashboard", layout="wide")
    st.title("🛡️ TrustRA: Trust-First AutoML")

    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write("### Data Preview", df.head())
        target = st.selectbox("Select Target", df.columns)
        if st.button("Run TrustRA"):
            from trustra import TrustRA
            X, y = df.drop(columns=[target]), df[target]
            model = TrustRA(target=target)
            model.fit(X, y)
            st.success("✅ TrustRA pipeline completed!")
            st.write("Best CV AUC:", f"{model.trainer_.best_score_:.3f}")
            st.markdown("[View Full Trust Report](trustra_report.html)")

if __name__ == "__main__":
    main()