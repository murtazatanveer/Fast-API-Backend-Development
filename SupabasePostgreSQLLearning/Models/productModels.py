from Configuration.supabaseClient import Base
from sqlalchemy import Column, String, Integer, ForeignKey

from Utils.genUid import generateUid

class ProductModel(Base):
    __tablename__ = "products"

    pid = Column("pid", String(36), primary_key=True, default=generateUid, index=True)
    
    uid = Column("uid", String(36), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False,index=True)
    
    name = Column("name", String(100), nullable=False)
    quantity = Column("quantity", Integer, nullable=False)
    price = Column("price", Integer, nullable=False)