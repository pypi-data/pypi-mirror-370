from .carlapy import app

if __name__ in "__main__":
    try:
        app()
    except RuntimeError as e:
        print(e)
