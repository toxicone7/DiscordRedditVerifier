from enum import Enum


# An Enum to account for ReturnTypes
class ReturnType(Enum):
    Accepted = 1
    Declined = 2
    NoSuchUsername = 3
    AlreadyInDiscord = 4
