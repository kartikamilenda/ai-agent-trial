import streamlit as st
from database import init_database
from coordinator import Coordinator
from tools.task_tools import list_tasks, check_overdue, task_summary

st.set_page_config(page_title='Meeting Action AI Agent', page_icon='📋', layout='wide')
init_database()
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = Coordinator()
c = st.session_state.coordinator
st.title('Meeting Action AI Agent')
st.caption('Local Qwen3 + Ollama | Sequential two-agent prototype | SQLite')
tab1, tab2, tab3 = st.tabs(['Extract & approve', 'Manage tasks', 'Statistics'])
with tab1:
    notes = st.text_area('Meeting notes / transcript', height=200, placeholder='Andi menyelesaikan API login tanggal 6 November...')
    if st.button('Analyze meeting', type='primary'):
        try:
            st.session_state.preview = c.analyze(notes)
        except Exception as exc:
            st.error(f'Extraction failed: {exc}')
    if 'save_result' in st.session_state:
        result = st.session_state.pop('save_result')
        st.success(f"Saved {len(result['created'])} task(s).")
        if result['needs_clarification']:
            st.warning(f"{len(result['needs_clarification'])} incomplete task(s) remain for clarification.")
        if result['errors']:
            st.error(result['errors'])
    if c.pending:
        st.subheader('Review extracted items')
        st.info('Only complete tasks are saved. Missing PIC or deadline requires clarification. Nothing is saved until you approve.')
        for idx, item in enumerate(c.pending):
            with st.expander(f'{idx+1}. {item.title}', expanded=bool(item.missing)):
                st.caption(f'Source: {item.source_excerpt or "Not provided"}')
                pic = st.text_input('PIC', value=item.assignee or '', key=f'pic_{idx}')
                deadline = st.text_input('Deadline YYYY-MM-DD', value=item.deadline.isoformat() if item.deadline else '', key=f'date_{idx}')
                if st.button('Apply correction', key=f'edit_{idx}'):
                    try:
                        c.clarify(idx, pic, deadline)
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
                if item.missing:
                    st.warning('Missing: ' + ', '.join(item.missing))
        if st.button('Approve and save complete tasks'):
            st.session_state.save_result = c.confirm_and_save()
            st.rerun()
with tab2:
    query = st.text_input('Ask Agent 2', placeholder='Tampilkan semua tugas overdue / Ubah status tugas 1 menjadi completed')
    if st.button('Run task agent') and query.strip():
        try:
            st.write(c.command(query))
        except Exception as exc:
            st.error(f'Agent failed: {exc}')
    st.subheader('Stored tasks')
    st.dataframe(list_tasks(), use_container_width=True)
with tab3:
    st.json(task_summary())
    st.subheader('Overdue tasks')
    st.dataframe(check_overdue(), use_container_width=True)
