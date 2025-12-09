use actix_web::{web, App, HttpResponse, HttpServer, Result};
use serde_json::json;

async fn index() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(json!({
        "message": "Welcome to {{project_name}}"
    })))
}

async fn health() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(json!({
        "status": "healthy"
    })))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    
    println!("Starting {{project_name}} server...");
    
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(index))
            .route("/health", web::get().to(health))
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}
