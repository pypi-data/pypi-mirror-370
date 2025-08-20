def now():
    import pendulum
    return pendulum.now("Asia/Shanghai").strftime("%m-%d %H:%M:%S")
