use rweb::{get, reply, serve, Filter};
use serde::{Deserialize, Serialize};
use std::env;

#[get("/")]
#[cors(origins("*"))]
fn index() -> &'static str {
    "Index page"
}

#[derive(Debug, Serialize, Deserialize)]
struct Product {
    id: String,
    title: String,
}

#[get("/products")]
#[cors(origins("*"))]
fn products() -> reply::Json {
    let products = vec![
        Product {
            id: "1".to_owned(),
            title: "AAA".to_owned(),
        },
        Product {
            id: "2".to_owned(),
            title: "BBB".to_owned(),
        },
    ];
    reply::json(&products)
}

#[tokio::main]
async fn main() {
    if env::var_os("RUST_LOG").is_none() {
        env::set_var("RUST_LOG", "info");
    }
    pretty_env_logger::init();
    serve(index().or(products()))
        .run(([127, 0, 0, 1], 5000))
        .await;
}
