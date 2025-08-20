from carlapy.carlapy import app

if __name__ == "__main__":
    try:
        app()
    except RuntimeError as e:
        print(e)
