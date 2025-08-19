import streamlit as st
import pickle
import pandas as pd
import plotly.express as px

# ----------------------
# Load data
# ----------------------
df_feat = pickle.load(open("leetcode_dict.pkl", "rb"))
df_feat = pd.DataFrame(df_feat)  # ensure dataframe
similarity_matrix = pickle.load(open("similarity.pkl", "rb"))


# ----------------------
# Recommender function
# ----------------------
def recommend_problems_filtered(title, top_n=5, difficulty=None, company=None, topic=None):
    if title not in df_feat["title"].values:
        return []

    idx = df_feat.index[df_feat["title"] == title][0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]

    filtered = []
    for i, score in sim_scores:
        row = df_feat.iloc[i]
        if difficulty is not None and row["difficulty"] != difficulty:
            continue
        if company is not None and f"company_{company}" in df_feat.columns:
            if row[f"company_{company}"] != 1:
                continue
        if topic is not None and f"topic_{topic}" in df_feat.columns:
            if row[f"topic_{topic}"] != 1:
                continue
        filtered.append((row["title"], row["url"], row["difficulty"], score))
        if len(filtered) >= top_n:
            break
    return filtered


# ----------------------
# Streamlit UI
# ----------------------
st.set_page_config(page_title="LeetCode Recommender", page_icon="📘", layout="wide")

st.title("📘 LeetCode Problem Recommender")
st.markdown("### Get smart recommendations for similar problems with interactive filters 🚀")

# Sidebar for filters
st.sidebar.header("🔧 Filters")

difficulty = st.sidebar.selectbox("🎯 Difficulty", ["Any", "Easy", "Medium", "Hard"])
difficulty = None if difficulty == "Any" else difficulty

company = st.sidebar.selectbox(
    "🏢 Company", ["Any"] + [c.replace("company_", "") for c in df_feat.columns if c.startswith("company_")]
)
company = None if company == "Any" else company

topic = st.sidebar.selectbox(
    "📚 Topic", ["Any"] + [t.replace("topic_", "") for t in df_feat.columns if t.startswith("topic_")]
)
topic = None if topic == "Any" else topic

top_n = st.sidebar.slider("📊 Number of recommendations", 3, 10, 5)

# Search box for problem title
selected_problem = st.text_input("🔍 Enter a problem title", "")
if not selected_problem:
    selected_problem = st.selectbox("Or select from dropdown", df_feat["title"].values)

# Button
if st.button("✨ Get Recommendations"):
    recommendations = recommend_problems_filtered(selected_problem, top_n, difficulty, company, topic)

    if recommendations:
        st.subheader(f"✅ Top {top_n} Recommended Problems for **{selected_problem}**")

        # Convert to dataframe for table
        rec_df = pd.DataFrame(recommendations, columns=["Title", "URL", "Difficulty", "Similarity"])

        # Display in nice format
        for i, row in rec_df.iterrows():
            with st.expander(f"{i + 1}. {row['Title']}  |  🎯 {row['Difficulty']}"):
                st.markdown(f"[👉 Solve on LeetCode]({row['URL']})")
                st.progress(float(row["Similarity"]))  # similarity as progress bar
                st.write(f"Similarity Score: **{row['Similarity']:.2f}**")

                # -------------------
                # Extra Info
                # -------------------
                full_row = df_feat[df_feat["title"] == row["Title"]].iloc[0]

                # Companies
                company_cols = [c for c in df_feat.columns if c.startswith("company_")]
                companies = [c.replace("company_", "") for c in company_cols if full_row[c] == 1]
                if companies:
                    st.write("🏢 **Asked by Companies:** " + ", ".join(companies))
                else:
                    st.write("🏢 **Asked by Companies:** None")

                # Topics
                topic_cols = [t for t in df_feat.columns if t.startswith("topic_")]
                topics = [t.replace("topic_", "") for t in topic_cols if full_row[t] == 1]
                if topics:
                    st.write("📚 **Related Topics:** " + ", ".join(topics))
                else:
                    st.write("📚 **Related Topics:** None")


        # Show chart of similarity
        fig = px.bar(rec_df, x="Title", y="Similarity", color="Difficulty", title="🔎 Similarity Scores")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No recommendations found with the selected filters.")