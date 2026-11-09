
import streamlit as st

from database import init_database
from coordinator import Coordinator
from tools.task_tools import (
    list_tasks,
    check_overdue,
    task_summary
)


# =========================================================
# 1. Application Configuration
# =========================================================

st.set_page_config(
    page_title="Meeting Action AI Agent",
    page_icon="📋",
    layout="wide"
)

init_database()

if "coordinator" not in st.session_state:
    st.session_state.coordinator = Coordinator()

c = st.session_state.coordinator

st.title("Meeting Action AI Agent")
st.caption(
    "Local Qwen3 + Ollama | "
    "Sequential two-agent prototype | SQLite"
)


# =========================================================
# 2. Helper Functions
# =========================================================

def display_tasks(tasks, empty_message):
    """Display tasks without st.dataframe / PyArrow."""

    if not tasks:
        st.info(empty_message)
        return

    for task in tasks:
        with st.container(border=True):
            st.markdown(
                f"**Task #{task['id']} — {task['title']}**"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"**PIC:** {task['assignee']}"
                )

            with col2:
                st.write(
                    f"**Deadline:** {task['deadline']}"
                )

            with col3:
                st.write(
                    f"**Status:** {task['status']}"
                )


# =========================================================
# 3. Navigation
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "Extract & approve",
    "Manage tasks",
    "Statistics"
])


# =========================================================
# TAB 1 — Agent 1: Meeting Extraction & Approval
# =========================================================

with tab1:

    st.subheader("Meeting Action Item Extraction")

    notes = st.text_area(
        "Meeting notes / transcript",
        height=220,
        placeholder=(
            "Tuliskan / Pindahkan "
            "Hasil Notulensi disini.."
        )
    )

    if st.button(
        "Analyze meeting",
        type="primary"
    ):
        if not notes.strip():
            st.warning(
                "Masukkan catatan rapat terlebih dahulu."
            )
        else:
            try:
                with st.spinner(
                    "Agent 1 sedang menganalisis rapat..."
                ):
                    c.analyze(notes)

                st.success(
                    "Analisis rapat berhasil."
                )

            except Exception as exc:
                st.error(
                    f"Extraction failed: {exc}"
                )

    # Display result from previous save
    if "save_result" in st.session_state:

        result = st.session_state.pop(
            "save_result"
        )

        if result["created"]:
            st.success(
                f"{len(result['created'])} "
                "task berhasil diproses."
            )

        if result["needs_clarification"]:
            st.warning(
                f"{len(result['needs_clarification'])} "
                "task masih membutuhkan klarifikasi."
            )

        if result["errors"]:
            st.error(
                f"{len(result['errors'])} "
                "task gagal disimpan."
            )

            for error in result["errors"]:
                st.write(error)

    # Review extracted items
    if c.pending:

        st.divider()
        st.subheader("Review Extracted Action Items")

        preview = c.preview()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Pending",
            len(c.pending)
        )

        col2.metric(
            "Ready",
            preview["ready"]
        )

        col3.metric(
            "Incomplete",
            preview["incomplete"]
        )

        st.info(
            "Periksa hasil ekstraksi sebelum menyimpan. "
            "Task yang belum memiliki PIC atau deadline "
            "harus diklarifikasi. "
            "Penyimpanan memerlukan persetujuan pengguna."
        )

        has_unapplied_changes = False

        for idx, item in enumerate(c.pending):

            with st.expander(
                f"{idx + 1}. {item.title}",
                expanded=bool(item.missing)
            ):

                st.caption(
                    f"Source: "
                    f"{item.source_excerpt or 'Not provided'}"
                )

                # Stable keys using item_id
                pic_key = f"pic_{item.item_id}"
                date_key = f"date_{item.item_id}"

                pic = st.text_input(
                    "PIC",
                    value=item.assignee or "",
                    key=pic_key
                )

                deadline = st.text_input(
                    "Deadline (YYYY-MM-DD)",
                    value=(
                        item.deadline.isoformat()
                        if item.deadline
                        else ""
                    ),
                    key=date_key
                )

                current_pic = item.assignee or ""

                current_deadline = (
                    item.deadline.isoformat()
                    if item.deadline
                    else ""
                )

                changed = (
                    pic != current_pic
                    or deadline != current_deadline
                )

                if changed:
                    has_unapplied_changes = True

                    st.warning(
                        "Ada perubahan yang belum diterapkan."
                    )

                if st.button(
                    "Apply correction",
                    key=f"edit_{item.item_id}"
                ):
                    try:
                        c.clarify(
                            index=idx,
                            assignee=pic,
                            deadline=deadline
                        )

                        st.rerun()

                    except Exception as exc:
                        st.error(str(exc))

                if item.missing:
                    st.warning(
                        "Missing: "
                        + ", ".join(item.missing)
                    )

        # Approval button OUTSIDE the loop
        st.divider()

        if has_unapplied_changes:
            st.warning(
                "Terapkan seluruh perubahan sebelum "
                "melakukan approval."
            )

        if st.button(
            "Approve and save complete tasks",
            type="primary",
            disabled=(
                has_unapplied_changes
                or preview["ready"] == 0
            )
        ):
            try:
                c.approve()

                st.session_state.save_result = (
                    c.confirm_and_save()
                )

                st.rerun()

            except (ValueError, PermissionError) as exc:
                st.error(str(exc))

            except Exception as exc:
                st.error(
                    f"Task saving failed: {exc}"
                )


# =========================================================
# TAB 2 — Agent 2: Task Management
# =========================================================

with tab2:

    st.subheader("Task Management Agent")

    query = st.text_input(
        "Ask Agent 2",
        placeholder=(
            "Tampilkan tugas overdue / "
            "Ubah status tugas 1 menjadi completed"
        )
    )

    if st.button("Run task agent"):

        if not query.strip():
            st.warning(
                "Masukkan perintah terlebih dahulu."
            )
        else:
            try:
                with st.spinner(
                    "Agent 2 sedang memproses permintaan..."
                ):
                    response = c.command(query)

                st.write(response)

            except Exception as exc:
                st.error(
                    f"Agent failed: {exc}"
                )

    st.divider()
    st.subheader("Stored Tasks")

    try:
        tasks = list_tasks()

        display_tasks(
            tasks,
            "Belum ada tugas tersimpan."
        )

    except Exception as exc:
        st.error(
            f"Failed to load tasks: {exc}"
        )


# =========================================================
# TAB 3 — Statistics and Overdue Monitoring
# =========================================================

with tab3:

    st.subheader("Task Statistics")

    try:
        summary = task_summary()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Tasks",
            summary["total"]
        )

        col2.metric(
            "Pending",
            summary["pending"]
        )

        col3.metric(
            "In Progress",
            summary["in_progress"]
        )

        col4.metric(
            "Completed",
            summary["completed"]
        )

        st.metric(
            "Overdue Tasks",
            summary["overdue"]
        )

        st.divider()
        st.subheader("Overdue Tasks")

        overdue_tasks = check_overdue()

        display_tasks(
            overdue_tasks,
            "Tidak ada tugas overdue."
        )

    except Exception as exc:
        st.error(
            f"Failed to load statistics: {exc}"
        )
