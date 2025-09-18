from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    trainer = "trainer"
    trainee = "trainee"

class GenderEnum(str, Enum):
    male = "male"
    female = "female"