from flask import Flask, render_template


def init_error_handling(app: Flask):
    def render_error(code: int, message: str):
        return render_template("base/error.html", code=code, error_msg=message), code

    @app.errorhandler(401)
    def unauthorized(e):
        return render_error(401, "กรุณาเข้าสู่ระบบก่อนใช้งานหน้านี้")

    @app.errorhandler(403)
    def forbidden(e):
        return render_error(403, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_error(404, "ไม่พบหน้าที่ต้องการ")

    @app.errorhandler(500)
    def server_error(e):
        return render_error(500, "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง")
