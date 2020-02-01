use std::env;
use warp::Filter;

mod models;

#[tokio::main]
async fn main() {
    if env::var_os("RUST_LOG").is_none() {
        env::set_var("RUST_LOG", "info");
    }
    pretty_env_logger::init();

    let filters = all_filters();
    warp::serve(filters).run(([127, 0, 0, 1], 5000)).await;
}

pub fn all_filters() -> impl Filter<Extract = impl warp::Reply, Error = warp::Rejection> + Clone {
    let articles_list = warp::path!("articles")
        .and(warp::get())
        .and_then(handlers::articles_list);

    let articles_create = warp::path!("articles")
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handlers::articles_create);

    articles_list.or(articles_create)
}

mod handlers {
    use std::convert::Infallible;
    use warp::Reply;

    pub async fn articles_list() -> Result<impl Reply, Infallible> {
        // TODO
        Ok(warp::http::StatusCode::INTERNAL_SERVER_ERROR)
    }

    pub async fn articles_create(_data: serde_json::Value) -> Result<impl Reply, Infallible> {
        // TODO
        Ok(warp::http::StatusCode::INTERNAL_SERVER_ERROR)
    }
}
