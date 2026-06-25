from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "storage-service"
    environment: str = "development"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/storage"

    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "storage"
    keycloak_client_id: str = "storage-app"
    keycloak_client_secret: str = ""

    file_storage_path: str = "C:\\pr_files"
    max_upload_size_bytes: int = 1_073_741_824  # 1 ГБ на файл

    default_quota_bytes: int = 3_221_225_472  # 3 ГБ на хранилище
    default_max_file_size: int = 1_073_741_824  # 1 ГБ на файл

    jwt_algorithm: str = "RS256"
    jwt_audience: str = "account"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
