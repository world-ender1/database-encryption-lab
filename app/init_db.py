"""Create the demo schema; this is not a migration system."""
from app import models  # noqa: F401
from app.database import Base, engine


def main() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
