# sql课上演示.py
# 个人信息管理系统 — Streamlit + SQLite3 最小示例（课堂演示版）

import sqlite3
from datetime import datetime
import streamlit as st

DB_PATH = "pmis.db"
CATEGORIES = ["荣誉", "教育经历", "竞赛", "证书", "账号", "其他"]

# ---------- 数据访问层（封装 SQL，便于课堂逐条讲解）----------
def init_db() -> None:
    """建表：CREATE TABLE IF NOT EXISTS"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            category   TEXT,
            notes      TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_all() -> list:
    """查询全部：SELECT ... ORDER BY"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # 让行支持按列名取值
    rows = conn.execute(
        "SELECT id, title, category, notes, created_at FROM records ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows

def insert(title: str, category: str, notes: str) -> None:
    """新增：INSERT INTO ... VALUES (?)  -- 用占位符防 SQL 注入"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO records (title, category, notes, created_at) VALUES (?, ?, ?, ?)",
        (title, category, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()

def delete(rid: int) -> None:
    """删除：DELETE FROM ... WHERE id = ?"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM records WHERE id = ?", (rid,))
    conn.commit()
    conn.close()

# ---------- 页面层 ----------
st.set_page_config(page_title="个人信息管理系统", page_icon="📋", layout="wide")
init_db()

st.title("📋 个人信息管理系统")
st.caption("技术栈：Streamlit（前端） + SQLite3（数据底座） · 课堂最小演示")

# 1) 输入表单（对应 INSERT）
with st.form("add_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    title = c1.text_input("标题 *", placeholder="例如：三好学生")
    category = c2.selectbox("类别", CATEGORIES, index=0)
    notes = st.text_area("备注（可选）", placeholder="关键信息、链接或行动项…", height=100)
    if st.form_submit_button("保存", type="primary", use_container_width=True):
        if not title.strip():
            st.error("标题不能为空")
        else:
            insert(title.strip(), category, notes.strip())
            st.success("已保存 ✅")

# 2) 列表展示（对应 SELECT）
st.subheader("记录列表")
rows = fetch_all()
if not rows:
    st.info("暂无数据，请在上方添加一条记录。")
else:
    headers = ["ID", "标题", "类别", "备注", "创建时间", "操作"]
    cols = st.columns([1, 4, 2, 4, 2, 1])
    for col, h in zip(cols, headers):
        col.write(f"**{h}**")
    for row in rows:
        cols = st.columns([1, 4, 2, 4, 2, 1])
        cols[0].write(row["id"])
        cols[1].write(row["title"])
        cols[2].write(row["category"])
        cols[3].write(row["notes"] or "")
        cols[4].write(row["created_at"])
        if cols[5].button("删除", key=f"del_{row['id']}"):
            delete(row["id"])
            st.rerun()

# 3) 课堂加分项：把当前用到的 SQL 集中展示
with st.expander("📚 本示例涉及的 SQL 语句"):
    st.code(
        """
-- 建表
CREATE TABLE IF NOT EXISTS records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    category   TEXT,
    notes      TEXT,
    created_at TEXT
);

-- 查询全部
SELECT id, title, category, notes, created_at FROM records ORDER BY id DESC;

-- 新增（参数化，防注入）
INSERT INTO records (title, category, notes, created_at) VALUES (?, ?, ?, ?);

-- 删除
DELETE FROM records WHERE id = ?;
""",
        language="sql",
    )