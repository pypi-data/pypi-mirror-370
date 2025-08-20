from sparrow.api import create_app

__all__ = ["create_application"]


def create_application():
    app = create_app(
        title="{{project_name}}",
        version="1.0",
    )

    app.add_exception_handler()
    return app
