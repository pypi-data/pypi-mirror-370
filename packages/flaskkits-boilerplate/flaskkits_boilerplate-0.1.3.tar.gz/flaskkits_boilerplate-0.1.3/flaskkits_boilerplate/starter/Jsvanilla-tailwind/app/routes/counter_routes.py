from ..blueprints import main
from ..controllers.counter_controller import counter_view

@main.route('/', methods=['GET'])
def home():
    return counter_view()
