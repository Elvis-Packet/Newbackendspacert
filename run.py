from app import create_app
from app.models.user import User
from app.models.space import Space, SpaceImage
from app.models.booking import Booking, Payment
from app import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Space': Space,
        'SpaceImage': SpaceImage,
        'Booking': Booking,
        'Payment': Payment
    }

if __name__ == '__main__':
    app.run(debug=True) 