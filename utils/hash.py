import werkzeug.security
def generate_password_hash(password):
    return werkzeug.security.generate_password_hash(password)

def check_password_hash(hash, password):
    return werkzeug.security.check_password_hash(hash, password)