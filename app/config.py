from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # This tells Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()


if __name__ == '__main__':
    print(settings.DATABASE_URL)
    print(settings.model_config)
