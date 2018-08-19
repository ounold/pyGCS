import pykka


class JobsStateStorage(pykka.ThreadingActor):
    def __init__(self, parsing_states):
        super(JobsStateStorage, self).__init__()
        self.parsing_states = parsing_states

    def update_cell_state(self, i, j):
        self.parsing_states[i][j] = True

    def get_cell_state(self, i, j):
        return self.parsing_states[i][j]
