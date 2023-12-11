# let the database save nums rather than terms
import enum


class SkillTargets(enum.IntEnum):
    Herself = 1
    Her_Team = 2
    All = 3
    Opponent_TeamA = 4
    Opponent_TeamK = 5
    Opponent_TeamB = 6
    Opponent_Team4 = 7
    Opponent_Team8 = 8

    def display_name(self):
        return self.name.replace("_", " ")

    @classmethod
    def from_display_name(cls, display_name):
        enum_name = display_name.replace(" ", "_")
        return getattr(cls, enum_name, None)


class SkillTypes(enum.IntEnum):
    singing = 1
    dancing = 2
    variety = 3
    style = 4

    def display_name(self):
        return self.name.capitalize()

    @classmethod
    def from_display_name(cls, display_name):
        enum_name = display_name.lower()
        return getattr(cls, enum_name, None)
