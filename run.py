"""Flask application entrypoint for the weather data API."""
# run.py

from flask import Flask
from flask_smorest import Api

from app.models import Base, engine
from app.routes.stats import blp as stats_blp
from app.routes.weather import blp as weather_blp

# --- Auto-create any missing tables on startup ---
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config.update(
    {
        "API_TITLE": "Agro Data API",
        "API_VERSION": "v1",
        "OPENAPI_VERSION": "3.0.2",
        "OPENAPI_URL_PREFIX": "/",  # serve spec at /openapi.json
        # you can also set OPENAPI_JSON_PATH (default "openapi.json")
    }
)

api = Api(app)

# register weather endpoints
api.register_blueprint(weather_blp)  # GET /api/weather/
api.register_blueprint(stats_blp)  # GET /api/weather/stats/

if __name__ == "__main__":
    # for local development; in Docker the compose file will map port 5001
    app.run(host="0.0.0.0", port=5000, debug=True)
