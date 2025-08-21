from strenum import StrEnum

class Visibility(StrEnum):
    All = 'All'
    Company = 'Company'
    Owner = 'Owner'

class Editability(StrEnum):
    All = 'All'
    Company = 'Company'
    Owner = 'Owner'
    Locked = 'Locked'
