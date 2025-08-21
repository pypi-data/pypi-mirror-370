from ewokscore.task import Task
from ewoksdata.data.bliss import last_lima_image


class LastLimaImage(
    Task, input_names=["db_name"], optional_input_names=["demo"], output_names=["image"]
):
    """Get the last Lima image from Redis"""

    def run(self):
        image = last_lima_image(self.inputs.db_name)
        if self.inputs.demo:
            image = image[:-1, :-1]
        self.outputs.image = image
