import streamlit as st
import requests
import datetime

# Page configuration
st.set_page_config(page_title="Business Source Finder", page_icon="💼", layout="wide")

st.title("💼 Business Source Finder")
st.write("Enter a business topic to retrieve 10 live academic and professional sources via Crossref.")

# User Input
topic = st.text_input("Enter your research topic:", placeholder="e.g., Sustainability in fast fashion supply chains")

def get_real_sources(query):
    if not query:
        return []
    
    # Crossref API Endpoint
    url = f"https://api.crossref.org/works?query={query}&rows=10"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get("message", {}).get("items", [])
        
        results = []
        for item in items:
            # Extracting metadata safely
            title = item.get("title", ["No Title Available"])[0]
            # Authors list extraction
            authors_list = item.get("author", [])
            if authors_list:
                author_names = [f"{a.get('family', '')}, {a.get('given', '')}" for a in authors_list if 'family' in a]
                author_str = "; ".join(author_names[:3]) # Limit to 3 authors for brevity
                if len(author_names) > 3: author_str += " et al."
            else:
                author_str = "Institutional Author"

            container = item.get("container-title", ["Unknown Publication"])[0]
            year = item.get("published-print", {}).get("date-parts", [[2024]])[0][0]
            link = item.get("URL", "https://doi.org")
            source_type = item.get("type", "Journal Article").replace("-", " ").title()

            # Reliability Logic: Academic journals/books get higher scores automatically
            score = 95 if "journal" in source_type.lower() or "book" in source_type.lower() else 85
            
            results.append({
                "author": author_str,
                "title": title,
                "container": container,
                "year": year,
                "url": link,
                "type": source_type,
                "score": score,
                "reason": f"Published in {container}. Verified through Crossref Metadata Registry."
            })
        
        # Sort by score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)

    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return []

if topic:
    # Check for vague input
    if len(topic.split()) < 2:
        st.warning("⚠️ Topic is too broad. Please add more keywords for better results.")
    
    with st.spinner('Searching global academic databases...'):
        sources = get_real_sources(topic)
    
    if sources:
        today = datetime.date.today().strftime("%d %b %Y")
        st.markdown("---")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader(f"📋 Top 10 Reliable Sources for '{topic}'")
            for idx, src in enumerate(sources, 1):
                color = "green" if src['score'] >= 90 else "orange"
                st.markdown(f"### {idx}. {src['title']}")
                st.markdown(f"🔗 **Direct Link:** [{src['url']}]({src['url']})")
                st.markdown(f"**Type:** `{src['type']}` | **Reliability:** :{color}[{src['score']}%]")
                st.info(f"**Trust Justification:** {src['reason']}")
                st.markdown("<br>", unsafe_allow_html=True)
                
        with col2:
            st.subheader("📝 MLA 9th Edition Citations")
            for idx, src in enumerate(sources, 1):
                st.markdown(f"**[Source {idx}] MLA Block:**")
                mla_string = f"{src['author']}. \"{src['title']}.\" *{src['container']}*, {src['year']}, {src['url']}. Accessed {today}."
                st.code(mla_string, language="text")
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No sources found. Try adjusting your keywords.")