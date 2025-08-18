"""
if __name__ == "__main__":
    import uvicorn
    from {{project_name}}.api import create_application

    app = create_application()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        app_dir=".",
        reload=False,
        log_config="conf/uvicorn.log.yaml",
    )
"""
