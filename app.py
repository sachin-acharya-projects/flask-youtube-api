from crypt import methods
from youtubesearchpython import (
    VideosSearch,
    Playlist,
    Video,
    StreamURLFetcher,
    ResultMode,
    CustomSearch,
    SearchMode,
)
from flask import request, jsonify, Flask
import os, json, dotenv

dotenv.load_dotenv()
app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
fetcher = StreamURLFetcher()


def save(data: VideosSearch):
    with open("data.json", "w") as file:
        file.seek(0)
        file.truncate()
        json.dump(data, file, indent=4)


@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "_": "Format for requesting data. (ommit 'message' parameter) (require JSON)",
            "secret_key": "SECRET_REGISTERED_KEY",
            "media_url": "YouTube url of Playlist or Video",
            "video_title": "Title of YouTube video",
            "limit": "<int: 5>",
            "endpoints": [
                "/api/video",
                "/api/playlist",
                "/api/search",
            ],
        }
    )


@app.route("/api/search/", methods=["POST"])
def search_video():
    queries = request.args
    secret_key = queries.get("secret_key", None)
    if secret_key and secret_key == SECRET_KEY:
        try:
            video_name = queries["video_title"]
        except:
            return (
                jsonify(
                    {
                        "message": "Invalid input parameter ── video_title",
                        "status": "failed",
                        "status_code": 400,
                    }
                ),
                400,
            )
        limit = int(queries.get("limit", "5"))
        if limit > 20:
            limit = 20
        searched_videos = VideosSearch(video_name, limit)
        return searched_videos.result()
    else:
        return (
            jsonify(
                {
                    "message": "unauthorized user",
                    "help": "recheck secret_key for invalidity or incorrectness",
                    "status": "failed",
                    "accepted_queries": [
                        "secret_key (required) ── Secret Authorization Key",
                        "video_title (required) ── Name or title of YouTube video to search",
                        "limit (optional, default: 5) ── Total number of results required, max. 20",
                    ],
                    "request_time": "unlimited",
                    "status_code": 401,
                }
            ),
            401,
        )


@app.route("/api/playlist/", methods=["POST"])
def get_playlist():
    pass


@app.route("/api/video/", methods=["POST"])
def get_videos():
    queries = request.args
    secret_key = queries.get("secret_key", None)
    if secret_key and secret_key == SECRET_KEY:
        try:
            media_url = queries["media_url"]
            result_mode = queries["result_mode"]
            videos = ""
            if result_mode == "info":
                videos = Video.getInfo(media_url, mode=ResultMode.json)
            elif result_mode == "formats":
                stuff = Video.get(media_url, mode=ResultMode.json)
                videos = fetcher.getAll(stuff)
            else:
                videos = Video.get(media_url, mode=ResultMode.json)
            return videos
        except Exception as e:
            print(e)
            return (
                jsonify(
                    {
                        "message": "invalid input parameters",
                        "status": "failed",
                        "status_code": 400,
                    }
                ),
                400,
            )

    else:
        return (
            jsonify(
                {
                    "message": "unauthorized user",
                    "help": "recheck secret_key for invalidity or incorrectness",
                    "status": "failed",
                    "accepted_queries": [
                        "media_url (required) ── YouTube video URL (/watch?v=)",
                        "result_mode (required) ── accepted_value: [all | formats | info]",
                    ],
                    "request_time": "unlimited",
                    "status_code": 401,
                }
            ),
            401,
        )


if __name__ == "__main__":
    app.run(debug=True)
