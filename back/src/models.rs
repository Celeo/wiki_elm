#![allow(unused)]

use rusqlite::{params, Connection, Result as DbResult};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub struct Article {
    id: i64,
    title: String,
    content: String,
    created_by: String,
    time_created: i64,
    last_edited_by: Option<String>,
    last_edit_time: Option<i64>,
}

#[derive(Debug)]
pub struct User {
    id: i64,
    name: String,
    password: String,
}

impl Article {
    pub fn new(title: &str, content: &str, created_by: &str) -> Self {
        Self {
            id: 0,
            title: title.to_owned(),
            content: content.to_owned(),
            created_by: created_by.to_owned(),
            time_created: chrono::Utc::now().timestamp(),
            last_edited_by: None,
            last_edit_time: None,
        }
    }
}

pub fn open_db() -> DbResult<Connection> {
    Connection::open("./data.db")
}

pub fn create_tables(conn: &Connection) -> DbResult<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_by TEXT NOT NULL,
            time_created BIGINT,
            last_edited_by TEXT,
            last_edit_time BIGINT
        )",
        params![],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )",
        params![],
    )?;
    Ok(())
}

pub fn get_all_articles(conn: &Connection) -> DbResult<Vec<Article>> {
    let mut statement = conn.prepare("SELECT * FROM articles")?;
    let article_iter = statement.query_map(params![], |row| {
        Ok(Article {
            id: row.get(0)?,
            title: row.get(1)?,
            content: row.get(2)?,
            created_by: row.get(3)?,
            time_created: row.get(4)?,
            last_edited_by: row.get(5)?,
            last_edit_time: row.get(6)?,
        })
    })?;
    article_iter.collect()
}

pub fn add_article(conn: &Connection, article: &Article) -> DbResult<()> {
    conn.execute(
        "INSERT INTO articles (title, created_by, time_created) VALUES (?1, ?2, ?3)",
        params![article.title, article.created_by, article.time_created],
    )?;
    Ok(())
}

pub fn update_article(
    conn: &Connection,
    id: i64,
    title: &str,
    content: &str,
    by: &str,
) -> DbResult<()> {
    conn.execute(
        "UPDATE articles SET
            title=?1,
            content=?2,
            last_edited_by=?2,
            last_edit_time=?4
        WHERE
            id=?5",
        params![title, content, by, chrono::Utc::now().timestamp(), id],
    )?;
    Ok(())
}
