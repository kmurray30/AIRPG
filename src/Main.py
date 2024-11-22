from View import View
from Presenter import Presenter

def main() -> None:
    # model = Model()
    view = View()
    presenter = Presenter(view)
    presenter.run()

if __name__ == "__main__":
    main()