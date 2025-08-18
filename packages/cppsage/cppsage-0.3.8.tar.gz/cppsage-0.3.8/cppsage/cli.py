from .commands import app

def main():
    import sys
    if len(sys.argv)==1:
        app(["about"])
    else:
        app()
if __name__ == "__main__":
    main()