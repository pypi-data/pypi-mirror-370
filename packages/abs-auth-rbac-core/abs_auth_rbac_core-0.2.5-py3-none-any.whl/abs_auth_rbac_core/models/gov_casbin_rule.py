from casbin_sqlalchemy_adapter import CasbinRule as BaseCasbinRule
from sqlalchemy import Column, Integer, String


class GovCasbinRule(BaseCasbinRule):
    __tablename__ = "gov_casbin_rule"
    __mapper_args__ = {"polymorphic_identity": "gov_casbin_rule", "concrete": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))

    def __init__(self, ptype=None, v0=None, v1=None, v2=None, v3=None, v4=None, v5=None):
        self.ptype = ptype
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.v5 = v5


    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3):
            if v is None:
                break
            arr.append(v)
        return ", ".join(arr)
