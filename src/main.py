from app import TaggingApp
from music import MusicClient


def main() -> None:
    MusicClient()
    app = TaggingApp()
    app.run()


if __name__ == "__main__":
    main()
