from app import create_app  # or from run import app if that's how you structured it

app = create_app()

if __name__ == "__main__":
    app.run()


