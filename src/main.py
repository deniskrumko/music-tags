from app import TaggingApp

# from music import MusicClient


def main() -> None:
    # MusicClient().tag_options
    app = TaggingApp()
    app.run()


if __name__ == "__main__":
    main()
