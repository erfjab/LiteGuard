def create_qr(content: str) -> str:
    return f"https://api.qrserver.com/v1/create-qr-code/?data={content}&margin=20&qzone=1"
