from app import create_app

app = create_app()

if __name__ == "__main__":
    # Run with HTTPS using self-signed certs
    app.run(
        host="127.0.0.1",
        port=433,
        ssl_context=("certs/cert.pem", "certs/key.pem")
    )
