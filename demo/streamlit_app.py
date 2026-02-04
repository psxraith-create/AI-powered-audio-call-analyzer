"""Simple Streamlit UI for the AI Call Guardian demo.
Upload audio -> POST to FastAPI -> display transcript and risk meter.

For Codespaces, pass the public URL via environment:
  BACKEND_URL=https://your-codespace-8000.app.github.dev streamlit run demo/streamlit_app.py
"""
import streamlit as st
import requests
import os

# Get backend URL from environment, sidebar input, or default
default_backend = os.getenv('BACKEND_URL', 'http://localhost:8000')
BACKEND_URL = st.sidebar.text_input('Backend URL', default_backend)

st.sidebar.markdown("""
---
### 📌 Codespaces Users
Copy your public URL here:
```
https://<codespace-name>-8000.app.github.dev
```
""")

st.title('AI Call Guardian — Demo')
st.markdown('Upload a call audio (wav/mp3) to analyze scam risk (English + Hindi + Hinglish)')

# One-click demo button
if st.button('🚀 Run one-click demo (no upload needed)'):
    with st.spinner('Analyzing sample...'):
        try:
            r = requests.get(BACKEND_URL + '/analyze_sample', timeout=10)
            if r.status_code == 200:
                res = r.json()
                st.success('✓ Demo analysis complete!')
                
                if res.get('fallback_mode'):
                    st.warning(res.get('fallback_message', 'Fallback demo mode enabled.'))
                
                st.subheader('Transcript')
                st.write(res.get('transcript', ''))
                
                st.subheader('Matched Keywords')
                st.write(res.get('matched_keywords', []))
                
                st.subheader('Behavior Analysis')
                st.json(res.get('behavior', {}))
                
                st.subheader('Risk Assessment')
                risk = res.get('risk', {}).get('risk_score', 0)
                alert = res.get('risk', {}).get('alert', False)
                st.progress(int(min(100, max(0, risk))))
                if alert:
                    st.error('🚨 **ALERT: Potential Scam Detected**')
                else:
                    st.info('✓ **No immediate scam detected**')
            else:
                st.error(f'Demo failed with status {r.status_code}')
        except Exception as e:
            st.error(f'Error contacting backend: {str(e)}')

st.markdown('---')

# File upload option
uploaded = st.file_uploader('(Or) Upload your own audio', type=['wav', 'mp3', 'm4a'])
if uploaded is not None:
    with st.spinner('Uploading and analyzing...'):
        files = {'file': (uploaded.name, uploaded.getvalue(), uploaded.type)}
        try:
            r = requests.post(BACKEND_URL + '/analyze', files=files, timeout=30)
            r.raise_for_status()
            res = r.json()

            st.success('✓ Analysis complete!')

            # Show fallback notice if active
            if res.get('fallback_mode'):
                st.warning(res.get('fallback_message', 'Fallback demo mode enabled.'))
                st.info(f"Reason: {res.get('fallback_reason')}")

            st.subheader('Transcript')
            st.write(res.get('transcript', ''))

            st.subheader('Matched Keywords')
            st.write(res.get('matched_keywords', []))

            st.subheader('Behavior Analysis')
            st.json(res.get('behavior', {}))

            st.subheader('Risk Assessment')
            risk = res.get('risk', {}).get('risk_score', 0)
            alert = res.get('risk', {}).get('alert', False)
            st.progress(int(min(100, max(0, risk))))
            if alert:
                st.error('🚨 **ALERT: Potential Scam Detected**')
            else:
                st.info('✓ **No immediate scam detected**')

        except requests.exceptions.ConnectionError:
            st.error(f'❌ Cannot connect to backend at `{BACKEND_URL}`\n\nIs the server running? Check the backend URL in the sidebar.')
        except Exception as e:
            st.error(f'Error: {str(e)}')

else:
    st.info('💡 Click "Run one-click demo" above for instant analysis without uploading files.')

