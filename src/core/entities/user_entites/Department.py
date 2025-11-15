from enum import Enum


class Department(str, Enum):
    HR = "hr"
    IT = "it"
    SALES = "sales"
    SUPPORT = "support"
    MANAGEMENT = "management"